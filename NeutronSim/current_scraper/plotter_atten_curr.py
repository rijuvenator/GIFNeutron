import numpy as n
import Plotter
from ROOT import *
import sys

def average(x):
	return float(sum([float(i) for i in x]))/float(len(x))

f = open(sys.argv[1])
a1 = []
c1 = []
a2 = []
c21 = []
c22 = []
c23 = []
for line in f:
	s = line.strip("\n").split()
	if line[0] == "#":
		continue
	if len(s) == 8:
		a1.append(float(s[0]))
		c1.append(average(s[2:8]))
	else:
		a2.append(float(s[0]))
		c21.append(average(s[2:8]))
		c22.append(average(s[8:14]))
		c23.append(average(s[14:20]))

# ME11
me11_a = n.array(a1)
me11_c = n.array(c1)

# ME21
me21_a = n.array(a2)
me21_c1 = n.array(c21)
me21_c2 = n.array(c22)
me21_c3 = n.array(c23)

#gr1 =  TGraph(len(me11_a),n.reciprocal(me11_a),me11_c )
#gr21 = TGraph(len(me21_a),n.reciprocal(me21_a),me21_c1)
#gr22 = TGraph(len(me21_a),n.reciprocal(me21_a),me21_c2)
#gr23 = TGraph(len(me21_a),n.reciprocal(me21_a),me21_c3)
gr1 =  TGraph(len(me11_a),n.log10(n.reciprocal(me11_a)),n.log10(me11_c ))
gr21 = TGraph(len(me21_a),n.log10(n.reciprocal(me21_a)),n.log10(me21_c1))
gr22 = TGraph(len(me21_a),n.log10(n.reciprocal(me21_a)),n.log10(me21_c2))
gr23 = TGraph(len(me21_a),n.log10(n.reciprocal(me21_a)),n.log10(me21_c3))

def plotterMacro():
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

	# Step 1
	gr1plot = Plotter.Plot(gr1, "ME1/1", "p","AP")
	gr21plot = Plotter.Plot(gr21, "ME2/1 (Segment 1)", "p","P")
	gr22plot = Plotter.Plot(gr22, "ME2/1 (Segment 2)", "p","P")
	gr23plot = Plotter.Plot(gr23, "ME2/1 (Segment 3)", "p","P")

	# Step 2
	#canvas = Plotter.Canvas("", True, 0., "Internal", 800, 700)
	canvas = Plotter.Canvas("", False, 0., "Internal", 800, 700)

	# Step 3
	canvas.makeLegend(.3,.15,"br",0.05,0.035)

	# Step 4
	canvas.addMainPlot(gr1plot,True,False)
	canvas.addMainPlot(gr21plot,False,False)
	canvas.addMainPlot(gr22plot,False,False)
	canvas.addMainPlot(gr23plot,False,False)

	#f1 = TF1("f1","[1] * pow(x,1) + [0]",1./46000.,1./3.3)
	f1 = TF1("f1","[1] * pow(x,1) + [0]",-5.0,0.)
	#f1 = TF1("f1","[0] * pow(x,[1])",-5.0,0.)
	f1.SetParName(0,"c")
	f1.SetParName(1,"k")
	f1.SetParameter(0,1.0)
	f1.SetParameter(1,1.0)
	gr1.Fit("f1")
	#f21 = TF1("f21","[1] * pow(x,1) + [0]",1./46000.,1./3.3)
	f21 = TF1("f21","[1] * pow(x,1) + [0]",-5.0,0.)
	#f21 = TF1("f21","[0] * pow(x,[1])",-5.0,0.)
	f21.SetParName(0,"c")
	f21.SetParName(1,"k")
	f21.SetParameter(0,1.0)
	f21.SetParameter(1,1.0)
	gr21.Fit("f21")
	#f22 = TF1("f22","[1] * pow(x,1) + [0]",1./46000.,1./3.3)
	f22 = TF1("f22","[1] * pow(x,1) + [0]",-5.0,0.)
	#f22 = TF1("f22","[0] * pow(x,[1])",-5.0,0.)
	f22.SetParName(0,"c")
	f22.SetParName(1,"k")
	f22.SetParameter(0,1.0)
	f22.SetParameter(1,1.0)
	gr22.Fit("f22")
	#f23 = TF1("f23","[1] * pow(x,1) + [0]",1./46000.,1./3.3)
	f23 = TF1("f23","[1] * pow(x,1) + [0]",-5.0,0.)
	#f23 = TF1("f23","[0] * pow(x,[1])",-5.0,0.)
	f23.SetParName(0,"c")
	f23.SetParName(1,"k")
	f23.SetParameter(0,1.0)
	f23.SetParameter(1,1.0)
	gr23.Fit("f23")

	f1.Draw("same")
	f21.Draw("same")
	f22.Draw("same")
	f23.Draw("same")

	f1.SetLineColor(kBlue)
	f21.SetLineColor(kRed-2)
	f22.SetLineColor(kRed-3)
	f23.SetLineColor(kRed-4)

	canvas.setFitBoxStyle(gr1,0.3,0.1,"tl",0.05,0.02)
	s1 = gr1.FindObject("stats")
	s1.SetTextColor(kBlue)
	canvas.setFitBoxStyle(gr21,0.3,0.1,"tl",0.05,0.02)
	s21 = gr21.FindObject("stats")
	s21.SetTextColor(kRed-2)
	s21.SetY1NDC(s21.GetY1NDC()-.11)
	s21.SetY2NDC(s21.GetY2NDC()-.11)
	canvas.setFitBoxStyle(gr22,0.3,0.1,"tl",0.05,0.02)
	s22 = gr22.FindObject("stats")
	s22.SetTextColor(kRed-3)
	s22.SetY1NDC(s22.GetY1NDC()-.22)
	s22.SetY2NDC(s22.GetY2NDC()-.22)
	canvas.setFitBoxStyle(gr23,0.3,0.1,"tl",0.05,0.02)
	s23 = gr23.FindObject("stats")
	s23.SetTextColor(kRed-4)
	s23.SetY1NDC(s23.GetY1NDC()-.33)
	s23.SetY2NDC(s23.GetY2NDC()-.33)

	# Step 5
	#canvas.mainPad.SetLogx(True)
	gr1.GetYaxis().SetTitle("(log) Mean Current across 6 Layers [#muA]")
	gr1.GetXaxis().SetTitle("(log) 1 / Downstream Attenuation Factor")
	gr1.GetYaxis().SetMoreLogLabels(True)
	#gr1.GetXaxis().SetLabelSize(gr1.GetXaxis().GetLabelSize() * 0.8)
	gr1.GetXaxis().SetNdivisions(509)
	#gr1.GetXaxis().SetMoreLogLabels(True)
	gr1.SetMarkerColor(kBlue)

	gr21.SetMarkerColor(kRed-2)
	gr22.SetMarkerColor(kRed-3)
	gr23.SetMarkerColor(kRed-4)

	f = TLatex()
	f.SetTextFont(42)
	f.SetTextAlign(13)
	#f.DrawLatexNDC(.35,.82,"I = c #upoint A^{k}")
	#f.DrawLatexNDC(.35,.82,"I = k(1/A) + c")
	f.DrawLatexNDC(.5,.8,"I = k(1/A) + c")

	# Step 6
	canvas.addLegendEntry(gr1plot)
	canvas.addLegendEntry(gr21plot)
	canvas.addLegendEntry(gr22plot)
	canvas.addLegendEntry(gr23plot)

	# Step 7

	# Step 8
	canvas.finishCanvas()

	canvas.c.SaveAs("attenVcurr.pdf")

plotterMacro()
