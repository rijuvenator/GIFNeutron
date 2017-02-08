import os
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.OldPlotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS

PFN = 'hotWires.root'

FP = None
#FP = PFN

clist = range(-18, 0) + range(1, 19)

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

# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	self.HISTS = {}
	FN = PARAMS
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	for c in clist:
		self.HISTS[c] = R.TH1F('h'+str(c), '', 160, 1, 161)
		self.HISTS[c].SetDirectory(0)

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
			cham = CH.Chamber(lct.cham)
			if cham.display('{S}{R}') != '21' : continue
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
							if comp.timeBin >= 1 and comp.timeBin <= 5:
								self.HISTS[cham.endcap * cham.chamber].Fill(comp.staggeredHalfStrip)

	self.F_OUT.cd()
	for c in clist:
		self.HISTS[c].Write()

# if file is already made
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	for c in clist:
		self.HISTS[c] = f.Get('h'+str(c))
		self.HISTS[c].SetDirectory(0)

# override class methods
R.gROOT.SetBatch(True)
MS. P5Analyzer.analyze = analyze
MS. P5Analyzer.load = load
MS. P5Analyzer.setup = setup

# run analysis!
pdata = MS.P5Analyzer (PARAMS=PFN, F_DATAFILE=FP, RUNLIST=[282663])

##### MAKEPLOT FUNCTIONS #####
def makePlot(h, ch):
	if h.Integral() == 0: return
	plot = Plotter.Plot(h, option='hist')
	canvas = Plotter.Canvas(lumi=ch.display('ME{E}{S}/{R}/{C}'), logy=False)
	canvas.makeLegend()
	canvas.addMainPlot(plot, addToLegend=False)
	canvas.makeTransparent()
	canvas.firstPlot.plot.SetMinimum(0)
	canvas.firstPlot.plot.SetMaximum(20)
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/HotStrips'+'_'+ch.display('ME{E}{S}{R}_{C}')+'.pdf')
	R.SetOwnership(canvas.c, False)

for c in clist:
	ch = CH.Chamber(108+(c if c>0 else 300+abs(c)))
	makePlot(pdata.HISTS[c], ch)

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
