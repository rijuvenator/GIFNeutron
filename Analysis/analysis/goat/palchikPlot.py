import sys, os, argparse, math
#import numpy as np
import ROOT as R
#import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
#import Gif.Analysis.ChamberHandler as CH
#import Gif.Analysis.MegaStruct as MS
#import Gif.Analysis.BGDigi as BGDigi
#import logging,lumberjack
R.gROOT.SetBatch(True)
R.gStyle.SetOptFit(0)
# area histograms calculated on the fly
import areas as areas
areaHists = areas.areaHists

outputRoot = R.TFile('~/public/GIF/CSCBackgroundRate_UCLA.root','recreate')

lumi=10**34
fillfrac = 0.613705215349

ringlist = ['11','12','13','21','22','31','32','41','42']
whenlist = ['early','total']
stationlist = ['1','2','3','4']
howlist = ['area','counts']
nWG = {
		'11':48.,
		'12':64.,
		'13':32.,
		'21':112.,
		'31':96.,
		'41':96.,
		'22':64.,
		'32':64.,
		'42':64.,
		}
def lumi_weight(lumi,ring,when):
	# return weight for each ring to scale to given lumi
	rate = {
			'11':{
				'early':{
					'lumi':6.30045847e-36,
					'int':0.055660178,
					},
				'total':{
					'lumi':2.52572991e-35,
					'int':0.220812403,
					},
				},
			'12':{
				'early':{
					'lumi':3.21137770e-37,
					'int':0.003487345,
					},
				'total':{
					'lumi':7.57075984e-37,
					'int':0.006811074,
					},
				},
			'13':{
				'early':{
					'lumi':1.79040442e-37,
					'int':0.001586545,
					},
				'total':{
					'lumi':1.68617148e-37,
					'int':0.001750057,
					},
				},
			'21':{
				'early':{
					'lumi':9.87934634e-36,
					'int':0.087238800,
					},
				'total':{
					'lumi':1.92725035e-35,
					'int':0.168528998,
					},
				},
			'22':{
				'early':{
					'lumi':9.01695534e-37,
					'int':0.008826611,
					},
				'total':{
					'lumi':1.39573501e-36,
					'int':0.012364968,
					},
				},
			'31':{
				'early':{
					'lumi':5.66408170e-36,
					'int':0.050829182,
					},
				'total':{
					'lumi':1.20217410e-35,
					'int':0.105380685,
					},
				},
			'32':{
				'early':{
					'lumi':1.06254037e-36,
					'int':0.009578961,
					},
				'total':{
					'lumi':1.91051137e-36,
					'int':0.016935445,
					},
				},
			'41':{
				'early':{
					'lumi':4.37294677e-36,
					'int':0.039538830,
					},
				'total':{
					'lumi':1.55318201e-35,
					'int':0.136183733,
					},
				},
			'42':{
				'early':{
					'lumi':2.33653524e-36,
					'int':0.020857750,
					},
				'total':{
					'lumi':6.03756494e-36,
					'int':0.052915872,
					},
				},
			}
	#return (0.38*rate[ring]['early']+0.62*rate[ring]['total'])*lumi/rate[ring]['int']
	return lumi*rate[ring][when]['lumi']/rate[ring][when]['int']

# histogram for each station, from 90 cm to 700 cm bin width of 10 cm
#hists = {when:{station:{how:R.TH1D('h_{station}_{when}_{how}'.format(**locals()),'',61,90,700) for how in howlist} for station in stationlist} for when in whenlist}

hists = {when:{station:{how:R.TH1D('h_{station}_{when}_{how}'.format(station=station,when=when,how=how),'',61,90,700) for how in howlist} for station in stationlist} for when in whenlist+['all']}
def get_data(line,nWG):
	cols = line.strip('\n').split()
	skip = False
	if cols[0]=='Bin':
		skip = True
	elif cols[0]=='wire':
		skip = True
	elif cols[0]=='tot':
		skip = True
	elif cols[0][0]=='*':
		skip = True
	if not skip:
		wg = float(cols[2])
		area = float(cols[4])
		counts = float(cols[8])
		err = float(cols[10])
	else:
		wg = -1.
		area = -1.
		counts = -1.
		err = -1.
	if (1.0 > wg or wg > nWG):
		skip = True
	data = {
			'skip':skip,
			'wg':wg,
			'area':area,
			'counts':counts,
			'err':err,
			}
	return data

# round up to nearst 10
def roundup(x):
	return math.ceil(x/10.0)*10.
# round down to nearst 10
def rounddown(x):
	return math.floor(x/10.0)*10.

datadict = {ring:{wg:{when:{} for when in whenlist} for wg in range(1,int(nWG[ring])+1)} for ring in ringlist}

# loop on files and make dictionary
for ring in ringlist:
	station = ring[0]
	for when in whenlist:
		occFile = open( 'logs/palchik/occLog_{ring}_{when}.log'.format(**locals()) )
		for line in occFile:
			data = get_data(line,nWG[ring])
			if data['skip']: continue
			r = Aux.getRofWG(ring,data['wg'])
			# calculate area of 10 cm wide annulus
			ringarea = math.pi*(roundup(r)**2 - rounddown(r)**2)
			#chamarea = areaHists['wire'][ring].Integral()
			#print ring,data['wg'],r,data['counts'],ringarea
			lumiweight = lumi_weight(lumi,ring,when)
			datadict[ring][data['wg']][when]['r'] = r
			datadict[ring][data['wg']][when]['counts'] = data['counts']
			datadict[ring][data['wg']][when]['area'] = ringarea
			datadict[ring][data['wg']][when]['lumi'] = lumiweight
			#hists[when][station]['area'].Fill(r,data['counts']/chamarea)
			#hists[when][station]['area'].Fill(r,data['counts']*lumiweight/ringarea)
			#hists[when][station]['counts'].Fill(r,data['counts']*lumiweight)

for ring in ringlist:
	station = ring[0]
	for wg in range(1,int(nWG[ring])+1):
		earlyr = datadict[ring][wg]['early']['r']
		totalr = datadict[ring][wg]['total']['r']
		earlyarea = datadict[ring][wg]['early']['area']
		totalarea = datadict[ring][wg]['total']['area']
		earlycounts = datadict[ring][wg]['early']['counts']
		totalcounts = datadict[ring][wg]['total']['counts']
		earlylumi = datadict[ring][wg]['early']['lumi']
		totallumi = datadict[ring][wg]['total']['lumi']

		if earlyr!=totalr: print 'r not equal?', ring, wg, earlyr, totalr
		if earlyarea!=totalarea: print 'area not equal?', ring, wg, earlyarea,totalarea
		hists['early'][station]['area'].Fill(earlyr, earlycounts*earlylumi/earlyarea)
		hists['total'][station]['area'].Fill(totalr, totalcounts*totallumi/totalarea)

		comb = (1.-fillfrac)*earlycounts*earlylumi/earlyarea + fillfrac*totalcounts*totallumi/totalarea
		hists['all'][station]['area'].Fill(totalr, comb)

def make_plot(hist,when,station,how):
	hist.Scale(4*10**8/10**3) # convert from counts/bx to counts/1000s
	#whentitle = 'In-Train Rate' if when=='total' else 'In-Gap Rate'
	#title = 'Station {station} {whentitle}'.format(**locals())
	#title = 'Station {station} Background Rate'.format(**locals())
	title = 'Station {station} Background Rate'.format(**locals())
	#title = ''
	for logy in [True,False]:
		plot = Plotter.Plot(hist,option='hist')
		canv = Plotter.Canvas(lumi=title,logy=logy)
		canv.addMainPlot(plot)
		canv.firstPlot.SetFillColor(R.kOrange)
		if how=='area':
			canv.firstPlot.SetMaximum(10.)
			canv.firstPlot.SetMinimum(3*10**-4)
		elif how=='counts':
			canv.firstPlot.SetMaximum(5*(10.**4))
		canv.makeTransparent()
		y = 'Rate [kHz'+('/cm^{2}]' if how=='area' else ']')
		canv.firstPlot.setTitles(X='Radius [cm]',Y=y)
		canv.finishCanvas('BOB')
		log = '_log' if logy else ''
		canv.save('plots/palchik/rate_{station}_{when}_{how}{log}.pdf'.format(**locals()))
		whentype = 'intrain'
		if when=='all':
			whentype = 'combined'
		elif when=='early':
			whentype = 'ingap'
		name = 'ME'+str(station)+'_'+whentype+('_log' if logy else '')
		outputRoot.cd()
		canv.Write(name)
		canv.deleteCanvas()

for station in stationlist:
	for when in whenlist+['all']:
		make_plot(hists[when][station]['area'],when,station,'area')
		#for how in howlist:
		#	make_plot(hists[when][station][how],when,station,how)


