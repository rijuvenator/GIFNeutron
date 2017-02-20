import os, math, sys
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.roottools as roottools
# 
import Cluster as SH

RINGLIST = ['-42', '-41', '-32', '-31', '-22', '-21', '-13', '-12', '-11', '+11', '+12', '+13', '+21', '+22', '+31', '+32', '+41', '+42']

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'MC'  : 'compMatch_MC.root'
	#'MC'  : 'compMatchDeltaZ_MC.root'
	#'MC'  : 'compMatchOnlyDeltaZGT0P1_MC.root'
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

##### ANALYZER FUNCTIONS #####
# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	FN = PARAMS
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HISTS = {}
	self.HISTS['All'] = R.TH1F('hAll', '', 200, 0, 200*10**-6)
	self.HISTS['Match'] = R.TH1F('hMatch', '', 200, 0, 200*10**-6)
	self.HISTS['NoMatch'] = R.TH1F('hNoMatch', '', 200, 0, 200*10**-6)


# once per file
def analyze(self, t, PARAMS):
	for idx, entry in enumerate(t):
		#if idx == 1000: break
		print 'Events:', idx, '\r',

		E = Primitives.ETree(t, DecList=['SIMHIT','COMP'])
		simhits  = [Primitives.SimHit(E, i) for i in range(len(E.sim_cham))]
		comps  = [Primitives.Comp(E, i) for i in range(len(E.comp_cham))]

		# Make simhit cluster objects
		uniqueChamList = list(set(E.sim_cham))
		for cham in uniqueChamList:
			# Get SimHit Clusters
			simHitClusters = SH.findSimHitClusters(simhits,cham)
			for layer in [1,2,3,4,5,6]:
				for cluster in simHitClusters[layer]:
					'''
					skip = False
					for dz in cluster.deltaZ:
						if abs(dz) < 0.1: skip = True
					if skip: continue
					'''
					# Compare comparators to clusters
					# Fill All energy histogram
					self.HISTS['All'].Fill(cluster.energy)
					# Find matching comparators
					for comp in comps:
						if comp.cham!=cham: continue
						if comp.layer!=layer: continue
						if cluster.matchComp(comp): 
							cluster.matchedComps.append(comp)
					if len(cluster.matchedComps)>0:
						# Fill Matched energy histogram 
						self.HISTS['Match'].Fill(cluster.energy)
					else:
						# Fill Not Matched energy histogram
						self.HISTS['NoMatch'].Fill(cluster.energy)

	self.F_OUT.cd()
	self.HISTS['All'].Write()
	self.HISTS['Match'].Write()
	self.HISTS['NoMatch'].Write()

def cleanup(self, PARAMS):
	print ''

# if file is already made
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	self.HISTS['All'] = f.Get('hAll')
	self.HISTS['Match'] = f.Get('hMatch')
	self.HISTS['NoMatch'] = f.Get('hNoMatch')
	for title in ['All','Match','NoMatch']:
		self.HISTS[title].SetDirectory(0)

#### RUN ANALYSIS #####
R.gROOT.SetBatch(True)
methods = ['analyze', 'load', 'setup', 'cleanup']
kwargs = {\
	'PARAMS'     : OFN,
	'F_DATAFILE' : FDATA
}

# override class methods and run analysis!
Analyzer = getattr(MS, TYPE+'Analyzer')
for method in methods:
	setattr(Analyzer, method, locals()[method])
data = Analyzer(**kwargs)

##### MAKEPLOT FUNCTIONS #####
def makePlots(HISTS):
	for match in ['All','Match','NoMatch']:
		if match=='All':
			title = 'All SimHit Clusters'
			color = R.kOrange+1
		elif match=='Match':
			title = 'SimHit Clusters Matched to Comparators'
			color = R.kRed
		else:
			title = 'SimHit Clusters Not Matched to Comparators'
			color = R.kBlue
		hist = roottools.DrawOverflow(HISTS[match])
		plot = Plotter.Plot(hist,option='HIST')
		plot.SetFillColor(color)
		plot.setTitles(X='SimHit Energy Loss [GeV]',Y='Counts')
		for logy in [True,False]:
			canvas = Plotter.Canvas(lumi=title,logy=logy)
			canvas.addMainPlot(plot)
			canvas.makeTransparent()
			canvas.finishCanvas()
			canvas.save('pdfs/simHitEnergy_comp'+match+ ('_logy' if logy else '') + '.pdf')
			canvas.deleteCanvas()

def makeStack(HISTS):
	stack = R.THStack('stack','')
	plotList = []
	for match in ['Match','NoMatch']:
		if match=='Match':
			title = 'Matched to Comparator'
			color = R.kRed
		else:
			title = 'Not Matched to Comparator'
			color = R.kBlue
		hist = roottools.DrawOverflow(HISTS[match])
		plot = Plotter.Plot(hist,legName=title,option='HIST',legType='f')
		plot.SetFillColor(color)
		plot.setTitles(X='SimHit Energy Loss [GeV]',Y='Counts')
		plotList.append(plot)
		stack.Add(hist)
	stackPlot = Plotter.Plot(stack,option='HIST')
	for logy in [True,False]:
		canvas = Plotter.Canvas(lumi='Energy Deposited by SimHit Clusters',logy=logy)
		canvas.addMainPlot(stackPlot,addToPlotList=False)
		stackPlot.setTitles(X='SimHit Energy Loss [GeV]',Y='Counts')
		canvas.makeLegend(pos='tr',autoOrder=False)
		for plot in plotList:
			canvas.addLegendEntry(plot)
		canvas.legend.moveLegend(X=-0.25,Y=-0.1)
		canvas.legend.resizeHeight()
		canvas.makeTransparent()
		canvas.finishCanvas()
		canvas.save('pdfs/simHitEnergy_comp_stack'+ ('_logy' if logy else '') + '_OnlyDeltaZGT0P1' ,['.pdf'])
		canvas.deleteCanvas()

makePlots(data.HISTS)
makeStack(data.HISTS)