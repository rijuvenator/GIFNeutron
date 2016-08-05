import numpy as np
import Plotter
import commands # python 2.6 on UNIX only
from ROOT import *

data1 = []
data2 = []
#yaxis = "CFEB"
yaxis = "ALCT*CLCT"
#yaxis = "CLCT0"
f = open('tmb')
doingME11 = True
for line in f:
	if line[0]=='%':
		doingME11 = False
		continue
	if line[0]=='#':
		continue
	s = line.strip('\n').split()
	currs = []
	for currm in s[1:5]:
		curr = commands.getoutput('grep " '+currm+'-" attenhut').strip('\n').split()
		currs.append(sum([float(i) for i in curr[2:]])/float(len(curr[2:])))
	rates = []
	for m in s[5:9]:
		#x = float(commands.getoutput('awk \'/^'+m+'/ {x = $3 + $4 + $5 + $6 + $7 + $8 + $9; print x}\' trigdata'))
		x = float(commands.getoutput('awk \'/^'+m+'/ {x = $(NF); print x}\' trigdata'))
		#x = float(commands.getoutput('awk \'/^'+m+'/ {x = $(NF-2); print x}\' trigdata'))
		rates.append(x)
	l = [float(s[0])]
	l.extend(currs)
	l.extend(rates)
	if doingME11:
		data1.append(l)
	else:
		data2.append(l)

data1 = np.array(data1)
data2 = np.array(data2)

print "=== ME11 ==="
print "%10s %10s %10s %10s %10s %10s %10s %10s %10s" % ('Filter', 'Curr1', 'Curr2', 'Curr3', 'Curr4', 'Rate1', 'Rate2', 'Rate3', 'Rate4')
for i in data1:
	for j in i:
		print "%10.3f" % j,
	print ""
print "=== ME21 ==="
print "%10s %10s %10s %10s %10s %10s %10s %10s %10s" % ('Filter', 'Curr1', 'Curr2', 'Curr3', 'Curr4', 'Rate1', 'Rate2', 'Rate3', 'Rate4')
for i in data2:
	for j in i:
		print "%10.3f" % j,
	print ""

yrange1 = [np.amin(data1[:,5:]), np.amax(data1[:,5:])]
yrange2 = [np.amin(data2[:,5:]), np.amax(data2[:,5:])]

def makePlot(x, y, ytit, fn, extra, makeFit):
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

	cols = [kRed-3, kBlue-1, kOrange, kGreen+2]
	#mars = [kOpenCircle, kOpenSquare, kOpenTriangleUp, kOpenCross]
	#mars = [kOpenCircle, kPlus, kStar, kMultiply]
	mars = [kFullCircle, kFullSquare, kFullTriangleUp, kFullCross]

	gr0 = TGraph(len(x), np.array(x[:,0]), np.array(y[:,0]))
	gr1 = TGraph(len(x), np.array(x[:,1]), np.array(y[:,1]))
	gr2 = TGraph(len(x), np.array(x[:,2]), np.array(y[:,2]))
	gr3 = TGraph(len(x), np.array(x[:,3]), np.array(y[:,3]))

	if makeFit:
		fit0 = TF1("fit0", "[0] * pow(x,[1])", 0.0, 50.0)
		fit0.SetParName(0,'c')
		fit0.SetParName(1,'e')
		fit0.SetParameter(0,1.0)
		fit0.SetParameter(1,2.0)
		gr0.Fit('fit0')
		fit1 = TF1("fit1", "[0] * pow(x,[1])", 0.0, 50.0)
		fit1.SetParName(0,'c')
		fit1.SetParName(1,'e')
		fit1.SetParameter(0,1.0)
		fit1.SetParameter(1,2.0)
		gr1.Fit('fit1')
		fit2 = TF1("fit2", "[0] * pow(x,[1])", 0.0, 50.0)
		fit2.SetParName(0,'c')
		fit2.SetParName(1,'e')
		fit2.SetParameter(0,1.0)
		fit2.SetParameter(1,2.0)
		gr2.Fit('fit2')
		fit3 = TF1("fit3", "[0] * pow(x,[1])", 0.0, 50.0)
		fit3.SetParName(0,'c')
		fit3.SetParName(1,'e')
		fit3.SetParameter(0,1.0)
		fit3.SetParameter(1,2.0)
		gr3.Fit('fit3')

	# Step 1
	gr0plot = Plotter.Plot(gr0, "Original"    , "p","AP")
	gr1plot = Plotter.Plot(gr1, "TightPreCLCT", "p","P")
	gr2plot = Plotter.Plot(gr2, "TightCLCT"   , "p","P")
	gr3plot = Plotter.Plot(gr3, "TightALCT"   , "p","P")

	# Step 2
	#canvas = Plotter.Canvas(extra, False, 0., "Internal", 800, 700)
	canvas = Plotter.Canvas(extra, True, 0., "Internal", 800, 700)

	# Step 3
	canvas.makeLegend(.2,0.15,'tl',0.04)

	# Step 4
	canvas.addMainPlot(gr0plot,True ,True)
	canvas.addMainPlot(gr1plot,False,True)
	canvas.addMainPlot(gr2plot,False,True)
	canvas.addMainPlot(gr3plot,False,True)

	# Step 5
	TGaxis.SetExponentOffset(-0.08, 0.02, "y")
#	canvas.mainPad.SetLogx(True)
	gr0.GetYaxis().SetTitle(ytit)
	gr0.GetXaxis().SetTitle('Mean Current [#muA]')
	gr0.SetMinimum((yrange1[0] if extra=='ME1/1' else yrange2[0])*0.8)
	gr0.SetMaximum((yrange1[1] if extra=='ME1/1' else yrange2[1])*1.2)

	gr0.SetMarkerColor(cols[0])
	gr1.SetMarkerColor(cols[1])
	gr2.SetMarkerColor(cols[2])
	gr3.SetMarkerColor(cols[3])

	gr0.SetMarkerStyle(mars[0])
	gr1.SetMarkerStyle(mars[1])
	gr2.SetMarkerStyle(mars[2])
	gr3.SetMarkerStyle(mars[3])

	gr0.SetMarkerSize(2.2)
	gr1.SetMarkerSize(2.2)
	gr2.SetMarkerSize(2.2)
	gr3.SetMarkerSize(2.2)

	if makeFit:
		# bl, +0.05 for linear; br, +0.0 for log
		#loc = 'bl'
		#add = 0.05
		loc = 'br'
		add = 0.0
		fit0.Draw("same")
		fit1.Draw("same")
		fit2.Draw("same")
		fit3.Draw("same")
		fit0.SetLineColor(cols[0])
		fit1.SetLineColor(cols[1])
		fit2.SetLineColor(cols[2])
		fit3.SetLineColor(cols[3])
		canvas.setFitBoxStyle(gr0,0.3,0.1,loc,0.05,0.02)
		s0 = gr0.FindObject('stats')
		s0.SetTextColor(cols[0])
		s0.SetY1NDC(s0.GetY1NDC()+add)
		s0.SetY2NDC(s0.GetY2NDC()+add)
		canvas.setFitBoxStyle(gr1,0.3,0.1,loc,0.05,0.02)
		s1 = gr1.FindObject('stats')
		s1.SetTextColor(cols[1])
		s1.SetY1NDC(s1.GetY1NDC()+.11+add)
		s1.SetY2NDC(s1.GetY2NDC()+.11+add)
		canvas.setFitBoxStyle(gr2,0.3,0.1,loc,0.05,0.02)
		s2 = gr2.FindObject('stats')
		s2.SetTextColor(cols[2])
		s2.SetY1NDC(s2.GetY1NDC()+.22+add)
		s2.SetY2NDC(s2.GetY2NDC()+.22+add)
		canvas.setFitBoxStyle(gr3,0.3,0.1,loc,0.05,0.02)
		s3 = gr3.FindObject('stats')
		s3.SetTextColor(cols[3])
		s3.SetY1NDC(s3.GetY1NDC()+.33+add)
		s3.SetY2NDC(s3.GetY2NDC()+.33+add)

		f = TLatex()
		f.SetTextFont(42)
		f.SetTextAlign(13)
		f.DrawLatexNDC(0.6,0.7,"R = c I^{e}")

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs(fn)

makePlot(data1[:,1:5], data1[:,5:], yaxis+' Rate [Hz]', 'me11.pdf', 'ME1/1', False)
makePlot(data2[:,1:5], data2[:,5:], yaxis+' Rate [Hz]', 'me21.pdf', 'ME2/1', False)
