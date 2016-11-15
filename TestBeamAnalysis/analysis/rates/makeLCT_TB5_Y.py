import ROOT as R
import numpy as np
from Gif.TestBeamAnalysis.DualMeasurements import meas
import Gif.TestBeamAnalysis.Plotter as Plotter

# number of firmware configurations
nCat = 6

# order matters! measurements must be in identical order to attenhut files
measList = [3412,3413,3414,3415,3416,3418,3419,3420,3421,3422,3423,3424,3425,3426,3427,3428,3429,3430,3437,3438,3439,3440,3441,3442]

# Fill dictionary for currents
# curr = {'att', [I_s1l1, I_s1l2, ...], ...}
'''
curr11 = {}
curr11File = open('../currents/attenhut11')
for i,line in enumerate(curr11File):
    if i%nCat==0: 
        l = line.strip('\n').split()
        curr11[l[0]]=[float(k) for k in l[2:]]
curr21 = {}
curr21File = open('../currents/attenhut21')
for i,line in enumerate(curr21File):
    if i%nCat==0: 
        l = line.strip('\n').split()
        curr21[l[0]]=[float(k) for k in l[2:]]
'''
currY = {}
currYFile = open('../currents/attenhut_Y_good')
for i,line in enumerate(currYFile):
    if i%nCat==0: 
        l = line.strip('\n').split()
        currY[l[0]]=[float(k) for k in l[2:]]


#data11 = []
#data21 = []
dataY = []

for i,m in enumerate(measList):
    f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/TestBeam5/ana_'+str(m)+'.root')
    t = f.Get('GIFTree/GIFDigiTree')
    nLCT_11 = 0
    nLCT_21 = 0
    nLCT_Y = 0
    # Count number of entries with at least one LCT
    for entry in t:
        # ID for ME1/1/GIF = 1
        #if list(t.lct_id).count(1)>0: nLCT_11 = nLCT_11 + 1
        # ID for ME2/1/GIF = 110
        #if list(t.lct_id).count(110)>0: nLCT_21 = nLCT_21 + 1
        if list(t.lct_id).count(1)>0: nLCT_Y = nLCT_Y + 1

    nTot = t.GetEntries()
    #print '%4i %5i %5i %5i' % (m, nLCT_11, nLCT_21, nTot)
    print '%4i %5i %5i' % (m, nLCT_Y, nTot)

    # Measurements are done in serial sets of nCat (usually), choose the first in every set of 8
    # to calculate the current for the whole set (skip the last nCat-1)
    if i%nCat==0 and i<len(measList)-nCat+1:
        dataY.append([float(meas[str(m)].dAtt)])
        dataY[i/nCat].append(sum(currY[meas[str(m)].dAtt])/6.)

        #data11.append([float(meas[str(m)].dAtt)])
        #data11[i/nCat].append(sum(curr11[meas[str(m)].dAtt])/6.)

        #data21.append([float(meas[str(m)].dAtt)])
        #data21[i/nCat].append(sum(curr21[meas[str(m)].dAtt])/18.)

    # insert efficiency at each current index
    # if in the last 7 measurements by hand set to the measurement type
    dataY[i/nCat if i<len(measList)-nCat+1 else 3].append(float(nLCT_Y)/float(nTot))
    #data11[i/nCat if i<len(measList)-7 else 10].append(float(nLCT_11)/float(nTot))
    #data21[i/nCat if i<len(measList)-7 else 10].append(float(nLCT_21)/float(nTot))

'''
print 'ME1/1'
print '\033[4m%6s %6s %6s %6s %6s %6s %6s %6s %6s %6s\033[m' % ('Filter', 'Curr', 'FF-1', 'FF-2', 'FF-3', 'FF-4', 'FF-5', 'FF-6', 'FF-7', 'FF-8')
for i in data11:
	for j in i:
		print '%6.2f' % j,
	print ''

print 'ME2/1'
print '\033[4m%6s %6s %6s %6s %6s %6s %6s %6s %6s %6s\033[m' % ('Filter', 'Curr', 'FF-1', 'FF-2', 'FF-3', 'FF-4', 'FF-5', 'FF-6', 'FF-7', 'FF-8')
for i in data21:
    for j in i:
        print '%6.2f' % j,
    print ''
'''
print 'ME1/1 new otmb fw'
print '\033[4m%6s %6s %6s %6s %6s %6s %6s %6s %6s %6s\033[m' % ('Filter', 'Curr', 'FF-1', 'FF-2', 'FF-3', 'FF-4', 'FF-5', 'FF-6', 'FF-7', 'FF-8')
for i in dataY:
    for j in i:
        print '%6.2f' % j,
    print ''

dataY = np.array(dataY)
#data11 = np.array(data11)
#data21 = np.array(data21)

# Array of ratio of efficiencies to the 'Original' setting efficiency
ndataY = dataY[:,2:] / np.transpose(np.tile(dataY[:,2], (nCat,1)))
#ndata11 = data11[:,2:] / np.transpose(np.tile(data11[:,2], (nCat,1)))
#ndata21 = data21[:,2:] / np.transpose(np.tile(data21[:,2], (nCat,1)))

def makePlot(x, y,cham, xtitle, ytitle, title):
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

	cols = [R.kRed-3, R.kBlue-1, R.kOrange, R.kGreen+2, R.kMagenta, R.kAzure+8]
	mars = [R.kFullCircle, R.kFullSquare, R.kFullTriangleUp, R.kFullCross, R.kFullDiamond, R.kFullStar]

	gr0 = R.TGraph(len(x), np.array(x), np.array(y[:,0]))
	gr1 = R.TGraph(len(x), np.array(x), np.array(y[:,1]))
	gr2 = R.TGraph(len(x), np.array(x), np.array(y[:,2]))
	gr3 = R.TGraph(len(x), np.array(x), np.array(y[:,3]))
	gr4 = R.TGraph(len(x), np.array(x), np.array(y[:,4]))
	gr5 = R.TGraph(len(x), np.array(x), np.array(y[:,5]))

	# Step 1
	gr0plot = Plotter.Plot(gr0, "Original" , "p","AP")
	gr1plot = Plotter.Plot(gr1, "Algo0"    , "p","P")
	gr2plot = Plotter.Plot(gr2, "Algo1"    , "p","P")
	gr3plot = Plotter.Plot(gr3, "Algo2"    , "p","P")
	gr4plot = Plotter.Plot(gr4, "Algo3"    , "p","P")
	gr5plot = Plotter.Plot(gr5, "Algo4"    , "p","P")

	# Step 2
	if cham=='11': canvas = Plotter.Canvas('ME1/1 External Trigger', False, 0., "Internal", 800, 700)
	if cham=='21': canvas = Plotter.Canvas('ME2/1 External Trigger', False, 0., "Internal", 800, 700)

	# Step 3
	canvas.makeLegend(.2,0.25,'bl',0.04, 0.03)

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
	gr0.GetYaxis().SetTitle(ytitle)
	gr0.GetXaxis().SetTitle(xtitle)
	gr0plot.scaleTitles(0.8)
	gr0plot.scaleLabels(0.8)
	gr0.SetMinimum(0.0)
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
	canvas.c.SaveAs('LCT_'+cham+'_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

# Make plots with Luminosity on x-axis
lctEff = 'LCT Efficiency'
lumi = 'Luminosity [Hz/cm^{2}]'
makePlot(3.3e33 * dataY[:,1], dataY[:,2:], '11', lumi, lctEff, 'lumi_yuiry')

# Make plots with current on x-axis
currlabel = 'Mean Current [#muA]'
makePlot(dataY[:,1], dataY[:,2:], '11', currlabel, lctEff, 'curr_yuiry')

# Normalized efficiency to original
lctNorm = 'Normalized LCT Efficiency'
makePlot(3.3e33 * dataY[:,1], ndataY,'11', lumi, lctNorm, 'lumi_norm_yuiry')
makePlot(dataY[:,1], ndataY,'11', currlabel, lctNorm, 'curr_norm_yuiry')

# Source intensity on x-axis
attY = []
for aY in dataY[:,0]:
    if aY == 0.: attY.append(0.)
    else: attY.append(1./aY)

srclabel = 'Source Intensity 1/A'
makePlot(attY, dataY[:,2:],'11', srclabel, lctEff, 'att_yuiry')
makePlot(attY, ndataY,'11', srclabel, lctNorm, 'att_norm_yuiry')
