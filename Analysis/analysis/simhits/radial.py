import os, math, sys
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS

RINGLIST = ['-42', '-41', '-32', '-31', '-22', '-21', '-13', '-12', '-11', '+11', '+12', '+13', '+21', '+22', '+31', '+32', '+41', '+42']

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'GIF' : 'radial_GIF.root',
	'P5'  : 'radial_P5.root',
	'MC'  : 'radial_MC.root'
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.SetFileNames(CONFIG)
if TYPE != 'MC':
	print 'This script will only work for MC.'
	exit()

##### ANALYZER FUNCTIONS #####
# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HISTS = {}
	self.HISTS['SUM'] = R.TH1F('h'+'SUM', '', 100, 0, 10)
	for RING in RINGLIST:
		self.HISTS[RING] = R.TH1F('h'+RING, '', 100, 0, 10)
		self.HISTS[RING].SetDirectory(0)

# once per file
def analyze(self, t, PARAMS):
	TYPE = PARAMS[1]
	for idx, entry in enumerate(t):
		#if idx == 1000: break
		print 'Events:', idx, '\r',

		if TYPE == 'P5':
			if      t.Z_mass <= 98. and t.Z_mass >= 84.\
				and t.nJets20 == 0\
				and t.Z_pT <= 20.:
				pass
			else:
				continue

		E = Primitives.ETree(t, DecList=['SIMHIT'])
		simhits  = [Primitives.SimHit(E, i) for i in range(len(E.sim_cham))]

		for sh in simhits:
			ch = CH.Chamber(sh.cham)
			r = (sh.globalPos['x']**2. + sh.globalPos['y']**2.)**0.5
			#print ch.display('ME{E}{S}/{R}/{C}'), r/100.
			self.HISTS[ch.display('{E}{S}{R}')].Fill(r/100.)
			self.HISTS['SUM'].Fill(r/100.)

	self.F_OUT.cd()
	self.HISTS['SUM'].Write()
	for RING in RINGLIST:
		self.HISTS[RING].Write()

def cleanup(self, PARAMS):
	print ''

# if file is already made
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	self.HISTS['SUM'] = f.Get('h'+'SUM')
	for RING in RINGLIST:
		self.HISTS[RING] = f.Get('h'+RING)
		self.HISTS[RING].SetDirectory(0)

#### RUN ANALYSIS #####
R.gROOT.SetBatch(True)
methods = ['analyze', 'load', 'setup', 'cleanup']
kwargs = {\
	'PARAMS'     : [OFN, TYPE],
	'F_DATAFILE' : FDATA
}
if TYPE == 'GIF':
	# extra argument to constructor for GIF analyzer
	kwargs['ATTLIST'] = [4.6]

# override class methods and run analysis!
Analyzer = getattr(MS, TYPE+'Analyzer')
for method in methods:
	setattr(Analyzer, method, locals()[method])
data = Analyzer(**kwargs)

##### MAKEPLOT FUNCTIONS #####
def makePlots(HISTS):
	for STATION in ['1', '2', '3', '4']:
		plots = {}
		for RING in RINGLIST:
			if RING[1] == STATION:
				plots[RING] = Plotter.Plot(HISTS[RING], option='hist', legName='ME'+RING.replace('-','#minus'), legType='l')
		canvas = Plotter.Canvas(logy=True, lumi='SimHit Distribution, Station '+STATION)
		for RING in sorted(plots.keys()): # do 1, 2, [3] in that order
			canvas.addMainPlot(plots[RING])
			plots[RING].SetLineColor((R.kRed if RING[0]=='+' else R.kBlue)+int(RING[2])-1)
		canvas.makeLegend()
		canvas.firstPlot.setTitles(X='Distance [m]', Y='Counts')
		canvas.firstPlot.SetMaximum(10**4)
		canvas.firstPlot.SetMinimum(0.1)
		canvas.scaleMargins(0.8, 'L')
		canvas.finishCanvas()
		canvas.save('pdfs/Radial_ME'+STATION+'.pdf')

makePlots(data.HISTS)
