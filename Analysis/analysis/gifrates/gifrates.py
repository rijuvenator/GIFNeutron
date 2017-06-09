import sys, os
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi

###################################################
# A skeleton analyzer template to be used with MS #
# Setup involves specifying a CONFIG of filenames #
# Defines analyze, load, setup, cleanup for a     #
# MS class; declares the analyzer which runs it   #
# Plotting functions at the bottom                #
###################################################

#########################
## IMPLEMENT ANALYZERS ##
#########################

# analysis function; runs once per tree
def analyze(self, t, PARAMS):
	#Primitives.SelectBranches(t, DecList=[], branches=['*'])
	for idx, entry in enumerate(t):
		print 'Events:', idx+1, '\r',
		loopFunction(self, t, PARAMS)
	print '\n', self.ATT, 'Done'

# loop function; runs once per event
def loopFunction(self, t, PARAMS):
	E = Primitives.ETree(t, DecList=['WIRE'])
	wires = [Primitives.Wire(E, i) for i in range(len(E.wire_cham))]

	N = t.GetEntries()
	for wire in wires:
		if wire.timeBin < 1 or wire.timeBin > 5: continue
		self.VALDATA[wire.cham][(self.ATT, wire.layer)] += 1./N * 1./5. * 1./25. * 1.e9

# load function; loads the file specified in config instead of running analysis
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)

# pre-analysis function; declare histograms, etc.
def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	for cham in (1, 110):
		for layer in range(1, 7):
			for att in self.attVector():
				self.VALDATA[cham][(att, layer)] = 0

# post-analysis function; print extra lines, etc.
def cleanup(self, PARAMS):
	print ''
	self.F_OUT.cd()
	self.GRAPHS = { 1 : {}, 110 : {} }
	for cham in (1, 110):
		for layer in range(1, 7):
			currs = self.atomicCurrentVector(cham, layer, 1)
			counts = np.array([float(self.VALDATA[cham][(att, layer)]) for att in self.attVector()])
			self.GRAPHS[cham][layer] = R.TGraph(len(currs), counts, currs)
			self.GRAPHS[cham][layer].SetNameTitle('g_L'+str(layer)+'_C'+str(cham), 'Layer '+str(layer)+' Chamber '+str(cham)+';Hits/s;Current [#muA]')
			self.GRAPHS[cham][layer].Write()

		currs = sum([self.atomicCurrentVector(cham, layer, 1) for layer in range(1, 7)])
		counts = sum([np.array([float(self.VALDATA[cham][(att, layer)]) for att in self.attVector()]) for layer in range(1, 7)])
		self.GRAPHS[cham]['ALL'] = R.TGraph(len(counts), counts, currs)
		self.GRAPHS[cham]['ALL'].SetNameTitle('g_ALL_C'+str(cham), 'Chamber '+str(cham)+';Hits/s;Current [#muA]')
		self.GRAPHS[cham]['ALL'].Write()


########################
## PLOTTING FUNCTIONS ##
########################

def makePlot(hist):
	plot = Plotter.Plot(hist, legName='', legType='felp', option='hist')
	canvas = Plotter.Canvas(lumi='')
	canvas.addMainPlot(plot)
	canvas.makeLegend()
	canvas.finishCanvas()
	canvas.save('plot', ['.pdf', '.png'])

########################
##  MAIN MODULE CODE  ##
########################

if __name__ == '__main__':
	#### SETUP SCRIPT #####
	# Output file names
	CONFIG = {
		'GIF' : 'rates.root',
	}
	# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
	TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

	##### DECLARE ANALYZERS AND RUN ANALYSIS #####
	R.gROOT.SetBatch(True)
	METHODS = ['analyze', 'load', 'setup', 'cleanup']
	ARGS = {
		'PARAMS'     : [OFN, TYPE],
		'F_DATAFILE' : FDATA
	}
	if TYPE == 'GIF':
		ARGS['ATTLIST'] = None
	Analyzer = getattr(MS, TYPE+'Analyzer')
	for METHOD in METHODS:
		setattr(Analyzer, METHOD, locals()[METHOD])
	data = Analyzer(**ARGS)
