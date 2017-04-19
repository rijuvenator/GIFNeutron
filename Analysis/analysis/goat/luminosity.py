import sys, os, argparse
import numpy as np
import ROOT as R
import math as math
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi
R.gROOT.SetBatch(True)


RINGLIST = ['42', '41', '32', '31', '22', '21', '13', '12', '11']
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

minEntries = 1. # Minimum number of entries in each luminosity bin of the rate histogram

#FILE = R.TFile.Open('/afs/cern.ch/user/a/adasgupt/public/GOAT_P5_TREE.root')
FILE = R.TFile.Open('/afs/cern.ch/user/a/adasgupt/public/GOAT_P5_TREE_5M.root')
tree = FILE.Get('t')

# Set Histograms
nBins = 30
Upper = 15E33
NUM  = {RING:{DIGI:{WHEN:{} for WHEN in BXDICT[DIGI].keys()} for DIGI in BXDICT.keys()} for RING in RINGLIST}
DEN = NUM.copy()
RATE = NUM.copy()
for DIGI in BXDICT.keys():
	for WHEN in BXDICT[DIGI].keys():
		for RING in RINGLIST:
			NUM[RING][DIGI][WHEN] = {
					HALF:R.TH1D(DIGI+'_num_'+HALF+'_'+RING+'_'+WHEN,'',nBins,0,Upper) for HALF in HALVES[DIGI][0:2]
				}
			DEN[RING][DIGI][WHEN] = {
					HALF:R.TH1D(DIGI+'_den_'+HALF+'_'+RING+'_'+WHEN,'',nBins,0,Upper) for HALF in HALVES[DIGI][0:2]
				}
			RATE[RING][DIGI][WHEN] = {
					HALF:R.TH1D(DIGI+'_rate_'+HALF+'_'+RING+'_'+WHEN,'',nBins,0,Upper) for HALF in HALVES[DIGI]
				}

# Fill Data Histograms
for idx,entry in enumerate(tree):
	for WHEN in BXDICT[str(entry.DIGI)].keys():
		if entry.BX in BXDICT[str(entry.DIGI)][WHEN].keys():
			nDigi = 0.
			for time in entry.D_TIME:
				if time >= BXDICT[str(entry.DIGI)][WHEN][entry.BX]['lower'] and \
				   time <= BXDICT[str(entry.DIGI)][WHEN][entry.BX]['upper']:
					nDigi+=1
			NUM[str(entry.RING)][str(entry.DIGI)][WHEN][str(entry.HALF)].Fill(entry.LUMI,nDigi)
			DEN[str(entry.RING)][str(entry.DIGI)][WHEN][str(entry.HALF)].Fill(entry.LUMI,1.)

# Custom divide function
def divide(hist,numHist,denHist,minEntries):
	# hist = numHist / denHist
	# sets bin content to 0 if den bin contnet is < minEntries
	# uncertainty in each bin is statistical and relative to the numerator
	binit = denHist.GetNbinsX()
	for i in range(1,binit+1):
		num = float(numHist.GetBinContent(i))
		den = float(denHist.GetBinContent(i))
		rate = 0.
		numRelErr = 0.
		if den>0 and float(num)>=minEntries:
			rate = float(num)/den
			numRelErr = 1./math.sqrt(num)
		hist.SetBinContent(i,rate)
		hist.SetBinError(i,rate*numRelErr)

# Divide Data histograms to get rate
for DIGI in BXDICT.keys():
	for WHEN in BXDICT[DIGI].keys():
		for RING in RINGLIST:
			# do each half-detector separately
			# rate = num / den and each lumi bin has at least minEntries entries
			divide(RATE[RING][DIGI][WHEN][HALVES[DIGI][0]],NUM[RING][DIGI][WHEN][HALVES[DIGI][0]],DEN[RING][DIGI][WHEN][HALVES[DIGI][0]],minEntries)
			divide(RATE[RING][DIGI][WHEN][HALVES[DIGI][1]],NUM[RING][DIGI][WHEN][HALVES[DIGI][1]],DEN[RING][DIGI][WHEN][HALVES[DIGI][1]],minEntries)
			# Add each half into the total
			RATE[RING][DIGI][WHEN][HALVES[DIGI][2]].Add(RATE[RING][DIGI][WHEN][HALVES[DIGI][0]])
			RATE[RING][DIGI][WHEN][HALVES[DIGI][2]].Add(RATE[RING][DIGI][WHEN][HALVES[DIGI][1]])

### Make plots
def makePlot(dataHist,DIGI,RING,WHEN):
	# Plot counts vs. luminosity for sum of half-detector
	dataPlot = Plotter.Plot(dataHist,option='p')
	TITLE = 'ME'+RING+(' Wire Group Rate ' if DIGI=='wire' else ' Comparator Rate ')+'vs. Luminosity'
	for LOGY in [True,False]:
		canvas = Plotter.Canvas(lumi=TITLE,logy=LOGY)
		canvas.addMainPlot(dataPlot)
		canvas.firstPlot.SetMinimum(1E-3 if LOGY else 0.)
		canvas.firstPlot.setTitles(X='Luminosity [cm^{-2}s^{-1}]', Y='Rate')
		canvas.makeTransparent()
		canvas.finishCanvas('BOB')
		name = 'luminosity_'+RING+'_'+DIGI+'_'+WHEN+('_logy' if LOGY else '')
		canvas.save('pdfs/'+name+'.pdf')
		canvas.deleteCanvas()

def makeSepPlot(hist1,hist2,DIGI,RING,WHEN):
	# Make counts vs. luminosity plots for each half separately and plot them on 
	# the same axis
	plot1 = Plotter.Plot(hist1,legType='p',legName='Upper half' if DIGI=='wire' else 'Right half',option='p')
	plot2 = Plotter.Plot(hist2,legType='p',legName='Lower half' if DIGI=='wire' else 'Left half',option='p')
	TITLE = 'ME'+RING+(' Wire Group Rate ' if DIGI=='wire' else ' Comparator Rate ')+'vs. Luminosity'
	for LOGY in [True,False]:
		canvas = Plotter.Canvas(lumi=TITLE,logy=LOGY)
		canvas.addMainPlot(plot1)
		canvas.addMainPlot(plot2)
		plot1.SetLineColor(R.kRed)
		plot1.SetMarkerColor(R.kRed)
		plot2.SetLineColor(R.kBlue)
		plot2.SetMarkerColor(R.kBlue)
		maximum = max(plot1.GetMaximum(),plot2.GetMaximum())
		canvas.firstPlot.SetMaximum(maximum * 1.075)
		canvas.firstPlot.SetMinimum(1E-3 if LOGY else 0.)
		canvas.firstPlot.setTitles(X='Luminosity [cm^{-2}s^{-1}]', Y='Rate')
		canvas.makeLegend(pos='tl')
		canvas.makeTransparent()
		canvas.finishCanvas('BOB')
		name = 'luminosity_'+RING+'_separate_'+DIGI+'_'+WHEN+('_logy' if LOGY else '')
		canvas.save('pdfs/'+name+'.pdf')
		canvas.deleteCanvas()

for DIGI in BXDICT.keys():
	for WHEN in BXDICT[DIGI].keys():
		for RING in RINGLIST:
			makePlot(RATE[RING][DIGI][WHEN][HALVES[DIGI][2]],DIGI,RING,WHEN)
			makeSepPlot(RATE[RING][DIGI][WHEN][HALVES[DIGI][0]],RATE[RING][DIGI][WHEN][HALVES[DIGI][1]],DIGI,RING,WHEN)
