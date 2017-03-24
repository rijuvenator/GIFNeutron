import numpy as np
import ROOT as R
import Gif.Analysis.Plotter as Plotter

R.gROOT.SetBatch(True)

#hCap = R.TH2F('hCap', '', 100, 1, 2.e10, 100, 1, 2.e8)
hCap = R.TH2F('hCap', '', 100, np.logspace(0-6, 15-6, 101), 100, np.logspace(0-9, 8-9, 101))

hIne = R.TH2F('hIne', '', 100, np.logspace(0-6, 15-6, 101), 100, np.logspace(0-9, 8-9, 101))
hWHAT= R.TH2F('hWHAT', '', 100, np.logspace(0-6, 15-6, 101), 100, np.logspace(0-9, 8-9, 101))

f = open('capetof/fulllog.log')
for line in f:
	if ' nCapture ' in line :
		cols = line.strip('\n').split()
		tof = float(cols[-3])/1e9
		cape = float(cols[-1])/1e6
		hCap.Fill(cape, tof)
	elif ' neutronInelastic ' in line:
		cols = line.strip('\n').split()
		tof = float(cols[-3])/1e9
		inee = float(cols[-1])/1e6
		if inee <= 1000. and inee >= 0.1:
			hWHAT.Fill(inee, tof)
		else:
			hIne.Fill(inee, tof)

plotCap = Plotter.Plot(hCap, legName='Capture' , legType='l', option='')
plotIne = Plotter.Plot(hIne, legName='Inelastic Scatter', legType='l', option='')
plotWHAT = Plotter.Plot(hWHAT, legName='"Inelastic Scatter"', legType='l', option='')
canvas  = Plotter.Canvas(lumi='SimHit TOF vs. Last Neutron Energy', logy=True)
canvas.addMainPlot(plotCap)
canvas.addMainPlot(plotIne)
canvas.addMainPlot(plotWHAT, addToPlotList=False)
canvas.mainPad.SetLogx(True)
plotCap.SetMarkerColor(R.kRed)
plotCap.SetLineColor(R.kRed)
plotIne.SetMarkerColor(R.kBlue)
plotIne.SetLineColor(R.kBlue)
#plotWHAT.SetMarkerColor(R.kGreen)
#plotWHAT.SetLineColor(R.kGreen)
plotWHAT.SetMarkerColor(R.kBlue)
plotWHAT.SetLineColor(R.kBlue)
canvas.firstPlot.setTitles(X='Last Recorded Neutron Energy [eV]', Y='Time of Flight [s]')
canvas.firstPlot.scaleTitleOffsets(1.25, 'X')
canvas.makeTransparent()
canvas.makeLegend()
canvas.legend.moveEdges(L=-.16)
canvas.legend.resizeHeight()
#canvas.drawText(pos=(canvas.legend.GetX1()+.08, canvas.legend.GetY1()), text='(still to be understood)', align='tl', fontscale=0.8)
canvas.finishCanvas()
canvas.save('lolol.pdf')
