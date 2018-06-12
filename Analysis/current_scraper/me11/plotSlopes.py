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
from helper11 import fills,make_conv,setup_logger
from handScanList import handScanList

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-o','--offset',dest='OFFSET',action='store_true',default=False,help='if -o then IvsL fits have offset')
parser.add_argument('-lumi','--lumi',dest='LUMI',action='store_true',default=False,help='Use fits that only use higher lumi IvsL points')
args = parser.parse_args()
OFFSET = args.OFFSET
LUMI = args.LUMI
conv = make_conv(OFFSET, LUMI,test=True)

R.gROOT.SetBatch(True)
R.gStyle.SetLineWidth(1)

save = 'test_tmp/'+('no_' if not OFFSET else '')+'offset_'+('high' if LUMI else 'all')+'_lumi/'
outputFile = R.TFile(save+'output_all.root','recreate')

color = {1:R.kBlue,2:R.kCyan+2,3:R.kGreen+1,4:R.kOrange+1,5:R.kRed,6:R.kViolet}
fillList = fills.keys()
#fillList = [5338,5450,5451,5394,5418]#5443,,5433,5416,5406,5405,5401,5395]
fillList.sort()

logNames = ['fill_slope','fill_offset','fill_current']
logDict = {logName:{} for logName in logNames}
for logName in logNames:
	setup_logger(logName,'test_tmp/logs/'+logName+'.log')
	logDict[logName] = logging.getLogger(logName)

lims = {
		'slope':{
			'bins':100,
			'min':0,
			'max':5,
			'leg':'tr',
			'label':'Current',
			'units':'[#muA]',
			},
		'curr':{
			'bins':100,
			'min':0,
			'max':5,
			'leg':'tr',
			'label':'Current',
			'units':'[#muA]',
			},
		'offset':{
			'bins':100,
			'min':-2.,
			'max':2.,
			'leg':'bl',
			'label':'Offset',
			'units':'[#muA]',
			},
		'chi2':{
			'bins':100,
			'min':0.,
			'max':10000.,
			'leg':'tr',
			'label':'#chi^{2}',
			'units':False,
			},
		'ndf':{
			'bins':1000,
			'min':0.,
			'max':1000.,
			'leg':'tr',
			'label':'ndf',
			'units':False,
			},
		'chi2ndf':{
			'bins':100,
			'min':0.,
			'max':100.,
			'leg':'tr',
			'label':'#chi^{2}/ndf',
			'units':False,
			},
		'P':{
			'bins':100,
			'min':0.,
			'max':1.,
			'leg':'tr',
			'label':'P',
			'units':False,
			},
		'logP':{
			'bins':100,
			'min':-100.,
			'max':1.,
			'leg':'bl',
			'label':'log_{10}(P)',
			'units':False,
			},

		'logP_ndf':{
			'xbins':1000,'xmax':1000.,'xmin':0.,# ndf
			'ybins':100,'ymax':1.,'ymin':-100.,# logP
			},
		'chi2ndf_ndf':{
			'xbins':1000,'xmax':1000.,'xmin':0.,# ndf
			'ybins':100,'ymax':100.,'ymin':0.,# logP
			},
		'offset_slope':{
			'xbins':100,'xmax':5.,'xmin':0.,# slope
			'ybins':100,'ymax':2.,'ymin':-2,# offset
			},

		'all':{
			'label':'',
			},
		'ndf40':{
			'label':' for ndf<40',
			},
		'cuts':{
			'label':' with cuts',
			},
		'a':{
			'label':' hand selected',
			},
		'n':{
			'label':' not selected',
			},
		'a_sel':{
			'label':' hand selected, small offset',
			},
		}

def make_plot_vs_fill(plots,ptype,plot,ec,cham):
	'''
	Makes plots of any value vs. fill number for a particular chamber
	'''
	title = 'ME'+('+' if ec=='P' else '-')+'1/1/'+str(cham)+' '+lims[plot]['label']+lims[ptype]['label']+' vs Fill'
	canv = Plotter.Canvas(lumi=title)
	plotExist=False
	for layer in range(1,7):
		if not plots[layer]: continue
		canv.addMainPlot(plots[layer])
		plotExist=True
	if not plotExist: return
	for layer in range(1,7):
		if not plots[layer]: continue
		plots[layer].SetMarkerColor(color[layer])
	# re-label bins
	for b in range(len(fillList)):
		ibin = canv.firstPlot.GetXaxis().FindBin(b)
		canv.firstPlot.GetXaxis().SetBinLabel(ibin,str(fillList[b]))
	x = 'Fill Number'
	y = lims[plot]['label']+(' '+lims[plot]['units'] if lims[plot]['units'] else '')
	canv.firstPlot.setTitles(X=x,Y=y)
	canv.firstPlot.SetMinimum(lims[plot]['min'])
	canv.firstPlot.SetMaximum(lims[plot]['max'])
	canv.makeLegend(pos=lims[plot]['leg'])
	canv.makeTransparent()
	canv.finishCanvas('BOB')
	name = 'me11_'+ec+str(cham)+'_'+ptype+'_'+plot+'_vs_fill'
	canv.save(save+name+'.pdf')
	outputFile.cd()
	canv.Write(name)
	canv.deleteCanvas()

print 'Starting plots as a function of fill'

# Which plots to make
plotList = {
#		'all':[
#			'logP','P','chi2','ndf','chi2ndf',
#			'slope'] + (['offset','curr'] if OFFSET else []),
#		'ndf40':[
#			'logP','chi2','ndf','chi2ndf','P',
#			'slope'] + (['offset','curr'] if OFFSET else []),
#		'cuts':[
#			'logP','chi2','ndf','chi2ndf','P',
#			'slope'] + (['offset','curr'] if OFFSET else []),
#		'a':[
#			'logP','chi2','ndf','chi2ndf','P',
#			'slope'] + (['offset','curr'] if OFFSET else []),
#		'n':[
#			'logP','chi2','ndf','chi2ndf','P',
#			'slope'] + (['offset','curr'] if OFFSET else []),
		'a_sel':[
			'logP','chi2','ndf','chi2ndf','P',
			'slope'] + (['offset','curr'] if OFFSET else []),
		}

plot2dList = ['logP_ndf','chi2ndf_ndf']+(['offset_slope'] if OFFSET else [])

# plots as a function of fill

for ec in ['P','N']:
	for cham in range(1,37):
		graphs = {ptype:{plot:{lay:{} for lay in range(1,7)} for plot in plotList[ptype]} for ptype in plotList.keys()}
		plots = {ptype:{plot:{lay:{} for lay in range(1,7)} for plot in plotList[ptype]} for ptype in plotList.keys()}
		x = {ptype:{layer:np.array([]) for layer in range(1,7)} for ptype in plotList.keys()}
		for layer in range(1,7):
			y = {ptype:{plot:np.array([]) for plot in plotList[ptype]} for ptype in plotList.keys()}
			for f,fill in enumerate(fillList):
				if 'slope' not in conv[fill][ec][cham][layer].keys(): continue

				# Slope, Offset, Current
				slope = conv[fill][ec][cham][layer]['slope']
				if OFFSET:
					offset = conv[fill][ec][cham][layer]['offset']
					curr = slope - offset
				chi2 = conv[fill][ec][cham][layer]['chi2']
				ndf = conv[fill][ec][cham][layer]['ndf']
				P = R.TMath.Prob(chi2,int(ndf))
				logP = R.TMath.Log10(P)
				if logP==-float('inf'): logP = 0.99

				#chan = 'CSC_ME_{ec}11_C{cham:02}_{layer}_f{fill}'.format(**locals())
				chan = 'CSC_ME_{ec}11_C{cham:02}_{layer}_f5394'.format(**locals())
				good = True if 'a' in handScanList[chan] else False

				cuts = {
						'all':True,
						'ndf40':ndf>40,
						'cuts':(ndf > 6 and ndf < 25 and logP > -10. and logP < 0.),
						'a':good==True,
						'n':good!=True,
						'a_sel':(good==True and abs(offset)<0.10),
						}

				for ptype in plotList.keys():
					if cuts[ptype]:
						x[ptype][layer] = np.append(x[ptype][layer],f)
						y[ptype]['slope'] = np.append(y[ptype]['slope'],slope)
						if OFFSET:
							y[ptype]['offset'] = np.append(y[ptype]['offset'],offset)
							y[ptype]['curr'] = np.append(y[ptype]['curr'],curr)
						y[ptype]['chi2'] = np.append(y[ptype]['chi2'],chi2)
						y[ptype]['ndf'] = np.append(y[ptype]['ndf'],ndf)
						y[ptype]['chi2ndf'] = np.append(y[ptype]['chi2ndf'],float(chi2)/ndf)
						y[ptype]['P'] = np.append(y[ptype]['P'],P)
						y[ptype]['logP'] = np.append(y[ptype]['logP'],logP)


			# Make graphs/plots plots of curr/slope/offset vs fill
			for ptype in plotList.keys():
				for plot in plotList[ptype]:
					if len(x[ptype][layer])<1: continue
					#if len(y[ptype][plot])<1: continue
					#print ptype,plot, x[ptype][layer], y[ptype][plot]
					graphs[ptype][plot][layer] = R.TGraph(len(x[ptype][layer]),x[ptype][layer],y[ptype][plot])
					plots[ptype][plot][layer] = Plotter.Plot(graphs[ptype][plot][layer],option='p',legType='p',legName='Layer '+str(layer))
		# Draw/save plots of curr/slope/offset vs fill
		for ptype in plotList.keys():
			for plot in plotList[ptype]:
				make_plot_vs_fill(plots[ptype][plot],ptype,plot,ec,cham)

		# Summed plots go here but summed plots are kind of useless...

print 'Finished plots as a function of fill'

def make_plot_vs_cham(plots,ptype,plot,fill):
	'''
	Makes plots of any value vs chamber number for a particular fill
	'''
	title = 'ME1/1 '+lims[plot]['label']+lims[ptype]['label']+' Fill '+str(fill)
	canv = Plotter.Canvas(lumi=title)
	if len(plots)<1: return
	for layer in plots.keys():
		try:
			canv.addMainPlot(plots[layer])
		except:
			continue
	for layer in plots.keys():
		try:
			plots[layer].SetMarkerColor(color[layer])
		except:
			continue
	x = 'Chamber Number'
	y = lims[plot]['label']+(' '+lims[plot]['units'] if lims[plot]['units'] else '')
	canv.firstPlot.setTitles(X=x,Y=y)
	canv.firstPlot.GetXaxis().SetLimits(-37,37)
	canv.firstPlot.SetMinimum(lims[plot]['min'])
	canv.firstPlot.SetMaximum(lims[plot]['max'])
	canv.makeLegend(pos='bl')
	canv.makeTransparent()
	canv.finishCanvas('BOB')
	name = 'me11_fill_{fill}_{ptype}_{plot}'.format(**locals())
	canv.save(save+name+'.pdf')
	outputFile.cd()
	canv.Write(name)
	canv.deleteCanvas()

def make_plot_hist(plots,ptype,plot,fill):
	'''
	Makes histogram of any value for all chambers for a particular fill
	(separates by endcap)
	'''
	title = 'ME1/1 '+lims[plot]['label']+lims[ptype]['label']+' Fill '+str(fill)
	canv = Plotter.Canvas(lumi=title)
	canv.addMainPlot(plots['N'])
	canv.addMainPlot(plots['P'])
	plots['P'].SetLineColor(R.kBlue)
	plots['N'].SetLineColor(R.kOrange+1)
	x = lims[plot]['label']+(' '+lims[plot]['units'] if lims[plot]['units'] else '')
	y = 'Counts'
	canv.firstPlot.setTitles(X=x,Y=y)
	canv.firstPlot.SetMinimum(0.)
	if plot in ['slope','offset','curr']:
		plusMean, plusRMS = plots['P'].GetMean(), plots['P'].GetStdDev()
		minusMean, minusRMS = plots['N'].GetMean(), plots['N'].GetStdDev()
		plustxt = '#color[600]{plus mean = %5.3f, rms = %5.3f}'%(plusMean,plusRMS) # 600 = R.kBlue
		minustxt = '#color[801]{minus mean = %5.3f, rms = %5.3f}'%(minusMean,minusRMS) # 801 = R.kOrange+1
		text = '#splitline{%s}{%s}'%(plustxt,minustxt)
		canv.drawText(text, pos = (0.9,0.8), align='tr')
		log = '{fill:4} {plusMean:6.4f} {plusRMS:6.4f} {minusMean:6.4f} {minusRMS:6.4f}'.format(**locals())
		for logName in logNames:
			if plot in logName:
				logDict[logName].info(log)
	else:
		canv.makeLegend(pos='tl')
	canv.makeTransparent()
	canv.finishCanvas('BOB')
	name = 'me11_fill_{fill}_{ptype}_{plot}_hist'.format(**locals())
	canv.save(save+name+'.pdf')
	outputFile.cd()
	canv.Write(name)
	canv.deleteCanvas()
	
def make_plot_hist2d(plot,plotname,fill,ec):
	'''
	Makes 2D histogram of any 2 values for all chambers for a particular fill
	(separates by endcap)
	'''
	names = plotname.split('_')
	x = names[1]
	y = names[0]
	xlabel = lims[x]['label']+(' '+lims[x]['units'] if lims[x]['units'] else '')
	ylabel = lims[y]['label']+(' '+lims[y]['units'] if lims[y]['units'] else '')
	ecname = '+' if ec=='P' else '-'
	title = 'ME{ecname}1/1 {ylabel} vs {xlabel} Fill {fill}'.format(**locals())
	#title = 'ME'+('+' if ec=='P' else '-')+'1/1 '+ylabel+' vs '+xlabel+' Fill '+str(fill)
	canv = Plotter.Canvas(lumi=title)
	canv.addMainPlot(plot)
	canv.firstPlot.setTitles(X=xlabel,Y=ylabel)
	canv.makeTransparent()
	canv.finishCanvas('BOB')
	name = 'me11_fill_{fill}_{ec}_{y}_vs_{x}_hist'.format(**locals())
	canv.save(save+name+'.pdf')
	outputFile.cd()
	canv.Write(name)
	canv.deleteCanvas()


print 'Starting plots for each fill'

for fill in fillList:
	hists = {ptype:{plot:{ec:R.TH1D('h_'+plot+'_'+ptype+'_ME'+ec+'_fill_'+str(fill),'',
		lims[plot]['bins'],lims[plot]['min'],lims[plot]['max']) for ec in ['P','N']} for plot in plotList[ptype]} for ptype in plotList.keys()}
	hists2d = {plot2d:{ec:R.TH2D('h_'+plot2d+'_ME'+ec+'_fill_'+str(fill),'',
		lims[plot2d]['xbins'],lims[plot2d]['xmin'],lims[plot2d]['xmax'],
		lims[plot2d]['ybins'],lims[plot2d]['ymin'],lims[plot2d]['ymax']) for ec in ['P','N']} for plot2d in plot2dList}

	plotHists = {ptype:{plot:{ec:{} for ec in ['P','N']} for plot in plotList[ptype]} for ptype in plotList.keys()}
	plotHists2d = {plot2d:{ec:{} for ec in ['P','N']} for plot2d in plot2dList}

	graphs = {ptype:{plot:{layer:{} for layer in range(1,7)} for plot in plotList[ptype]} for ptype in plotList.keys()}
	plots  = {ptype:{plot:{layer:{} for layer in range(1,7)} for plot in plotList[ptype]} for ptype in plotList.keys()}
	x = {ptype:{layer:np.array([]) for layer in range(1,7)} for ptype in plotList.keys()}
	y = {ptype:{plot:{layer:np.array([]) for layer in range(1,7)} for plot in plotList[ptype]} for ptype in plotList.keys()}
	for layer in range(1,7):
		for ec in ['P','N']:
			for cham in range(1,37):
				if 'slope' not in conv[fill][ec][cham][layer].keys(): continue
				
				slope = conv[fill][ec][cham][layer]['slope']
				if OFFSET:
					offset = conv[fill][ec][cham][layer]['offset']
					curr = slope-offset
				chi2 = conv[fill][ec][cham][layer]['chi2']
				ndf = conv[fill][ec][cham][layer]['ndf']
				P = R.TMath.Prob(chi2,int(ndf))
				logP = R.TMath.Log10(P)
				if logP==-float('inf'): logP = 0.99

				#chan = 'CSC_ME_{ec}11_C{cham:02}_{layer}_f{fill}'.format(**locals()) # only fill 5394 was hand scanned
				chan = 'CSC_ME_{ec}11_C{cham:02}_{layer}_f5394'.format(**locals())
				good = True if 'a' in handScanList[chan] else False

				cuts = {
						'all':True,
						'ndf40':ndf>40,
						'cuts':(ndf > 6 and ndf < 25 and logP > -10. and logP < 0.),
						'a':good==True,
						'n':good!=True,
						'a_sel':(good==True and abs(offset)<0.10),
						}

				for ptype in plotList.keys():
					if cuts[ptype]: 
						x[ptype][layer] = np.append(x[ptype][layer],cham*1. if ec=='P' else cham*-1.)

						y[ptype]['slope'][layer] = np.append(y[ptype]['slope'][layer],slope)
						if OFFSET:
							y[ptype]['offset'][layer] = np.append(y[ptype]['offset'][layer],offset)
							y[ptype]['curr'][layer] = np.append(y[ptype]['curr'][layer],curr)
						y[ptype]['chi2'][layer] = np.append(y[ptype]['chi2'][layer],chi2)
						y[ptype]['ndf'][layer] = np.append(y[ptype]['ndf'][layer],ndf)
						y[ptype]['chi2ndf'][layer] = np.append(y[ptype]['chi2ndf'][layer],float(chi2)/ndf)
						y[ptype]['P'][layer] = np.append(y[ptype]['P'][layer],P)
						y[ptype]['logP'][layer] = np.append(y[ptype]['logP'][layer],logP)

						hists[ptype]['slope'][ec].Fill(slope)
						if OFFSET:
							hists[ptype]['offset'][ec].Fill(offset)
							hists[ptype]['curr'][ec].Fill(curr)
						hists[ptype]['chi2'][ec].Fill(chi2)
						hists[ptype]['ndf'][ec].Fill(ndf)
						hists[ptype]['chi2ndf'][ec].Fill(float(chi2)/ndf)
						hists[ptype]['P'][ec].Fill(P)
						hists[ptype]['logP'][ec].Fill(logP)

				hists2d['logP_ndf'][ec].Fill(ndf,logP)
				hists2d['chi2ndf_ndf'][ec].Fill(ndf,float(chi2)/ndf)
				if OFFSET:
					hists2d['offset_slope'][ec].Fill(slope,offset)


		# Make graphs/plots of curr/slope/offset vs cham
		for ptype in plotList.keys():
			if len(x[ptype][layer])<1: continue
			for plot in plotList[ptype]:
				#if len(y[ptype][plot][layer])<1:continue
				graphs[ptype][plot][layer] = R.TGraph(len(x[ptype][layer]),x[ptype][layer],y[ptype][plot][layer])
				plots[ptype][plot][layer] = Plotter.Plot(graphs[ptype][plot][layer],option='p',legType='p',legName='Layer '+str(layer))
	# Draw plots of curr/slope/offset vs cham
	for ptype in plotList.keys():
		for plot in plotList[ptype]:
			# make plots vs cham
			make_plot_vs_cham(plots[ptype][plot],ptype,plot,fill)
			# Make hists
			for ec in ['P','N']:
				plotHists[ptype][plot][ec] = Plotter.Plot(hists[ptype][plot][ec],option='hist',legType='l',legName='Plus' if ec=='P' else 'Minus')
			make_plot_hist(plotHists[ptype][plot],ptype,plot,fill)
	for plot2d in plot2dList:
		for ec in ['P','N']:
			plotHists2d[plot2d][ec] = Plotter.Plot(hists2d[plot2d][ec],option='colz')
			make_plot_hist2d(plotHists2d[plot2d][ec],plot2d,fill,ec)

print 'Finished plots for each fill'
