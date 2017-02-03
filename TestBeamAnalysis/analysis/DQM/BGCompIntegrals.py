import os
import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.Plotter as Plotter
import Gif.TestBeamAnalysis.Auxiliary as Aux
import Gif.TestBeamAnalysis.ChamberHandler as CH
import Gif.TestBeamAnalysis.MegaStruct as MS

PFN = 'integrals.root'

FP = None
FP = PFN

ringlist = ['-42', '-41', '-32', '-31', '-22', '-21', '-13', '-12', '-11', '+11', '+12', '+13', '+21', '+22', '+31', '+32', '+41', '+42']
ringmap  = range(-9,0) + range(1,10)
ringdict = dict(zip(ringlist, ringmap))

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
	FN = PARAMS
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HIST = R.TH1F('h', '', 20, -10, 10)
	self.HIST.SetDirectory(0)

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

		twolcts = list(set([i for i in E.lct_cham if E.lct_cham.count(i)>1]))
		for lct in lcts:
			if lct.cham in twolcts: continue
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
							if comp.timeBin >= 1 and comp.timeBin <= 5:
								self.HIST.Fill(ringdict[cham.display('{E}{S}{R}')])

	self.F_OUT.cd()
	self.HIST.Write()

# if file is already made
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HIST = f.Get('h')
	self.HIST.SetDirectory(0)

# override class methods
R.gROOT.SetBatch(True)
MS. P5Analyzer.analyze = analyze
MS. P5Analyzer.load = load
MS. P5Analyzer.setup = setup

# run analysis!
pdata = MS.P5Analyzer (PARAMS=PFN, F_DATAFILE=FP, RUNLIST=[282663])

##### MAKEPLOT FUNCTIONS #####
def makePlot(h):
	plot = Plotter.Plot(h, option='hist')

	canvas = Plotter.Canvas(lumi='Background Comparators by Ring', cWidth=1000)

	canvas.addMainPlot(plot)

	canvas.makeTransparent()
	h.GetXaxis().SetRangeUser(-9,10)
	for ring in ringlist:
		bin_ = ringdict[ring] + 11
		h.GetXaxis().SetBinLabel(bin_, ring.replace('-','#minus'))
	plot.SetLineColor(0)
	plot.SetFillColor(R.kOrange)
	plot.scaleLabels(1.25, 'X')
	plot.setTitles(X='CSC Ring', Y='Counts')

	canvas.finishCanvas()
	canvas.save('pdfs/Integral.pdf')
	R.SetOwnership(canvas, False)

makePlot(pdata.HIST)
