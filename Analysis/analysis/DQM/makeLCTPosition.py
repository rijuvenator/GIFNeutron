import numpy as np
import Gif.Analysis.OldPlotter as Plotter
import Gif.Analysis.Primitives as Primitives
import ROOT as R
from Gif.Analysis.MegaStruct import F_GIFDATA

R.gROOT.SetBatch(True)

xmin = [0, 0]
ymin = [0, 0]
#xmax = [100, 125]
#ymax = [50 , 110]
xmax = [224, 160]
ymax = [48 , 112]

sxmin = [25-6, 8-6]
sxmax = [72+6,38+6]
symin = [37-3,55-3]
symax = [43+3,65+3]

h, c, o = {}, {}, {}
h[1  ] = R.TH2F('h1','',xmax[0]-xmin[0],xmin[0],xmax[0],ymax[0]-ymin[0],ymin[0],ymax[0])
h[110] = R.TH2F('h2','',xmax[1]-xmin[1],xmin[1],xmax[1],ymax[1]-ymin[1],ymin[1],ymax[1])
c[1  ] = R.TH2F('c1','',xmax[0]-xmin[0],xmin[0],xmax[0],ymax[0]-ymin[0],ymin[0],ymax[0])
c[110] = R.TH2F('c2','',xmax[1]-xmin[1],xmin[1],xmax[1],ymax[1]-ymin[1],ymin[1],ymax[1])
o[1  ] = R.TH2F('o1','',xmax[0]-xmin[0],xmin[0],xmax[0],ymax[0]-ymin[0],ymin[0],ymax[0])
o[110] = R.TH2F('o2','',xmax[1]-xmin[1],xmin[1],xmax[1],ymax[1]-ymin[1],ymin[1],ymax[1])

counts = {1:0, 110:0}
lctcounts = {1:0, 110:0}

f = R.TFile.Open(F_GIFDATA.replace('XXXX','3284'))
t = f.Get('GIFTree/GIFDigiTree')
for entry in t:
	alreadyFilled = {1:False, 110:False}
	E = Primitives.ETree(t, DecList=['LCT'])
	lcts = [Primitives.LCT(E, i) for i in range(len(E.lct_cham))]
	for CHAM in (1, 110):
		if CHAM in E.lct_cham:
			lctcounts[CHAM] += 1
	for lct in lcts:
		h[lct.cham].Fill(lct.keyHalfStrip, lct.keyWireGroup)
		idx = 0 if lct.cham == 1 else 1
		if lct.keyHalfStrip <= sxmax[idx] and lct.keyHalfStrip >= sxmin[idx] and lct.keyWireGroup <= symax[idx] and lct.keyWireGroup >= symin[idx]:
			c[lct.cham].Fill(lct.keyHalfStrip, lct.keyWireGroup)
			if not alreadyFilled[lct.cham]:
				counts[lct.cham] += 1
				alreadyFilled[lct.cham] = True
		else:
			o[lct.cham].Fill(lct.keyHalfStrip, lct.keyWireGroup)

print '{:5d} {:5d} {:5d} {:.4f} {:.4f} {:5d} {:5d} {:.4f} {:.4f}'.format(
		counts[1],
		counts[110],
		10008,
		float(counts[1])/10008,
		float(counts[110])/10008,
		lctcounts[1],
		lctcounts[110],
		float(lctcounts[1])/10008,
		float(lctcounts[110])/10008,
)

def makePlot(h, cham, which):
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
	canvas.save('pdfs/area_'+which+'_'+str(cham)+'.pdf')
	R.SetOwnership(canvas.c, False)

makePlot(h[1  ], 1, 'all')
makePlot(h[110], 2, 'all')
makePlot(c[1  ], 1, 'cut')
makePlot(c[110], 2, 'cut')
makePlot(o[1  ], 1, 'out')
makePlot(o[110], 2, 'out')
