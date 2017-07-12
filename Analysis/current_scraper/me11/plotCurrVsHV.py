'''
Script to scrape txt output files and make a plot of curr at 10^34 lumi vs 
channel HV
6-July-2017 : 14:24 - first attempt is to plot curr vs HV separately for layer and endcap
11-July-2017 : 18:11 - move conv dictionary into a module
'''

import ROOT as R
import numpy as np
import math as math
import array as array

import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.roottools as tools

from fillDict import fills
R.gROOT.SetBatch(True)
R.gStyle.SetLineWidth(1)
colors = [R.kBlue,R.kCyan+2,R.kGreen+1,R.kOrange+1,R.kRed,R.kViolet]

from plotDict import conv

## Make dict of conversions and HV
## Loop on data files and fill dictionary
#conv = {fill:{ec:{cham:{layer:{} for layer in range(1,7)} for cham in range(1,37)} for ec in ['P','N']} for fill in fills.keys()}

# Make plot
for ec in ['P','N']:
	for layer in range(1,7):
		# Plot a single layer on one endcap
		HVs = np.array([])
		currs = np.array([])
		for fill in fills.keys():
			for cham in conv[fill][ec].keys():
				if 'HV' not in conv[fill][ec][cham][layer].keys(): continue
				if conv[fill][ec][cham][layer]['HV']<0: continue
				HVs = np.append(HVs,conv[fill][ec][cham][layer]['HV'])
				currs = np.append(currs,conv[fill][ec][cham][layer]['slope'])
		graph = R.TGraph(len(HVs),HVs,currs)
		plot = Plotter.Plot(graph,option='ap')
		canvas = Plotter.Canvas(lumi='ME'+('+' if ec=='P' else '-')+' L'+str(layer))
		canvas.addMainPlot(plot)
		plot.setTitles(X='HV [V]',Y='Current [#muA] at L=10^{34}/cm^{2}/s')
		canvas.makeTransparent()
		canvas.finishCanvas('BOB')
		canvas.save('plots/currentVsHV_ME'+ec+'_L'+str(layer)+'.pdf')
		canvas.deleteCanvas()
