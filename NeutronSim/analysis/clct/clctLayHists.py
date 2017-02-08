import os
import numpy as np
import ROOT as R
import Gif.NeutronSim.Primitives as Primitives
import Gif.NeutronSim.OldPlotter as Plotter
import Gif.NeutronSim.Auxiliary as Aux
import Gif.NeutronSim.ChamberHandler as CH
import Gif.NeutronSim.MegaStruct as MS

PFN = 'output_clct.root'

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

# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	self.HISTS = {}
	FN = PARAMS
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	for ring in ringlist:
		self.HISTS[ring] = R.TH1F('h'+ring, '', 6, 1, 7)
		self.HISTS[ring].SetDirectory(0)

ringlist = ['11', '12', '13', '21', '22', '31', '32', '41', '42']

# once per file
def analyze(self, t, PARAMS):
	for idx, entry in enumerate(t):
		#if idx == 10000: break

		E = Primitives.ETree(t, DecList=['CLCT'])
		clcts  = [Primitives.CLCT(E, i) for i in range(len(E.clct_cham))]

		for clct in clcts:
			c = CH.Chamber(clct.cham)
			self.HISTS[c.display('{S}{R}')].Fill(clct.quality)

	self.F_OUT.cd()
	for ring in ringlist:
		self.HISTS[ring].Write()

# if file is already made
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	for ring in ringlist:
		self.HISTS[ring] = f.Get('h'+ring)
		self.HISTS[ring].SetDirectory(0)

# override class methods
R.gROOT.SetBatch(True)
MS. P5Analyzer.analyze = analyze
MS. P5Analyzer.load = load
MS. P5Analyzer.setup = setup

# run analysis!
pdata = MS.P5Analyzer (PARAMS=PFN, F_DATAFILE=FP, RUNLIST=[282663])

##### MAKEPLOT FUNCTIONS #####
def makePlot(h, ring):
	if h.Integral() == 0: return
	plot = Plotter.Plot(h, option='hist')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.makeLegend()
	canvas.addMainPlot(plot, addToLegend=False)
	canvas.makeTransparent()
	#canvas.firstPlot.plot.SetMaximum(1.05)
	canvas.firstPlot.plot.SetMinimum(0)
	canvas.makeTransparent()
	canvas.moveExponent()

	canvas.drawText(pos=(.2, .8), text='Mean: '+'{:5.3f}'.format(h.GetMean()))


	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/CLCTQ'+'_'+ring+'.pdf')
	R.SetOwnership(canvas.c, False)

for ring in ringlist:
	makePlot(pdata.HISTS[ring], ring)
