''' 
Script is to scrape txt output files and makes two plots
- the conversion factor between current and luminosity as a function of fill 
  for each chamber and layer
- the conversion factor for all chambers and layers in a specific fill
'''
import ROOT as R
import numpy as np
import math as math
import array as array

import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.roottools as tools

import logging
from helper21 import fills,make_conv,setup_logger

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-o','--offset',dest='OFFSET',action='store_true',default=False)
args = parser.parse_args()

R.gROOT.SetBatch(True)
R.gStyle.SetLineWidth(1)
colors = [R.kBlue,R.kCyan+2,R.kGreen+1,R.kOrange+1,R.kRed,R.kViolet]

conv = make_conv(args.OFFSET)

## Make dict of conversions
#conv = {fill:{ec:{cham:{seg:{layer:{} for layer in range(1,7)} for seg in range(1,4)} for cham in range(1,19)} for ec in ['P','N']} for fill in fills.keys()}
## Loop on data files and fill dictionary
#for idx,fill in enumerate(fills.keys()):
#	newpdfname = where+'/fill'+str(fill)+'/'+'f'+str(fill)
#	timestampMin = fills[fill][0]
#	timestampMax = fills[fill][1]
#	if(len(timestampMax)>0 or len(timestampMin)>0):
#		newpdfname+= '_'+timestampMin.replace(' ','_')#+'-'+timestampMax.replace(' ','_')
#		newpdfname=newpdfname[:len(newpdfname)-3]+'-'+timestampMax.replace(' ','_')
#		newpdfname=newpdfname[:len(newpdfname)-3].replace(':','h')
#	newpdfname+='.txt'
#	print 'creating pdf: '+newpdfname
#	dFile = newpdfname
#
#	#dFile = 'results/fill'+str(fill)+'/f'+str(fill)+'_['+start+'-'+end+'].txt' # old ME11
#	#dFile = 'results_noOffset/fill'+str(fill)+'/f'+str(fill)+'_'+start+'-'+end+'.txt'
#	#dFile = 'results/fill5451/f5451_26.10.16_08h50-26.10.16_23h00.txt'
#	data = open(dFile,'r')
#	#print dFile
#	for jdx,columns in enumerate(data):
#		# Skip the header line
#		if jdx==0: continue
#		# Skip empty lines
#		if columns=='\n': continue
#		col = columns.strip('\n').split()
#		# Skip channels which are problematic
#		if col[0]=='CSC_ME_P21_C06_2_2': continue # 2 points a crappy fit makes
#		if col[0]=='CSC_ME_P21_C13_1_3': continue # 2 points a crappy fit makes
#		# Skip lines w/o data
#		if col[0] == '###': continue
#		if len(col)<8: 
#			#print fill,col[0],len(col)
#			continue
#
#		# channel = CSC_ME_P21_C01_1_1 
#		channel = col[0].split('_')
#		ec = channel[2][0]
#		ring = channel[2][1:3]
#		cham = int(channel[3][1:])
#		segment = int(channel[4])
#		layer = int(channel[5])
#		HV = float(col[2])
#		#print ec, cham, layer, col[8], col[9]
#		cslope = 10 if args.OFFSET else 8
#		cerr = 11 if args.OFFSET else 9
#		conv[fill][ec][cham][segment][layer] = {
#				'slope':float(col[cslope]),
#				'err'  :float(col[cerr]),
#				'HV':HV
#				}
print conv
	
fillList = fills.keys()
#fillList = [5338,5416,5450,5451,5394,5443,5418,5433,5406,5405,5401,5395]
fillList.sort()
#print fillList
## Make plot of conversion factor as a function of fill for every chamber
for ec in ['P','N']:
	for cham in range(1,19):
		for segment in range(1,4):
			convs = {lay:np.array([]) for lay in conv[fill][ec][cham][segment].keys()}
			converrs = {lay:np.array([]) for lay in conv[fill][ec][cham][segment].keys()}
			xerr = {lay:np.array([]) for lay in conv[fill][ec][cham][segment].keys()}
			x = {lay:np.array([]) for lay in conv[fill][ec][cham][segment].keys()}
			n = {lay:0. for lay in conv[fill][ec][cham][segment].keys()}
			for layer in range(1,7):
				# Get data from dict
				for fill in fillList:
					# Skip if the data doesn't exist
					if len(conv[fill][ec][cham][segment][layer].keys())<1: continue
					#print fill, ec, cham, layer, conv[fill][ec][cham][segment][layer]['slope']
					convs[layer]    = np.append(convs[layer],   conv[fill][ec][cham][segment][layer]['slope'])
					converrs[layer] = np.append(converrs[layer],conv[fill][ec][cham][segment][layer]['err'])
					xerr[layer] = np.append(xerr[layer],0.)
					x[layer] = np.append(x[layer],n[layer])
					n[layer] += 1
					#print ec, cham, layer, fill, conv[fill][ec][cham][segment][layer]['slope'], conv[fill][ec][cham][segment][layer]['err']
				# make a plot of only this channel vs fill
				#print len(fillList),len(x[layer]), len(convs[layer]), len(xerr[layer]), len(converrs[layer])
				#print fillList,x[layer], convs[layer], xerr[layer], converrs[layer]
				convVsFill = R.TGraphErrors(len(fillList), x[layer], convs[layer], xerr[layer], converrs[layer])
				plot = Plotter.Plot(convVsFill,option='ap')
				canv = Plotter.Canvas(lumi=ec+str(cham)+' '+str(layer)+'curr/lumi conv vs. fill')
				canv.addMainPlot(plot)
				plot.setTitles(X='Fill Number',Y='Conversion current/lumi [#muA/cm^{-2}s^{-1}]')
				plot.SetMinimum(0.)
				# re-label bins
				for b in range(len(fillList)):
					ibin = plot.GetXaxis().FindBin(b)
					plot.GetXaxis().SetBinLabel(ibin,str(fillList[b]))
				canv.makeTransparent()
				canv.finishCanvas('BOB')
				canv.save(save+ec+str(cham)+'_S'+str(segment)+'_L'+str(layer)+'_convVsFill.pdf')
				canv.deleteCanvas()
			# Make all layers in one plot
			plots = []
			graphs = []
			maxes = []
			canvA = Plotter.Canvas(lumi=ec+str(cham)+' HVs'+str(segment)+' curr/lumi conv vs. fill')
			for lay in range(1,7):
				#print ec,cham,lay
				#print len(fillList),len(x[lay]), len(convs[lay]), len(xerr[lay]), len(converrs[lay])
				#print fillList,x[lay], convs[lay], xerr[lay], converrs[lay]
				if len(x[lay])<1: continue
				graph = R.TGraphErrors(len(fillList), x[lay], convs[lay], xerr[lay], converrs[lay])
				graphs.append(graph)
				plot = Plotter.Plot(graph,option='p',legType='p',legName='Layer %i'%lay)
				plots.append(plot)
			for plot in plots:
				canvA.addMainPlot(plot)
			for p,plot in enumerate(plots):
				plot.SetMarkerSize(1)
				plot.SetMarkerColor(colors[p])
				plot.setTitles(X='Fill Number',Y='Conversion current/lumi [#muA/10^{34}cm^{-2}s^{-1}]')
				plot.SetMinimum(0.)
				# re-label bins
				for b in range(len(fillList)):
					ibin = plot.GetXaxis().FindBin(b)
					plot.GetXaxis().SetBinLabel(ibin,str(fillList[b]))
			canvA.makeLegend(pos='bl')
			maximum = max([plot.GetHistogram().GetMaximum() for plot in plots])
			canvA.firstPlot.SetMaximum(maximum*1.1)
			canvA.makeTransparent()
			canvA.finishCanvas('BOB')
			canvA.save(save+ec+str(cham)+'_HVs'+str(segment)+'convVsFill.pdf')
			canvA.deleteCanvas()

# Make plot of conversion factor as a function of channel for every fill
for fill in fillList:
	for segment in range(1,4):
		convs = {lay:np.array([]) for lay in range(1,7)}
		converrs = {lay:np.array([]) for lay in range(1,7)}
		labels = []
		x = {lay:np.array([]) for lay in range(1,7)}
		xerr = {lay:np.array([]) for lay in range(1,7)}
		n = {lay:0. for lay in range(1,7)}
		for ec in conv[fill].keys():
			for cham in conv[fill][ec].keys():
				label = ('+' if ec=='P' else '-')+str(cham)
				labels.append(label)
				for layer in conv[fill][ec][cham][segment].keys():
					if len(conv[fill][ec][cham][segment][layer].keys())<1: continue
					#print fill,ec,cham,layer
					convs[layer]    = np.append(convs[layer],   conv[fill][ec][cham][segment][layer]['slope'])
					converrs[layer] = np.append(converrs[layer],conv[fill][ec][cham][segment][layer]['err'])
					x[layer] = np.append(x[layer],n[layer])
					xerr[layer] = np.append(xerr[layer], 0.)
					n[layer]+=1
		# Make Plot
		graphs = []
		plots = []
		canv = Plotter.Canvas(lumi='fill '+str(fill)+' curr/lumi conv vs. HV channel '+str(segment),cWidth=1500)
		for l in range(1,7):
			graph = R.TGraphErrors(len(convs[l]),x[l], convs[l], xerr[l], converrs[l])
			graphs.append(graph)
			plot = Plotter.Plot(graph,option='p',legType='p',legName='Layer %i'%l)
			plots.append(plot)
		print 'a'
		for p,plot in enumerate(plots):
			canv.addMainPlot(plot)
		print 'b'
		for p,plot in enumerate(plots):
			plot.SetMarkerColor(colors[p])
			plot.SetMarkerSize(1)
			plot.SetMinimum(0.)
			plot.setTitles(X='Chamber',Y='Conversion current/lumi [#muA/10^{34}cm^{-2}s^{-1}]')
			# re-label bins
			for b in x[p+1]:
				ibin = plot.GetXaxis().FindBin(b)
				plot.GetXaxis().SetBinLabel(ibin,labels[int(b)])
		print 'c'
		maximum = max([plot.GetHistogram().GetMaximum() for plot in plots])
		canv.firstPlot.SetMaximum(maximum*1.1)
		canv.makeLegend(pos='tr')
		canv.makeTransparent()
		canv.finishCanvas('BOB')
		canv.save(save+'fill'+str(fill)+'_convVsChan'+str(segment)+'.pdf')
		canv.deleteCanvas()



'''
# Plot summed HV currents for a whole chamber in one fill vs. chamber #
for fill in conv.keys():
	labels = []
	graphs = []
	plots = []
	means = []
	stds = []
	for ec in conv[fill].keys():
		n=0.
		x = np.array([])
		xerr = np.array([])
		totals = np.array([])
		totalerrs = np.array([])
		for cham in conv[fill][ec].keys():
			convs = np.array([])
			converrs = np.array([])
			for segment in range(1,4):
				for layer in conv[fill][ec][cham][segment].keys():
					if 'slope' not in conv[fill][ec][cham][segment][layer].keys(): continue
					convs = np.append(convs,conv[fill][ec][cham][segment][layer]['slope'])
					converrs = np.append(converrs,conv[fill][ec][cham][segment][layer]['err'])
			labels.append(str(cham))
			totals = np.append(totals,np.sum(convs))
			totalerrs = np.append(totalerrs,math.sqrt(np.sum(converrs**2)))
			x = np.append(x,n)
			xerr = np.append(xerr,0.)
			n+=1
		graph = R.TGraphErrors(len(totals),x,totals,xerr,totalerrs)
		graphs.append(graph)
		plot = Plotter.Plot(graph,legName=('Plus' if ec=='P' else 'Minus')+' endcap',legType='P',option='p')
		plots.append(plot)
		means.append(totals.mean())
		stds.append(totals.std())
	canv = Plotter.Canvas(lumi='Fill '+str(fill)+' Summed chamber current/lumi conversion')
	for plot in plots:
		canv.addMainPlot(plot)
	for p,plot in enumerate(plots):
		plot.SetMarkerSize(1)
		plot.SetMarkerColor(R.kBlue if p==0 else R.kOrange+1)
		plot.SetMinimum(0.)
		plot.setTitles(X='Chamber',Y='Conversion current/lumi [#muA/10^{34}cm^{-2}s^{-1}]')
		# re-label bins
		for b in range(18):
			ibin = plot.GetXaxis().FindBin(b)
			plot.GetXaxis().SetBinLabel(ibin,labels[int(b)])
	#canv.firstPlot.SetMaximum(20.)
	res='#splitline{#color[%s]{Plus mean %6.3f #pm %5.3f}}{#color[%s]{Minus mean %6.3f #pm %5.3f}}'%(plots[0].GetMarkerColor(),means[0],stds[0],plots[1].GetMarkerColor(),means[1],stds[1])
	print str(fill)
	print 'plus',means[0],stds[0]
	print 'minus',means[1],stds[1]
	canv.drawText(text=res,pos=(0.2,0.85),align='tl')
	#canv.makeLegend(pos='tr')
	canv.makeTransparent()
	canv.finishCanvas('BOB')
	canv.save(save+'fill'+str(fill)+'_convVsCham.pdf')
	canv.deleteCanvas()
'''
