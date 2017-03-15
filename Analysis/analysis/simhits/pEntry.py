import os, math, sys
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.roottools as roottools

TITLE = '_short'
#TITLE = '_GT300ns'
#TITLE=''

RINGLIST = ['11', '12', '13', '21', '22', '31', '32', '41', '42','all']
PARTICLELIST = ['muon','electron','pion','proton','other','all']

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'MC'  : 'pEntry_MC_HP_ThermalON'+TITLE+'.root'
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

##### ANALYZER FUNCTIONS #####
# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HISTS = {RING:{PARTICLE:{} for PARTICLE in PARTICLELIST} for RING in RINGLIST}
	self.HISTS2D = {RING:{PARTICLE:{} for PARTICLE in PARTICLELIST} for RING in RINGLIST}
	for RING in RINGLIST:
		for PARTICLE in PARTICLELIST:
			self.HISTS[RING]['muon']['pabsEntry']     = R.TH1F('h_'+RING+'_muon_pabsEntry',     '', 100, 0, 10)
			self.HISTS[RING]['all']['pabsEntry']      = R.TH1F('h_'+RING+'_all_pabsEntry',      '', 100, 0, 10)
			self.HISTS[RING]['electron']['pabsEntry'] = R.TH1F('h_'+RING+'_electron_pabsEntry', '', 100, 0, 0.06)
			self.HISTS[RING]['pion']['pabsEntry']     = R.TH1F('h_'+RING+'_pion_pabsEntry',     '', 100, 0, 3)
			self.HISTS[RING]['proton']['pabsEntry']   = R.TH1F('h_'+RING+'_proton_pabsEntry',   '', 100, 0, 10)
			self.HISTS[RING]['other']['pabsEntry']    = R.TH1F('h_'+RING+'_other_pabsEntry',    '', 100, 0, 3)
			self.HISTS2D[RING]['muon']['eVSp']     = R.TH2F('h_'+RING+'_muon_eVSp',     '', 100, 0, 10, 100, 0, 10**-5)
			self.HISTS2D[RING]['all']['eVSp']      = R.TH2F('h_'+RING+'_all_eVSp',      '', 100, 0, 10, 100, 0, 10**-5)
			self.HISTS2D[RING]['electron']['eVSp'] = R.TH2F('h_'+RING+'_electron_eVSp', '', 100, 0, 10**-4, 100, 0, 10**-4)
			self.HISTS2D[RING]['pion']['eVSp']     = R.TH2F('h_'+RING+'_pion_eVSp',     '', 100, 0, 1, 100, 0, 2*10**-5)
			self.HISTS2D[RING]['proton']['eVSp']   = R.TH2F('h_'+RING+'_proton_eVSp',   '', 100, 0, 1, 100, 0, 10**-4)
			self.HISTS2D[RING]['other']['eVSp']    = R.TH2F('h_'+RING+'_other_eVSp',    '', 100, 0, 1, 100, 0, 10**-4)

# once per file
def analyze(self, t, PARAMS):
	TYPE = PARAMS[1]
	#Primitives.SelectBranches(t, DecList=['SIMHIT'])
	for idx, entry in enumerate(t):
		#if idx == 1000: break
		print 'Events:', idx, '\r',

		E = Primitives.ETree(t, DecList=['SIMHIT'])
		# all
		simhits  = [Primitives.SimHit(E, i) for i in range(len(E.sim_cham))]
		# tof > 300 ns
		#simhits  = [Primitives.SimHit(E, i) for i in range(len(E.sim_cham)) if E.sim_tof > 300]
		# short sim hit < 0.01 cm
		#simhits  = [Primitives.SimHit(E, i) for i in range(len(E.sim_cham)) if math.sqrt(sum( [ (E.sim_entry[j][i]-E.sim_exit[j][i])**2 for j in [0,1,2] ] )) < 0.01 ]

		for sh in simhits:
			ch = CH.Chamber(sh.cham)
			pabs = sh.pabsEntry
			eloss = sh.energyLoss
			if abs(sh.particleID) == 13:
				PARTICLE='muon'
				m = 105*10**-3
			elif abs(sh.particleID) == 11:
				PARTICLE='electron'
				m = 511*10**-6
			elif abs(sh.particleID) == 211:
				PARTICLE='pion'
				140*18**-3
			elif abs(sh.particleID) == 2212:
				PARTICLE='proton'
				938*10**-3
			else:
				PARTICLE='other'
				m = 0

			#
			self.HISTS['all']['all']['pabsEntry'].Fill(pabs)
			self.HISTS['all'][PARTICLE]['pabsEntry'].Fill(pabs)
			self.HISTS[ch.display('{S}{R}')]['all']['pabsEntry'].Fill(pabs)
			self.HISTS[ch.display('{S}{R}')][PARTICLE]['pabsEntry'].Fill(pabs)
			# 
			entryE = math.sqrt(pabs**2 + m**2) - m
			self.HISTS2D['all']['all']['eVSp'].Fill(entryE,eloss)
			self.HISTS2D['all'][PARTICLE]['eVSp'].Fill(entryE,eloss)
			self.HISTS2D[ch.display('{S}{R}')]['all']['eVSp'].Fill(entryE,eloss)
			self.HISTS2D[ch.display('{S}{R}')][PARTICLE]['eVSp'].Fill(entryE,eloss)

	self.F_OUT.cd()
	for RING in RINGLIST:
		for PARTICLE in PARTICLELIST:
			self.HISTS[RING][PARTICLE]['pabsEntry'].Write()
			self.HISTS2D[RING][PARTICLE]['eVSp'].Write()

def cleanup(self, PARAMS):
	print ''

# if file is already made
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {RING:{PARTICLE:{} for PARTICLE in PARTICLELIST} for RING in RINGLIST}
	for RING in RINGLIST:
		for PARTICLE in PARTICLELIST:
			self.HISTS[RING][PARTICLE]['pabsEntry'] = f.Get('h_'+RING+'_'+PARTICLE+'_pabsEntry')
			self.HISTS[RING][PARTICLE]['pabsEntry'].SetDirectory(0)
			self.HISTS2D[RING][PARTICLE]['eVSp'] = f.Get('h_'+RING+'_'+PARTICLE+'_eVSp')
			self.HISTS2D[RING][PARTICLE]['eVSp'].SetDirectory(0)

#### RUN ANALYSIS #####
R.gROOT.SetBatch(True)
methods = ['analyze', 'load', 'setup', 'cleanup']
F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/HP_Thermal_ON/ana_neutronMC_HPThermalON.root'
kwargs = {\
	'PARAMS'     : [OFN, TYPE],
	'F_DATAFILE' : FDATA,
	'INPUTFILE'  : F_MCDATA
}

# override class methods and run analysis!
Analyzer = getattr(MS, TYPE+'Analyzer')
for method in methods:
	setattr(Analyzer, method, locals()[method])
data = Analyzer(**kwargs)

##### MAKEPLOT FUNCTIONS #####
def makePlots(HISTS):
	for RING in RINGLIST:
		for PARTICLE in PARTICLELIST:
			for logy in [True,False]:
				hist = roottools.DrawOverflow(HISTS[RING][PARTICLE]['pabsEntry'])
				plot = Plotter.Plot(hist,option='hist')
				canvas = Plotter.Canvas(lumi='SimHit Momentum : '+str(PARTICLE)+' : ME'+str(RING),logy=logy)
				canvas.addMainPlot(plot)
				plot.setTitles(X='Momentum [GeV]', Y='Counts')
				plot.SetFillColor(R.kOrange)
				#canvas.makeLegend()
				canvas.makeTransparent()
				canvas.finishCanvas()
				name = 'pabsEntry_'+str(RING)+'_'+str(PARTICLE) + ('_logy' if logy else '') + TITLE
				canvas.save('pdfs/'+name,['.pdf'])
				canvas.deleteCanvas()
			
def makePlots2D(HISTS):
	for RING in RINGLIST:
		for PARTICLE in PARTICLELIST:
			hist = HISTS[RING][PARTICLE]['eVSp']
			plot = Plotter.Plot(hist,option='colz')
			canvas = Plotter.Canvas(lumi='SimHit Energy Loss vs. Momentum : '+str(PARTICLE)+' : ME'+str(RING))
			canvas.addMainPlot(plot)
			plot.setTitles(X='Entry Energy [GeV]', Y='Energy Loss [GeV]')
			canvas.moveExponent()
			canvas.makeTransparent()
			canvas.finishCanvas()
			name = 'eVSp_'+str(RING)+'_'+str(PARTICLE) + TITLE
			canvas.save('pdfs/'+name,['.pdf'])
			canvas.deleteCanvas()

makePlots(data.HISTS)
makePlots2D(data.HISTS2D)
