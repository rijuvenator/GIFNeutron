import ROOT as R
import Gif.TestBeamAnalysis.Plotter as Plotter
import numpy as np

# makes a plot of the captured neutron energy spectrum
# note that the x axis is log scale, and the bins are equally spaced on a log scale

nBins = 100
h = R.TH1F('spectrum','',nBins,np.linspace(0., 10. ,nBins+1))
f = open('../files/photons')
for line in f:
	l = [float(x) for x in line.strip('\n').split()]
	#for val in l: h.Fill(val)
	h.Fill(sum(l) * 1000.)

hplot = Plotter.Plot(h, 'Spectrum', 'f', 'hist')
canvas = Plotter.Canvas('Captured Neutrons', False, 0., 'Internal', 950, 600)
canvas.makeLegend()
canvas.addMainPlot(hplot,True,False)

# cosmetics
h.GetYaxis().SetTitle('Counts')
h.GetXaxis().SetTitle('Total Photon Energy [MeV]')
h.GetYaxis().SetTitleOffset(h.GetYaxis().GetTitleOffset()*1.2)
h.GetXaxis().SetTitleOffset(h.GetXaxis().GetTitleOffset()*1.2)
hplot.scaleTitles(0.8)
hplot.scaleLabels(0.8)
#canvas.mainPad.SetLogx(True)
h.GetXaxis().SetMoreLogLabels(True)
h.SetLineColor(R.kOrange)
h.SetFillColor(R.kOrange)
#canvas.mainPad.SetRightMargin(canvas.mainPad.GetRightMargin()*1.2)

canvas.finishCanvas()

canvas.c.SaveAs('../pdfs/hPhotonSpec.pdf')