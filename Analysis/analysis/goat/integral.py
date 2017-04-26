import sys, os, argparse
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi
R.gROOT.SetBatch(True)


RINGLIST = ['-42', '-41', '-32', '-31', '-22', '-21', '-13', '-12', '-11', '+11', '+12', '+13', '+21', '+22', '+31', '+32', '+41', '+42']
ringmap  = range(-9,0) + range(1,10)
RINGDICT = dict(zip(RINGLIST, ringmap))
HALVES = {
		'comp':['l','r','a'],
		'wire':['l','u','a'],
		}

BXDICT = {
		'wire':{
			'base':{
				1:{'lower':1,'upper':5},
				},
			'early':{
				1:{'lower':1,'upper':7},
				2:{'lower':1,'upper':6},
				3:{'lower':1,'upper':5},
				4:{'lower':1,'upper':4},
				5:{'lower':1,'upper':3},
				6:{'lower':1,'upper':2},
				7:{'lower':1,'upper':1},
				},
			'late':{
				43:{'lower':10,'upper':15},
				44:{'lower':10,'upper':14},
				45:{'lower':10,'upper':13},
				46:{'lower':10,'upper':12},
				47:{'lower':10,'upper':11},
				48:{'lower':10,'upper':10},
				},
			},
		'comp':{
			'base':{
				1:{'lower':1,'upper':5},
				},
			'early':{
				1:{'lower':1,'upper':5},
				2:{'lower':1,'upper':4},
				3:{'lower':1,'upper':3},
				4:{'lower':1,'upper':2},
				5:{'lower':1,'upper':1},
				},
			'late':{
				48:{'lower':9,'upper':9},
				},
			}
		}

#FILE = R.TFile.Open('/afs/cern.ch/user/a/adasgupt/public/GOAT_P5_TREE.root')
FILE = R.TFile.Open('/afs/cern.ch/user/a/adasgupt/public/GOAT_P5_TREE_5M.root')
tree = FILE.Get('t')

### Set Histograms
HISTS = {DIGI:{WHEN:{} for WHEN in BXDICT[DIGI].keys()} for DIGI in BXDICT.keys()}
for DIGI in ['comp','wire']:
	for WHEN in BXDICT[DIGI].keys():
		HISTS[DIGI][WHEN] = {HALF:R.TH1D(DIGI+'_'+HALF+'_'+WHEN,'',  20,-10,10) for HALF in HALVES[DIGI]}

### Fill Data Histograms
for idx,entry in enumerate(tree):
	for WHEN in BXDICT[str(entry.DIGI)].keys():
		if entry.BX in BXDICT[str(entry.DIGI)][WHEN].keys():
			nDigi = 0.
			for time in entry.D_TIME:
				if time >= BXDICT[str(entry.DIGI)][WHEN][entry.BX]['lower'] and \
				   time <= BXDICT[str(entry.DIGI)][WHEN][entry.BX]['upper']:
					nDigi+=1
			HISTS[str(entry.DIGI)][WHEN][str(entry.HALF)].Fill(RINGDICT[str(entry.ENDCAP)+str(entry.RING)],nDigi)

### Normalize and combine histograms
for DIGI in BXDICT.keys():
	for WHEN in BXDICT[DIGI].keys():
		HISTS[DIGI][WHEN][HALVES[DIGI][0]].Scale(1./HISTS[DIGI][WHEN][HALVES[DIGI][0]].GetEntries())
		HISTS[DIGI][WHEN][HALVES[DIGI][1]].Scale(1./HISTS[DIGI][WHEN][HALVES[DIGI][1]].GetEntries())
		HISTS[DIGI][WHEN][HALVES[DIGI][2]].Add(HISTS[DIGI][WHEN][HALVES[DIGI][0]])
		HISTS[DIGI][WHEN][HALVES[DIGI][2]].Add(HISTS[DIGI][WHEN][HALVES[DIGI][1]])

### Make plots
def makePlot(dataHist,DIGI,WHEN):
	# Make integral plot for each digi and plot type
	dataPlot = Plotter.Plot(dataHist,option='p')
	TITLE = ('Comparator ' if DIGI=='comp' else 'Wire Group ')+'Integral Occupancy'
	for LOGY in [True,False]:
		canvas = Plotter.Canvas(lumi=TITLE,logy=LOGY)
		canvas.addMainPlot(dataPlot)
		maximum = max(dataPlot.GetMaximum(),0.)#,mcPlot.GetMaximum())
		canvas.firstPlot.SetMaximum(maximum * 1.075)
		canvas.firstPlot.SetMinimum(1E-4 if LOGY else 0.)
		canvas.firstPlot.setTitles(X='CSC Ring', Y='Counts')
		canvas.firstPlot.GetXaxis().SetRangeUser(-9,10)
		for RING in RINGLIST:
			bin_ = RINGDICT[RING] + 11
			canvas.firstPlot.GetXaxis().SetBinLabel(bin_, RING.replace('-','#minus'))
		canvas.makeTransparent()
		canvas.finishCanvas('BOB')
		#name = 'mcdata_'+DIGI+'_integrals_'+mcType+('_logy' if LOGY else '')
		name = 'integral_'+DIGI+'_'+WHEN+('_logy' if LOGY else '')
		canvas.save('pdfs/'+name+'.pdf')
		canvas.deleteCanvas()

for DIGI in HISTS.keys():
	for WHEN in BXDICT[DIGI].keys():
		makePlot(HISTS[DIGI][WHEN]['a'],DIGI,WHEN)
