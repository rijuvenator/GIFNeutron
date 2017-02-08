import ROOT as R
import numpy as np
import Gif.Analysis.OldPlotter as Plotter

#dataY= [\
#	(3412, float('inf')),
#	(3425, 100.        ),
#	(3419, 46.         ),
#	(3437, 33.         )
#]
#
#dataR = [\
#	(3284 ,float('inf')),
#	(3222 ,46000.0     ),
#	(3308 ,  330.0     ),
#	(3295 ,  100.0     ),
#	(3317 ,   69.0     ),
#	(3232 ,   46.0     ),
#	(3241 ,   33.0     ),
#	(3250 ,   22.0     ),
#	(3339 ,   15.0     ),
#	(3347 ,   10.0     ),
#	(3384 ,    4.6     )
#]
#
#for data in dataY + dataR:
#	f = R.TFile.Open('../trees/ana_'+str(data[0])+'.root')
#	t = f.Get('GIFTree/GIFDigiTree')
#
#	nLCT = 0
#	nL1A = t.GetEntries()
#
#	for entry in t:
#		if list(t.lct_id).count(1) > 0:
#			nLCT += 1
#	
#	print data[0], '{:>7.1f}'.format(data[1]), nLCT, nL1A, '{:.4f}'.format(float(nLCT)/float(nL1A))
#
#'''
#3412 2.00000000e+32     inf 14991 15000 0.9994
#3425 1.94950000e+34   100.0 14957 15000 0.9971
#3419 3.79800000e+34    46.0 14918 15000 0.9945
#3437 5.50700000e+34    33.0 14774 15000 0.9849
#
#3284 2.00000000e+32     inf 10000 10008 0.9992
#3222 2.36500000e+33 46000.0 10001 10010 0.9991
#3308 1.23000000e+34   330.0 14981 15014 0.9978
#3295 1.94950000e+34   100.0 19954 20017 0.9969
#3317 3.14500000e+34    69.0 14952 15013 0.9959
#3232 3.79800000e+34    46.0 9937  10011 0.9926
#3241 5.50700000e+34    33.0 9887  10011 0.9876
#3250 7.00250000e+34    22.0 9815  10009 0.9806
#3339 1.03225000e+35    15.0 9447  10008 0.9439
#3347 1.22390000e+35    10.0 13766 15005 0.9174
#3384 2.28225000e+35     4.6 10455 15020 0.6961
#'''

curr_R = np.array([\
	6.66666667e-02,
	7.88333333e-01,
	4.10000000e+00,
	6.49833333e+00,
	1.04833333e+01,
	1.26600000e+01,
	1.83566667e+01,
	2.33416667e+01,
	3.44083333e+01,
	4.07966667e+01,
	7.60750000e+01])
lumi_R = np.array([\
	2.00000000e+32,
	2.36500000e+33,
	1.23000000e+34,
	1.94950000e+34,
	3.14500000e+34,
	3.79800000e+34,
	5.50700000e+34,
	7.00250000e+34,
	1.03225000e+35,
	1.22390000e+35,
	2.28225000e+35])
eff_R  = np.array([0.9992, 0.9991, 0.9978, 0.9969, 0.9959, 0.9926, 0.9876, 0.9806, 0.9439, 0.9174, 0.6961])

lumi_Y = np.array([lumi_R[0], lumi_R[3], lumi_R[5], lumi_R[6]])
curr_Y = np.array([curr_R[0], curr_R[3], curr_R[5], curr_R[6]])
eff_Y  = np.array([0.9994, 0.9971, 0.9945, 0.9849])

R.gROOT.SetBatch(True)

gY = R.TGraph(len(lumi_Y), lumi_Y, eff_Y)
gR = R.TGraph(len(lumi_R), lumi_R, eff_R)

plotY = Plotter.Plot(gY, 'Test P5 Firmware'   , 'p', 'P')
plotR = Plotter.Plot(gR, 'Current P5 Firmware', 'p', 'P')

canvas = Plotter.Canvas(lumi='ME1/1 External Trigger', cWidth=800, cHeight=700)

canvas.makeLegend(pos='bl',lOffset=0.04)
canvas.leg.SetY1(canvas.leg.GetY1() + 0.1)
canvas.leg.SetY2(canvas.leg.GetY2() + 0.1)

canvas.addMainPlot(plotR)
canvas.addMainPlot(plotY)

canvas.scaleMargins(1.25, 'R')
gY.SetMarkerColor(R.kRed)
gR.SetMarkerColor(R.kBlue)
gY.SetMarkerSize(2)
gR.SetMarkerSize(2)
gY.SetMarkerStyle(R.kFullCross)
gR.SetMarkerStyle(R.kFullCircle)
canvas.firstPlot.plot.GetXaxis().SetRangeUser(-10.E34, 250.E34)
canvas.firstPlot.plot.SetMinimum(0.)
canvas.firstPlot.plot.SetMaximum(1.05)
canvas.firstPlot.setTitles(X='Luminosity [Hz/cm^{2}]', Y='LCT/L1A')
canvas.firstPlot.scaleTitles(600./canvas.cHeight)
canvas.firstPlot.scaleLabels(600./canvas.cHeight)
canvas.makeTransparent()

canvas.finishCanvas()

# Extra Axis
xmax = canvas.firstPlot.plot.GetXaxis().GetXmax()
axis = canvas.makeExtraAxis(0., xmax/3.e33)
axis.SetTitle('Current [#muA]')

canvas.c.SaveAs('pdfs/YuriyLastStraw.pdf')
