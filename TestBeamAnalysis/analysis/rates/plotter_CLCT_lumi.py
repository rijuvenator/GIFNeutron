#!/usr/bin/env python

from ROOT import *
import Plotter
import numpy as np
import sys, shlex

# First argument to the script should be the "data card" filename.
dfile = sys.argv[1]

# "Data card" class. Stores the data and meta data.
# First non-commented line should be
# XTitle YTitle MainLegendName OutputFile BoolMakeFit BoolMakeSecondGraph [SecondLegendName]
# Multi-word parameters should be quoted, e.g. "X Title" YTitle "Legend Name" output.pdf 1 0
# Then follows the data. Two columns, X and Y.
# If making a second graph, separate the second set of data with a line containing only %
# Then follows the second data. Two columns, X and Y.
class Data:
	def __init__(self,data):
		f = open(data)
		paramsSet = False
		atSecond = False
		for line in f:
			if '#' == line[0]:
				continue

			if not paramsSet:
				params = shlex.split(line)
				self.xtit = params[0]
				self.ytit = params[1]
				self.leg = params[2]
				self.output = params[3]
				self.makeFit = bool(int(params[4]))
				self.makeGraph = bool(int(params[5]))
				self.leg2 = ""
				if self.makeGraph:
					self.leg2 = params[6]
				xL = []
				yL = []
				x2L = []
				y2L = []
				paramsSet = True
				continue

			if '%' in line:
				atSecond = True
				continue

			if paramsSet:
				point = [float(i) for i in line.split()]
				if not atSecond:
					self.fillPoint(xL, yL, point)
				if atSecond:
					self.fillPoint(x2L, y2L, point)
		self.x = np.array(xL)
		self.y = np.array(yL)
		self.x2 = np.array(x2L)
		self.y2 = np.array(y2L)
	
	def fillPoint(self, xarray, yarray, point):
		xarray.append(point[0])
		yarray.append(point[1])

data = Data(dfile)


# Plotting function
def makePlot(x, y, xtit, ytit, leg, output, makeFit, makeGraph, x2, y2, leg2):
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

	gr = TGraph(len(x), x, y)

	if makeFit:
		fit = TF1("fit", "[0] * pow(x,[1])", 0.1e34, 6.0e34)
		fit.SetParameter(0,1.0)
		fit.SetParameter(1,2.0)
		gr.Fit("fit")
	if makeGraph:
		gr2 = TGraph(len(x2), x2, y2)

	# Step 1: Prepare Plotter.Plot
	grplot = Plotter.Plot(gr, leg, "p","AP")
	if makeGraph:
		gr2plot = Plotter.Plot(gr2, leg2, "p", "P")

	# Step 2: Prepare Plotter.Canvas
	canvas = Plotter.Canvas("1 fb^{-1} (13 TeV)", False, 0., "Preliminary", 800, 700)

	# Step 3: Prepare legend
	canvas.makeLegend(.3,.1,"tr",0.02,0.03)

	# Step 4: Add plots
	canvas.addMainPlot(grplot,True,(True if makeGraph else False))
	if makeFit:
		fit.Draw("same")
		canvas.setFitBoxStyle(gr)
	if makeGraph:
		canvas.addMainPlot(gr2plot,False,True)

	# Step 5: Add cosmetic changes
	canvas.mainPad.SetLeftMargin(canvas.mainPad.GetLeftMargin() * 1.2)
	TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	gr.GetXaxis().SetTitle(xtit)
	gr.GetYaxis().SetTitle(ytit)
	grplot.scaleTitles(.8)
	grplot.scaleLabels(.8)
	gr.GetYaxis().SetTitleOffset(gr.GetYaxis().GetTitleOffset() * 1.5)
	gr.SetMarkerColor(kRed)
	gr.SetMarkerStyle(kFullCircle)
	gr.SetMarkerSize(2)
	if makeFit:
		fit.SetLineColor(kRed)
		fit.SetLineWidth(2)
	if makeGraph:
		gr2.SetMarkerColor(kBlue)
		gr2.SetMarkerStyle(kFullSquare)
		gr2.SetMarkerSize(2)
		gr.SetMinimum(0)
		gr.SetMaximum(1.2 * max(max(y),max(y2)))
		gr.GetXaxis().SetLimits(0, 1.2 * max(max(x),max(x2)))

	# Step 6: Add additional legend entries

	# Step 7: Make ratio plot

	# Step 8: Finish canvas (draw extra text)
	canvas.finishCanvas()

	# Draw or save output here
	canvas.c.SaveAs(output)

makePlot(data.x, data.y, data.xtit, data.ytit, data.leg, data.output, data.makeFit, data.makeGraph, data.x2, data.y2, data.leg2)
