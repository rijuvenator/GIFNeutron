import os, math, sys
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi

DOZJETS = False
DOGAP   = True
DOROAD  = True
GAP     = 35

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'GIF' : 'bgpatterns_GIF.root',
	'P5'  : 'bgpatterns_P5.root',
	'MC'  : 'bgpatterns_MC.root'
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA, REMAINDER = MS.ParseArguments(CONFIG, extraArgs=True)

NUM = REMAINDER[0]
START = int(REMAINDER[1])
END = int(REMAINDER[2])

OFN = OFN.replace('.root', '_'+NUM+'.root')
FDATA = OFN if FDATA is not None else None

if FDATA is not None:
	print 'Use the other script!!'
	exit()

##### CLUSTER CLASSES #####
class Cluster(object):
	def __init__(self, complist):
		self.complist = complist
		SHSList = [comp.staggeredHalfStrip for comp in self.complist]
		LAYList = [comp.layer              for comp in self.complist]
		self.TL = (min(SHSList), max(LAYList))
		self.H = max(LAYList) - min(LAYList) + 1
		self.PID = self.PatternID()
		self.edges = {'T':max(LAYList), 'R':max(SHSList), 'B':min(LAYList), 'L':min(SHSList)}

	# Pattern ID function
	def PatternID(self):
		# skip if cluster size > 3 high
		if self.H > 3:
			return -1
		id_ = 0

		# definition of bits (wrt TL)
		# 0 1 2
		# 3 4 5
		# 6 7 8
		bits = (\
			( 0, 0), # 0
			(+1, 0), # 1
			(+2, 0), # 2
			( 0,-1), # 3
			(+1,-1), # 4
			(+2,-1), # 5
			( 0,-2), # 6
			(+1,-2), # 7
			(+2,-2)  # 8
		)
		# compute ID
		for c in self.complist:
			for bit,(SHS,LAY) in enumerate(bits):
				if  int(c.staggeredHalfStrip) == int(self.TL[0]) + SHS\
				and int(c.layer             ) == int(self.TL[1]) + LAY:
					id_ = id_ | (1<<bit) # turn on bit
		
		return id_

class ClusterCollection(object):
	def __init__(self, complist):
		self.complist = complist
		self.ClusterList = []
		# for keeping track of which comparators are already in a cluster
		self.compcopy = self.complist[:]
		# loop through the comparators that are still in compcopy, find cluster
		# remove from comp copy, make Cluster, repeat until loop ends
		for comp in self.complist:
			if comp not in self.compcopy: continue
			cluster = [comp]
			self.findCluster(comp, cluster)
			for thisComp in cluster:
				self.compcopy.remove(thisComp)
			self.ClusterList.append(Cluster(cluster))
	
	def findCluster(self, keycomp, cluster):
		# find cluster: if comp in cluster, ignore, else, if nearby, add to cluster, recurse until loop ends
		for comp in self.compcopy:
			if comp in cluster: continue
			if abs(comp.staggeredHalfStrip-keycomp.staggeredHalfStrip) <= 1 and abs(comp.layer-keycomp.layer) <= 1:
				cluster.append(comp)
				self.findCluster(comp, cluster)

##### ANALYZER FUNCTIONS #####
# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HIST = R.TH1F('h', '', 512, 0, 512)
	self.HIST.SetDirectory(0)

# once per file
def analyze(self, t, PARAMS):
	TYPE = PARAMS[1]
	Primitives.SelectBranches(t, DecList=['LCT','COMP','WIRE'], branches=['Event_RunNumber', 'Event_BXCrossing'])
	#for idx, entry in enumerate(t):
	for idx in xrange(START, END+1):
		#if idx == 1000: break
		t.GetEntry(idx)
		print 'Events:', idx, '\r',

		if TYPE == 'P5':
			if DOZJETS:
				if      t.Z_mass <= 98. and t.Z_mass >= 84.\
					and t.nJets20 == 0\
					and t.Z_pT <= 20.:
					pass
				else:
					continue

			if DOGAP:
				# Only after gap BXs
				size, diff, train = self.getBunchInfo(t.Event_RunNumber, t.Event_BXCrossing, minSize=GAP)
				if size == 0: continue

			# Background comparators
			if list(t.lct_id) == [] or list(t.comp_id) == []: continue
			E = Primitives.ETree(t, DecList=['LCT','COMP'])
			lcts  = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham ))]
			comps = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham))]

			bgLCTs,oppHalfComps = BGDigi.getBGCompCandList(lcts,comps)
			if len(bgLCTs)==0: continue # skip event if there were no isolated LCTs
			if DOROAD:
				roadChams = BGDigi.removeDigiRoads(oppHalfComps)
			else:
				roadChams = []
			for lct in bgLCTs:
				# Skip Chamber if there's a background road
				if lct.cham in roadChams and DOROAD: continue
				cham = CH.Chamber(lct.cham)

				# Make clusters from remaining comps and compute PIDs
				complist = [comp for comp in oppHalfComps if comp.cham == lct.cham and comp.timeBin <= 5 and comp.timeBin >= 1]
				if complist != []:
					cc = ClusterCollection(complist)
					for cluster in cc.ClusterList:
						pid = cluster.PID
						if pid >= 0:
							self.HIST.Fill(pid)

	self.F_OUT.cd()
	self.HIST.Write()

def cleanup(self, PARAMS):
	print ''

# if file is already made
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HIST = f.Get('h')
	self.HIST.SetDirectory(0)

##### DECLARE ANALYZERS AND RUN ANALYSIS #####
R.gROOT.SetBatch(True)
METHODS = ['analyze', 'load', 'setup', 'cleanup']
ARGS = {
	'PARAMS'     : [OFN, TYPE],
	'F_DATAFILE' : FDATA
}
if TYPE == 'GIF':
	ARGS['ATTLIST'] = [float('inf')]
Analyzer = getattr(MS, TYPE+'Analyzer')
for METHOD in METHODS:
	setattr(Analyzer, METHOD, locals()[METHOD])
data = Analyzer(**ARGS)
