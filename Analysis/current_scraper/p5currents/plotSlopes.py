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

from fillDict import fills
R.gROOT.SetBatch(True)
R.gStyle.SetLineWidth(1)
colors = [R.kBlue,R.kCyan+2,R.kGreen+1,R.kOrange+1,R.kRed,R.kViolet]

# Make dict of conversions
conv = {fill:{ec:{cham:{layer:{} for layer in range(1,7)} for cham in range(1,37)} for ec in ['P','N']} for fill in fills.keys()}
# Loop on data files and fill dictionary
for idx,fill in enumerate(fills.keys()):
	start = fills[fill][0].replace(' ','_')
	end   = fills[fill][1].replace(' ','_')
	dFile = 'results_noOffset/fill'+str(fill)+'/f'+str(fill)+'_['+start+'-'+end+'].txt'
	data = open(dFile,'r')
	#print dFile
	for jdx,columns in enumerate(data):
		# Skip the header line
		if jdx==0: continue
		# Skip empty lines
		if columns=='\n': continue
		col = columns.strip('\n').split()
		# Skip Chambers which are problematic
		if col[0] == 'CSC_ME_P11_C01_5': continue
		if col[0] == 'CSC_ME_P11_C10_4': continue
		if col[0] == 'CSC_ME_P11_C33_3': continue
		if col[0] == 'CSC_ME_N11_C04_4': continue
		if col[0] == 'CSC_ME_N11_C08_3': continue
		if col[0] == 'CSC_ME_N11_C09_2': continue
		if col[0] == 'CSC_ME_N11_C12_3': continue
		if col[0] == 'CSC_ME_N11_C12_6': continue
		if col[0] == '###': continue
		if len(col)<8: 
			#print fill,col[0],len(col)
			continue

		channel = col[0].split('_')
		ec = channel[2][0]
		cham = int(channel[3][1:])
		layer = int(channel[4])
		#print ec, cham, layer, col[8], col[9]
		conv[fill][ec][cham][layer] = {
				'slope':float(col[8]),
				'err'  :float(col[9]),
				}
	
## Make plot of conversion factor as a function of fill for every chamber
fillList = fills.keys()
fillList.sort()
#print fillList
for ec in ['P','N']:
	for cham in range(1,37):
		convs = {lay:np.array([]) for lay in conv[fill][ec][cham].keys()}
		converrs = {lay:np.array([]) for lay in conv[fill][ec][cham].keys()}
		xerr = {lay:np.array([]) for lay in conv[fill][ec][cham].keys()}
		x = {lay:np.array([]) for lay in conv[fill][ec][cham].keys()}
		n = {lay:0. for lay in conv[fill][ec][cham].keys()}
		for layer in range(1,7):
			if ec=='P' and cham==1 and layer==5: continue
			if ec=='P' and cham==10 and layer==4: continue
			if ec=='P' and cham==33 and layer==3: continue
			if ec=='N' and cham==4 and layer==4: continue
			if ec=='N' and cham==9 and layer==2: continue
			if ec=='N' and cham==8 and layer==3: continue
			if ec=='N' and cham==12 and layer==3: continue
			if ec=='N' and cham==12 and layer==6: continue
			# Get data from dict
			for fill in fillList:
				# Skip if the data doesn't exist
				if len(conv[fill][ec][cham][layer].keys())<1: continue
				#print fill, ec, cham, layer, conv[fill][ec][cham][layer]['slope']
				convs[layer]    = np.append(convs[layer],   conv[fill][ec][cham][layer]['slope'])
				converrs[layer] = np.append(converrs[layer],conv[fill][ec][cham][layer]['err'])
				xerr[layer] = np.append(xerr[layer],0.)
				x[layer] = np.append(x[layer],n[layer])
				n[layer] += 1
				#print ec, cham, layer, fill, conv[fill][ec][cham][layer]['slope'], conv[fill][ec][cham][layer]['err']
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
			canv.save('plots/'+ec+str(cham)+'_L'+str(layer)+'_convVsFill.pdf')
			canv.deleteCanvas()
		# Make all layers in one plot
		plots = []
		graphs = []
		maxes = []
		canvA = Plotter.Canvas(lumi=ec+str(cham)+' curr/lumi conv vs. fill')
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
		canvA.save('plots/'+ec+str(cham)+'_convVsFill.pdf')
		canvA.deleteCanvas()

# Make plot of conversion factor as a function of channel for every fill
for fill in fillList:
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
			for layer in conv[fill][ec][cham].keys():
				if len(conv[fill][ec][cham][layer].keys())<1: continue
				if ec=='P' and cham==1 and layer==5: continue
				if ec=='P' and cham==10 and layer==4: continue
				if ec=='P' and cham==33 and layer==3: continue
				if ec=='N' and cham==4 and layer==4: continue
				if ec=='N' and cham==9 and layer==2: continue
				#print fill,ec,cham,layer
				convs[layer]    = np.append(convs[layer],   conv[fill][ec][cham][layer]['slope'])
				converrs[layer] = np.append(converrs[layer],conv[fill][ec][cham][layer]['err'])
				x[layer] = np.append(x[layer],n[layer])
				xerr[layer] = np.append(xerr[layer], 0.)
				n[layer]+=1
	# Make Plot
	graphs = []
	plots = []
	canv = Plotter.Canvas(lumi='fill '+str(fill)+' curr/lumi conv vs. HV channel',cWidth=1500)
	for l in range(1,7):
		graph = R.TGraphErrors(len(convs[l]),x[l], convs[l], xerr[l], converrs[l])
		graphs.append(graph)
		plot = Plotter.Plot(graph,option='p',legType='p',legName='Layer %i'%l)
		plots.append(plot)
	for p,plot in enumerate(plots):
		canv.addMainPlot(plot)
	for p,plot in enumerate(plots):
		plot.SetMarkerColor(colors[p])
		plot.SetMarkerSize(1)
		plot.SetMinimum(0.)
		plot.setTitles(X='Chamber',Y='Conversion current/lumi [#muA/10^{34}cm^{-2}s^{-1}]')
		# re-label bins
		for b in x[p+1]:
			ibin = plot.GetXaxis().FindBin(b)
			plot.GetXaxis().SetBinLabel(ibin,labels[int(b)])
	maximum = max([plot.GetHistogram().GetMaximum() for plot in plots])
	canv.firstPlot.SetMaximum(maximum*1.1)
	canv.makeLegend(pos='tr')
	canv.makeTransparent()
	canv.finishCanvas('BOB')
	canv.save('plots/fill'+str(fill)+'_convVsChan.pdf')
	canv.deleteCanvas()



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
			for layer in conv[fill][ec][cham].keys():
				if 'slope' not in conv[fill][ec][cham][layer].keys(): continue
				convs = np.append(convs,conv[fill][ec][cham][layer]['slope'])
				converrs = np.append(converrs,conv[fill][ec][cham][layer]['err'])
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
		for b in range(36):
			ibin = plot.GetXaxis().FindBin(b)
			plot.GetXaxis().SetBinLabel(ibin,labels[int(b)])
	canv.firstPlot.SetMaximum(20.)
	res='#splitline{#color[%s]{Plus mean %6.3f #pm %5.3f}}{#color[%s]{Minus mean %6.3f #pm %5.3f}}'%(plots[0].GetMarkerColor(),means[0],stds[0],plots[1].GetMarkerColor(),means[1],stds[1])
	print str(fill)
	print 'plus',means[0],stds[0]
	print 'minus',means[1],stds[1]
	canv.drawText(text=res,pos=(0.2,0.85),align='tl')
	#canv.makeLegend(pos='tr')
	canv.makeTransparent()
	canv.finishCanvas('BOB')
	canv.save('plots/fill'+str(fill)+'_convVsCham.pdf')
	canv.deleteCanvas()
