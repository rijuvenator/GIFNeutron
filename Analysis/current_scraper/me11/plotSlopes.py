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
import logging

import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.roottools as tools

R.gROOT.SetBatch(True)
R.gStyle.SetLineWidth(1)
colors = [R.kBlue,R.kCyan+2,R.kGreen+1,R.kOrange+1,R.kRed,R.kViolet]

from helper11 import fills,conv,setup_logger

## Make dict of conversions
## Loop on data files and fill dictionary
#conv = {fill:{ec:{cham:{layer:{} for layer in range(1,7)} for cham in range(1,37)} for ec in ['P','N']} for fill in fills.keys()}

##############################################################################
# Set up logging

# Summed channel slope logger
fillSumSlopeName = 'fillSumSlope'
setup_logger(fillSumSlopeName,'logs/'+fillSumSlopeName+'.log')
fillSumSlopeLog = logging.getLogger(fillSumSlopeName)

# Individual channel slope logger
fillIndvSlopeName = 'fillIndvSlope'
setup_logger(fillIndvSlopeName,'logs/'+fillIndvSlopeName+'.log')
fillIndvSlopeLog = logging.getLogger(fillIndvSlopeName)
	
##############################################################################

## Make plot of conversion factor as a function of fill for every chamber
fillList = fills.keys()
fillList.sort()
#print fillList
for ec in ['P','N']:
	for cham in range(1,37):
		filltmp = 5451
		convs = {lay:np.array([]) for lay in conv[filltmp][ec][cham].keys()}
		converrs = {lay:np.array([]) for lay in conv[filltmp][ec][cham].keys()}
		xerr = {lay:np.array([]) for lay in conv[filltmp][ec][cham].keys()}
		x = {lay:np.array([]) for lay in conv[filltmp][ec][cham].keys()}
		n = {lay:0. for lay in conv[filltmp][ec][cham].keys()}
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

##############################################################################

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

##############################################################################

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
	res='#splitline{#color[%s]{Plus mean %6.3f, std %5.3f}}{#color[%s]{Minus mean %6.3f, std %5.3f}}'%(plots[0].GetMarkerColor(),means[0],stds[0],plots[1].GetMarkerColor(),means[1],stds[1])
	print str(fill)
	print 'plus',means[0],stds[0]
	print 'minus',means[1],stds[1]
	canv.drawText(text=res,pos=(0.2,0.85),align='tl')
	#canv.makeLegend(pos='tr')
	canv.makeTransparent()
	canv.finishCanvas('BOB')
	canv.save('plots/fill'+str(fill)+'_convVsCham.pdf')
	canv.deleteCanvas()

##############################################################################

#conv = {fill:{ec:{cham:{layer:{} for layer in range(1,7)} for cham in range(1,37)} for ec in ['P','N']} for fill in fills.keys()}
# Histogram individual channel currents
# +/- for each fill (2*nFills plots) hist1
# +/-/layer for each fill (72*6*nFills plots) hist5
# summed over channels
# +/- for each fill (2*nFills plots) hist7

def makeIndvSlope_fill_ec(hist,fill,ec):
	plot = Plotter.Plot(hist,option='le')
	title = 'Currents on ME'+('+' if ec=='P' else '-')+' Fill '+str(fill)
	canv = Plotter.Canvas(lumi=title)
	canv.addMainPlot(plot)
	plot.setTitles(X='Current at L=10^{34}/cm^{2}/s [#muA]',Y='Counts/0.10 #muA')
	mean,stddev,nentries = hist.GetMean(),hist.GetStdDev(),hist.GetEntries()
	text = '#splitline{Mean : %5.3f}{Std. Dev. : %5.3f}'%(hist.GetMean(),hist.GetStdDev())
	log = '{fill:>5} {ec:>3} {mean:>5.3f} {stddev:>5.3f} {nentries:>4}'.format(**locals())
	fillIndvSlopeLog.info(log)
	canv.drawText(text,align='tl',pos=(0.6,0.7))
	canv.finishCanvas('BOB')
	canv.save('plots/histIndvSlope_f%s_ME%s.pdf'%(str(fill),ec))
	canv.deleteCanvas()

def makeSumSlope_fill_ec(hist,fill,ec):
	plot = Plotter.Plot(hist,option='le')
	title = 'Summed Currents on ME'+('+' if ec=='P' else '-')+'1/1 Fill '+str(fill)
	canv = Plotter.Canvas(lumi=title)
	canv.addMainPlot(plot)
	plot.setTitles(X='Chamber Current at L=10^{34}/cm^{2}/s [#muA]',Y='Counts/0.25 #muA')
	mean,stddev,nentries = hist.GetMean(),hist.GetStdDev(),hist.GetEntries()
	text = '#splitline{Mean : %5.3f}{Std. Dev. : %5.3f}'%(mean,stddev)
	canv.drawText(text,align='tl',pos=(0.6,0.7))
	log = '{fill:>5} {ec:>3} {mean:>5.3f} {stddev:>5.3f} {nentries:>4}'.format(**locals())
	fillSumSlopeLog.info(log)
	canv.finishCanvas('BOB')
	canv.save('plots/histSumSlope_f%s_ME%s.pdf'%(str(fill),ec))
	canv.deleteCanvas()

def makeIndvSlope_fill_ec_layer(hist,fill,ec,layer):
	plot = Plotter.Plot(hist,option='le')
	title = 'Currents on ME'+('+' if ec=='P' else '-')+'1/1 Layer '+str(layer)+' Fill '+str(fill)
	canv = Plotter.Canvas(lumi=title)
	canv.addMainPlot(plot)
	plot.setTitles(X='Current at L=10^{34}/cm^{2}/s [#muA]',Y='Counts/0.10 #muA')
	#print fill, ec, layer, 'chan', hist.GetMean(), hist.GetStdDev()
	text = '#splitline{Mean : %5.3f}{Std. Dev. : %5.3f}'%(hist.GetMean(),hist.GetStdDev())
	canv.drawText(text,align='tl',pos=(0.6,0.7))
	canv.finishCanvas('BOB')
	canv.save('plots/histIndvSlope_f%s_ME%s_L%s.pdf'%(str(fill),ec,layer))
	canv.deleteCanvas()

for fill in fillList:
	for ec in ['P','N']:
		# set hist1
		histIndvSlope_fill_ec = R.TH1D('histIndvSlope_f%s_ME%s'%(str(fill),ec),'',50,0,5) # bin width 0.10 uA
		# set hist7
		histSumSlope_fill_ec = R.TH1D('histSumSlope_f%s_ME%s'%(str(fill),ec),'',80,0,20) # bin width 0.25 uA
		for cham in range(1,37):
			currSumCham = 0.
			for layer in range(1,7):
				# fill hist1
				if 'slope' not in conv[fill][ec][cham][layer].keys(): continue
				histIndvSlope_fill_ec.Fill(conv[fill][ec][cham][layer]['slope'])
				# sum hist7
				currSumCham += conv[fill][ec][cham][layer]['slope']
			# fill hist7
			histSumSlope_fill_ec.Fill(currSumCham)
		# plot hist1
		makeIndvSlope_fill_ec(histIndvSlope_fill_ec,fill,ec)
		# plot hist7
		makeSumSlope_fill_ec(histSumSlope_fill_ec,fill,ec)
		for layer in range(1,7):
			# set hist5
			histIndvSlope_fill_ec_layer = R.TH1D('histIndvSlope_f%s_ME%s_L%s'%(str(fill),ec,str(layer)),'',50,0,5) # bin width 0.10 uA
			for cham in range(1,37):
				if 'slope' not in conv[fill][ec][cham][layer].keys(): continue
				# fill hist5
				histIndvSlope_fill_ec_layer.Fill(conv[fill][ec][cham][layer]['slope'])
			# plot hist5
			makeIndvSlope_fill_ec_layer(histIndvSlope_fill_ec_layer,fill,ec,layer)

##############################################################################

# Individual channels
# +/- for all fills (2 plots) hist2 - filled 6*36*nFills times
# +/-/chamber for all fills (72 plots) hist4 - filled 6*nFills times
# +/-/layer for all fills (72*6 plots) hist6 - filled 36*nFills times
# Summed over channels
# +/- for all fills (2 plots) hist8 - filled 36*nFills times
# +/-/chamber for all fills (72 plots) hist10 - filled 6*nFills times

def makeIndvSlope_ec(hist,ec):
	plot = Plotter.Plot(hist,option='le')
	title = 'Currents on ME'+('+' if ec=='P' else '-')+'1/1 at L=10^{34}/cm^{2}/s'
	canv = Plotter.Canvas(lumi=title)
	canv.addMainPlot(plot)
	plot.setTitles(X='Current [#muA]',Y='Counts/0.10 #muA')
	#print ec, 'chan', hist.GetMean(), hist.GetStdDev()
	text = '#splitline{Mean : %5.3f}{Std. Dev. : %5.3f}'%(hist.GetMean(),hist.GetStdDev())
	canv.drawText(text,align='tl',pos=(0.6,0.7))
	canv.finishCanvas('BOB')
	canv.save('plots/histIndvSlope_ME%s.pdf'%(ec))
	canv.deleteCanvas()

def makeIndvSlope_ec_ch(hist,ec,cham):
	plot = Plotter.Plot(hist,option='le')
	title = 'Currents on ME'+('+' if ec=='P' else '-')+'1/1/'+str(cham)+' at L=10^{34}/cm^{2}/s'
	canv = Plotter.Canvas(lumi=title)
	canv.addMainPlot(plot)
	plot.setTitles(X='Current [#muA]',Y='Counts/0.10 #muA')
	#print ec,cham, 'chan', hist.GetMean(), hist.GetStdDev()
	text = '#splitline{Mean : %5.3f}{Std. Dev. : %5.3f}'%(hist.GetMean(),hist.GetStdDev())
	canv.drawText(text,align='tl',pos=(0.6,0.7))
	canv.finishCanvas('BOB')
	canv.save('plots/histIndvSlope_ME%s_ch%s.pdf'%(ec,str(cham)))
	canv.deleteCanvas()

def makeIndvSlope_ec_l(hist,ec,layer):
	plot = Plotter.Plot(hist,option='le')
	title = 'Currents on ME'+('+' if ec=='P' else '-')+'1/1 Layer '+str(layer)+' at L=10^{34}/cm^{2}/s'
	canv = Plotter.Canvas(lumi=title)
	canv.addMainPlot(plot)
	plot.setTitles(X='Current [#muA]',Y='Counts/0.10 #muA')
	#print ec,layer, 'chan', hist.GetMean(), hist.GetStdDev()
	text = '#splitline{Mean : %5.3f}{Std. Dev. : %5.3f}'%(hist.GetMean(),hist.GetStdDev())
	canv.drawText(text,align='tl',pos=(0.6,0.7))
	canv.finishCanvas('BOB')
	canv.save('plots/histIndvSlope_ME%s_L%s.pdf'%(ec,str(layer)))
	canv.deleteCanvas()

def makeSumSlope_ec(hist,ec):
	plot = Plotter.Plot(hist,option='le')
	title = 'Summed Currents on ME'+('+' if ec=='P' else '-')+'1/1 at L=10^{34}/cm^{2}/s'
	canv = Plotter.Canvas(lumi=title)
	canv.addMainPlot(plot)
	plot.setTitles(X='Summed Currents [#muA]',Y='Counts/0.10 #muA')
	#print ec, 'sum', hist.GetMean(), hist.GetStdDev()
	text = '#splitline{Mean : %5.3f}{Std. Dev. : %5.3f}'%(hist.GetMean(),hist.GetStdDev())
	canv.drawText(text,align='tl',pos=(0.6,0.7))
	canv.finishCanvas('BOB')
	canv.save('plots/histSumSlope_ME%s.pdf'%(ec))
	canv.deleteCanvas()

def makeSumSlope_ec_ch(hist,ec,cham):
	plot = Plotter.Plot(hist,option='le')
	title = 'Summed Currents on ME'+('+' if ec=='P' else '-')+'1/1/'+str(cham)+' at L=10^{34}/cm^{2}/s'
	canv = Plotter.Canvas(lumi=title)
	canv.addMainPlot(plot)
	plot.setTitles(X='Summed Currents [#muA]',Y='Counts/0.10 #muA')
	#print ec,cham, 'sum', hist.GetMean(), hist.GetStdDev()
	text = '#splitline{Mean : %5.3f}{Std. Dev. : %5.3f}'%(hist.GetMean(),hist.GetStdDev())
	canv.drawText(text,align='tl',pos=(0.6,0.7))
	canv.finishCanvas('BOB')
	canv.save('plots/histSumSlope_ME%s_ch%s.pdf'%(ec,str(cham)))
	canv.deleteCanvas()

for ec in ['P','N']:
	# Set hist2
	histIndvSlope_ec = R.TH1D('histIndvSlope_ME%s'%(ec),'',50,0,5) # bin width 0.10 uA
	for cham in range(1,37):
		# set hist4
		histIndvSlope_ec_ch = R.TH1D('histIndvSlope_ME%s_ch%s'%(ec,str(cham)),'',50,0,5) # bin width 0.10 uA
		for layer in range(1,7):
			for fill in fillList:
				if 'slope' not in conv[fill][ec][cham][layer].keys(): continue
				# fill hist2
				histIndvSlope_ec.Fill(conv[fill][ec][cham][layer]['slope'])
				# fill hist4
				histIndvSlope_ec_ch.Fill(conv[fill][ec][cham][layer]['slope'])
		# plot hist4
		makeIndvSlope_ec_ch(histIndvSlope_ec_ch,ec,cham)
	for layer in range(1,7):
		# set hist6
		histIndvSlope_ec_l = R.TH1D('histIndvSlope_ME%s_L%s'%(ec,str(layer)),'',50,0,5) # bin width 0.10 uA
		for cham in range(1,37):
			for fill in fillList:
				if 'slope' not in conv[fill][ec][cham][layer].keys(): continue
				# fill hist6
				histIndvSlope_ec_l.Fill(conv[fill][ec][cham][layer]['slope'])
		# plot hist6
		makeIndvSlope_ec_l(histIndvSlope_ec_l,ec,layer)
	# plot hist2
	makeIndvSlope_ec(histIndvSlope_ec,ec)
	# set hist8
	histSumSlope_ec = R.TH1D('histSumSlope_ME%s'%(ec),'',80,0,20) # bin width 0.25 uA
	for cham in range(1,37):
		# set hist10
		histSumSlope_ec_ch = R.TH1D('histSumSlope_ME%s_ch%s'%(ec,str(cham)),'',80,0,20) # bin width 0.25 uA
		for fill in fillList:
			sumSlope = 0.
			for layer in range(1,7):
				if 'slope' not in conv[fill][ec][cham][layer].keys(): continue
				sumSlope += conv[fill][ec][cham][layer]['slope']
			# fill hist8
			histSumSlope_ec.Fill(sumSlope)
			# fill hist10
			histSumSlope_ec_ch.Fill(sumSlope)
		# plot hist10
		makeSumSlope_ec_ch(histSumSlope_ec_ch,ec,cham)
	# plot hist8
	makeSumSlope_ec(histSumSlope_ec,ec)

# 


# Histogram chamber currents (sum over channels)

# Calculate weighted sum of slopes for +/- separately and combine

