import sys, os
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS

import Cluster as SH

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'GIF' : 'deltaZ_GIF.root',
	'P5'  : 'deltaZ_P5.root',
	'MC'  : 'deltaZ_MC.root'
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

##### IMPLEMENT ANALYZERS #####

particleList = ['all','electron','muon','proton','pion','other']
histList = ['deltaZ']

def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HISTS = {particle:{} for particle in particleList}
	for particle in self.HISTS.keys():
		for name in histList:
			self.HISTS[particle][name] = R.TH1F('hDeltaZ'+particle,'',200,-1,1)
	#self.HISTS[].SetDirectory(0)

def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {particle:{} for particle in particleList}
	histNames = ['hDeltaZ']
	for particle in self.HISTS.keys():
		for hist in histList:
			for name in histNames:
				self.HISTS[particle][hist] = f.Get(name+particle)
				self.HISTS[particle][hist].SetDirectory(0)

def analyze(self, t, PARAMS):
	for idx, entry in enumerate(t):
		#print 'Events:', idx+1, '\r',
		E = Primitives.ETree(t, DecList=['SIMHIT'])
		simhits  = [Primitives.SimHit(E, i) for i in range(len(E.sim_cham))]

		for simhit in simhits:
			deltaZ = simhit.entryPos['z'] - simhit.exitPos['z']
			# Make deltaZ by particle ID 
			self.HISTS['all']['deltaZ'].Fill(deltaZ)
			if abs(simhit.particleID)==11:
				self.HISTS['electron']['deltaZ'].Fill(deltaZ)
			elif abs(simhit.particleID)==13:
				self.HISTS['muon']['deltaZ'].Fill(deltaZ)
			elif abs(simhit.particleID)==2212:
				self.HISTS['proton']['deltaZ'].Fill(deltaZ)
			elif abs(simhit.particleID)==211:
				self.HISTS['pion']['deltaZ'].Fill(deltaZ)
			else:
				self.HISTS['other']['deltaZ'].Fill(deltaZ)
			if abs(simhit.particleID)==13:
				if deltaZ < -0.95:
					print '< -0.95',CH.Chamber(simhit.cham).display('ME{E}{S}/{R}/{C}')
				if deltaZ > 0.95:
					print '>  0.95',CH.Chamber(simhit.cham).display('ME{E}{S}/{R}/{C}')
				if deltaZ > 0.65 and deltaZ < 0.75:
					print '~  0.70',CH.Chamber(simhit.cham).display('ME{E}{S}/{R}/{C}')
				if deltaZ < -0.65 and deltaZ > -0.75:
					print '~ -0.70',CH.Chamber(simhit.cham).display('ME{E}{S}/{R}/{C}')


	self.F_OUT.cd()
	for particle in self.HISTS.keys():
		for hist in self.HISTS[particle].keys():
			self.HISTS[particle][hist].Write()

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
def makePlot(HISTS):
	for particle in HISTS.keys():
		for name in HISTS[particle].keys():
			hist = HISTS[particle][name]
			plot = Plotter.Plot(hist, legName='', legType='felp', option='hist')
			plot.setTitles(X='Entry-Exit #Delta Z',Y='N(SimHits)')
			for logy in [True,False]:
				if logy: plot.SetMinimum(0.1)
				else: plot.SetMinimum(0)
				canvas = Plotter.Canvas(lumi=particle+' #Delta Z',logy=logy)
				canvas.addMainPlot(plot)
				plot.SetFillColor(R.kOrange+1)
				if not logy: canvas.moveExponent()
				#canvas.makeLegend()
				canvas.finishCanvas()
				canvas.save('pdfs/simHit_'+name+'_'+particle + ( '_logy' if logy else ''), ['.pdf'])
				canvas.deleteCanvas()

makePlot(data.HISTS)
