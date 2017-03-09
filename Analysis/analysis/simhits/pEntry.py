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
	'MC'  : 'pEntry_MC_HP_ThermalON.root'
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)
F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/HP_Thermal_ON/ana_neutronMC_HPThermalON.root'
#F_MCDATA = None

##### ANALYZER FUNCTIONS #####
# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HISTS = {}
	self.HISTS['pabsEntry'] = R.TH1F('h'+'pabsEntry', '', 100, 0, 10)
	for RING in RINGLIST:
		self.HISTS[RING] = R.TH1F('h'+RING, '', 100, 0, 10)
		self.HISTS[RING].SetDirectory(0)

# once per file
def analyze(self, t, PARAMS):
	TYPE = PARAMS[1]
	#Primitives.SelectBranches(t, DecList=['SIMHIT'])
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
			p = sh.pabsEntry
			self.HISTS[ch.display('{E}{S}{R}')].Fill(p)
			self.HISTS['pabsEntry'].Fill(p)

	self.F_OUT.cd()
	self.HISTS['pabsEntry'].Write()
	for RING in RINGLIST:
		self.HISTS[RING].Write()

def cleanup(self, PARAMS):
	print ''

# if file is already made
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	self.HISTS['pabsEntry'] = f.Get('h'+'pabsEntry')
	for RING in RINGLIST:
		self.HISTS[RING] = f.Get('h'+RING)
		self.HISTS[RING].SetDirectory(0)

#### RUN ANALYSIS #####
R.gROOT.SetBatch(True)
methods = ['analyze', 'load', 'setup', 'cleanup']
kwargs = {\
	'PARAMS'     : [OFN, TYPE],
	'F_DATAFILE' : FDATA,
	'INPUTFILE'  : F_MCDATA
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
				HISTS[RING].Scale(1./HISTS[RING].Integral())
				plots[RING] = Plotter.Plot(HISTS[RING], option='hist', legName='ME'+RING.replace('-','#minus'), legType='l')
		canvas = Plotter.Canvas(logy=True, lumi='SimHit Distribution, Station '+STATION)
		for RING in sorted(plots.keys()): # do 1, 2, [3] in that order
			canvas.addMainPlot(plots[RING])
			plots[RING].SetLineColor((R.kRed if RING[0]=='+' else R.kBlue)+int(RING[2])-1)
		canvas.makeLegend()
		canvas.firstPlot.setTitles(X='Distance [m]', Y='Counts')
		#canvas.firstPlot.SetMaximum(10**4)
		canvas.firstPlot.SetMaximum(1)
		canvas.firstPlot.SetMinimum(10**-5)
		canvas.scaleMargins(0.8, 'L')
		canvas.makeTransparent()
		canvas.finishCanvas()
		canvas.save('pdfs/Radial_ME'+STATION+'.pdf')

makePlots(data.HISTS)
