import numpy as n
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.Plotter as Plotter
import Gif.TestBeamAnalysis.Auxiliary as Aux
import Gif.TestBeamAnalysis.ChamberHandler as CH
import Gif.TestBeamAnalysis.MegaStruct as MS

R.gROOT.SetBatch(True)
FG = None
FP = None
FG = 'output_gif.root'
FP = 'output_p5.root' 

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

ringlist = ['11', '12', '13', '21', '22', '31', '32', '41', '42']

def analyze(self, t, PARAMS):
	self.HISTS = {}
	for ring in ringlist:
		self.HISTS[ring] = R.TH1F('h'+ring, '', 11, 0., 11.)
		self.HISTS[ring].SetDirectory(0)

	F_OUT = R.TFile(PARAMS,'RECREATE')
	F_OUT.cd()

	for idx, entry in enumerate(t):
		if list(t.lct_id) == [] or list(t.comp_id) == []: continue
		E = Primitives.ETree(t, DecList=['LCT','COMP','SEGMENT'])
		lcts  = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham ))]
		comps = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham))]
		segs  = [Primitives.Segment(E, i) for i in range(len(E.seg_cham ))]

	#	for comp in comps:
	#		if comp.timeBin == 0 or comp.timeBin >= 5: continue
	#		cham = CH.Chamber(comp.cham)
	#		self.HISTS[cham.display('{S}{R}')].Fill(comp.timeBin)

		for lct in lcts:
			cham = CH.Chamber(lct.cham)
			nHS = cham.nstrips*2
			nWG = cham.nwires
			LCTAreas = \
			{
				0 : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : 0.          , 'hs1' : nHS*0.25},
				1 : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
				2 : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
				3 : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : 0.          , 'hs1' : nHS*0.25},
			}
			CompAreas = \
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
						if comp.staggeredHalfStrip >= LCTAreas[key]['hs0'] and comp.staggeredHalfStrip <= LCTAreas[key]['hs1']:
							#print '{:4d} {:s} {} {:2d}'.format(idx, cham.display('ME{E}{S}{R}{C}'), t.Event_EventNumber, comp.timeBin)
							self.HISTS[cham.display('{S}{R}')].Fill(comp.timeBin)

	for key in self.HISTS:
		self.HISTS[key].Write()

def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	for ring in ringlist:
		self.HISTS[ring] = f.Get('h'+ring)
		self.HISTS[ring].SetDirectory(0)

MS.GIFAnalyzer.analyze = analyze
MS. P5Analyzer.analyze = analyze
MS.GIFAnalyzer.load = load
MS. P5Analyzer.load = load

gdata = MS.GIFAnalyzer(ATTLIST=[100.], PARAMS='output_gif.root', F_DATAFILE=FG)
pdata = MS.P5Analyzer (                PARAMS='output_p5.root' , F_DATAFILE=FP)

def makePlot(h, key, m):
	h.Scale(1./h.Integral() if h.Integral() != 0 else 1.)
	plot = Plotter.Plot(h, option='hist')
	canvas = Plotter.Canvas(lumi='ME'+key, logy=True)
	canvas.makeLegend()
	canvas.addMainPlot(plot, addToLegend=False)
	canvas.makeTransparent()
	canvas.firstPlot.plot.SetMaximum(1.05)
	#canvas.firstPlot.plot.SetMinimum(0)
	canvas.firstPlot.plot.SetMinimum(0.00001)
	canvas.finishCanvas()
	canvas.c.SaveAs('h'+key+'.pdf')

m = 0.
for key in ringlist:
	m = max(m, pdata.HISTS[key].GetMaximum())
	m = max(m, gdata.HISTS[key].GetMaximum())

for key in ringlist:
	makePlot(pdata.HISTS[key], key+'_P5' , m)
	makePlot(gdata.HISTS[key], key+'_GIF', m)
