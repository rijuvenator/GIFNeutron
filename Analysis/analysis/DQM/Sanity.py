import numpy as np
import Gif.TestBeamAnalysis.OldPlotter as Plotter
import Gif.TestBeamAnalysis.Primitives as Primitives
import ROOT as R
import sys

R.gROOT.SetBatch(True)

##### PARAMETERS #####
# Measurement List, Chamber IDs (1, 110), Event List (1 indexed)
MEASLIST = [3284, 3384]
CHAMS    = [1, 110]

##### BEGIN CODE #####
for MEAS in MEASLIST:
	f = R.TFile.Open('../../trees/ana_'+str(MEAS)+'.root')
	t = f.Get('GIFTree/GIFDigiTree')

	h = {}
	s = {}
	w = {}
	for CHAM in CHAMS:
		HS_MAX   = 230 if CHAM == 1 else 164
		WIRE_MAX = 50  if CHAM == 1 else 113
		h[CHAM]  = R.TH1F('h'+str(CHAM),'', 500          , 0, 3500    )
		s[CHAM]  = R.TH1F('s'+str(CHAM),'', HS_MAX/2 * 10, 0, HS_MAX/2)
		w[CHAM]  = R.TH1F('w'+str(CHAM),'', WIRE_MAX     , 0, WIRE_MAX)

	for entry in t:
		print t.Event_EventNumber, '\r',
		sys.stdout.flush()
		E = Primitives.ETree(t, ['RECHIT'])
		for i in range(len(E.rh_cham)):
			h[E.rh_cham[i]].Fill(E.rh_energy[i])
			s[E.rh_cham[i]].Fill((E.rh_strips[1][i] if E.rh_nStrips == 3 else E.rh_strips[0][i]) + E.rh_posStrip[i])
			w[E.rh_cham[i]].Fill(E.rh_wireGroup[i])

	def makePlot(h, CHAM, option):
		# *** USAGE:
		#  1) construct Plotter.Plot(Object, legName, legType="felp", option)
		#  2) construct Plotter.Canvas(lumi, logy, ratioFactor, extra, cWidth=800, cHeight=600)
		#  3) call Plotter.Canvas.makeLegend(lWidth=0.125, lHeight=0.2, pos="tr", lOffset=0.02, fontsize=0.04)
		#  4) call Plotter.Canvas.addMainPlot(Plot, addToLegend)
		#  5) apply any cosmetic commands here
		# *6) call Plotter.Canvas.addLegendEntry(Plot)
		# *7) call Plotter.Canvas.makeRatioPlot(top, bottom, plusminus, option, ytit, xtit)
		#  8) call Plotter.Canvas.finishCanvas()
		#
		# * = optional; if addToLegend is always true, and/or if no ratio plot needed (ratioFactor = 0), neither of these steps are required
		#
		# Plotter.Canvas class members c, mainPad, ratPad, leg, rat, and gr are available
		#

		CHAMSTR = '2' if CHAM == 110 else '1'
		hist = h

		# Step 1
		plot = Plotter.Plot(hist, option='hist P')

		# Step 2
		canvas = Plotter.Canvas(lumi='ME'+CHAMSTR+'/1')

		# Step 3
		canvas.makeLegend()

		# Step 4
		canvas.addMainPlot(plot, addToLegend=False)

		# Step 5
		hist.GetYaxis().SetTitle('Count')
		if option == 'energy':
			hist.GetXaxis().SetTitle('RecHit Energy')
		elif option == 'strip':
			hist.GetXaxis().SetTitle('Position [Strip Units]')
		elif option == 'wire':
			hist.GetXaxis().SetTitle('Wire Group Number')

		plot.scaleTitles(0.8)
		plot.scaleLabels(0.8)
		plot.scaleTitleOffsets(1.35, 'Y')
		canvas.makeTransparent()

		# Step 6

		# Step 7

		# Step 8
		canvas.finishCanvas()
		mantissa = option
		canvas.save('pdfs/'+mantissa+'_'+str(MEAS)+'_'+CHAMSTR+'.pdf')
		R.SetOwnership(canvas.c, False)

	for CHAM in CHAMS:
		makePlot(h[CHAM], CHAM, 'energy')
		makePlot(s[CHAM], CHAM, 'strip')
		makePlot(w[CHAM], CHAM, 'wire')
