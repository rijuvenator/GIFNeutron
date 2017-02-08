import numpy as np
import Gif.TestBeamAnalysis.OldPlotter as Plotter
import Gif.TestBeamAnalysis.Primitives as Primitives
import ROOT as R

R.gROOT.SetBatch(True)

#xmin = [0, 0]
#ymin = [0, 0]
#xmax = [100, 125]
#ymax = [50 , 110]
xmin = [25, 8]
xmax = [72,38]
ymin = [37,55]
ymax = [43,65]
h = {}
h[1  ] = R.TH2F('h1','',xmax[0]-xmin[0],xmin[0],xmax[0],ymax[0]-ymin[0],ymin[0],ymax[0])
h[110] = R.TH2F('h2','',xmax[1]-xmin[1],xmin[1],xmax[1],ymax[1]-ymin[1],ymin[1],ymax[1])

f = R.TFile.Open('../../trees/ana_3284.root')
t = f.Get('GIFTree/GIFDigiTree')
for entry in t:
	E = Primitives.ETree(t, DecList=['LCT'])
	lcts = [Primitives.LCT(E, i) for i in range(len(E.lct_cham))]
	for lct in lcts:
		h[lct.cham].Fill(lct.keyHalfStrip, lct.keyWireGroup)

def makePlot(h, cham):
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

	hist = h
	# Step 1
	plot = Plotter.Plot(hist, option='colz')

	# Step 2
	canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 LCT Position')

	# Step 3
	canvas.makeLegend()

	# Step 4
	R.gStyle.SetPalette(56)
	canvas.addMainPlot(plot, addToLegend=False)
	plot.setTitles(X='keyHalfStrip', Y='keyWireGroup')
	plot.scaleTitles(0.8, axes='XYZ')
	plot.scaleLabels(0.8, axes='XYZ')
	canvas.scaleMargins(0.8, 'L')
	canvas.scaleMargins(1.4, 'R')
	canvas.makeTransparent()


	# Step 5

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.save('pdfs/area_'+str(cham)+'.pdf')
	R.SetOwnership(canvas.c, False)

makePlot(h[1  ], 1)
makePlot(h[110], 2)
