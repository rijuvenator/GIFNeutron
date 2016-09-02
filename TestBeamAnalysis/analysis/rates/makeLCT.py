import ROOT as R
import numpy as np
from Gif.TestBeamAnalysis.Measurements import meas
import Gif.TestBeamAnalysis.Plotter as Plotter

# Cameron
#3092, 3103, 3113, 3123, 2758
#3094, 3080, 2970, 2843, 2756

nCat = 6

measList = [\
		3084,3086,3088,3090,     3092,3094,
		3095,3097,3099,3101,     3103,3080,
		3105,3107,3109,3111,     3113,2970,
		3115,3117,3119,3121,     3123,2843,
		3125,3127,3129,3131,3133,2758,2756
		]

curr = {}
curr['100'] = [ 2.28 , 2.16 , 1.97 , 2.04 , 1.83 , 1.96 , 2.41 , 2.50 , 2.36 , 2.32 , 2.46 , 1.96 , 3.39 , 3.22 , 3.16 , 3.00 , 3.62 , 2.54]
curr[ '46'] = [ 6.40 , 6.20 , 5.68 , 5.89 , 5.41 , 5.60 , 6.97 , 7.01 , 6.73 , 6.60 , 6.91 , 5.66 , 9.70 , 9.16 , 8.97 , 8.77 ,10.34 , 7.19]
curr[ '33'] = [ 9.70 , 9.37 , 8.60 , 8.88 , 8.32 , 8.58 ,10.62 ,10.57 ,10.19 , 9.98 ,10.44 , 8.61 ,14.68 ,13.82 ,13.59 ,13.35 ,15.62 ,10.91]
curr[ '22'] = [12.07 ,11.71 ,10.80 ,11.10 ,10.60 ,10.78 ,13.24 ,13.20 ,12.82 ,12.61 ,13.21 ,10.93 ,18.57 ,17.47 ,17.24 ,17.13 ,19.93 ,14.05]
curr[ '15'] = [18.86 ,18.44 ,17.14 ,17.62 ,16.80 ,16.97 ,20.30 ,20.48 ,20.08 ,19.79 ,20.63 ,17.17 ,28.19 ,26.89 ,26.73 ,26.80 ,30.93 ,21.87]

data = []

for i,m in enumerate(measList):
	if m==3133: continue
	elif m==3131:
		f = R.TFile.Open('/afs/cern.ch/work/a/adasgupt/GIF/data/ana_'+str(m)+'.root')
		t = f.Get('GIFTree/GIFDigiTree')
		nLCT = t.Draw('n_lcts','n_alcts>0','goff')
		nTot = t.GetEntries()
		f = R.TFile.Open('/afs/cern.ch/work/a/adasgupt/GIF/data/ana_3133.root')
		t = f.Get('GIFTree/GIFDigiTree')
		nLCT += t.Draw('n_lcts','n_alcts>0','goff')
		nTot += t.GetEntries()
		#print '%4i %5i %5i' % (m, nLCT, nTot)
	else:
		f = R.TFile.Open('/afs/cern.ch/work/a/adasgupt/GIF/data/ana_'+str(m)+'.root')
		t = f.Get('GIFTree/GIFDigiTree')
		nLCT = t.Draw('n_lcts','n_alcts>0','goff')
		nTot = t.GetEntries()
		#print '%4i %5i %5i' % (m, nLCT, nTot)

	if i%nCat==0 and i<len(measList)-3:
		data.append([float(meas[str(m)].dAtt)])
		data[i/nCat].append(sum(curr[meas[str(m)].dAtt])/18.)

	data[i/nCat if i<len(measList)-3 else 4].append(float(nLCT)/float(nTot))

#print '\033[4m%6s %6s %6s %6s %6s %6s\033[m' % ('Filter', 'Curr', 'FF-1', 'FF-2', 'FF-3', 'FF-4')
print '\033[4m%6s %6s %6s %6s %6s %6s %6s %6s\033[m' % ('Filter', 'Curr', 'FF-1', 'FF-2', 'FF-3', 'FF-4', 'FF-5', 'FF-6')
for i in data:
	for j in i:
		print '%6.2f' % j,
	print ''

data = np.array(data)
ndata = data[:,2:] / np.transpose(np.tile(data[:,2], (nCat,1)))

def makePlot(x, y):
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

#	cols = [R.kRed-3, R.kBlue-1, R.kOrange, R.kGreen+2]
#	mars = [R.kFullCircle, R.kFullSquare, R.kFullTriangleUp, R.kFullCross]

	cols = [R.kRed-3, R.kBlue-1, R.kOrange, R.kGreen+2, R.kMagenta, R.kAzure+8]
	mars = [R.kFullCircle, R.kFullSquare, R.kFullTriangleUp, R.kFullCross, R.kFullDiamond, R.kFullStar]

	gr0 = R.TGraph(len(x), np.array(x), np.array(y[:,0]))
	gr1 = R.TGraph(len(x), np.array(x), np.array(y[:,1]))
	gr2 = R.TGraph(len(x), np.array(x), np.array(y[:,2]))
	gr3 = R.TGraph(len(x), np.array(x), np.array(y[:,3]))
	gr4 = R.TGraph(len(x), np.array(x), np.array(y[:,4]))
	gr5 = R.TGraph(len(x), np.array(x), np.array(y[:,5]))

	# Step 1
	gr0plot = Plotter.Plot(gr0, "Original"    , "p","AP")
	gr1plot = Plotter.Plot(gr1, "TightPreCLCT", "p","P")
	gr2plot = Plotter.Plot(gr2, "TightCLCT"   , "p","P")
	gr3plot = Plotter.Plot(gr3, "TightALCT"   , "p","P")
	gr4plot = Plotter.Plot(gr4, "TightPreID"  , "p","P")
	gr5plot = Plotter.Plot(gr5, "TightID"     , "p","P")

	# Step 2
	canvas = Plotter.Canvas('ME2/1 External Trigger', False, 0., "Internal", 800, 700)
	#canvas = Plotter.Canvas(extra, True, 0., "Internal", 800, 700)

	# Step 3
	canvas.makeLegend(.2,0.18,'bl',0.04, 0.03)

	# Step 4
	canvas.addMainPlot(gr0plot,True ,True)
	canvas.addMainPlot(gr1plot,False,True)
	canvas.addMainPlot(gr2plot,False,True)
	canvas.addMainPlot(gr3plot,False,True)
	canvas.addMainPlot(gr4plot,False,True)
	canvas.addMainPlot(gr5plot,False,True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
#	canvas.mainPad.SetLogx(True)
#	gr0.GetYaxis().SetTitle('LCT Efficiency')
	gr0.GetYaxis().SetTitle('Normalized LCT Efficiency')
	gr0.GetXaxis().SetTitle('Mean Current [#muA]')
	gr0plot.scaleTitles(0.8)
	gr0plot.scaleLabels(0.8)
	gr0.SetMinimum(0.4)
	gr0.SetMaximum(1.1)

	gr0.SetMarkerColor(cols[0])
	gr1.SetMarkerColor(cols[1])
	gr2.SetMarkerColor(cols[2])
	gr3.SetMarkerColor(cols[3])
	gr4.SetMarkerColor(cols[4])
	gr5.SetMarkerColor(cols[5])

	gr0.SetMarkerStyle(mars[0])
	gr1.SetMarkerStyle(mars[1])
	gr2.SetMarkerStyle(mars[2])
	gr3.SetMarkerStyle(mars[3])
	gr4.SetMarkerStyle(mars[4])
	gr5.SetMarkerStyle(mars[5])

	gr0.SetMarkerSize(2.2)
	gr1.SetMarkerSize(2.2)
	gr2.SetMarkerSize(2.2)
	gr3.SetMarkerSize(2.2)
	gr4.SetMarkerSize(2.2)
	gr5.SetMarkerSize(2.2)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('LCT.pdf')
	R.SetOwnership(canvas.c, False)

#makePlot(data[:,1], data[:,2:])
makePlot(data[:,1], ndata)
