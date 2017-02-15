import sys, os
import subprocess as bash
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH

# Useful globals
CMSSW_PATH  = bash.check_output('echo $CMSSW_BASE',shell=True).strip('\n') + '/src/'
GITLAB_PATH = CMSSW_PATH + 'Gif/Analysis/'

GIFDATA_PATH = GITLAB_PATH + 'trees_gif/'
P5DATA_PATH  = GITLAB_PATH + 'trees_p5/'
MCDATA_PATH  = GITLAB_PATH + 'trees_mc/'
F_GIFDATA    = GIFDATA_PATH + 'ana_XXXX.root'
F_P5DATA     = P5DATA_PATH  + 'ana_P5.root'
F_MCDATA     = MCDATA_PATH  + 'ana_neutronMC.root'

F_MEASGRID = GITLAB_PATH + 'analysis/datafiles/measgrid'
F_ATTENHUT = GITLAB_PATH + 'analysis/datafiles/attenhut'
F_RUNGRID  = GITLAB_PATH + 'analysis/datafiles/runlumigrid'
F_GAPDATA  = GITLAB_PATH + 'analysis/datafiles/gapdata'

# Sets module globals; run at the beginning of an analysis script
def SetFileNames(CONFIG):
	if sorted(CONFIG.keys()) != sorted(['GIF', 'P5', 'MC']):
		print 'Only GIF, P5, and MC are allowed keys in CONFIG.'
		exit()
	SCRIPTNAME = sys.argv[0]
	USAGESTRING = 'Usage: python {SCRIPT} MODE[GIF/P5/MC] RECREATE[1,0]'.format(SCRIPT=SCRIPTNAME)
	if len(sys.argv) < 3:
		print USAGESTRING
		exit()
	else:
		TYPE = sys.argv[1]
		if TYPE in CONFIG.keys():
			OFN = CONFIG[sys.argv[1]]
		else:
			print 'Invalid argument;', USAGESTRING
			exit()

		RECREATE = sys.argv[2]
		if RECREATE == '1':
			FDATA = None
			print '(Re)creating '+OFN+'...'
		elif RECREATE == '0':
			if not os.path.isfile(OFN):
				print 'Input file', OFN, 'does not exist; exiting now...'
				exit()
			FDATA = OFN
		else:
			print 'Invalid argument;', USAGESTRING
			exit()
	return TYPE, OFN, FDATA

##### GIF MEGASTRUCT BASE CLASS #####
class GIFMegaStruct():
	def __init__(self):
		self.fillMeas()
		self.fillCurr()
	
	# general fill measurement data function
	def fillMeas(self):
		f = open(F_MEASGRID)
		self.MEASDATA = {}
		for line in f:
			cols = line.strip('\n').split()
			self.MEASDATA[float(cols[0])] = [int(j) for j in cols[1:]]
		f.close()

	# general fill current data function
	def fillCurr(self):
		f = open(F_ATTENHUT)
		self.CURRDATA = { 1 : {}, 110: {} }
		currentCham = 1
		for line in f:
			if line == '\n':
				currentCham = 110
				continue
			cols = line.strip('\n').split()
			currentMeas = int(cols[1])
			self.CURRDATA[currentCham][currentMeas] = [float(i) for i in cols[2:]]
		f.close()

	# get a current measurement given a chamber and measurement number
	def current(self, cham, meas):
		if cham == 1:
			return sum(self.CURRDATA[cham][meas])/6.0
		elif cham == 110:
			#return sum(self.CURRDATA[cham][meas][6:12])/6.0
			return sum(self.CURRDATA[cham][meas][0:6])/6.0
	
	# get a vector of attenuations
	def attVector(self, castrated=False):
		if castrated: # for comparing to Yuriy
			return np.array([33., 46., 100., float('inf')])
		else:
			return np.array(sorted(self.MEASDATA.keys()))

	# get a vector of currents
	def currentVector(self, cham, ff, castrated=False):
		return np.array([self.current(cham, self.MEASDATA[att][ff]) for att in self.attVector(castrated)])

	# get a vector of equivalent luminosities
	def lumiVector(self, cham, ff, castrated=False):
		factor = 3.e33 if cham == 1 else 5.e33
		return factor * np.array([self.current(cham, self.MEASDATA[att][ff]) for att in self.attVector(castrated)])

##### GIF ANALYZER CLASS #####
class GIFAnalyzer(GIFMegaStruct):
	def __init__(self, F_DATAFILE=None, ATTLIST=None, FFLIST=[0], PARAMS=None):
		GIFMegaStruct.__init__(self)
		self.F_DATAFILE = F_DATAFILE
		self.PARAMS = PARAMS
		if ATTLIST is None:
			self.ATTLIST = list(reversed(sorted(self.MEASDATA.keys())))
		else:
			self.ATTLIST = ATTLIST
		self.FFLIST = FFLIST
		self.fillData()

	# get measlist from ATT and FFLIST
	def getMeaslist(self, ATT):
		return [meas for i, meas in enumerate(self.MEASDATA[ATT]) if i in self.FFLIST]

	# the skeleton around the analyze function which fills a data dictionary
	def fillData(self):
		# fill a data dictionary as desired
		self.VALDATA = { 1 : {}, 110: {} }
		if self.F_DATAFILE is None:
			self.setup(self.PARAMS)
			for ATT in self.ATTLIST:
				self.ATT = ATT
				for MEAS in self.getMeaslist(ATT):
					self.MEAS = MEAS
					f = R.TFile.Open(F_GIFDATA.replace('XXXX',str(MEAS)))
					t = f.Get('GIFTree/GIFDigiTree')
					self.analyze(t, self.PARAMS)
			self.cleanup(self.PARAMS)
		# for obtaining data dictionary from a file
		else:
			self.load(self.PARAMS)

	# get a value given a chamber and measurement number
	def val(self, cham, meas):
		return float(self.VALDATA[cham][meas])

	# get a vector of values
	def valVector(self, cham, ff):
		return np.array([self.val(cham, self.MEASDATA[att][ff]) for att in self.attVector()])

	# analysis function -- gets called when F_DATAFILE is None
	def analyze(self, t, PARAMS):
		pass
		#for entry in t:
		#	E = Primitives.ETree(t)
	
	# load data from file -- gets called when F_DATAFILE is not None
	def load(self, PARAMS):
		pass

	# setup before opening any files
	def setup(self, PARAMS):
		pass

	# cleanup after analysis is done
	def cleanup(self, PARAMS):
		pass

##### P5 MEGASTRUCT BASE CLASS #####
class P5MegaStruct():
	def __init__(self):
		self.fillRunLumi()
		self.fillGaps()
	
	# general fill run and lumi data function
	def fillRunLumi(self):
		f = open(F_RUNGRID)
		self.RUNLUMIDATA = {}
		for line in f:
			cols = line.strip('\n').split()
			RUN = int(cols[1])
			LS = int(cols[2])
			ILUMI = float(cols[3])*1.e33
			if RUN not in self.RUNLUMIDATA.keys():
				self.RUNLUMIDATA[RUN] = {}
			self.RUNLUMIDATA[RUN][LS] = ILUMI
		f.close()

	# general fill gap data function
	def fillGaps(self):
		f = open(F_GAPDATA)
		self.GAPDATA = {}
		for line in f:
			cols = line.strip('\n').split()
			if cols[0] == 'RUN':
				RUN = int(cols[1])
				self.GAPDATA[RUN] = {}
			elif cols[0] == 'SIZE':
				pass
			else:
				SIZE = int(cols[0])
				START = int(cols[1])
				END = int(cols[2])
				if SIZE not in self.GAPDATA[RUN].keys():
					self.GAPDATA[RUN][SIZE] = []
				self.GAPDATA[RUN][SIZE].append((START, END))

	# get a luminosity given a run and lumisection
	def lumi(self, run, ls):
		return self.RUNLUMIDATA[run][ls]

	# determine if a BX is after a gap
	def afterGapSize(self, run, bx, minSize=1, maxSize=3564):
		for size in self.GAPDATA[run].keys():
			if size < minSize or size > maxSize: continue
			for bxrange in self.GAPDATA[run][size]:
				if bx == bxrange[1] + 1:
					return size
		return 0

##### P5 ANALYZER CLASS #####
class P5Analyzer(P5MegaStruct):
	def __init__(self, F_DATAFILE=None, PARAMS=None):
		P5MegaStruct.__init__(self)
		self.F_DATAFILE = F_DATAFILE
		self.PARAMS = PARAMS
		self.fillData()

	# the skeleton around the analyze function which fills a data dictionary
	def fillData(self):
		self.VALDATA = {}
		if self.F_DATAFILE is None:
			self.setup(self.PARAMS)
			f = R.TFile.Open(F_P5DATA)
			t = f.Get('GIFTree/GIFDigiTree')
			self.analyze(t, self.PARAMS)
			self.cleanup(self.PARAMS)
		# for obtaining data dictionary from a file
		else:
			self.load(self.PARAMS)

	# analysis function
	def analyze(self, t, PARAMS):
		pass
		#for entry in t:
		#	E = Primitives.ETree(t)

	# load data from file
	def load(self, PARAMS):
		pass

	# setup before opening any files
	def setup(self, PARAMS):
		pass

	# cleanup after analysis is done
	def cleanup(self, PARAMS):
		pass

##### NEUTRON MC MEGASTRUCT BASE CLASS #####
class MCMegaStruct():
	def __init__(self):
		pass

##### NEUTRON MC ANALYZER CLASS #####
class MCAnalyzer(MCMegaStruct):
	def __init__(self, F_DATAFILE=None, PARAMS=None):
		MCMegaStruct.__init__(self)
		self.F_DATAFILE = F_DATAFILE
		self.PARAMS = PARAMS
		self.fillData()

	# the skeleton around the analyze function which fills a data dictionary
	def fillData(self):
		self.VALDATA = {}
		if self.F_DATAFILE is None:
			self.setup(self.PARAMS)
			f = R.TFile.Open(F_MCDATA)
			t = f.Get('GIFTree/NeutronDigiTree')
			self.analyze(t, self.PARAMS)
			self.cleanup(self.PARAMS)
		# for obtaining data dictionary from a file
		else:
			self.load(self.PARAMS)

	# analysis function
	def analyze(self, t, PARAMS):
		pass
		#for entry in t:
		#	E = Primitives.ETree(t)

	# load data from file
	def load(self, PARAMS):
		pass

	# setup before opening any files
	def setup(self, PARAMS):
		pass

	# cleanup after analysis is done
	def cleanup(self, PARAMS):
		pass

