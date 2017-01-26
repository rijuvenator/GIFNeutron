import os
import numpy as n
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.Plotter as Plotter
import Gif.TestBeamAnalysis.Auxiliary as Aux
import Gif.TestBeamAnalysis.ChamberHandler as CH
import Gif.TestBeamAnalysis.MegaStruct as MS

GFN = 'output_gif.root'
PFN = 'output_p5.root'

FG = None
FP = None
#FG = GFN
#FP = PFN

# make sure you're not accidentally overwriting anything
if (os.path.isfile(GFN) and FG is None) or (os.path.isfile(PFN) and FP is None):
	answer = raw_input('OK to overwrite existing files? [y/n] ')
	if answer == 'y':
		print 'Overwriting files...'
	else:
		print 'Using existing files...'
		FG = GFN
		FP = PFN

# make sure the file exists
if (not os.path.isfile(GFN) and FG is not None) or (not os.path.isfile(PFN) and FP is not None):
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

# runs before file loop; open a file, delcare a hist dictionary
def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.HISTS = {}

ringlist = ['11', '12', '13', '21', '22', '31', '32', '41', '42']

# once per file
def analyze(self, t, PARAMS):
	isGIF = PARAMS[1]

	if isGIF:
		index = self.MEAS
	else:
		index = self.RUN
	
	self.HISTS[index] = {}
	self.F_OUT.cd()
	for ring in ringlist:
		self.HISTS[index][ring] = R.TH1F('h'+str(index)+ring, '', 11, 0., 11.)
		self.HISTS[index][ring].SetDirectory(0)

	for idx, entry in enumerate(t):
		if list(t.lct_id) == [] or list(t.comp_id) == []: continue
		E = Primitives.ETree(t, DecList=['LCT','COMP','WIRE'])
		lcts  = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham ))]
		comps = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham))]
		wires = [Primitives.Wire   (E, i) for i in range(len(E.wire_cham))]

	#	for comp in comps:
	#		if comp.timeBin == 0 or comp.timeBin >= 5: continue
	#		cham = CH.Chamber(comp.cham)
	#		self.HISTS[index][cham.display('{S}{R}')].Fill(comp.timeBin)
		
		twolcts = list(set([i for i in E.lct_cham if E.lct_cham.count(i)>1]))
		for lct in lcts:
			if lct.cham in twolcts: continue
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
									#if not isGIF: print '{:4d} {:s} {} {:2d}'.format(idx, cham.display('ME{E}{S}{R}{C}'), t.Event_EventNumber, comp.timeBin)
									if not isGIF: print '{:4d} {:s} {:3d} {} {:2d}'.format(idx, cham.display('ME{E}{S}{R}{C}'), cham.id, t.Event_EventNumber, comp.timeBin)
									self.HISTS[index][cham.display('{S}{R}')].Fill(comp.timeBin)
									break

	self.F_OUT.cd()
	for key in self.HISTS[index]:
		self.HISTS[index][key].Write()
	print index, 'Done'

# if file is already made
def load(self, PARAMS):
	isGIF = PARAMS[1]
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	if isGIF:
		for ATT in self.ATTLIST:
			for MEAS in self.getMeaslist(ATT):
				self.HISTS[MEAS] = {}
				for ring in ringlist:
					self.HISTS[MEAS][ring] = f.Get('h'+str(MEAS)+ring)
					self.HISTS[MEAS][ring].SetDirectory(0)
	else:
		for RUN in self.RUNLIST:
			self.HISTS[RUN] = {}
			for ring in ringlist:
				self.HISTS[RUN][ring] = f.Get('h'+str(RUN)+ring)
				self.HISTS[RUN][ring].SetDirectory(0)

# override class methods
R.gROOT.SetBatch(True)
MS.GIFAnalyzer.analyze = analyze
MS. P5Analyzer.analyze = analyze
MS.GIFAnalyzer.load = load
MS. P5Analyzer.load = load
MS.GIFAnalyzer.setup = setup
MS. P5Analyzer.setup = setup

# run analysis!
pdata = MS.P5Analyzer (PARAMS=[PFN, False], F_DATAFILE=FP, RUNLIST=[282663])
gdata = MS.GIFAnalyzer(PARAMS=[GFN, True ], F_DATAFILE=FG                  )

##### MAKEPLOT FUNCTIONS #####
def makePlot(h, id_, ring, extra):
	if h.Integral() == 0: return
	#h.Scale(1./h.Integral())
	plot = Plotter.Plot(h, option='hist')
	canvas = Plotter.Canvas(lumi='ME'+key+'_'+extra, logy=False)
	canvas.makeLegend()
	canvas.addMainPlot(plot, addToLegend=False)
	canvas.makeTransparent()
	#canvas.firstPlot.plot.SetMaximum(1.05)
	#canvas.firstPlot.plot.SetMinimum(0)
	#canvas.firstPlot.plot.SetMinimum(0.00001)
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/BGCompTime'+'_'+ring+'_'+extra+'_'+id_+'.pdf')

for RUN in [282663]: #pdata.RUNLIST:
	for key in ringlist:
		makePlot(pdata.HISTS[RUN][key], str(RUN), key, 'P5')

for ATT in gdata.ATTLIST:
	for MEAS in gdata.getMeaslist(ATT):
		for key in ringlist:
			makePlot(gdata.HISTS[MEAS][key], str(MEAS), key, 'GIF')
