import os
import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.OldPlotter as Plotter
import Gif.TestBeamAnalysis.Auxiliary as Aux
import Gif.TestBeamAnalysis.ChamberHandler as CH
import Gif.TestBeamAnalysis.MegaStruct as MS

PFN = 'output_p5.root'

FP = None
FP = PFN

# make sure you're not accidentally overwriting anything
if os.path.isfile(PFN) and FP is None:
	answer = raw_input('OK to overwrite existing files? [y/n] ')
	if answer == 'y':
		print 'Overwriting files...'
	else:
		print 'Using existing files...'
		FP = PFN

# make sure the file exists
if not os.path.isfile(PFN) and FP is not None:
	print 'Input files do not exist; exiting now...'
	exit()

# Pattern class
class Pattern():
	def __init__(self, k):
		self.khs = k
		self.pat = {\
			2  : {6:[k-5, k-4, k-3], 5:[k-4, k-3, k-2], 4:[k-2, k-1, k], 3:[k            ], 2:[k+1, k+2     ], 1:[k+3, k+4, k+5]},
			3  : {1:[k-5, k-4, k-3], 2:[k-2, k-1     ], 3:[k          ], 4:[k  , k+1, k+2], 5:[k+2, k+3, k+4], 6:[k+3, k+4, k+5]},
			4  : {6:[k-4, k-3, k-2], 5:[k-4, k-3, k-2], 4:[k-2, k-1   ], 3:[k            ], 2:[k+1, k+2     ], 1:[k+2, k+3, k+4]},
			5  : {1:[k-4, k-3, k-2], 2:[k-2, k-1     ], 3:[k          ], 4:[k+1, k+2     ], 5:[k+2, k+3, k+4], 6:[k+2, k+3, k+4]},
			6  : {6:[k-3, k-2, k-1], 5:[k-2, k-1     ], 4:[k-1, k     ], 3:[k            ], 2:[k  , k+1     ], 1:[k+1, k+2, k+3]},
			7  : {1:[k-3, k-2, k-1], 2:[k-1, k       ], 3:[k          ], 4:[k  , k+1     ], 5:[k+1, k+2     ], 6:[k+1, k+2, k+3]},
			8  : {6:[k-2, k-1, k  ], 5:[k-2, k-1, k  ], 4:[k-1, k     ], 3:[k            ], 2:[k  , k+1     ], 1:[k  , k+1, k+2]},
			9  : {1:[k-2, k-1, k  ], 2:[k-1, k       ], 3:[k          ], 4:[k  , k+1     ], 5:[k  , k+1, k+2], 6:[k  , k+1, k+2]},
			10 : {6:[k-1, k  , k+1], 5:[k-1, k  , k+1], 4:[k          ], 3:[k            ], 2:[k            ], 1:[k-1, k  , k+1]}
		}

# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	self.HISTS = {}
	FN = PARAMS
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	for ring in ringlist:
		self.HISTS[ring] = {\
			'time': R.TH1F('t'+ring, '', 10, 0., 10.),
			'lumi': R.TH1F('l'+ring, '', 30, 0., 15.e33),
			'totl': R.TH1F('a'+ring, '', 30, 0., 15.e33),
		}
		self.HISTS[ring]['time'].SetDirectory(0)
		self.HISTS[ring]['lumi'].SetDirectory(0)
		self.HISTS[ring]['totl'].SetDirectory(0)

ringlist = ['11', '12', '13', '21', '22', '31', '32', '41', '42']

# once per file
def analyze(self, t, PARAMS):
	for idx, entry in enumerate(t):
		#if idx == 10000: break

		if      t.Z_mass <= 98. and t.Z_mass >= 84.\
			and t.nJets20 == 0\
			and t.Z_pT <= 20.:
			pass
		else:
			continue

		if list(t.lct_id) == [] or list(t.comp_id) == []: continue
		E = Primitives.ETree(t, DecList=['LCT','COMP','WIRE'])
		lcts  = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham ))]
		comps = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham))]
		wires = [Primitives.Wire   (E, i) for i in range(len(E.wire_cham))]

		twolcts = list(set([i for i in E.lct_cham if E.lct_cham.count(i)>1]))
		for lct in lcts:
			if lct.cham in twolcts: continue
			nComp = 0
			cham = CH.Chamber(lct.cham)
			nHS = cham.nstrips*2
			nWG = cham.nwires
			LCTAreas = \
			{
				0 : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : 0.          , 'hs1' : nHS*0.25},
				1 : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : 0.          , 'hs1' : nHS*0.25},
				2 : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
				3 : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
			}
			OppAreas = \
			{
				0 : {'hs0' : (1-0.50)*nHS, 'hs1' : nHS     },
				1 : {'hs0' : (1-0.50)*nHS, 'hs1' : nHS     },
				2 : {'hs0' : 0.          , 'hs1' : nHS*0.50},
				3 : {'hs0' : 0.          , 'hs1' : nHS*0.50},
			}
			for key in LCTAreas.keys():
				if  lct.keyWireGroup >= LCTAreas[key]['wg0'] and lct.keyWireGroup <= LCTAreas[key]['wg1']\
				and lct.keyHalfStrip >= LCTAreas[key]['hs0'] and lct.keyHalfStrip <= LCTAreas[key]['hs1']:
					for comp in comps:
						if comp.cham != lct.cham: continue
						if comp.staggeredHalfStrip >= OppAreas[key]['hs0'] and comp.staggeredHalfStrip <= OppAreas[key]['hs1']:
							self.HISTS[cham.display('{S}{R}')]['time'].Fill(comp.timeBin)
							if comp.timeBin >= 1 and comp.timeBin <= 5:
								nComp += 1
					self.HISTS[cham.display('{S}{R}')]['lumi'].Fill(self.lumi(t.Event_RunNumber, t.Event_LumiSection), float(nComp))
					self.HISTS[cham.display('{S}{R}')]['totl'].Fill(self.lumi(t.Event_RunNumber, t.Event_LumiSection), float(1.   ))

	self.F_OUT.cd()
	for ring in ringlist:
		self.HISTS[ring]['time'].Write()
		self.HISTS[ring]['lumi'].Write()
		self.HISTS[ring]['totl'].Write()

# if file is already made
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	for ring in ringlist:
		self.HISTS[ring] = {\
			'time' : f.Get('t'+ring),
			'lumi' : f.Get('l'+ring),
			'totl' : f.Get('a'+ring),
		}
		self.HISTS[ring]['time'].SetDirectory(0)
		self.HISTS[ring]['lumi'].SetDirectory(0)
		self.HISTS[ring]['totl'].SetDirectory(0)

# override class methods
R.gROOT.SetBatch(True)
MS. P5Analyzer.analyze = analyze
MS. P5Analyzer.load = load
MS. P5Analyzer.setup = setup

# run analysis!
pdata = MS.P5Analyzer (PARAMS=PFN, F_DATAFILE=FP, RUNLIST=[282663])

##### MAKEPLOT FUNCTIONS #####
def makeTimePlot(h, ring):
	if h.Integral() == 0: return
	plot = Plotter.Plot(h, option='hist')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.makeLegend()
	canvas.addMainPlot(plot, addToLegend=False)
	canvas.makeTransparent()
	#canvas.firstPlot.plot.SetMaximum(1.05)
	canvas.firstPlot.plot.SetMinimum(0)
	#canvas.firstPlot.plot.SetMinimum(0.00001)
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/BGCompTimeNew'+'_'+ring+'.pdf')
	R.SetOwnership(canvas.c, False)

def makeLumiPlot(h1, h2, ring):
	binit = range(1, h1.GetNbinsX()+1)
	ncomps = [h1.GetBinContent(i) for i in binit]
	totals = [h2.GetBinContent(i) for i in binit]
	#lumi = np.array([])
	#lumi = h1.GetXaxis().GetCenter(lumi)
	#lumi = np.array(lumi)
	lumiA = np.array([(15.e33)/30 * (i+0.5) for i in range(30)])
	dataA = np.array([ncomp/float(total) if total != 0 else 0. for ncomp,total in zip(ncomps,totals)])
	lumi = np.array(lumiA[10:26])
	data = np.array(dataA[10:26])
	h = R.TGraph(len(lumi), lumi, data)
	#print lumi, data
	plot = Plotter.Plot(h, option='PE')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.makeLegend()
	canvas.addMainPlot(plot, addToLegend=False)
	canvas.makeTransparent()
	canvas.scaleMargins(1.25, 'R')
	canvas.firstPlot.setTitles(X='Luminosity [Hz/cm^{2}]', Y='#LT Number of Background Comparators #GT')
	canvas.firstPlot.plot.GetXaxis().SetLimits(0., 15.e33)
	canvas.firstPlot.plot.SetMinimum(0. )
	canvas.firstPlot.plot.SetMaximum(0.6)
	canvas.firstPlot.scaleTitles(0.8)
	canvas.firstPlot.scaleLabels(0.8)
	canvas.firstPlot.scaleTitleOffsets(1.2)
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/BGCompAvgNNew'+'_'+ring+'.pdf')
	R.SetOwnership(canvas.c, False)

def makeNumDum(h, ring, which):
	plot = Plotter.Plot(h, option='P')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.makeLegend()
	canvas.addMainPlot(plot, addToLegend=False)
	canvas.makeTransparent()
	canvas.scaleMargins(1.25, 'R')
	canvas.firstPlot.setTitles(X='Luminosity [Hz/cm^{2}]', Y='Number of Background Comparators' if which == 'ncomp' else 'Counts')
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/BGCompAvgNNew'+'_'+ring+'_'+which+'.pdf')
	R.SetOwnership(canvas.c, False)

for ring in ringlist:
	makeTimePlot(pdata.HISTS[ring]['time'], ring)
	makeLumiPlot(pdata.HISTS[ring]['lumi'], pdata.HISTS[ring]['totl'], ring)
	makeNumDum(pdata.HISTS[ring]['lumi'], ring, 'ncomp')
	makeNumDum(pdata.HISTS[ring]['totl'], ring, 'lumi')

##### WITH WIRES
'''
			LCTAreas = \
			{
				0 : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : 0.          , 'hs1' : nHS*0.25},
				1 : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
				2 : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
				3 : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : 0.          , 'hs1' : nHS*0.25},
			}
			OppAreas = \
			{
				0 : {'wg0' : (1-0.50)*nWG, 'wg1' : nWG     , 'hs0' : (1-0.50)*nHS, 'hs1' : nHS     },
				1 : {'wg0' : (1-0.50)*nWG, 'wg1' : nWG     , 'hs0' : 0.          , 'hs1' : nHS*0.50},
				2 : {'wg0' : 0.          , 'wg1' : nWG*0.50, 'hs0' : 0.          , 'hs1' : nHS*0.50},
				3 : {'wg0' : 0.          , 'wg1' : nWG*0.50, 'hs0' : (1-0.50)*nHS, 'hs1' : nHS     },
			}
			for key in LCTAreas.keys():
				if  lct.keyWireGroup >= LCTAreas[key]['wg0'] and lct.keyWireGroup <= LCTAreas[key]['wg1']\
				and lct.keyHalfStrip >= LCTAreas[key]['hs0'] and lct.keyHalfStrip <= LCTAreas[key]['hs1']:
					for comp in comps:
						if comp.cham != lct.cham: continue
						#if comp.timeBin == 0 or comp.timeBin >= 5: continue
						if comp.staggeredHalfStrip >= OppAreas[key]['hs0'] and comp.staggeredHalfStrip <= OppAreas[key]['hs1']:
							#self.HISTS[index][cham.display('{S}{R}')].Fill(comp.timeBin)
							for wire in wires:
								if wire.cham != comp.cham: continue
								if wire.layer != comp.layer: continue
								if abs(wire.timeBin - comp.timeBin) > 1: continue
								#if wire.number >= OppAreas[key]['wg0'] and wire.number <= OppAreas[key]['wg1']:
								if True:
									#if not isGIF: print '{:4d} {:s} {:3d} {} {:2d}'.format(idx, cham.display('ME{E}{S}{R}{C}'), cham.id, t.Event_EventNumber, comp.timeBin)
									self.HISTS[index][cham.display('{S}{R}')].Fill(comp.timeBin)
									break
'''
