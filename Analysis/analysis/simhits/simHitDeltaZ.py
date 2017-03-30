'''
Analysis if simhit entry and exit position differences
'''
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
histList2D = ['dZdR','dZenergy']

def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HISTS = {particle:{} for particle in particleList}
	self.HISTS2D = {particle:{} for particle in particleList}
	for particle in self.HISTS2D.keys():
		self.HISTS2D[particle]['dZdR']              = R.TH2F('hDZDR'+particle,             '',200,-1,1,200,0,-1)
		self.HISTS2D[particle]['dZdRZoom']          = R.TH2F('hDZDRZoom'+particle,         '',200,-0.005,0.005,200,0,0.01)
		self.HISTS2D[particle]['dZenergy']          = R.TH2F('hDZenergy'+particle,         '',200,-1,1,200,0,-1)#200*10**-6)
		self.HISTS2D[particle]['dZenergyZoom']      = R.TH2F('hDZenergyZoom'+particle,     '',200,-0.01,0.01,200,0,15*10**-6)
		self.HISTS2D[particle]['dZdRCutEnergy']     = R.TH2F('hDZDRCutEnergy'+particle,    '',200,-1,1,200,0,5*10**-6)
		self.HISTS2D[particle]['dZdRCutEnergyZoom'] = R.TH2F('hDZDRCutEnergyZoom'+particle,'',200,-0.01,0.01,200,0,5*10**-6)
	for particle in self.HISTS.keys():
		self.HISTS[particle]['deltaZ'] = R.TH1F('hDeltaZ'+particle,'',200,-1,1)
	#self.HISTS[].SetDirectory(0)

def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {particle:{} for particle in particleList}
	self.HISTS2D = {particle:{} for particle in particleList}
	histNames = ['hDeltaZ']
	histNames2D = ['hDZDR','hDZenergy','hDZDRZoom','hDZenergyZoom','hDZDRCutEnergy','hDZDRCutEnergyZoom']
	for particle in self.HISTS.keys():
		for hist in histList:
			for name in histNames:
				self.HISTS[particle][hist] = f.Get(name+particle)
				self.HISTS[particle][hist].SetDirectory(0)
		for hist in histList2D:
			self.HISTS2D[particle]['dZdR'] = f.Get('hDZDR'+particle)
			self.HISTS2D[particle]['dZdR'].SetDirectory(0)
			self.HISTS2D[particle]['dZdRZoom'] = f.Get('hDZDRZoom'+particle)
			self.HISTS2D[particle]['dZdRZoom'].SetDirectory(0)
			self.HISTS2D[particle]['dZenergy'] = f.Get('hDZenergy'+particle)
			self.HISTS2D[particle]['dZenergy'].SetDirectory(0)
			self.HISTS2D[particle]['dZenergyZoom'] = f.Get('hDZenergyZoom'+particle)
			self.HISTS2D[particle]['dZenergyZoom'].SetDirectory(0)
			self.HISTS2D[particle]['dZdRCutEnergy'] = f.Get('hDZDRCutEnergy'+particle)
			self.HISTS2D[particle]['dZdRCutEnergy'].SetDirectory(0)
			self.HISTS2D[particle]['dZdRCutEnergyZoom'] = f.Get('hDZDRCutEnergyZoom'+particle)
			self.HISTS2D[particle]['dZdRCutEnergyZoom'].SetDirectory(0)

def analyze(self, t, PARAMS):
	#Primitives.SelectBranches(t,DecList=['SIMHIT'])
	for idx, entry in enumerate(t):
		print 'Events:', idx+1, '\r',
		E = Primitives.ETree(t, DecList=['SIMHIT'])
		simhits  = [Primitives.SimHit(E, i) for i in range(len(E.sim_cham))]

		for simhit in simhits:
			deltaZ = simhit.entryPos['z'] - simhit.exitPos['z']
			deltaX = simhit.entryPos['x'] - simhit.exitPos['x']
			deltaY = simhit.entryPos['y'] - simhit.exitPos['y']
			deltaR = (deltaX**2 + deltaY**2)**0.5
			energy = simhit.energyLoss
			# Make deltaZ by particle ID 
			self.HISTS['all']['deltaZ'].Fill(deltaZ)
			self.HISTS2D['all']['dZdR'].Fill(deltaZ,deltaR)
			self.HISTS2D['all']['dZdRZoom'].Fill(deltaZ,deltaR)
			self.HISTS2D['all']['dZenergy'].Fill(deltaZ,energy)
			self.HISTS2D['all']['dZenergyZoom'].Fill(deltaZ,energy)
			if deltaR < 0.004: self.HISTS2D['all']['dZdRCutEnergy'].Fill(deltaZ,energy)
			if deltaR < 0.004: self.HISTS2D['all']['dZdRCutEnergyZoom'].Fill(deltaZ,energy)
			if abs(simhit.particleID)==11:
				self.HISTS['electron']['deltaZ'].Fill(deltaZ)
				self.HISTS2D['electron']['dZdR'].Fill(deltaZ,deltaR)
				self.HISTS2D['electron']['dZdRZoom'].Fill(deltaZ,deltaR)
				self.HISTS2D['electron']['dZenergy'].Fill(deltaZ,energy)
				self.HISTS2D['electron']['dZenergyZoom'].Fill(deltaZ,energy)
				if deltaR < 0.004: self.HISTS2D['electron']['dZdRCutEnergy'].Fill(deltaZ,energy)
				if deltaR < 0.004: self.HISTS2D['electron']['dZdRCutEnergyZoom'].Fill(deltaZ,energy)
			elif abs(simhit.particleID)==13:
				self.HISTS['muon']['deltaZ'].Fill(deltaZ)
				self.HISTS2D['muon']['dZdR'].Fill(deltaZ,deltaR)
				self.HISTS2D['muon']['dZenergy'].Fill(deltaZ,energy)
				self.HISTS2D['muon']['dZdRZoom'].Fill(deltaZ,deltaR)
				self.HISTS2D['muon']['dZenergyZoom'].Fill(deltaZ,energy)
				if deltaR < 0.004: self.HISTS2D['muon']['dZdRCutEnergy'].Fill(deltaZ,energy)
				if deltaR < 0.004: self.HISTS2D['muon']['dZdRCutEnergyZoom'].Fill(deltaZ,energy)
			elif abs(simhit.particleID)==2212:
				self.HISTS['proton']['deltaZ'].Fill(deltaZ)
				self.HISTS2D['proton']['dZdR'].Fill(deltaZ,deltaR)
				self.HISTS2D['proton']['dZenergy'].Fill(deltaZ,energy)
				self.HISTS2D['proton']['dZdRZoom'].Fill(deltaZ,deltaR)
				self.HISTS2D['proton']['dZenergyZoom'].Fill(deltaZ,energy)
				if deltaR < 0.004: self.HISTS2D['proton']['dZdRCutEnergy'].Fill(deltaZ,energy)
				if deltaR < 0.004: self.HISTS2D['proton']['dZdRCutEnergyZoom'].Fill(deltaZ,energy)
			elif abs(simhit.particleID)==211:
				self.HISTS['pion']['deltaZ'].Fill(deltaZ)
				self.HISTS2D['pion']['dZdR'].Fill(deltaZ,deltaR)
				self.HISTS2D['pion']['dZenergy'].Fill(deltaZ,energy)
				self.HISTS2D['pion']['dZdRZoom'].Fill(deltaZ,deltaR)
				self.HISTS2D['pion']['dZenergyZoom'].Fill(deltaZ,energy)
				if deltaR < 0.004: self.HISTS2D['pion']['dZdRCutEnergy'].Fill(deltaZ,energy)
				if deltaR < 0.004: self.HISTS2D['pion']['dZdRCutEnergyZoom'].Fill(deltaZ,energy)
			else:
				self.HISTS['other']['deltaZ'].Fill(deltaZ)
				self.HISTS2D['other']['dZdR'].Fill(deltaZ,deltaR)
				self.HISTS2D['other']['dZenergy'].Fill(deltaZ,energy)
				if deltaR < 0.004: self.HISTS2D['other']['dZdRCutEnergy'].Fill(deltaZ,energy)
				if deltaR < 0.004: self.HISTS2D['other']['dZdRCutEnergyZoom'].Fill(deltaZ,energy)
			'''
			if abs(simhit.particleID)==13:
				if deltaZ < -0.95:
					print '< -0.95',CH.Chamber(simhit.cham).display('ME{E}{S}/{R}/{C}')
				if deltaZ > 0.95:
					print '>  0.95',CH.Chamber(simhit.cham).display('ME{E}{S}/{R}/{C}')
				if deltaZ > 0.65 and deltaZ < 0.75:
					print '~  0.70',CH.Chamber(simhit.cham).display('ME{E}{S}/{R}/{C}')
				if deltaZ < -0.65 and deltaZ > -0.75:
					print '~ -0.70',CH.Chamber(simhit.cham).display('ME{E}{S}/{R}/{C}')
			'''


	self.F_OUT.cd()
	for particle in self.HISTS.keys():
		for hist in self.HISTS[particle].keys():
			self.HISTS[particle][hist].Write()
		for hist in self.HISTS2D[particle].keys():
			self.HISTS2D[particle][hist].Write()

def cleanup(self, PARAMS):
	pass
	print ''

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

##### MAKE PLOTS #####
def makePlot(HISTS):
	for particle in HISTS.keys():
		for name in HISTS[particle].keys():
			hist = HISTS[particle][name]
			plot = Plotter.Plot(hist, legName='', legType='felp', option='hist')
			plot.setTitles(X='Entry-Exit #Delta Z [cm]',Y='N(SimHits)')
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

def make2DPlot(HISTS2D,histDict2D):
	for particle in HISTS2D.keys():
		for name in HISTS2D[particle].keys():
			hist = HISTS2D[particle][name]
			plot = Plotter.Plot(hist,legName='',option='COLZ')
			plot.setTitles(X='Entry-Exit #Delta Z [cm]',Y=histDict2D[name]['Y'])
			canvas = Plotter.Canvas(lumi=particle+' '+histDict2D[name]['title'])
			canvas.addMainPlot(plot)
			canvas.finishCanvas()
			canvas.save('pdfs/simHit_'+name+'_'+particle, ['.pdf'])
			canvas.deleteCanvas()

histDict2D = {
			'dZdR':{
				'title':'#Delta R vs #Delta Z',
				'Y':'#Delta R [cm]'},
			'dZdRZoom':{
				'title':'#Delta R vs #Delta Z',
				'Y':'#Delta R [cm]'},
			'dZenergy':{
				'title':'Energy loss vs #Delta Z',
				'Y':'Energy loss [GeV]'},
			'dZenergyZoom':{
				'title':'Energy loss vs #Delta Z',
				'Y':'Energy loss [GeV]'},
			'dZdRCutEnergy':{
				'title':'Energy loss vs #Delta Z for #Delta R < 0.004 cm',
				'Y':'Energy loss [GeV]'},
			'dZdRCutEnergyZoom':{
				'title':'Energy loss vs #Delta Z for #Delta R < 0.004 cm',
				'Y':'Energy loss [GeV]'},
			}

makePlot(data.HISTS)
make2DPlot(data.HISTS2D,histDict2D)
