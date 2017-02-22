import sys, os
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'GIF' : 'BASIC_GIF.root',
	'P5'  : 'BASIC_P5.root',
	'MC'  : 'BASIC_MC.root'
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

##### IMPLEMENT ANALYZERS #####
def analyze(self, t, PARAMS):
	#Primitives.SelectBranches(t, DecList=[], branches=['*'])
	for idx, entry in enumerate(t):
		print 'Events:', idx+1, '\r',
		E = Primitives.ETree(t)

	self.F_OUT.cd()
	#self.HISTS[].Write()

def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	#self.HISTS[].SetDirectory(0)

def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HISTS = {}
	#self.HISTS[].SetDirectory(0)

def cleanup(self, PARAMS):
	pass
	print ''

##### DECLARE ANALYZERS AND RUN ANALYSIS #####
R.gROOT.SetBatch(True)
METHODS = ['analyze', 'load', 'setup', 'cleanup']
ARGS = {\
	'PARAMS'     : [OFN, TYPE],
	'F_DATAFILE' : FDATA
}
if TYPE == 'GIF':
	ARGS['ATTLIST'] = [float('inf')]
Analyzer = getattr(MS, TYPE+'Analyzer')
for METHOD in METHODS:
	setattr(Analyzer, METHOD, locals()[METHOD])
data = Analyzer(**ARGS)

##### MAKE PLOTS #####
def makePlot(hist):
	plot = Plotter.Plot(hist, legName='', legType='felp', option='hist')
	canvas = Plotter.Canvas(lumi='')
	canvas.addMainPlot(plot)
	canvas.makeLegend()
	canvas.finishCanvas()
	canvas.save('plot', ['.pdf', '.png'])
