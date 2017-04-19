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


RINGLIST = ['42', '41', '32', '31', '22', '21', '13', '12', '11']
halves = {
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
OCC = {
		RING:{DIGI:{WHEN:{} for WHEN in BXDICT[DIGI].keys()} for DIGI in BXDICT.keys()} for RING in RINGLIST
		}
for RING in RINGLIST:
	cham = CH.Chamber(CH.serialID(1, int(RING[0]), int(RING[1]), 1))
	nhs = cham.nstrips*2+2
	nwg = cham.nwires+2
	for DIGI in BXDICT.keys():
		lim = nhs if DIGI=='comp' else nwg
		for WHEN in BXDICT[DIGI].keys():
			OCC[RING][DIGI][WHEN] = {
					HALF:{'hist':R.TH1D(DIGI+'_occ_'+RING+'_'+HALF+'_'+WHEN,'',lim,0,lim),'count':0.} for HALF in halves[DIGI]
					}

# Fill Data Histograms
for idx,entry in enumerate(tree):
	for WHEN in BXDICT[str(entry.DIGI)].keys():
		if entry.BX in BXDICT[str(entry.DIGI)][WHEN].keys():
			OCC[str(entry.RING)][str(entry.DIGI)][WHEN][str(entry.HALF)]['count']+=1
			for idigi,time in enumerate(entry.D_TIME):
				if time >= BXDICT[str(entry.DIGI)][WHEN][entry.BX]['lower'] and \
				   time <= BXDICT[str(entry.DIGI)][WHEN][entry.BX]['upper']:
					OCC[str(entry.RING)][str(entry.DIGI)][WHEN][str(entry.HALF)]['hist'].Fill(entry.D_POS[idigi])

### Normalize and combine histograms
for DIGI in BXDICT.keys():
	for WHEN in BXDICT[DIGI].keys():
		for RING in RINGLIST:
			### Normalize each half of the detector individually
			OCC[RING][DIGI][WHEN][halves[DIGI][0]]['hist'].Scale(1./OCC[RING][DIGI][WHEN][halves[DIGI][0]]['count'])
			OCC[RING][DIGI][WHEN][halves[DIGI][1]]['hist'].Scale(1./OCC[RING][DIGI][WHEN][halves[DIGI][1]]['count'])
			### Add each half into single histogram
			OCC[RING][DIGI][WHEN][halves[DIGI][2]]['hist'].Add(OCC[RING][DIGI][WHEN][halves[DIGI][0]]['hist'])
			OCC[RING][DIGI][WHEN][halves[DIGI][2]]['hist'].Add(OCC[RING][DIGI][WHEN][halves[DIGI][1]]['hist'])

### Make plots
def makePlot(dataHist,DIGI,RING,WHEN):
	# Plot occupancy for each ring, digi, and type
	dataPlot = Plotter.Plot(dataHist,option='p')
	TITLE = 'ME'+RING+(' Comparator ' if DIGI=='comp' else ' Wire Group ')+'Occupancy'
	for LOGY in [True,False]:
		canvas = Plotter.Canvas(lumi=TITLE,logy=LOGY)
		canvas.addMainPlot(dataPlot)
		maximum = max(dataPlot.GetMaximum(),0.)#,mcPlot.GetMaximum())
		canvas.firstPlot.SetMaximum(maximum * 1.05)
		canvas.firstPlot.SetMinimum(1E-4 if LOGY else 0.)
		xaxis = 'Comparator Half Strip Number' if DIGI=='comp' else 'Wire Group Number'
		canvas.firstPlot.setTitles(X=xaxis, Y='Counts per BX')
		canvas.makeTransparent()
		canvas.finishCanvas('BOB')
		#name = 'occupancy_'+DIGI+'_ME'+RING+'_'+mcType+('_logy' if LOGY else '')
		name = 'occupancy_'+DIGI+'_ME'+RING+'_'+WHEN+('_logy' if LOGY else '')
		canvas.save('pdfs/'+name+'.pdf')
		canvas.deleteCanvas()

for DIGI in BXDICT.keys():
	for WHEN in BXDICT[DIGI].keys():
		for RING in RINGLIST:
			makePlot(OCC[RING][DIGI][WHEN]['a']['hist'],DIGI,RING,WHEN)
