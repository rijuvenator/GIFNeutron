import numpy as np
import Gif.TestBeamAnalysis.Plotter as Plotter
import ROOT as R

R.gROOT.SetBatch(True)

xmin = [0, 0]
ymin = [0, 0]
xmax = [100, 125]
ymax = [50 , 110]
#xmin = [25, 8]
#xmax = [72,38]
#ymin = [37,55]
#ymax = [43,65]
h1 = R.TH2F('h1','',xmax[0]-xmin[0],xmin[0],xmax[0],ymax[0]-ymin[0],ymin[0],ymax[0])
h2 = R.TH2F('h2','',xmax[1]-xmin[1],xmin[1],xmax[1],ymax[1]-ymin[1],ymin[1],ymax[1])

f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/TestBeam5/ana_3284.root')
t = f.Get('GIFTree/GIFDigiTree')
for entry in t:
	one = False
	two = False
	for i, id_ in enumerate(list(t.lct_id)):
		if id_ == 1:
			h1.Fill(float(ord(t.lct_keyHalfStrip[i])), float(ord(t.lct_keyWireGroup[i])))
			one = True
		if id_ == 110:
			h2.Fill(float(ord(t.lct_keyHalfStrip[i])), float(ord(t.lct_keyWireGroup[i])))
			two = True
		if one and two:
			pass
			#break

def makePlot(h, cham):
	# *** USAGE:
	#  1) construct Plotter.Plot(Object, legName, legType="felp", option)
	#  2) construct Plotter.Canvas(lumi, logy, ratioFactor, extra, cWidth=800, cHeight=600)
	#  3) call Plotter.Canvas.makeLegend(lWidth=0.125, lHeight=0.2, pos="tr", lOffset=0.02, fontsize=0.04)
	#  4) call Plotter.Canvas.addMainPlot(Plot, isFirst, addToLegend)
	#  5) apply any cosmetic commands here
	# *6) call Plotter.Canvas.addLegendEntry(Plot)
	# *7) call Plotter.Canvas.makeRatioPlot(top, bottom, plusminus, option, ytit, xtit)
	#  8) call Plotter.Canvas.finishCanvas()
	#
	# * = optional; if addToLegend is always true, and/or if no ratio plot needed (ratioFactor = 0), neither of these steps are required
	#
	# Plotter.Canvas class members c, mainPad, ratPad, leg, rat, and gr are available
	#
	# Note: If TYPE is a TGraph and option="P", a draw option of "AP" is required for the FIRST plot (first addMainPlot)
	# So change plot.option, either to "P" after (if option="AP"), or change plot.option to "AP" before and "P" after (if option="P")
	#

	hist = h
	# Step 1
	plot = Plotter.Plot(hist, option='colz')

	# Step 2
	canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 LCT-0 Position')

	# Step 3
	canvas.makeLegend()

	# Step 4
	R.gStyle.SetPalette(53)
	canvas.addMainPlot(plot, addToLegend=False)
	hist.GetXaxis().SetTitle('keyHalfStrip')
	hist.GetYaxis().SetTitle('keyWireGroup')
	plot.scaleTitles(0.8, axes'XYZ')
	plot.scaleLabels(0.8, axes'XYZ')
	canvas.mainPad.SetLeftMargin(canvas.mainPad.GetLeftMargin() * 0.8)
	canvas.mainPad.SetRightMargin(canvas.mainPad.GetRightMargin() * 1.4)
	canvas.makeTransparent()


	# Step 5

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.save('pdfs/area_'+str(cham)+'.pdf')
	R.SetOwnership(canvas.c, False)

makePlot(h1, 1)
makePlot(h2, 2)
