from ROOT import *
import Gif.TestBeamAnalysis.Plotter as Plotter

def plotterMacro():
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

	hist1 = TH1F("h1","Test1;X Axis;Y Axis",100,-10,10)
	hist1.FillRandom("gaus",10000)
	hist2 = TH1F("h2","Test2;X Axis;Y Axis",100,-10,10)
	hist2.FillRandom("gaus",10000)

	# Step 1
	hist1plot = Plotter.Plot(hist1, "hist1LegName", "fl","hist")
	hist2plot = Plotter.Plot(hist2, "hist2LegName", "fl","hist")

	# Step 2
	canvas = Plotter.Canvas("1 fb^{-1} (13 TeV)", False, 1/3., "Preliminary", 800, 700)

	# Step 3
	canvas.makeLegend(.2)

	# Step 4
	canvas.addMainPlot(hist1plot,False)
	canvas.addMainPlot(hist2plot,False)

	# Step 5
	hist1.GetYaxis().SetTitle("Events / 1 GeV")
	hist1.SetLineColor(kBlue-9)
	hist2.SetLineColor(kRed-3)

	# Step 6
	canvas.addLegendEntry(hist1plot)
	canvas.addLegendEntry(hist2plot)

	# Step 7
	canvas.makeRatioPlot(hist1, hist2)

	# Step 8
	canvas.finishCanvas()

plotterMacro()
