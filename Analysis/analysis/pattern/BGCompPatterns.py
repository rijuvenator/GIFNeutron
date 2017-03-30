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
TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

if TYPE == 'MC': DOROAD=False

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
	for idx, entry in enumerate(t):
		#if idx == 1000: break
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

		elif TYPE == 'MC':
			import itertools

			if list(t.lct_id) == [] or list(t.comp_id) == []: continue
			E = Primitives.ETree(t, DecList=['LCT','COMP'])
			lcts  = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham ))]
			comps = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham))]

			if DOROAD:
				roadChams = BGDigi.removeDigiRoads(comps)
			else:
				roadChams = []
			
			for cham, compsGen in itertools.groupby(sorted(comps, key=lambda comp: comp.cham), key=lambda comp: comp.cham):
				if cham in roadChams: continue
				complist = [comp for comp in compsGen if comp.timeBin <= 5 and comp.timeBin >= 1]
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

##### MAKEPLOT FUNCTIONS #####
def makePlot(h):
	# get non-empty PIDs
	print 'The histogram was filled', int(h.GetEntries()), 'times'
	pdict = {}
	for i in range(512):
		if h.GetBinContent(i+1)>0:
			#print '{:3d} {:6d}'.format(i, int(h.GetBinContent(i+1)))
			pdict[i] = int(h.GetBinContent(i+1))

	# enumerate and name PIDs
	labels = [\
		1,                # Lonely
		3, 9,             # 2-Horiz, 2-Vert
		10, 17,           # 2+Diag, 2-Diag
		11, 19, 25, 26,   # Gamma, Corner, L, J
		14, 28, 35, 49,   # Gun-R, Dog-R, Gun-L, Dog-L
		21, 42, 81, 138,  # C-U, C-D, C-L, C-R
		56, 73,           # 3-Horiz, 3-Vert
		74, 82, 137, 145, # Peri-TR, Peri-BL, Peri-BR, Peri-TL
		84, 273           # 3+Diag, 3-Diag
	]
	# fill empties and see if any are missing
	for label in labels:
		if label not in pdict.keys():
			pdict[label] = 0
	print 'List of new IDs are:', [i for i in pdict.keys() if i not in labels]

	# make multiple histograms based on number of hits
	binslices = {
		1 : range(1 , 2 ),
		2 : range(2 , 6 ),
		3 : range(6 , 26),
	}

	hists = {}
	for ncomps in binslices.keys():
		hists[ncomps] = R.TH1F('hists'+str(ncomps), '', len(labels), 0, len(labels))
		for bin_ in binslices[ncomps]:
			hists[ncomps].SetBinContent(bin_, pdict[labels[bin_-1]])
	for bin_, label in enumerate(labels):
		hists[1].GetXaxis().SetBinLabel(bin_+1, str(label))
	
	# make the plot and canvas objects and add the plots
	plots = {}
	for ncomps in binslices.keys():
		plots[ncomps] = Plotter.Plot(hists[ncomps], option='hist', legName=str(ncomps)+' hits', legType='f')

	canvas = Plotter.Canvas(lumi='Background Comparators Pattern ID', cWidth=1500, logy=True)
	R.gStyle.SetLineWidth(1)

	for ncomps in binslices.keys():
		canvas.addMainPlot(plots[ncomps])

	# decorate and format
	canvas.makeTransparent()
	canvas.scaleMargins(0.5, 'L')
	canvas.firstPlot.setTitles(X='Pattern ID', Y='Counts')
	canvas.firstPlot.scaleLabels(1.25, 'X')
	canvas.firstPlot.scaleTitleOffsets(0.6, 'Y')
	canvas.firstPlot.SetMaximum(10**math.ceil(math.log(canvas.firstPlot.GetMaximum(),10)) - 1)
	canvas.firstPlot.SetMinimum(10**-1 + 0.0001)

	# move legend
	canvas.scaleMargins(2., 'R')
	canvas.makeLegend()
	canvas.legend.moveLegend(X=.16)

	# colors
	colors = {1 : R.kGreen, 2 : R.kBlue, 3 : R.kOrange, 4 : R.kRed}
	for ncomps in binslices.keys():
		plots[ncomps].SetLineWidth(0)
		plots[ncomps].SetFillColor(colors[ncomps])

	# two neighboring comparators; should be suppressed
	shades = R.TH1F('shades','',len(labels), 0, len(labels))
	bins = [3, 11, 19, 25, 26, 14, 28, 35, 49, 56]
	for bin_ in bins:
		shades.SetBinContent(labels.index(bin_)+1, canvas.firstPlot.GetMaximum())
	shades.SetLineWidth(0)
	shades.SetFillStyle(3004)
	shades.SetFillColorAlpha(R.kBlack, 0.5)
	shades.Draw('same')
	for ncomps in binslices.keys():
		plots[ncomps].Draw('same')

	# grouping lines
	ymin = canvas.firstPlot.GetMinimum()
	ymax = canvas.firstPlot.GetMaximum()
	lines = []
	bins = [1, 3, 9, 17, 19, 26, 49, 138, 73, 145]
	for bin_ in bins:
		lines.append(R.TLine(labels.index(bin_)+1, ymin, labels.index(bin_)+1, ymax))
		lines[-1].Draw()

	# finish up
	canvas.finishCanvas()
	canvas.save('pdfs/BGPatterns_{TYPE}.pdf'.format(TYPE=TYPE))
	R.SetOwnership(canvas, False)

makePlot(data.HIST)
