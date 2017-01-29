import subprocess as bash
import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.Plotter as Plotter
import Gif.TestBeamAnalysis.Auxiliary as Aux
import Gif.TestBeamAnalysis.ChamberHandler as CH

CMSSW_PATH = bash.check_output('echo $CMSSW_BASE',shell=True).strip('\n') + '/src/'
GITLAB_PATH = CMSSW_PATH + 'Gif/TestBeamAnalysis/'
F_MEASGRID = GITLAB_PATH + 'analysis/datafiles/measgrid'
F_ATTENHUT = GITLAB_PATH + 'analysis/datafiles/attenhut'
F_RUNGRID  = GITLAB_PATH + 'analysis/datafiles/runlumigrid'

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
					f = R.TFile.Open(GITLAB_PATH+'trees/ana_'+str(MEAS)+'.root')
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

	# get a luminosity given a run and lumisection
	def lumi(self, run, ls):
		return self.RUNLUMIDATA[run][ls]

##### P5 ANALYZER CLASS #####
class P5Analyzer(P5MegaStruct):
	def __init__(self, F_DATAFILE=None, RUNLIST=None, PARAMS=None):
		P5MegaStruct.__init__(self)
		self.F_DATAFILE = F_DATAFILE
		self.PARAMS = PARAMS
		if RUNLIST is None:
			self.RUNLIST = self.RUNLUMIDATA.keys()
		else:
			self.RUNLIST = RUNLIST
		self.fillData()
	
	# the skeleton around the analyze function which fills a data dictionary
	def fillData(self):
		self.VALDATA = {}
		if self.F_DATAFILE is None:
			self.setup(self.PARAMS)
			for RUN in self.RUNLIST:
				self.RUN = RUN
				#f = R.TFile.Open(GITLAB_PATH+'trees/ana_'+str(RUN)+'.root')
				f = R.TFile.Open('/afs/cern.ch/user/c/cschnaib/public/GIF/ana_P5.root')
				t = f.Get('GIFTree/GIFDigiTree')
				self.analyze(t, self.PARAMS)
			self.cleanup(self.PARAMS)
		# for obtaining data dictionary from a file
		else:
			self.load(self.PARAMS)

	# get a value given a run and chamber number
	def val(self, run, cham):
		return float(self.VALDATA[run][cham])

	# get a vector of values
	def valVector(self, cham):
		return np.array([self.val(run, cham) for run in self.sortedRunList()])

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

