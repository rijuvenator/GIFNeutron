import sys
import ROOT as R
import Gif.TestBeamAnalysis.Plotter as Plotter
import numpy as np

# Requires 1 argument, the suffix used when making the tree
if len(sys.argv) < 2:
	eprint('Usage: script.py SUFFIX')
	exit()

# makes a plot of the captured neutron energy spectrum
# note that the x axis is log scale, and the bins are equally spaced on a log scale

nBins = 1000
h = R.TH1F('spectrum','',nBins,np.logspace(-15.,-2.,nBins+1))
f = open('../files/energies_'+sys.argv[1])
for line in f:
	h.Fill(float(line.strip('\n')))

a = np.logspace(-15.,-2.,nBins+1)
print a[696:699]

hplot = Plotter.Plot(h, 'Spectrum', 'f', 'hist')
canvas = Plotter.Canvas('Captured Neutrons', False, 0., 'Internal', 950, 600)
canvas.makeLegend()
canvas.addMainPlot(hplot,True,False)

# cosmetics
h.GetYaxis().SetTitle('Counts')
h.GetXaxis().SetTitle('Energy [GeV]')
h.GetYaxis().SetTitleOffset(h.GetYaxis().GetTitleOffset()*1.2)
h.GetXaxis().SetTitleOffset(h.GetXaxis().GetTitleOffset()*1.2)
hplot.scaleTitles(0.8)
hplot.scaleLabels(0.8)
canvas.mainPad.SetLogx(True)
h.SetLineColor(R.kOrange)
h.SetFillColor(R.kOrange)
#canvas.mainPad.SetRightMargin(canvas.mainPad.GetRightMargin()*1.2)

canvas.finishCanvas()

# thermal neutron line (0.025 eV)
line = R.TLine(0.025e-9,0.,0.025e-9,h.GetMaximum()*1.05)
line.SetLineStyle(2)
line.Draw()

canvas.c.SaveAs('../pdfs/hSpectrum_'+sys.argv[1]+'.pdf')
