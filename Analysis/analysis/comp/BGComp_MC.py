import sys, os
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS

MS.F_MCDATA = '$WS/public/Neutron/hacktrees2/hacktree.root'
RINGLIST = ['11', '12', '13', '21', '22', '31', '32', '41', '42']

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'MC'  : 'BGComp_MC.root'
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

##### IMPLEMENT ANALYZERS #####
def analyze(self, t, PARAMS):
	Primitives.SelectBranches(t, DecList=['COMP'])
	for idx, entry in enumerate(t):
		print 'Events:', idx+1, '\r',
		E = Primitives.ETree(t, DecList=['COMP'])
		comps = [Primitives.Comp(E, i) for i in range(len(E.comp_cham))]

		for comp in comps:
			cham = CH.Chamber(comp.cham)
			self.HISTS[cham.display('{S}{R}')]['time'].Fill(comp.timeBin)
			self.HISTS[cham.display('{S}{R}')]['occ' ].Fill(comp.staggeredHalfStrip)

	self.F_OUT.cd()
	for ring in RINGLIST:
		self.HISTS[ring]['time'].Write()
		self.HISTS[ring]['occ' ].Write()

def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	for ring in RINGLIST:
		self.HISTS[ring] = {
			'time' : f.Get('t'+ring),
			'occ'  : f.Get('o'+ring),
		}
		self.HISTS[ring]['time'].SetDirectory(0)
		self.HISTS[ring]['occ' ].SetDirectory(0)

def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HISTS = {}
	for ring in RINGLIST:
		cham = CH.Chamber(CH.serialID(1, int(ring[0]), int(ring[1]), 1))
		bins = cham.nstrips*2+2
		self.HISTS[ring] = {
			'time': R.TH1F('t'+ring, '', 10, 0., 10.),
			'occ' : R.TH1F('o'+ring, '', bins, 0., bins),
		}
		self.HISTS[ring]['time'].SetDirectory(0)
		self.HISTS[ring]['occ' ].SetDirectory(0)

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
def makePlot(hist, ring, tag):
	plot = Plotter.Plot(hist, legName='', legType='l', option='hist')
	canvas = Plotter.Canvas(lumi='ME'+ring)
	canvas.addMainPlot(plot)
	canvas.finishCanvas()
	canvas.save('pdfs/BGCompMC'+tag+'_'+ring+'.pdf')

for ring in RINGLIST:
	makePlot(data.HISTS[ring]['time'], ring, 'time')
	makePlot(data.HISTS[ring]['occ' ], ring, 'occ' )
