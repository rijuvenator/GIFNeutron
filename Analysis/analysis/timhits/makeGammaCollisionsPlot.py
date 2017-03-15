import numpy as np
import ROOT as R
import Gif.Analysis.Plotter as Plotter

R.gROOT.SetBatch(True)

N_GAMMA  = 21
N_ENERGY = 63

f = open('collisions.log')
entries = []
for line in f:
	for entry in line.strip('\n').split():
		entries.append(float(entry))

gammaBins   = entries[:N_GAMMA]
energyBins  = entries[N_GAMMA:N_ENERGY+N_GAMMA]
colTableRaw = entries[N_GAMMA+N_ENERGY:]
colTable    = [colTableRaw[i:i+N_GAMMA] for i in range(0, len(colTableRaw), N_GAMMA)]

gammaBins  = np.array(gammaBins)
energyBins = np.array(energyBins)
colTable   = np.array(colTable)

#for row in colTable:
#	for col in row:
#		print '{:8.4f}'.format(col),
#	print ''

graphE, graphG  = [], []

plot = []
canvas = Plotter.Canvas()
for i in range(N_GAMMA):
	graphE.append(R.TGraph(N_ENERGY, energyBins, np.array(colTable[:,i])))
	plot  .append(Plotter.Plot(graphE[i], option='P'))
	canvas.addMainPlot(plot[i])
	plot[i].SetMarkerColor(i)
canvas.firstPlot.SetMinimum(-6)
canvas.firstPlot.SetMaximum( 6)
canvas.firstPlot.setTitles(X='log Energy', Y='log Collisions')
canvas.save('Energy.pdf')

plot = []
canvas = Plotter.Canvas()
for i in range(N_ENERGY):
	graphG.append(R.TGraph(N_GAMMA, gammaBins, np.array(colTable[i,:])))
	plot  .append(Plotter.Plot(graphG[i], option='P'))
	canvas.addMainPlot(plot[i])
	plot[i].SetMarkerColor(i)
canvas.firstPlot.SetMinimum(-6)
canvas.firstPlot.SetMaximum( 6)
canvas.firstPlot.setTitles(X='log #gamma', Y='log Collisions')
canvas.save('Gamma.pdf')

h = R.TH2F('h', '', N_ENERGY-1, energyBins, N_GAMMA-1, gammaBins)
for gbin in range(1, N_GAMMA):
	for ebin in range(1, N_ENERGY):
		#h.SetBinContent(ebin, gbin, np.exp(colTable[ebin,gbin]))
		h.SetBinContent(ebin, gbin, colTable[ebin,gbin])
canvas = Plotter.Canvas()
R.gStyle.SetPalette(55)
R.gStyle.SetNumberContours(100)
plot = Plotter.Plot(h, option='colz')
canvas.addMainPlot(plot)
canvas.firstPlot.setTitles(X='log Energy', Y='log Gamma', Z='log Collisions')
canvas.firstPlot.scaleTitleOffsets(0.6, 'Y')
canvas.firstPlot.scaleTitleOffsets(0.9, 'Z')
canvas.scaleMargins(0.5, 'L')
canvas.scaleMargins(1.7, 'R')
canvas.save('Both.pdf')
