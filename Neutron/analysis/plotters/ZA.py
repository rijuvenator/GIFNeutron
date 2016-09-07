import sys
import ROOT as R
import Gif.TestBeamAnalysis.Plotter as Plotter
import numpy as np

# Requires 1 argument, the suffix used when making the tree
if len(sys.argv) < 2:
	eprint('Usage: script.py SUFFIX')
	exit()

# makes a 2D plot of Z vs A

upperright = [35, 75] # sets the upper right corner
h = R.TH2F('spectrum','',upperright[0],0.,float(upperright[0]),upperright[1],0.,float(upperright[1]))
f = open('../files/nuclei_'+sys.argv[1])
for line in f:
	l = line.strip('\n').split()
	h.Fill(float(l[0]), float(l[1]))

hplot = Plotter.Plot(h, '', 'p', 'colz')
canvas = Plotter.Canvas('Captured Neutrons', False, 0., 'Internal', 800, 600)
canvas.makeLegend()

R.TColor.CreateGradientColorTable(\
	4,                           # number of color stops
	np.array([0.0,0.5,0.7,1.0]), # position of color stops
	np.array([1.0,0.0,0.0,0.0]), # R channel
	np.array([1.0,0.7,0.0,0.0]), # G channel
	np.array([0.0,0.0,0.7,0.0]), # B channel
	50                           # granularity
)

canvas.addMainPlot(hplot,True,False)

# cosmetics
h.GetYaxis().SetTitle('A [Mass Number]')
h.GetXaxis().SetTitle('Z [Atomic Number]')
h.GetYaxis().SetTitleOffset(h.GetYaxis().GetTitleOffset()*1.2)
h.GetXaxis().SetTitleOffset(h.GetXaxis().GetTitleOffset()*1.2)
hplot.scaleTitles(0.8)
hplot.scaleLabels(0.8)
h.GetZaxis().SetLabelSize(h.GetZaxis().GetLabelSize()*0.8)
h.SetLineColor(R.kOrange)
h.SetFillColor(R.kOrange)
canvas.mainPad.SetRightMargin(canvas.mainPad.GetRightMargin()*1.8)

canvas.finishCanvas()

canvas.c.SaveAs('../pdfs/hZA_'+sys.argv[1]+'.pdf')

