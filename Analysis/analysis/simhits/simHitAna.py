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
import simHitCluster as SH

RINGLIST = ['-42', '-41', '-32', '-31', '-22', '-21', '-13', '-12', '-11', '+11', '+12', '+13', '+21', '+22', '+31', '+32', '+41', '+42']

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'GIF' : 'simHitAna_GIF.root',
	'P5'  : 'simHitAna_P5.root',
	'MC'  : 'simHitAna_MC.root'
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

if TYPE != 'MC':
	print 'Why are you trying to do a SimHit analysis on real data?'
	exit()

##### ANALYZER FUNCTIONS #####
# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	FN = PARAMS
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HISTS = {}
	# May also need to do these plots per ring...
	self.HISTS['clusterMult'] = R.TH1F('hClusterMult','',20,0,20) # draw overflow
	self.HISTS['simHitMult'] = R.TH1F('hSimHitMult','',20,0,20) # draw overflow
	self.HISTS['totalSimHit'] = R.TH1F('hTotalSimHit','',100,0,100) # draw overflow
	self.HISTS['energy'] = R.TH1F('hEnergy','',200,0,200*10**-6) # draw overflow
	### May move strip,X/wire,Y widths to own scripts
	#   still to define position 
	#   - simple average
	#   - averge weighted by energy loss
	#self.HISTS['Xpos'] = R.TH1F('hXPos','',100,0,5)
	#self.HISTS['Ypos'] = R.TH1F('hYPos','',100,0,5)
	#self.HISTS['strippos'] = R.TH1F('hStripPos','',5,0,5)
	#self.HISTS['wirepos'] = R.TH1F('hWirePos','',5,0,5)
	#self.HISTS['Xwidth'] = R.TH1F('hXWidth','',100,0,5)
	#self.HISTS['Ywidth'] = R.TH1F('hYWidth','',100,0,5)
	#self.HISTS['stripwidth'] = R.TH1F('hStripWidth','',5,0,5)
	#self.HISTS['wirewidth'] = R.TH1F('hWireWidth','',5,0,5)
	# need to fix ID bounds
	self.HISTS['ID'] = R.TH1F('hID','',4,0,4) # most common particle ID
	self.HISTS['nID'] = R.TH1F('hNID','',6,0,6) # number of different particle IDs
	self.HISTS['extraID'] = R.TH1F('hExtraID','',4,0,4) # Extra IDs in Cluster
	self.HISTS['layer'] = R.TH1F('hLayer','',6,1,7)
	# need decent tof bounds
	#self.HISTS['tof'] = R.TH1F('hTOF','', 

IDmap = {11  :{'bin':0},
		 2212:{'bin':1},
		 221 :{'bin':2}}

# once per file
def analyze(self, t, PARAMS):
	for idx, entry in enumerate(t):
		#if idx == 1000: break
		print 'Events:', idx, '\r',

		E = Primitives.ETree(t, DecList=['SIMHIT'])
		simhits  = [Primitives.SimHit(E, i) for i in range(len(E.sim_cham))]

		# Make simhit cluster objects
		uniqueChamList = list(set(E.sim_cham))
		for cham in uniqueChamList:
			# Get SimHit Clusters
			simHitClusters = SH.findSimHitClusters(simhits,cham)
			clusterMult = 0
			totalSimHits = 0
			for layer in [1,2,3,4,5,6]:
				for cluster in simHitClusters[layer]:
					#print cluster
					self.HISTS['simHitMult'].Fill(cluster.mult())
					totalSimHits += cluster.mult()
					self.HISTS['energy'].Fill(cluster.energy())
					self.HISTS['layer'].Fill(cluster.layer())
					if cluster.ID() in IDmap.keys():
						self.HISTS['ID'].Fill(IDmap[cluster.ID()]['bin']) # mode ID in cluster
					else:
						self.HISTS['ID'].Fill(3)
					self.HISTS['nID'].Fill(cluster.nID()) # number of unique IDs in cluster
					# extra IDs in cluster
					if cluster.extraIDlist() is not None:
						for extraID in cluster.extraIDlist():
							if extraID in IDmap.keys():
								self.HISTS['extraID'].Fill(IDmap[extraID]['bin'])
							else:
								self.HISTS['extraID'].Fill(3)
				clusterMult += len(simHitClusters[layer])
			self.HISTS['clusterMult'].Fill(clusterMult)
			self.HISTS['totalSimHit'].Fill(totalSimHits)

	self.F_OUT.cd()
	for name in self.HISTS.keys():
		self.HISTS[name].Write()
	'''
	self.HISTS['clusterMult'].Write()
	self.HISTS['simHitMult'].Write()
	self.HISTS['totalSimHit'].Write()
	self.HISTS['energy'].Write()
	self.HISTS['layer'].Write()
	self.HISTS['ID'].Write()
	self.HISTS['ID'].Write()
	'''

def cleanup(self, PARAMS):
	print ''

# if file is already made
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	histDict = {'clusterMult':'hClusterMult',
				'simHitMult':'hSimHitMult',
				'totalSimHit':'hTotalSimHit',
				'energy':'hEnergy',
				'layer':'hLayer',
				'ID':'hID',
				'nID':'hNID',
				'extraID':'hExtraID',
				}
	for name in histDict.keys():
		self.HISTS[name] = f.Get(histDict[name])
		self.HISTS[histDict[name]].SetDirectory(0)

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
def makePlots(HISTS,histDict):
	for histName in histDict.keys():
		hist = HISTS[histName]
		title = histDict[histName]['title']
		#hist = roottools.DrawOverflow(HISTS[match])
		plot = Plotter.Plot(hist,option='HIST')
		plot.SetFillColor(R.kOrange+1)
		plot.setTitles(X=histDict[histName]['X'],Y=histDict[histName]['Y'])
		if histName == 'extraID' or histName=='ID':
			# bin counter is +1 dont forget
			plot.GetXaxis().SetBinLabel(1,'e^{#pm}')
			plot.GetXaxis().SetBinLabel(2,'proton')
			plot.GetXaxis().SetBinLabel(3,'#pi^{#pm}')
			plot.GetXaxis().SetBinLabel(4,'other')
		for logy in [True,False]:
			canvas = Plotter.Canvas(lumi=title,logy=logy)
			canvas.addMainPlot(plot)
			if not logy: canvas.moveExponent()
			canvas.makeTransparent()
			canvas.finishCanvas()
			canvas.save('pdfs/simHit_' + histName + ('_logy' if logy else '') + '.pdf')
			canvas.deleteCanvas()

histDict = {'clusterMult' :{'title':'Number of SimHit Clusters in an Event',
							'X':'N(clusters)',
							'Y':'Counts'},
			'simHitMult'  :{'title':'Number of SimHits in a Cluster',
							'X':'N(SimHit) in Clusters',
							'Y':'Counts'},
			'totalSimHit' :{'title':'Total Number of SimHits in an Event',
							'X':'N(SimHit)',
							'Y':'Counts'},
			'energy'      :{'title':'Energy Loss by SimHit Clusters',
							'X':'Cluster Energy Loss [GeV]',
							'Y':'Counts'},
			'ID'          :{'title':'SimHit Cluster Mode Particle Type',
							'X':'Particle ID',
							'Y':'Counts'},
			'nID'         :{'title':'Number of Different SimHit Particle Types',
							'X':'Number of Particle Types',
							'Y':'Counts'},
			'extraID'     :{'title':'Extra Particle IDs in Cluster',
							'X':'Particle ID',
							'Y':'Counts'},
			'layer'       :{'title':'SimHit Cluster Layer Occupancy',
							'X':'CSC Layer',
							'Y':'Counts'},
}

makePlots(data.HISTS,histDict)
