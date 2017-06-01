import sys, os, argparse
import subprocess as bash
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH

R.PyConfig.IgnoreCommandLineOptions = True

# Useful globals
LHC_BUNCHES = 3564

CMSSW_PATH  = bash.check_output('echo $CMSSW_BASE',shell=True).strip('\n') + '/src/'
GITLAB_PATH = CMSSW_PATH + 'Gif/Analysis/'

GIFDATA_PATH = GITLAB_PATH + 'trees_gif/'
P5DATA_PATH  = GITLAB_PATH + 'trees_p5/'
MCDATA_PATH  = GITLAB_PATH + 'trees_mc/'
F_GIFDATA    = GIFDATA_PATH + 'ana_XXXX.root'
F_P5DATA     = P5DATA_PATH  + 'ana_Neutron_P5_ALL.root'
F_MCDATA     = MCDATA_PATH  + 'ana_Neutron_MC_102100_NomTOF.root'

F_MEASGRID = GITLAB_PATH + 'analysis/datafiles/measgrid'
F_ATTENHUT = GITLAB_PATH + 'analysis/datafiles/attenhut'
F_RUNGRID  = GITLAB_PATH + 'analysis/datafiles/runlumigrid'
F_GAPDATA  = GITLAB_PATH + 'analysis/datafiles/gapdata'
F_BUNCHES  = GITLAB_PATH + 'analysis/datafiles/bunchstructures'

# Parses command-line arguments; run at the beginning of an analysis script
def ParseArguments(CONFIG, extraArgs=False):
	parser = argparse.ArgumentParser()
	parser.add_argument('TYPE'            , choices=CONFIG.keys()               , help='which data type to use')
	parser.add_argument('-r', '--recreate', dest='RECREATE', action='store_true', help='whether or not to (re)create an output data file')
	if extraArgs:
		parser.add_argument('REMAINDER'   , nargs=argparse.REMAINDER            , help='any remaining custom arguments')
	args = parser.parse_args()

	OFN = CONFIG[args.TYPE]
	if args.RECREATE:
		FDATA = None
		print '(Re)creating '+OFN+'...'
	else:
		if not os.path.isfile(OFN):
			print 'Input file', OFN, 'does not exist.'
			exit()
		FDATA = OFN

	if extraArgs:
		return args.TYPE, OFN, FDATA, args.REMAINDER
	else:
		return args.TYPE, OFN, FDATA

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
		self.fillBunches()
	
	# general fill run and lumi data function (and pileup!)
	def fillRunLumi(self):
		f = open(F_RUNGRID)
		self.RUNLUMIDATA = {}
		self.PILEUPDATA = {}
		for line in f:
			cols   = line.strip('\n').split()
			FILL   = int(cols[0])
			RUN    = int(cols[1])
			LS     = int(cols[2])
			ILUMI  = float(cols[3])*1.e33
			PILEUP = float(cols[4])
			if RUN not in self.RUNLUMIDATA.keys():
				self.RUNLUMIDATA[RUN] = {}
				self.PILEUPDATA [RUN] = {}
			self.RUNLUMIDATA[RUN]['FILL'] = FILL
			self.RUNLUMIDATA[RUN][LS    ] = ILUMI
			self.PILEUPDATA [RUN][LS    ] = PILEUP
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
		f.close()

	# general fill bunch structures function
	def fillBunches(self):
		f = open(F_BUNCHES)
		self.BUNCHDATA = {}
		for line in f:
			cols = line.strip('\n').split()
			FILL = int(cols[0])
			starts = [int(start) for start in cols[1::2]]
			trains = [int(train[1:]) for train in cols[2::2]]
			ends   = [start+train-1 for start,train in zip(starts,trains)]
			self.BUNCHDATA[FILL] = zip(starts, ends)
		f.close()

	# get a luminosity given a run and lumisection
	def lumi(self, run, ls):
		return self.RUNLUMIDATA[run][ls]

	# get a pileup given a run and lumisection
	def pileup(self, run, ls):
		return self.PILEUPDATA[run][ls]

	# get fill fraction
	def getFillFraction(self, run):
		fill = self.RUNLUMIDATA[run]['FILL']
		return sum([end-start+1 for start, end in self.BUNCHDATA[fill]])/float(LHC_BUNCHES)

	# get bunch information
	def getBunchInfo(self, run, bx, minSize=1, maxSize=3564):
		fill = self.RUNLUMIDATA[run]['FILL']
		abortGapSize = (LHC_BUNCHES-1) - self.BUNCHDATA[fill][-1][1] + self.BUNCHDATA[fill][0][0]
		size, train, diff = 0, 0, 0
		for i, (start, end) in enumerate(self.BUNCHDATA[fill]):
			if bx >= start and bx <= end:
				if i == 0:
					size = abortGapSize
				else:
					size = start - self.BUNCHDATA[fill][i-1][1] - 1
				train = end - start + 1
				diff = bx - start + 1
				break
		nextGap = self.BUNCHDATA[fill][i+1][0] - self.BUNCHDATA[fill][i][1] - 1
		if size < minSize or size > maxSize:
			return False, False, False, False
		return size, diff, train, nextGap

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

