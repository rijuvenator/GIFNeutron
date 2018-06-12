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
parser.add_argument('-o','--offset',dest='OFFSET',action='store_true',default=False,help='Use fits with offset')
parser.add_argument('-lumi','--lumi',dest='LUMI',action='store_true',default=False,help='Use high lumi fits')
args = parser.parse_args()
OFFSET = args.OFFSET
LUMI = args.LUMI

R.gROOT.SetBatch(True)
R.gStyle.SetLineWidth(1)

conv = make_conv(OFFSET,LUMI)
save = 'test/'+('no_' if not OFFSET else '')+'offset_'+('high' if LUMI else 'all')+'_lumi/'

names = ['slope','offset','val']
ptypes = ['all']#,'sel']
logNames = ['fill_'+ptype+'_'+name for ptype in ptypes for name in names]
logDict = {logName:{} for logName in logNames}
for logName in logNames:
	setup_logger(logName,'logs/'+logName+'.log')
	logDict[logName] = logging.getLogger(logName)

outputFile = R.TFile(save+'output_all.root','recreate')

plotList = {
		'all':[
			'HV',
			'logP','P','chi2','ndf','chi2ndf',
			'slope'] + (['offset','val'] if OFFSET else []),
		#'sel':[
		#	'logP','P','chi2','ndf','chi2ndf',
		#	'slope'] + (['offset','val'] if OFFSET else []),
		}


plot2dList = ['logP_ndf','chi2ndf_ndf']+(['offset_slope'] if OFFSET else [])

lims = {
		'HV':{
			'bins':200,
			1:{
				'min':3500,
				'max':3700,
				},
			2:{
				'min':3500,
				'max':3700,
				},
			3:{
				'min':3500,
				'max':3700,
				},
			'leg':'tr',
			'label':'High Voltage',
			'units':'[V]',
			},
		'slope':{
			'bins':100,
			1:{
				'min':0,
				'max':5,
				},
			2:{
				'min':0,
				'max':3,
				},
			3:{
				'min':0,
				'max':1,
				},
			'leg':'tr',
			'label':'Slope',
			'units':'[#muA/10^{34} cm^{-2}s^{-1}]',
			},
		'val':{
			'bins':100,
			1:{
				'min':0,
				'max':4,
				},
			2:{
				'min':0,
				'max':2,
				},
			3:{
				'min':0,
				'max':0.8,
				},
			'leg':'tr',
			'label':'Current',
			'units':'[#muA]',
			},
		'offset':{
			'bins':100,
			1:{
				'min':-2.,
				'max':2.,
				},
			2:{
				'min':-2.,
				'max':2.,
				},
			3:{
				'min':-2.,
				'max':2.,
				},
			'leg':'tr',
			'label':'Offset',
			'units':'[#muA]',
			},
		'chi2':{
			'bins':100,
			1:{
				'min':0.,
				'max':10000000.,
				},
			2:{
				'min':0.,
				'max':1000000.,
				},
			3:{
				'min':0.,
				'max':1000000.,
				},
			'leg':'tr',
			'label':'#chi^{2}',
			'units':False,
			},
		'ndf':{
			'bins':1000,
			1:{
				'min':0.,
				'max':1000.,
				},
			2:{
				'min':0.,
				'max':1000.,
				},
			3:{
				'min':0.,
				'max':1000.,
				},
			'leg':'tr',
			'label':'ndf',
			'units':False,
			},
		'chi2ndf':{
			'bins':100,
			1:{
				'min':0.,
				'max':100000.,
				},
			2:{
				'min':0.,
				'max':100000.,
				},
			3:{
				'min':0.,
				'max':100000.,
				},
			'leg':'tr',
			'label':'#chi^{2}/ndf',
			'units':False,
			},
		'P':{
			'bins':100,
			1:{
				'min':0.,
				'max':1.,
				},
			2:{
				'min':0.,
				'max':1.,
				},
			3:{
				'min':0.,
				'max':1.,
				},
			'leg':'tr',
			'label':'P',
			'units':False,
			},
		'logP':{
			'bins':100,
			1:{
				'min':-100.,
				'max':1.,
				},
			2:{
				'min':-100.,
				'max':1.,
				},
			3:{
				'min':-100.,
				'max':1.,
				},
			'leg':'bl',
			'label':'log_{10}(P)',
			'units':False,
			},

		'logP_ndf':{
			1:{
				'xbins':1000,'xmax':1000.,'xmin':0.,# ndf
				'ybins':100,'ymax':1.,'ymin':-100.,# logP
				},
			2:{
				'xbins':1000,'xmax':1000.,'xmin':0.,# ndf
				'ybins':100,'ymax':1.,'ymin':-100.,# logP
				},
			3:{
				'xbins':1000,'xmax':1000.,'xmin':0.,# ndf
				'ybins':100,'ymax':1.,'ymin':-100.,# logP
				},
			},
		'chi2ndf_ndf':{
			1:{
				'xbins':1000,'xmax':1000000.,'xmin':0.,# ndf
				'ybins':100,'ymax':100.,'ymin':0.,# logP
				},
			2:{
				'xbins':1000,'xmax':100000.,'xmin':0.,# ndf
				'ybins':100,'ymax':100.,'ymin':0.,# logP
				},
			3:{
				'xbins':1000,'xmax':100000.,'xmin':0.,# ndf
				'ybins':100,'ymax':100.,'ymin':0.,# logP
				},
			},
		'offset_slope':{
			1:{
				'xbins':1000,'xmin':0.,'xmax':4.,# slope
				'ybins':100,'ymin':-1.,'ymax':1.,# offset
				},
			2:{
				'xbins':1000,'xmin':0.,'xmax':2.,# slope
				'ybins':100,'ymin':-1.,'ymax':1.,# offset
				},
			3:{
				'xbins':1000,'xmin':0.,'xmax':1.,# slope
				'ybins':100,'ymin':-1.,'ymax':1.,# offset
				},
			},

		#'sel':{
		#	' with |offset|<0.1 #muA':'',
		#	},
		'all':{
			'label':'',
			},
		}


color = {1:R.kBlue,2:R.kCyan+2,3:R.kGreen+1,4:R.kOrange+1,5:R.kRed,6:R.kViolet}
style = {1:R.kFullCircle,2:R.kFullSquare,3:R.kFullTriangleUp}
fillList = fills.keys()
fillList.sort()

def make_plot_vs_fill(plots,ptype,plot,ec,cham,seg):
	title = 'ME'+('+' if ec=='P' else '-')+'2/1/'+str(cham)+' Segment '+str(seg)+' '+lims[plot]['label']+lims[ptype]['label']+' vs Fill'
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
	canv.firstPlot.SetMinimum(lims[plot][seg]['min'])
	canv.firstPlot.SetMaximum(lims[plot][seg]['max'])
	canv.makeLegend(pos=lims[plot]['leg'])
	canv.makeTransparent()
	canv.finishCanvas('BOB')
	name = 'me21_{ec}{cham}_S{seg}_{ptype}_{plot}_vs_fill'.format(**locals())
	canv.save(save+name+'.pdf')
	outputFile.cd()
	canv.Write(name)
	canv.deleteCanvas()

# plots as a function of fill
for ec in ['P','M']:
	for cham in range(1,19):
		graphs = {ptype:{plot:{seg:{lay:{} for lay in range(1,7)} for seg in range(1,4)} for plot in plotList[ptype]} for ptype in plotList.keys()}
		plots  = {ptype:{plot:{seg:{lay:{} for lay in range(1,7)} for seg in range(1,4)} for plot in plotList[ptype]} for ptype in plotList.keys()}
		for segment in range(1,4):
			x = {ptype:{lay:np.array([]) for lay in range(1,7)} for ptype in plotList.keys()}
			for layer in range(1,7):
				y = {ptype:{plot:np.array([]) for plot in plotList[ptype]} for ptype in plotList.keys()}
				#xerr = np.array([])
				#yerr = np.array([])
				for f,fill in enumerate(fillList):
					# skip bad channels
					if 'slope' not in conv[fill][ec][cham][segment][layer].keys():
						continue

					HV = conv[fill][ec][cham][segment][layer]['HV']
					slope = conv[fill][ec][cham][segment][layer]['slope']
					if OFFSET:
						offset = conv[fill][ec][cham][segment][layer]['offset']
						val = slope + offset
					chi2 = conv[fill][ec][cham][segment][layer]['chi2']
					ndf = conv[fill][ec][cham][segment][layer]['ndf']
					P = R.TMath.Prob(chi2,int(ndf))
					logP = R.TMath.Log10(P)
					if logP==-float('inf'): logP = 0.99

					cuts = {
							'all':True,
							#'sel':abs(offset)<0.10,
							}

					for ptype in plotList.keys():
						if cuts[ptype]:
							x[ptype][layer] = np.append(x[ptype][layer],f)
							y[ptype]['HV'] = np.append(y[ptype]['HV'],HV)
							y[ptype]['slope'] = np.append(y[ptype]['slope'],slope)
							if OFFSET:
								y[ptype]['offset'] = np.append(y[ptype]['offset'],offset)
								y[ptype]['val'] = np.append(y[ptype]['val'],val)
							y[ptype]['chi2'] = np.append(y[ptype]['chi2'],chi2)
							y[ptype]['ndf'] = np.append(y[ptype]['ndf'],ndf)
							y[ptype]['chi2ndf'] = np.append(y[ptype]['chi2ndf'],float(chi2)/ndf)
							y[ptype]['P'] = np.append(y[ptype]['P'],P)
							y[ptype]['logP'] = np.append(y[ptype]['logP'],logP)

				for ptype in plotList.keys():
					for plot in plotList[ptype]:
						if len(x[ptype][layer])<1: continue
						graphs[ptype][plot][segment][layer] = R.TGraph(len(x[ptype][layer]),x[ptype][layer],y[ptype][plot])
						plots[ptype][plot][segment][layer] = Plotter.Plot(graphs[ptype][plot][segment][layer],option='p',legType='p',legName='Layer '+str(layer))
			for ptype in plotList.keys():
				for plot in plotList[ptype]:
					make_plot_vs_fill(plots[ptype][plot][segment],ptype,plot,ec,cham,segment)


def make_plot_vs_cham(plots,ptype,plot,fill,seg):
	title = 'ME2/1 Segment '+str(seg)+' '+lims[plot]['label']+lims[ptype]['label']+' Fill '+str(fill)
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
	canv.firstPlot.GetXaxis().SetLimits(-19.,19.)
	x = 'Chamber Number'
	y = lims[plot]['label']+(' '+lims[plot]['units'] if lims[plot]['units'] else '')
	canv.firstPlot.setTitles(X=x,Y=y)
	canv.firstPlot.SetMinimum(lims[plot][seg]['min'])
	canv.firstPlot.SetMaximum(lims[plot][seg]['max'])
	canv.makeLegend(pos='bl')
	canv.makeTransparent()
	canv.finishCanvas('BOB')
	name = 'me21_fill_{fill}_seg_{seg}_{ptype}_{plot}'.format(**locals())
	canv.save(save+name+'.pdf')
	outputFile.cd()
	canv.Write(name)
	canv.deleteCanvas()

def make_plot_hist(plots,ptype,plot,fill,seg):
	title = 'ME2/1 Segment '+str(seg)+' '+lims[plot]['label']+lims[ptype]['label']+' Fill '+str(fill)
	canv = Plotter.Canvas(lumi=title)
	canv.addMainPlot(plots['M'])
	canv.addMainPlot(plots['P'])
	plots['P'].SetLineColor(R.kBlue)
	plots['M'].SetLineColor(R.kOrange+1)
	x = lims[plot]['label']+(' '+lims[plot]['units'] if lims[plot]['units'] else '')
	y = 'Counts'
	canv.firstPlot.setTitles(X=x,Y=y)
	canv.firstPlot.SetMinimum(0.)
	if plot in ['slope','offset','val']:
		plusMean, plusRMS = plots['P'].GetMean(), plots['P'].GetStdDev()
		minusMean, minusRMS = plots['M'].GetMean(), plots['M'].GetStdDev()
		plustxt = '#color[600]{plus mean = %5.3f, rms = %5.3f}'%(plusMean,plusRMS) # 600 = R.kBlue
		minustxt = '#color[801]{minus mean = %5.3f, rms = %5.3f}'%(minusMean,minusRMS) # 801 = R.kOrange+1
		text = '#splitline{%s}{%s}'%(plustxt,minustxt)
		canv.drawText(text, pos = (0.9,0.8), align='tr')
		log = '{fill:4} {seg:1} {plusMean:6.4f} {plusRMS:6.4f} {minusMean:6.4f} {minusRMS:6.4f}'.format(**locals())
		for logName in logNames:
			if (plot in logName) and (ptype in logName):
				logDict[logName].info(log)
	else:
		canv.makeLegend(pos='tl')
	canv.makeTransparent()
	canv.finishCanvas('BOB')
	name = 'me21_fill_{fill}_seg_{seg}_{ptype}_{plot}_hist'.format(**locals())
	canv.save(save+name+'.pdf')
	outputFile.cd()
	canv.Write(name)
	canv.deleteCanvas()
	
def make_plot_hist2d(plot,plotname,fill,seg):
	names = plotname.split('_')
	x = names[1]
	y = names[0]
	xlabel = lims[x]['label']
	ylabel = lims[y]['label']
	xaxis = lims[x]['label']+(' '+lims[x]['units'] if lims[x]['units'] else '')
	yaxis = lims[y]['label']+(' '+lims[y]['units'] if lims[y]['units'] else '')
	title = 'ME2/1 Segment {seg} {ylabel} vs {xlabel} Fill {fill}'.format(**locals())
	canv = Plotter.Canvas(lumi=title)
	canv.addMainPlot(plot)
	canv.firstPlot.setTitles(X=xaxis,Y=yaxis)
	canv.makeTransparent()
	canv.finishCanvas('BOB')
	name = 'me21_fill_{fill}_seg_{seg}_{y}_vs_{x}_hist'.format(**locals())
	canv.save(save+name+'.pdf')
	outputFile.cd()
	canv.Write(name)
	canv.deleteCanvas()


for fill in fillList:
	x = {ptype:{seg:{lay:np.array([]) for lay in range(1,7)} for seg in range(1,4)} for ptype in plotList.keys()}
	y = {ptype:{plot:{seg:{lay:np.array([]) for lay in range(1,7)} for seg in range(1,4)} for plot in plotList[ptype]} for ptype in plotList.keys()}
	graphs = {ptype:{plot:{seg:{lay:{} for lay in range(1,7)} for seg in range(1,4)} for plot in plotList[ptype]} for ptype in plotList.keys()}
	plots = {ptype:{plot:{seg:{lay:{} for lay in range(1,7)} for seg in range(1,4)} for plot in plotList[ptype]} for ptype in plotList.keys()}
	hists = {ptype:{plot:{seg:{ec:
		R.TH1D('h_'+ec+'21_seg'+str(seg)+'_'+ptype+'_'+plot+'_'+str(fill),'',lims[plot]['bins'],lims[plot][seg]['min'],lims[plot][seg]['max'])
		for ec in ['P','M']} for seg in range(1,4)} for plot in plotList[ptype]} for ptype in plotList.keys()}
	plotHists = {ptype:{plot:{seg:{ec:{} for ec in ['P','M']} for seg in range(1,4)} for plot in plotList[ptype]} for ptype in plotList.keys()}
	hists2d = {plot2d:{seg:{ec:R.TH2D('h_'+plot2d+'_ME'+ec+'_seg_'+str(seg)+'_fill_'+str(fill),'',
										lims[plot2d][seg]['xbins'],lims[plot2d][seg]['xmin'],lims[plot2d][seg]['xmax'],
										lims[plot2d][seg]['ybins'],lims[plot2d][seg]['ymin'],lims[plot2d][seg]['ymax']) 
		for ec in ['P','M']} for seg in range(1,4)} for plot2d in plot2dList}
	plotHists2d = {plot2d:{seg:{ec:{} for ec in ['P','M']} for seg in range(1,4)} for plot2d in plot2dList}
	for seg in range(1,4):
		for layer in range(1,7):
			for ec in ['P','M']:
				for cham in range(1,19):
					if 'slope' not in conv[fill][ec][cham][seg][layer].keys(): continue

					HV = conv[fill][ec][cham][seg][layer]['HV']
					slope = conv[fill][ec][cham][seg][layer]['slope']
					if OFFSET:
						offset = conv[fill][ec][cham][seg][layer]['offset']
						val = slope+offset
					chi2 = conv[fill][ec][cham][seg][layer]['chi2']
					ndf = conv[fill][ec][cham][seg][layer]['ndf']
					P = R.TMath.Prob(chi2,int(ndf))
					logP = R.TMath.Log10(P)
					if logP==-float('inf'): logP = 0.99

					cuts = {
							'all':True,
							#'sel':abs(offset)<0.10,
							}

					for ptype in plotList.keys():
						if cuts[ptype]: 
							x[ptype][seg][layer] = np.append(x[ptype][seg][layer],cham*1. if ec=='P' else cham*-1.)

							y[ptype]['HV'][seg][layer]   = np.append(y[ptype]['HV'][seg][layer],HV)
							y[ptype]['slope'][seg][layer]   = np.append(y[ptype]['slope'][seg][layer],slope)
							if OFFSET:
								y[ptype]['offset'][seg][layer] = np.append(y[ptype]['offset'][seg][layer],offset)
								y[ptype]['val'][seg][layer]   = np.append(y[ptype]['val'][seg][layer],val)
							y[ptype]['chi2'][seg][layer]    = np.append(y[ptype]['chi2'][seg][layer],chi2)
							y[ptype]['ndf'][seg][layer]     = np.append(y[ptype]['ndf'][seg][layer],ndf)
							y[ptype]['chi2ndf'][seg][layer] = np.append(y[ptype]['chi2ndf'][seg][layer],float(chi2)/ndf)
							y[ptype]['P'][seg][layer]       = np.append(y[ptype]['P'][seg][layer],P)
							y[ptype]['logP'][seg][layer]    = np.append(y[ptype]['logP'][seg][layer],logP)

							hists[ptype]['HV'][seg][ec].Fill(HV)
							hists[ptype]['slope'][seg][ec].Fill(slope)
							if OFFSET:
								hists[ptype]['offset'][seg][ec].Fill(offset)
								hists[ptype]['val'][seg][ec].Fill(val)
							hists[ptype]['chi2'][seg][ec].Fill(chi2)
							hists[ptype]['ndf'][seg][ec].Fill(ndf)
							hists[ptype]['chi2ndf'][seg][ec].Fill(float(chi2)/ndf)
							hists[ptype]['P'][seg][ec].Fill(P)
							hists[ptype]['logP'][seg][ec].Fill(logP)

					hists2d['logP_ndf'][seg][ec].Fill(ndf,logP)
					hists2d['chi2ndf_ndf'][seg][ec].Fill(ndf,float(chi2)/ndf)
					if OFFSET:
						hists2d['offset_slope'][seg][ec].Fill(slope,offset)

			# Make 1d plots
			for ptype in plotList.keys():
				if len(x[ptype][seg][layer])<1: continue
				for plot in plotList[ptype]:
					graphs[ptype][plot][seg][layer] = R.TGraph(len(x[ptype][seg][layer]),x[ptype][seg][layer],y[ptype][plot][seg][layer])
					plots[ptype][plot][seg][layer] = Plotter.Plot(graphs[ptype][plot][seg][layer],option='p',legType='p',legName='Layer '+str(layer))
		# Draw 1D plots
		for ptype in plotList.keys():
			for plot in plotList[ptype]:
				make_plot_vs_cham(plots[ptype][plot][seg],ptype,plot,fill,seg)
				for ec in ['P','M']:
					plotHists[ptype][plot][seg][ec] = Plotter.Plot(hists[ptype][plot][seg][ec],option='hist',legType='l',legName='Plus' if ec=='P' else 'Minus')
				make_plot_hist(plotHists[ptype][plot][seg],ptype,plot,fill,seg)
		# Draw 2D plots
		for plot2d in plot2dList:
			for ec in ['P','M']:
				plotHists2d[plot2d][seg][ec] = Plotter.Plot(hists2d[plot2d][seg][ec],option='colz')
				make_plot_hist2d(plotHists2d[plot2d][seg][ec],plot2d,fill,seg)
