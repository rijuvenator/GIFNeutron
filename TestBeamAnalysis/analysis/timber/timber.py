import os
from datetime import datetime as dt
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Token string')
parser.add_argument('-f', dest='file', help='Specify a TIMBER file with 4 columns', default='TB3.txt')
parser.add_argument('-t1', dest='starttime', help='Specify start time', default='2000-01-01 00:00:00.000000')
parser.add_argument('-t2', dest='stoptime', help='Specify start time', default='2020-01-01 00:00:00.000000')
parser.add_argument('-o', dest='outputFN', help='Specify output file tag', default='nom')
args = parser.parse_args()

outputFN = args.outputFN

f = open(args.file)
start = dt.strptime(args.starttime, "%Y-%m-%d %H:%M:%S.%f")
stop = dt.strptime(args.stoptime, "%Y-%m-%d %H:%M:%S.%f")

rtimes = []
scalars = []
isFirst = True
for line in f:
	if 'COUNTS' in line:
		continue
	l = line.strip('\n').split()
	tstamp = l[0] + ' ' + l[1][0:-4] + "." + str(int(l[1][-3:])*1000)
	d = dt.strptime(tstamp, "%Y-%m-%d %H:%M:%S.%f")
	if d < start:
		continue
	if d > stop:
		break
	rtimes.append(d)
	if isFirst:
		first = d
		isFirst = False
	scalars.append([float(i) for i in l[2:]])

def sinceFirst(t):
	td = t-first
	return (td.days*24*60*60*1000000 + td.seconds*1000000 +  td.microseconds)/1.0E6# /(24*60*60)

times = np.array([sinceFirst(t) for t in rtimes])
scalars = np.array(scalars)

import Gif.TestBeamAnalysis.Plotter as Plotter
from ROOT import *

gROOT.SetBatch(kTRUE)


def timePlot():
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

	gr1 = TGraph(len(times), times, np.array(scalars[:,0]))
	gr2 = TGraph(len(times), times, np.array(scalars[:,1]))
	gr3 = TGraph(len(times), times, np.array(scalars[:,2]))
	gr4 = TGraph(len(times), times, np.array(scalars[:,3]))

	# Step 1
	gr1plot = Plotter.Plot(gr1, "Upstream"       , "lp","AP")
	gr2plot = Plotter.Plot(gr2, "Downstream"     , "lp","P" )
	gr3plot = Plotter.Plot(gr3, "Coincidence"    , "lp","P" )
	gr4plot = Plotter.Plot(gr4, "Coincidence*CSC", "lp","P" )

	# Step 2
	canvas = Plotter.Canvas("GIF++", False, 0., "Internal", 2000, 700)

	# Step 3
	canvas.makeLegend(.125)

	# Step 4
	canvas.addMainPlot(gr1plot,True,True)
	canvas.addMainPlot(gr2plot,False,True)
	canvas.addMainPlot(gr3plot,False,True)
	canvas.addMainPlot(gr4plot,False,True)

	# Step 5
	gr1.GetXaxis().SetTimeDisplay(True)
	gr1.GetXaxis().SetTimeFormat('%b %d %H:%M%F'+first.strftime('%Y-%m-%d %H:%M:%S'))
	gr1.GetYaxis().SetTitle("Value")
	gr1.GetXaxis().SetTitle("Time [CET]")
	gr1.SetMarkerColor(kRed-3)
	gr1.SetLineColor  (kRed-3)
	gr2.SetMarkerColor(kBlue-2)
	gr2.SetLineColor  (kBlue-2)
	gr3.SetMarkerColor(kGreen-3)
	gr3.SetLineColor  (kGreen-3)
	gr4.SetMarkerColor(kMagenta)
	gr4.SetLineColor  (kMagenta)
	gr1plot.scaleTitles(0.8)
	gr1plot.scaleLabels(0.8)
	gr1.GetYaxis().SetTitleOffset(gr1.GetYaxis().GetTitleOffset()*0.7)
	gr1.GetXaxis().SetTitleOffset(gr1.GetXaxis().GetTitleOffset()*1.1)
	#gr1.GetXaxis().SetRangeUser(200000., 700000.)
	gr1.GetYaxis().SetRangeUser(0., 30000.)
	canvas.mainPad.SetLeftMargin(canvas.mainPad.GetLeftMargin() * 0.5)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()

	#f = TFile('output.root','RECREATE')
	#gr1.SetName(gr1plot.legName); gr1.Write()
	#gr2.SetName(gr2plot.legName); gr2.Write()
	#gr3.SetName(gr3plot.legName); gr3.Write()
	#gr4.SetName(gr4plot.legName); gr4.Write()

	canvas.c.SaveAs('plot_'+outputFN+'.pdf')
	SetOwnership(canvas.c, False)

timePlot()

def intPlot():
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

	h = TH1F("name", "title", 100, 0., 60.)
	for i,t in enumerate(times):
		if i == 0: continue
		h.Fill(t-times[i-1])
	
	# Step 1
	hplot = Plotter.Plot(h, "Interval", "f", "hist")

	# Step 2
	canvas = Plotter.Canvas("GIF++", False, 0., "Internal", 800, 700)

	# Step 3
	canvas.makeLegend(.18,.06)

	# Step 4
	canvas.addMainPlot(hplot, True, True)

	# Step 5
	h.SetFillColor(kOrange)
	h.GetXaxis().SetTitle("Interval [s]")
	h.GetYaxis().SetTitle("Events")
	h.GetYaxis().SetTitleOffset(h.GetYaxis().GetTitleOffset()*1.6)
	canvas.mainPad.SetLeftMargin(canvas.mainPad.GetLeftMargin() * 1.2)
	canvas.mainPad.SetRightMargin(canvas.mainPad.GetRightMargin() * 0.5)
	hplot.scaleTitles(0.8)
	hplot.scaleLabels(0.8)

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('int_'+outputFN+'.pdf')

intPlot()
