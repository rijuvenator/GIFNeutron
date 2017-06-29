import sys, os, argparse, math
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi
import logging,lumberjack
R.gROOT.SetBatch(True)
R.gStyle.SetOptFit(0)

# area histograms calculated on the fly
import areas as areas
areaHists = areas.areaHists

#####################################################

# parse arguments
parser = argparse.ArgumentParser()
# recreate
parser.add_argument('-r','--recreate',action='store_true',dest='RECREATE',
		default=False,help='whether or not to (re)create an output data file')
# input/output root file name
parser.add_argument('-n','--name',dest='NAME',default='',
		help='extra name to identify output (if -r is used) and input (if no -r) root file')
# histogram name
parser.add_argument('-hn','--histname',dest='HISTNAME',default='',
		help='extra name to identify output histograms')
# do track removal
parser.add_argument('-road','--road',dest='DOROADS',action='store_true',
		default=False,help='Wether or not to remove extra tracks found in roads')
# area
parser.add_argument('-a','--area',dest='AREA',action='store_true',
		default=False,help='whether or not to scale to counts/cm^2')
# time
parser.add_argument('-t','--time',dest='TIME',action='store_true',
		default=False,help='whether or not to scale to counts/s')
# pile-up
parser.add_argument('-pu','--pileup',dest='PILEUP',action='store_true',
		default=False,help='whether or not to scale to counts/pp-collision')
# whether or not to include MC on plots
parser.add_argument('-mc','--mc',dest='MC',
		default='',help='whether or not to make plots that include MC')
# Simulation geometry to use
parser.add_argument('-geo','--GEO',dest='GEO',
		default='',help='Which simulation geometry to use')
# Extra name for MC files for special use cases
parser.add_argument('-extra','--extra',dest='EXTRA',
		default='',help='Extra name for MC files for special use cases')
# Whether or not do fit line to hit rate vs. lumi
parser.add_argument('-f','--fit',dest='DOFIT',action='store_true',
		default=False,help='Whether or not to fit line of hit rate vs. lumi')
# Whether or not to make plots in 'BOB' mode
parser.add_argument('-bob','--BOB',dest='BOB',action='store_true',
		default=False,help='Whether or not to make plot titles in BOB mode')
parser.add_argument('-tdr','--TDR',dest='TDR',action='store_true',
		default=False,help='Whether or not to set lumi text to TDR style')
# Whether or not to make separate endcap plots
parser.add_argument('-ec','--DOEC',dest='DOEC',action='store_true',
		default=False,help='Whether or not to make separate endcap plots')
# Temporary directory to dump plots in plots/test
parser.add_argument('-d','--DIR',dest='DIR',
		default='TEST',help='Directory to save plots. Default is plots/TEST')
# Make logs
parser.add_argument('-log','--DOLOG',dest='DOLOG',action='store_true',
		default=False,help='Whether or not to save histogram logs')

args = parser.parse_args()
RECREATE = args.RECREATE
NAME = args.NAME
HISTNAME = args.HISTNAME
DOROADS = args.DOROADS
PILEUP = args.PILEUP
AREA = args.AREA
TIME = args.TIME
MC = args.MC
GEO = args.GEO
EXTRA = args.EXTRA
DOFIT = args.DOFIT
BOB = args.BOB
TDR = args.TDR
DOEC = args.DOEC
DIR = args.DIR
DOLOG = args.DOLOG

#####################################################

# Set up debug loggers
if DOLOG:
	# Occupancy plot logger
	occLog = logging.getLogger('occLog'+('PU' if PILEUP else ''))
	occLog.setLevel(logging.INFO)
	occLogFH = logging.FileHandler('logs/occLog'+('PU' if PILEUP else '')+'.log',mode='w')
	occLogFH.setFormatter(logging.Formatter('%(message)s'))
	occLog.addHandler(occLogFH)
	# Luminosity plot logger
	lumiLog = logging.getLogger('lumiLog'+('PU' if PILEUP else ''))
	lumiLog.setLevel(logging.INFO)
	lumiLogFH = logging.FileHandler('logs/lumiLog'+('PU' if PILEUP else '')+'.log',mode='w')
	lumiLogFH.setFormatter(logging.Formatter('%(message)s'))
	lumiLog.addHandler(lumiLogFH)
	# Luminosity plot logger (half chamber)
	lumiHalfLog = logging.getLogger('lumiHalfLog'+('PU' if PILEUP else ''))
	lumiHalfLog.setLevel(logging.INFO)
	lumiHalfLogFH = logging.FileHandler('logs/lumiHalfLog'+('PU' if PILEUP else '')+'.log',mode='w')
	lumiHalfLogFH.setFormatter(logging.Formatter('%(message)s'))
	lumiHalfLog.addHandler(lumiHalfLogFH)
	# Phi logger
	phiLog = logging.getLogger('phiLog'+('PU' if PILEUP else ''))
	phiLog.setLevel(logging.INFO)
	phiLogFH = logging.FileHandler('logs/phiLog'+('PU' if PILEUP else '')+'.log',mode='w')
	phiLogFH.setFormatter(logging.Formatter('%(message)s'))
	phiLog.addHandler(phiLogFH)
	# Integral logger
	intLog = logging.getLogger('intLog'+('PU' if PILEUP else ''))
	intLog.setLevel(logging.INFO)
	intLogFH = logging.FileHandler('logs/intLog'+('PU' if PILEUP else '')+'.log',mode='w')
	intLogFH.setFormatter(logging.Formatter('%(message)s'))
	intLog.addHandler(intLogFH)

#####################################################

# Which time bins to use in each BX
# lower = low edge
# upper = high edge
# inclusive
BXDICT = {
		'wire':{
			# Early Thermal
			1:{'lower':1,'upper':5},
			2:{'lower':1,'upper':4},
			3:{'lower':1,'upper':3},
			4:{'lower':1,'upper':2},
			5:{'lower':1,'upper':1},
			# Middle Thermal + Fast + Pileup
			12:{'lower':1,'upper':5},
			13:{'lower':1,'upper':5},
			14:{'lower':1,'upper':5},
			15:{'lower':1,'upper':5},
			16:{'lower':1,'upper':5},
			17:{'lower':1,'upper':5},
			18:{'lower':1,'upper':5},
			19:{'lower':1,'upper':5},
			20:{'lower':1,'upper':5},
			21:{'lower':1,'upper':5},
			22:{'lower':1,'upper':5},
			23:{'lower':1,'upper':5},
			24:{'lower':1,'upper':5},
			25:{'lower':1,'upper':5},
			26:{'lower':1,'upper':5},
			27:{'lower':1,'upper':5},
			28:{'lower':1,'upper':5},
			29:{'lower':1,'upper':5},
			30:{'lower':1,'upper':5},
			31:{'lower':1,'upper':5},
			32:{'lower':1,'upper':5},
			33:{'lower':1,'upper':5},
			34:{'lower':1,'upper':5},
			35:{'lower':1,'upper':5},
			36:{'lower':1,'upper':5},
			37:{'lower':1,'upper':5},
			38:{'lower':1,'upper':5},
			39:{'lower':1,'upper':5},
			40:{'lower':1,'upper':5},
			# Late Thermal + Fast
			46:{'lower':13,'upper':15},
			47:{'lower':14,'upper':15},
			48:{'lower':15,'upper':15},
			},
		'comp':{
			# Early Thermal
			1:{'lower':2,'upper':4},
			2:{'lower':2,'upper':3},
			3:{'lower':2,'upper':2},
			# Middle Thermal + Fast + Pileup
			12:{'lower':2,'upper':4},
			13:{'lower':2,'upper':4},
			14:{'lower':2,'upper':4},
			15:{'lower':2,'upper':4},
			16:{'lower':2,'upper':4},
			17:{'lower':2,'upper':4},
			18:{'lower':2,'upper':4},
			19:{'lower':2,'upper':4},
			20:{'lower':2,'upper':4},
			21:{'lower':2,'upper':4},
			22:{'lower':2,'upper':4},
			23:{'lower':2,'upper':4},
			24:{'lower':2,'upper':4},
			25:{'lower':2,'upper':4},
			26:{'lower':2,'upper':4},
			27:{'lower':2,'upper':4},
			28:{'lower':2,'upper':4},
			29:{'lower':2,'upper':4},
			30:{'lower':2,'upper':4},
			31:{'lower':2,'upper':4},
			32:{'lower':2,'upper':4},
			33:{'lower':2,'upper':4},
			34:{'lower':2,'upper':4},
			35:{'lower':2,'upper':4},
			36:{'lower':2,'upper':4},
			37:{'lower':2,'upper':4},
			38:{'lower':2,'upper':4},
			39:{'lower':2,'upper':4},
			40:{'lower':2,'upper':4},
			# Late Thermal + Fast
			48:{'lower':9,'upper':9},
			},
		}

#####################################################

# Which BXs to use in each plot
# FORMAT:
# 'digi':{
#     'hist-type':{
#         'bx':[list of bx to use],'tb':total number of time bins (user input)
#         }
#     }

PLOT = {
		'wire':{
			'early':{'bx':[1,2,3,4,5],'tb':15.},
#			'bx1':{'bx':[1],'tb':5.},
#			'bx2':{'bx':[2],'tb':4.},
#			'bx3':{'bx':[3],'tb':3.},
#			'bx4':{'bx':[4],'tb':2.},
#			'bx5':{'bx':[5],'tb':1.},

			'total':{'bx':range(12,41),'tb':145.},
#			'bx12':{'bx':[12],'tb':5.},
#			'bx13':{'bx':[13],'tb':5.},
#			'bx14':{'bx':[14],'tb':5.},
#			'bx15':{'bx':[15],'tb':5.},
#			'bx16':{'bx':[16],'tb':5.},
#			'bx17':{'bx':[17],'tb':5.},
#			'bx18':{'bx':[18],'tb':5.},
#			'bx19':{'bx':[19],'tb':5.},
#			'bx20':{'bx':[20],'tb':5.},
#			'bx21':{'bx':[21],'tb':5.},
#			'bx22':{'bx':[22],'tb':5.},
#			'bx23':{'bx':[23],'tb':5.},
#			'bx24':{'bx':[24],'tb':5.},
#			'bx25':{'bx':[25],'tb':5.},
#			'bx26':{'bx':[26],'tb':5.},
#			'bx27':{'bx':[27],'tb':5.},
#			'bx28':{'bx':[28],'tb':5.},
#			'bx29':{'bx':[29],'tb':5.},
#			'bx30':{'bx':[30],'tb':5.},
#			'bx31':{'bx':[31],'tb':5.},
#			'bx32':{'bx':[32],'tb':5.},
#			'bx33':{'bx':[33],'tb':5.},
#			'bx34':{'bx':[34],'tb':5.},
#			'bx35':{'bx':[35],'tb':5.},
#			'bx36':{'bx':[36],'tb':5.},
#			'bx37':{'bx':[37],'tb':5.},
#			'bx38':{'bx':[38],'tb':5.},
#			'bx39':{'bx':[39],'tb':5.},
#			'bx40':{'bx':[40],'tb':5.},

			'late':{'bx':[46,47,48],'tb':6.},
#			'bx46':{'bx':[46],'tb':1.},
#			'bx47':{'bx':[47],'tb':2.},
#			'bx48':{'bx':[48],'tb':3.},
			},
		'comp':{
			'early':{'bx':[1,2,3],'tb':6.},
#			'bx1':{'bx':[1],'tb':3.},
#			'bx2':{'bx':[2],'tb':2.},
#			'bx3':{'bx':[3],'tb':1.},

			'total':{'bx':range(12,41),'tb':87.},
#			'bx12':{'bx':[12],'tb':4.},
#			'bx13':{'bx':[13],'tb':4.},
#			'bx14':{'bx':[14],'tb':4.},
#			'bx15':{'bx':[15],'tb':4.},
#			'bx16':{'bx':[16],'tb':4.},
#			'bx17':{'bx':[17],'tb':4.},
#			'bx18':{'bx':[18],'tb':4.},
#			'bx19':{'bx':[19],'tb':4.},
#			'bx20':{'bx':[20],'tb':4.},
#			'bx21':{'bx':[21],'tb':4.},
#			'bx22':{'bx':[22],'tb':4.},
#			'bx23':{'bx':[23],'tb':4.},
#			'bx24':{'bx':[24],'tb':4.},
#			'bx25':{'bx':[25],'tb':4.},
#			'bx26':{'bx':[26],'tb':4.},
#			'bx27':{'bx':[27],'tb':4.},
#			'bx28':{'bx':[28],'tb':4.},
#			'bx29':{'bx':[29],'tb':4.},
#			'bx30':{'bx':[30],'tb':4.},
#			'bx31':{'bx':[31],'tb':4.},
#			'bx32':{'bx':[32],'tb':4.},
#			'bx33':{'bx':[33],'tb':4.},
#			'bx34':{'bx':[34],'tb':4.},
#			'bx35':{'bx':[35],'tb':4.},
#			'bx36':{'bx':[36],'tb':4.},
#			'bx37':{'bx':[37],'tb':4.},
#			'bx38':{'bx':[38],'tb':4.},
#			'bx39':{'bx':[39],'tb':4.},
#			'bx40':{'bx':[40],'tb':4.},

			'late':{'bx':[48],'tb':1.},
			},
		}

#####################################################

# User input maximum limits of plots
LIMITS = {
		'int':{
			'early':{
				#'wire':0.0052,
				#'comp':0.004,
			},
			'late':{
				#'wire':0.0052,
				#'comp':0.004,
			},
			'total':{
				#'wire':0.0052,
				#'comp':0.004,
			},
		},
		'occ':{
			'early':{
				'comp':{
					#'11':50e-6,
					#'12':12e-6,
					#'13':15e-6,
					#'21':45e-6,
					#'22':10e-6,
					#'31':30e-6,
					#'32':15e-6,
					#'41':30e-6,
					#'42':25e-6,
					},
				'wire':{
					# Counts / wg / 25 ns / pp
					#'11':0.2e-3,
					#'12':12e-6,
					#'13':16e-6,
					#'21':0.08e-3,
					#'22':26e-6,
					#'31':0.08e-3,
					#'32':40e-6,
					#'41':0.06e-3,
					#'42':0.05e-3,
					# Counts / area / s / pp
					#'11':12.,
					#'12':7,
					#'13':16e-6,
					#'21':7.,
					#'22':26e-6,
					#'31':0.08e-3,
					#'32':40e-6,
					#'41':0.06e-3,
					},
				},
			'late':{
				'wire':{},
				'comp':{},
				},
			'total':{
				'wire':{},
				'comp':{},
				},
			},
		'phi':{
			'early':{
				'wire':{
					# Counts / digi / bx / pp
					#'22':0.0012,
					#'32':0.001,
					#'42':0.0025,
					# Counts / cm2 / s / pp
					#'22':20.,
					#'32':14.,
					#'42':30.,
					},
				'comp':{
					},
				},
			'late':{
				'wire':{},
				'comp':{},
				},
			'total':{
				'wire':{},
				'comp':{},
				},
			},


		}


#####################################################

### Set globals
RINGLIST = ['11','21','31','41','12','13','22','32','42']
ERINGLIST = ['+11','-11','+21','-21','+31','-31','+41','-41',
			 '+12','-12','+13','-13','+22','-22','+32','-32','+42','-42']
ringMap = {ring:i for i,ring in enumerate(RINGLIST)}
eringMap = {ring:i for i,ring in enumerate(ERINGLIST)}
ECLIST = ['']
ectypelist = ['comb']
if DOEC: 
	ECLIST.append('+')
	ECLIST.append('-')
	ectypelist.append('sep')
HALVES = {
		'comp':['l','r','a'],
		'wire':['l','u','a'],
		}

TDRNAME = '8.73 fb^{-1} (13 TeV)'
path = 'plots/'+DIR # DIR defaults to 'TEST'

# convert counts/bx to counts/s
BXtoSconv = 25.*10**(-9)

# need to fix so that it only integrates wg and hs it needs to integrate
# currently it over estimates the chamber area by a small amount (ok for now I guess?)
chamArea = {digi:{ring:areaHists[digi][ring].Integral() for ring in RINGLIST} for digi in PLOT.keys()}
chamHalfArea = {digi:{half:{ring:{} for ring in RINGLIST} for half in HALVES[digi][0:2]} for digi in PLOT.keys()}
for digi in PLOT.keys():
	for half in HALVES[digi][0:2]:
		for ring in RINGLIST:
			# binnum 1 = wg 0 (doesn't exist)
			# binnum 2 = wg 1 etc.
			# Both area and occupancy hists are identically constructed
			cham = CH.Chamber(CH.serialID(1, int(ring[0]), int(ring[1]), 1))
			nHS = cham.nstrips*2
			nWG = cham.nwires
			if digi=='comp':
				area = areaHists[digi][ring].Integral(2,nHS+2)
				chamHalfArea[digi][half][ring] = area/2.
			if digi=='wire':
				if half=='l':
					low = 2
					high = nWG/2+1
				if half=='u':
					low = (nWG/2)+2
					high = nWG+1
				area = areaHists[digi][ring].Integral(low,high)
				chamHalfArea[digi][half][ring] = area

#####################################
### Get/make occupancy histograms ###
#####################################

if RECREATE:
	# Get Tree
	if DOROADS:
		FILE = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/goatees/GOAT_P5_DOROAD_13June2017.root')
	else:
		FILE = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/goatees/GOAT_P5_14June2017.root')
	tree = FILE.Get('t')
	### Set Histograms
	FOUT = R.TFile('root/occupancy'+('_'+NAME if NAME != '' else '')+'.root','RECREATE')
	FOUT.cd()
	HISTS = {ec+ring:{digi:{bx:{half:{} for half in HALVES[digi]} for bx in BXDICT[digi].keys()} for digi in BXDICT.keys()} for ring in RINGLIST for ec in ECLIST}
	PHI = {ec+ring:{digi:{bx:{half:{} for half in HALVES[digi]} for bx in BXDICT[digi].keys()} for digi in BXDICT.keys()} for ring in RINGLIST for ec in ECLIST}
	LUMI = {ec+ring:{digi:{bx:{half:{} for half in HALVES[digi]} for bx in BXDICT[digi].keys()} for digi in BXDICT.keys()} for ring in RINGLIST for ec in ECLIST}
	INT = {digi:{bx:{half:{} for half in HALVES[digi]} for bx in BXDICT[digi].keys()} for digi in PLOT.keys()}
	lumiBins = 30
	maxLumi = 1.5e34
	# Occ,Phi,Lumi
	for digi in PLOT.keys():
		for half in HALVES[digi]:
			for bx in BXDICT[digi].keys():
				# Set Integral Plots
				INT[digi][bx][half] = {
						'num_comb'  :R.TH1D('num_comb_int_'+digi+'_'+half+'_'+str(bx),'',9,0,9),
						'den_comb'  :R.TH1D('den_comb_int_'+digi+'_'+half+'_'+str(bx),'',9,0,9),
						'rate_comb' :R.TH1D('rate_comb_int_'+digi+'_'+half+'_'+str(bx),'',9,0,9),
						'num_sep'   :R.TH1D('num_sep_int_'+digi+'_'+half+'_'+str(bx),'',18,0,18),
						'den_sep'   :R.TH1D('den_sep_int_'+digi+'_'+half+'_'+str(bx),'',18,0,18),
						'rate_sep'  :R.TH1D('rate_sep_int_'+digi+'_'+half+'_'+str(bx),'',18,0,18),
						}
				INT[digi][bx][half]['num_comb'].SetDirectory(0)
				INT[digi][bx][half]['den_comb'].SetDirectory(0)
				INT[digi][bx][half]['rate_comb'].SetDirectory(0)
				INT[digi][bx][half]['num_sep'].SetDirectory(0)
				INT[digi][bx][half]['den_sep'].SetDirectory(0)
				INT[digi][bx][half]['rate_sep'].SetDirectory(0)
				for ring in RINGLIST:
					for ec in ECLIST:
						cham = CH.Chamber(CH.serialID(1, int(ring[0]), int(ring[1]), 1))
						nhs = cham.nstrips*2
						nwg = cham.nwires
						lim = nhs+2 if digi=='comp' else nwg+2
						# Set occupancy histograms
						HISTS[ec+ring][digi][bx][half] = {
								'num':R.TH1D('num_occ_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx),'',  lim,0,lim),
								'den':R.TH1D('den_occ_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx),'',  1,0,1),
								'rate':R.TH1D('rate_occ_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx),'',  lim,0,lim),
								}
						HISTS[ec+ring][digi][bx][half]['num'].SetDirectory(0)
						HISTS[ec+ring][digi][bx][half]['den'].SetDirectory(0)
						HISTS[ec+ring][digi][bx][half]['rate'].SetDirectory(0)
						# Set global phi histograms
						if ring=='21' or ring=='31' or ring=='41':
							ncham = 18
						else:
							ncham = 36
						PHI[ec+ring][digi][bx][half] = {
							'num':R.TH1D('num_phi_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx),'',  ncham,1,ncham+1),
							'den':R.TH1D('den_phi_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx),'',  ncham,1,ncham+1),
							'rate':R.TH1D('rate_phi_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx),'',ncham,1,ncham+1),
						}
						PHI[ec+ring][digi][bx][half]['num'].SetDirectory(0)
						PHI[ec+ring][digi][bx][half]['den'].SetDirectory(0)
						PHI[ec+ring][digi][bx][half]['rate'].SetDirectory(0)
						# Set luminosity histograms
						LUMI[ec+ring][digi][bx][half] = {
							'num' :R.TH1D('num_lumi_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx), '',lumiBins,0,maxLumi),
							'den' :R.TH1D('den_lumi_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx), '',lumiBins,0,maxLumi),
							'rate':R.TH1D('rate_lumi_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx),'',lumiBins,0,maxLumi),
						}
						LUMI[ec+ring][digi][bx][half]['num'].SetDirectory(0)
						LUMI[ec+ring][digi][bx][half]['den'].SetDirectory(0)
						LUMI[ec+ring][digi][bx][half]['rate'].SetDirectory(0)

	############################
	### Fill Data Histograms ###
	############################
	for idx,entry in enumerate(tree):
		sys.stdout.write('Entry {idx:>10}\r'.format(**locals()))
		sys.stdout.flush()
		ring = str(entry.RING)
		cham = CH.Chamber(CH.serialID(1, int(ring[0]), int(ring[1]), 1))
		ecr = str(entry.ENDCAP)+str(entry.RING)
		bx = str(entry.BX)
		half = str(entry.HALF)
		digi = str(entry.DIGI)
		weight = 1.
		if entry.BX in BXDICT[digi].keys():
			for idigi,time in enumerate(entry.D_TIME):
				if time >= BXDICT[digi][entry.BX]['lower'] and \
				   time <= BXDICT[digi][entry.BX]['upper']:
					# Set histogram weights
					weight = 1./entry.PILEUP if PILEUP else 1.
					# Fill Numerator Plots (endcaps combined)
					HISTS[ring][digi][entry.BX][half]['num'].Fill(entry.D_POS[idigi],weight)
					PHI[ring][digi][entry.BX][half]['num'].Fill(entry.CHAM,weight)
					LUMI[ring][digi][entry.BX][half]['num'].Fill(entry.LUMI,weight)
					INT[digi][entry.BX][half]['num_comb'].Fill(ringMap[str(entry.RING)],weight)
					# Fill Numerator Plots (endcaps separated)
					HISTS[ecr][digi][entry.BX][half]['num'].Fill(entry.D_POS[idigi],weight)
					LUMI[ecr][digi][entry.BX][half]['num'].Fill(entry.LUMI,weight)
					PHI[ecr][digi][entry.BX][half]['num'].Fill(entry.CHAM,weight)
					INT[digi][entry.BX][half]['num_sep'].Fill(eringMap[ecr],weight)

			# Fill Denominator Plots (endcaps combined)
			HISTS[ring][digi][entry.BX][half]['den'].Fill(0,1.)
			PHI[ring][digi][entry.BX][half]['den'].Fill(entry.CHAM,1.)
			LUMI[ring][digi][entry.BX][half]['den'].Fill(entry.LUMI,1.)
			INT[digi][entry.BX][half]['den_comb'].Fill(ringMap[str(entry.RING)],1.)
			# Fill denominatory plots (endcaps separated)
			HISTS[ecr][digi][entry.BX][half]['den'].Fill(0,1.)
			PHI[ecr][digi][entry.BX][half]['den'].Fill(entry.CHAM,1.)
			LUMI[ecr][digi][entry.BX][half]['den'].Fill(entry.LUMI,1.)
			INT[digi][entry.BX][half]['den_sep'].Fill(eringMap[ecr],1.)

	# Write histograms to output file
	FOUT.cd()
	for digi in BXDICT.keys():
		for half in HALVES[digi]:
			for bx in BXDICT[digi].keys():
				for TYPE in ['num','den','rate']:
					INT[digi][bx][half][TYPE+'_comb'].Write()
					INT[digi][bx][half][TYPE+'_sep'].Write()
					for ring in RINGLIST:
						for ec in ECLIST:
							HISTS[ec+ring][digi][bx][half][TYPE].Write()
							PHI[ec+ring][digi][bx][half][TYPE].Write()
							LUMI[ec+ring][digi][bx][half][TYPE].Write()
else:
	# Get occ,phi,lumi histograms from already created output file
	HISTS = {ec+ring:{digi:{bx:{half:{} for half in HALVES[digi]} for bx in BXDICT[digi].keys()} for digi in BXDICT.keys()} for ring in RINGLIST for ec in ECLIST}
	PHI = {ec+ring:{digi:{bx:{half:{} for half in HALVES[digi]} for bx in BXDICT[digi].keys()} for digi in BXDICT.keys()} for ring in RINGLIST for ec in ECLIST}
	LUMI = {ec+ring:{digi:{bx:{half:{} for half in HALVES[digi]} for bx in BXDICT[digi].keys()} for digi in BXDICT.keys()} for ring in RINGLIST for ec in ECLIST}
	INT = {digi:{bx:{half:{} for half in HALVES[digi]} for bx in BXDICT[digi].keys()} for digi in PLOT.keys()}
	FOUT = R.TFile.Open('root/occupancy'+('_'+NAME if NAME != '' else '')+'.root','READ')
	for digi in BXDICT.keys():
		for half in HALVES[digi]:
			for bx in BXDICT[digi].keys():
				# Get Integral histograms
				INT[digi][bx][half] = {
						'num_comb'  :FOUT.Get('num_comb_int_'+digi+'_'+half+'_'+str(bx)),
						'den_comb'  :FOUT.Get('den_comb_int_'+digi+'_'+half+'_'+str(bx)),
						'rate_comb' :FOUT.Get('rate_comb_int_'+digi+'_'+half+'_'+str(bx)),
						'num_sep'   :FOUT.Get('num_sep_int_'+digi+'_'+half+'_'+str(bx)),
						'den_sep'   :FOUT.Get('den_sep_int_'+digi+'_'+half+'_'+str(bx)),
						'rate_sep'  :FOUT.Get('rate_sep_int_'+digi+'_'+half+'_'+str(bx)),
						}
				INT[digi][bx][half]['num_comb'].SetDirectory(0)
				INT[digi][bx][half]['den_comb'].SetDirectory(0)
				INT[digi][bx][half]['rate_comb'].SetDirectory(0)
				INT[digi][bx][half]['num_sep'].SetDirectory(0)
				INT[digi][bx][half]['den_sep'].SetDirectory(0)
				INT[digi][bx][half]['rate_sep'].SetDirectory(0)
				for ring in RINGLIST:
					for ec in ECLIST:
						# Get occupancy histograms
						HISTS[ec+ring][digi][bx][half] = {
								'num' :FOUT.Get('num_occ_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx)).Clone(),
								'den' :FOUT.Get('den_occ_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx)).Clone(),
								'rate':FOUT.Get('rate_occ_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx)).Clone(),
								}
						HISTS[ec+ring][digi][bx][half]['num'].SetDirectory(0)
						HISTS[ec+ring][digi][bx][half]['den'].SetDirectory(0)
						HISTS[ec+ring][digi][bx][half]['rate'].SetDirectory(0)
						# Get chamber occupancy histograms (global phi)
						PHI[ec+ring][digi][bx][half] = {
								'num' :FOUT.Get('num_phi_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx)).Clone(),
								'den' :FOUT.Get('den_phi_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx)).Clone(),
								'rate':FOUT.Get('rate_phi_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx)).Clone(),
								}
						PHI[ec+ring][digi][bx][half]['num'].SetDirectory(0)
						PHI[ec+ring][digi][bx][half]['den'].SetDirectory(0)
						PHI[ec+ring][digi][bx][half]['rate'].SetDirectory(0)
						# Get luminosity histograms
						LUMI[ec+ring][digi][bx][half] = {
								'num' :FOUT.Get('num_lumi_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx)).Clone(),
								'den' :FOUT.Get('den_lumi_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx)).Clone(),
								'rate':FOUT.Get('rate_lumi_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx)).Clone(),
								}
						LUMI[ec+ring][digi][bx][half]['num'].SetDirectory(0)
						LUMI[ec+ring][digi][bx][half]['den'].SetDirectory(0)
						LUMI[ec+ring][digi][bx][half]['rate'].SetDirectory(0)

#########################
### Get MC histograms ###
#########################

# Set MC
if MC=='':
	MCLIST = ['']
elif MC=='all':
	#MCLIST = ['XS_ThermalON','XS_ThermalOFF','HP_ThermalON','HP_ThermalOFF']
	MCLIST = ['XS_ThermalON','HP_ThermalON']
else:
	MCLIST = [MC]

if MC:
	if 'PP' not in NAME: 
		print 'Data/MC comparisons only work if you normalize data by pileup'
		exit()
	MCHISTS = {mc:{ec+ring:{digi:{} for digi in PLOT.keys()} for ec in ECLIST for ring in RINGLIST} for mc in MCLIST}
	MCINT = {mc:{digi:{} for digi in PLOT.keys()} for mc in MCLIST}
	for mc in MCLIST:
		mcName = mc+'_TOF'+('_'+GEO if GEO!='' else '')+'_'+NAME
		FMC = R.TFile.Open('root/hists_'+mcName+'.root')
		print 'root/hists_'+mcName+'.root'
		for digi in PLOT.keys():
			# Get Integral histograms
			for pType in ['comb','sep']:
				MCINT[mc][digi]['comb'] = FMC.Get(digi+'_int_comb').Clone()
				MCINT[mc][digi]['sep']  = FMC.Get(digi+'_int_sep').Clone()
				MCINT[mc][digi]['comb'].SetDirectory(0)
				MCINT[mc][digi]['sep'].SetDirectory(0)
			# Get Phi and Occupancy histograms
			for ring in RINGLIST:
				for ec in ECLIST:
					MCHISTS[mc][ec+ring][digi] = {
							'occ' : FMC.Get(ec+ring+'_'+digi+'_occ').Clone(),
							'phi' : FMC.Get('phi_'+ec+ring+'_'+digi+'_occ').Clone(),
							}
					MCHISTS[mc][ec+ring][digi]['occ'].SetDirectory(0)
					MCHISTS[mc][ec+ring][digi]['phi'].SetDirectory(0)

###########################
### Make plot functions ###
###########################

def occNormArea(hist):
	# Divide by hand since Divide() doesn't handle bin errors correctly?
	for ibin in range(1,hist.GetNbinsX()+1):
		# don't add 1 since want histogram to start at 0
		# binnum 1 = wg 0 (doesn't exist)
		# binnum 2 = wg 1 etc.
		# Both area and occupancy hists are identically constructed
		binnum = ibin 
		content = hist.GetBinContent(binnum)
		digiarea = areaHists[digi][ring].GetBinContent(binnum)
		if content<1: continue
		if digiarea<1: continue
		hist.SetBinContent(binnum,content/digiarea)
		contenterr = hist.GetBinError(binnum)
		hist.SetBinError(binnum,contenterr/digiarea)

def makeOccupancyPlot(dataHist,digi,when,ec,ring,mc):
	# Make occupancy plot for each digi and plot type
	# Make MC plot
	if mc!='':
		mcname = mc.replace('_',' ')
		mchist = MCHISTS[mc][ec+ring][digi]['occ'].Clone()
		mcPlot = Plotter.Plot(mchist,legType='f',option='hist',legName='Geant4 '+mcname[0:2] if TDR else mcname)
	# normalize to counts per sec
	if TIME: 
		dataHist.Scale(1./BXtoSconv)
		if mc!='': mchist.Scale(1./BXtoSconv)
	# normalize to area (dataHist is already a clone)
	if AREA:
		occNormArea(dataHist)
		if mc!='': occNormArea(mchist)
	# Now make plot
	#dataPlot = Plotter.Plot(dataHist,option='p',legType='pe',legName='Data')
	title = 'ME'+ec+ring+' '+('Comparator' if digi=='comp' else 'Wire Group')+' Occupancy'
	for LOGY in [False]:#,True]:
		if mc!='':
			mcname = mc.replace('_',' ')
			TITLE = mcname
		else:
			TITLE = title
		canvas = Plotter.Canvas(extra='Preliminary',lumi=TDRNAME if TDR else TITLE,logy=LOGY)
		if mc!='':
			canvas.addMainPlot(mcPlot)
			mcPlot.SetFillColor(R.kOrange)
		#canvas.addMainPlot(dataPlot)
		if mc!='':
			canvas.makeLegend(pos='tr')
			canvas.legend.moveLegend(X=-0.2,Y=-0.1)
			canvas.legend.resizeHeight()
			if not TDR: canvas.drawText('MC integral : {:1.4f}'.format(mcPlot.Integral()),pos=(0.6,0.7))
		mcMax = mcPlot.GetMaximum() if mc!='' else 0.
		maximum = max(dataPlot.GetMaximum(),mcMax)
		if ring in LIMITS['occ'][when][digi].keys():
			canvas.firstPlot.SetMaximum(LIMITS['occ'][when][digi][ring])
		else: # set maximum dynamically
			canvas.firstPlot.SetMaximum(maximum * 1.2)
		canvas.firstPlot.SetMinimum(1e-2 if LOGY else 0.)
		x = 'Comparator Half Strip' if digi=='comp' else 'Wire Group Number'
		y = 'Counts'+('/pp' if PILEUP and not TDR else '')+('/cm^{2}' if AREA else '')+('/s' if TIME else '/BX')
		canvas.firstPlot.setTitles(X=x, Y=y)
		if not TDR: canvas.drawText('Data integral : {:1.4f}'.format(dataPlot.Integral()),pos=(0.6,0.6))
		canvas.firstPlot.scaleTitleOffsets(1.2,'Y')
		canvas.makeTransparent()
		if BOB:
			canvas.finishCanvas('BOB')
		else:
			canvas.finishCanvas()
		name = 'occupancy_'+ec+ring+'_'+digi+'_'+when+('_'+HISTNAME if HISTNAME!= '' else '')+('_logy' if LOGY else '')+('_'+mc if mc!='' else '')+'_MCONLY'
		name = name.replace('+','p')
		name = name.replace('-','m')
		canvas.save(path+'/'+name+'.pdf')
		canvas.deleteCanvas()

def makePhiPlot(dataHist,digi,when,ec,ring,mc):
	# Make occupancy plot for each digi and plot type
	# Make MC plot
	if mc!='':
		mcname = mc.replace('_',' ')
		mchist = MCHISTS[mc][ec+ring][digi]['phi'].Clone()
		mcPlot = Plotter.Plot(mchist,legType='f',option='hist',legName='Geant4 '+mcname[0:2] if TDR else mcname)
	# Scale by time
	if TIME: 
		dataHist.Scale(1./BXtoSconv)
		if mc!='': mchist.Scale(1./BXtoSconv)
	# scale by chamber area
	if AREA: 
		dataHist.Scale(1./chamArea[digi][ring])
		if mc!='': mchist.Scale(1./chamArea[digi][ring])
	# Now make plot
	#dataPlot = Plotter.Plot(dataHist.Clone(),option='pe',legName='Data',legType='pe')
	TITLE = 'ME'+ec+ring+' '+('Comparator ' if digi=='comp' else 'Wire Group ')+'Occupancy per Chamber'
	for LOGY in [False]:#,True]:
		canvas = Plotter.Canvas(extra='Preliminary',lumi=TDRNAME if TDR else TITLE,logy=LOGY)
		if mc!='':
			canvas.addMainPlot(mcPlot)
			mcPlot.SetFillColor(R.kOrange)
		#canvas.addMainPlot(dataPlot)
		if mc!='':
			canvas.makeLegend(pos='tr')
			canvas.legend.moveLegend(X=-0.2,Y=-0.1)
			canvas.legend.resizeHeight()
			if not TDR: canvas.drawText('MC integral : {:1.4f}'.format(mcPlot.Integral()),pos=(0.6,0.7))
		mcMax = mcPlot.GetMaximum() if mc!='' else 0.
		maximum = max(dataPlot.GetMaximum(),mcMax)
		if ring in LIMITS['phi'][when][digi].keys():
				canvas.firstPlot.SetMaximum(LIMITS['phi'][when][digi][ring])
		else: # set maximum dynamically
			canvas.firstPlot.SetMaximum(maximum * 1.2)
		canvas.firstPlot.SetMinimum(1e-2 if LOGY else 0.)
		x = 'CSC Chamber'
		y = 'Counts'+('/pp' if PILEUP and not TDR else '')+('/cm^{2}' if AREA else '')+('/s' if TIME else '/BX')
		canvas.firstPlot.setTitles(X=x, Y=y)
		canvas.firstPlot.scaleTitleOffsets(1.2,'Y')
		if not TDR: canvas.drawText('Data integral : {:1.4f}'.format(dataPlot.Integral()),pos=(0.6,0.6))
		canvas.makeTransparent()
		if BOB:
			canvas.finishCanvas('BOB')
		else:
			canvas.finishCanvas()
		name = 'phi_'+ec+ring+'_'+digi+'_'+when+('_'+HISTNAME if HISTNAME != '' else '')+('_logy' if LOGY else '')+('_'+mc if mc!='' else '')+'_MCONLY'
		name = name.replace('+','p')
		name = name.replace('-','m')
		canvas.save(path+'/'+name+'.pdf')
		canvas.deleteCanvas()

def intNormArea(hist):
	for ibin in range(1,hist.GetNbinsX()+1):
		content = hist.GetBinContent(ibin)
		contentErr = hist.GetBinError(ibin)
		if ectype=='comb':
			area = chamArea[digi][RINGLIST[ibin-1]]
		else:
			area = chamArea[digi][ERINGLIST[ibin-1][1:3]]
		if content==0.: continue
		if area==0.: continue
		hist.SetBinContent(ibin,content/area)
		hist.SetBinError(ibin,contentErr/area)

def makeIntegralPlot(dataHist,digi,when,ectype,mc):
	# Make integral plot for each digi and plot type
	# Make MC Plot
	if mc!='':
		mcname = mc.replace('_',' ')
		mchist = MCINT[mc][digi][ectype].Clone()
		mcPlot = Plotter.Plot(mchist,option='hist',legName='Geant4 '+mcname[0:2] if TDR else mcname,legType='f')
	# Scale by time
	if TIME: 
		dataHist.Scale(1./BXtoSconv)
		if mc!='': mchist.Scale(1./BXtoSconv)
	# Scale by area
	if AREA:
		intNormArea(dataHist)
		if mc!='': intNormArea(mchist)
	#dataPlot = Plotter.Plot(dataHist.Clone(),option='p',legType='pe',legName='Data')
	title = ('Comparator ' if digi=='comp' else 'Wire Group ')+'Integral Occupancy'
	for LOGY in [False]:#True]:
		if mc!='':
			mcname = mc.replace('_',' ')
			TITLE = mcname
		else:
			TITLE = title
		canvas = Plotter.Canvas(extra='Preliminary',lumi=TDRNAME if TDR else TITLE,logy=LOGY)
		if mc!='': 
			canvas.addMainPlot(mcPlot)
			mcPlot.SetFillColor(R.kOrange)
		#canvas.addMainPlot(dataPlot)
		if mc!='':
			canvas.makeLegend(pos='tr')
			canvas.legend.moveLegend(X=-0.2,Y=-0.1)
			canvas.legend.resizeHeight()
		if digi in LIMITS['int'][when].keys():
			canvas.firstPlot.SetMaximum(LIMITS['int'][when][digi])
		else: # set maximum dynamically
			mcMax = mcPlot.GetMaximum() if mc!='' else 0.
			maximum = max(dataPlot.GetMaximum(),mcMax)
			canvas.firstPlot.SetMaximum(maximum * 1.1)
		canvas.firstPlot.SetMinimum(1e-2 if LOGY else 0.)
		x = 'CSC Ring'
		if ectype=='comb':
			for ibin,ring in enumerate(RINGLIST):
				canvas.firstPlot.GetXaxis().SetBinLabel(ibin+1, ring)
		else:
			for ibin,ring in enumerate(ERINGLIST):
				canvas.firstPlot.GetXaxis().SetBinLabel(ibin+1, ring.replace('-','#minus'))
		y = 'Counts'+('/pp' if PILEUP and not TDR else '')+('/cm^{2}' if AREA else '')+('/s' if TIME else '/BX')
		canvas.firstPlot.setTitles(X=x,Y=y)
		canvas.firstPlot.scaleTitleOffsets(1.2,'Y')
		canvas.makeTransparent()
		if BOB:
			canvas.finishCanvas('BOB')
		else:
			canvas.finishCanvas()
		name = 'integral_'+ectype+'_'+digi+'_'+when+('_'+HISTNAME if HISTNAME != '' else '')+('_logy' if LOGY else '')+('_'+mc if mc!='' else '')+'_MCONLY'
		canvas.save(path+'/'+name+'.pdf')
		canvas.deleteCanvas()

def makeLuminosityPlot(dataHist,digi,when,ec,ring,DOFIT=False):
	# Scale by time
	if TIME: dataHist.Scale(1./BXtoSconv)
	# Scale by area
	if AREA: dataHist.Scale(1./chamArea[digi][ring])
	# Make occupancy plot for each digi and plot type
	dataPlot = Plotter.Plot(dataHist.Clone(),option='pe')
	TITLE = 'ME'+ec+ring+' '+('Comparator ' if digi=='comp' else 'Wire Group ')+'Rate vs. Lumi'
	for LOGY in [False]:#,True]:
		canvas = Plotter.Canvas(extra='Preliminary',lumi=TDRNAME if TDR else TITLE,logy=LOGY)
		canvas.addMainPlot(dataPlot,addToPlotList=False)
		if DOFIT:
			line = R.TF1('fitline_'+dataPlot.GetName(),'[0]*x',0,10**34)
			line.SetLineColor(R.kRed)
			dataPlot.Fit('fitline_'+dataPlot.GetName())
			fit = dataPlot.GetFunction('fitline_'+dataPlot.GetName())
			if not TDR:
				result = '#splitline{slope = %.3e #pm %.3e}{#chi^{2}/dof = %5.3f / %2i}'%(fit.GetParameter(0),fit.GetParError(0),fit.GetChisquare(),fit.GetNDF())
				canvas.drawText(text=result,pos=(0.2,0.8),align='tl')
		canvas.firstPlot.SetMinimum(1e-2 if LOGY else 0.)
		x = 'Luminosity [cm^{-2}s^{-1}]'
		y = 'Counts'+('/pp' if PILEUP and not TDR else '')+('/cm^{2}' if AREA else '')+('/s' if TIME else '/BX')
		canvas.firstPlot.setTitles(X=x, Y=y)
		canvas.firstPlot.scaleTitleOffsets(1.2,'Y')
		canvas.makeTransparent()
		if BOB:
			canvas.finishCanvas('BOB')
		else:
			canvas.finishCanvas()
		name = 'luminosity_'+ec+ring+'_'+digi+'_'+when+('_'+HISTNAME if HISTNAME != '' else '')+('_logy' if LOGY else '')+('_fit' if DOFIT else '')
		name = name.replace('+','p')
		name = name.replace('-','m')
		canvas.save(path+'/'+name+'.pdf')
		canvas.deleteCanvas()

def makeSepLumiPlot(hist1,hist2,digi,when,ec,ring,DOFIT):
	# Make counts vs. luminosity plots for each half separately and plot them on 
	# the same axis
	# hist1 = HALVES[digi][0] = ['l','l'] : Left and Lower
	# hist2 = HALVES[digi][1] = ['r','u'] : Right and Upper
	# Scale by area
	if AREA:
		hist1.Scale(1./chamHalfArea[digi][HALVES[digi][0]][ring])
		hist2.Scale(1./chamHalfArea[digi][HALVES[digi][1]][ring])
	if TIME:
		hist1.Scale(1./BXtoSconv)
		hist2.Scale(1./BXtoSconv)
	plot1 = Plotter.Plot(hist1,legType='pe',legName='Lower half' if digi=='wire' else 'Left half',option='p')
	plot2 = Plotter.Plot(hist2,legType='pe',legName='Upper half' if digi=='wire' else 'Right half',option='p')
	TITLE = 'ME'+ring+(' Wire Group' if digi=='wire' else ' Comparator')+' Rate vs. Lumi'
	for LOGY in [False]:#,True]:
		canvas = Plotter.Canvas(extra='Preliminary',lumi=TDRNAME if TDR else TITLE,logy=LOGY)
		canvas.addMainPlot(plot1)
		canvas.addMainPlot(plot2)
		plot1.SetLineColor(R.kRed)
		plot1.SetMarkerColor(R.kRed)
		plot2.SetLineColor(R.kBlue)
		plot2.SetMarkerColor(R.kBlue)
		if DOFIT:
			for p,plot in enumerate([plot1,plot2]):
				if plot.GetEntries()==0: continue
				line = R.TF1('fitline_'+plot.GetName(),'[0]*x',0,10**34)
				line.SetLineColor(plot.GetMarkerColor())
				plot.Fit('fitline_'+plot.GetName())
				fit = plot.GetFunction('fitline_'+plot.GetName())
				# fix me here to get both fit info on plot
				#result = '#color[%s]{#splitline{slope = %.3e #pm %.3e}{#chi^{2}/dof = %5.3f / %2i}}'%(plot.GetMarkerColor(),fit.GetParameter(0),fit.GetParError(0),fit.GetChisquare(),fit.GetNDF())
				#canvas.drawText(text=result,pos=(0.4,0.8 if p==0 else 0.7),align='tl')
		maximum = max(plot1.GetMaximum(),plot2.GetMaximum())
		canvas.firstPlot.SetMaximum(maximum * 1.075)
		canvas.firstPlot.SetMinimum(1E-3 if LOGY else 0.)
		x = 'Luminosity [cm^{-2}s^{-1}]'
		y = 'Counts'+('/pp' if PILEUP and not TDR else '')+('/cm^{2}' if AREA else '')+('/s' if TIME else '/BX')
		canvas.firstPlot.setTitles(X=x, Y=y)
		canvas.makeLegend(pos='tl')
		canvas.makeTransparent()
		if BOB:
			canvas.finishCanvas('BOB')
		else:
			canvas.finishCanvas()
		name = 'luminosity_sep_'+ec+ring+'_'+digi+'_'+when+('_'+HISTNAME if HISTNAME != '' else '')+('_logy' if LOGY else '')+('_fit' if DOFIT else '')
		name = name.replace('+','p')
		name = name.replace('-','m')
		canvas.save(path+'/'+name+'.pdf')
		canvas.deleteCanvas()

#####################
#### Make Plots! ####
#####################


# clone the 'rate' histograms since they're empty
RATES = {plot:{ec+ring:{digi:{half:{when:{} for when in PLOT[digi].keys()} for half in HALVES[digi]} for digi in BXDICT.keys()} for ring in RINGLIST for ec in ECLIST} for plot in ['occ','phi','lumi']}
INTRATES = {digi:{half:{when:{} for when in PLOT[digi].keys()} for half in HALVES[digi]} for digi in PLOT.keys()}
for digi in BXDICT.keys():
	for half in HALVES[digi]:
		for when in PLOT[digi].keys():
			INTRATES[digi][half][when] = {
					'num_comb'  : INT[digi][PLOT[digi][when]['bx'][0]][half]['rate_comb'].Clone(),
					'den_comb'  : INT[digi][PLOT[digi][when]['bx'][0]][half]['rate_comb'].Clone(),
					'rate_comb' : INT[digi][PLOT[digi][when]['bx'][0]][half]['rate_comb'].Clone(),
					'num_sep'  : INT[digi][PLOT[digi][when]['bx'][0]][half]['rate_sep'].Clone(),
					'den_sep'  : INT[digi][PLOT[digi][when]['bx'][0]][half]['rate_sep'].Clone(),
					'rate_sep' : INT[digi][PLOT[digi][when]['bx'][0]][half]['rate_sep'].Clone(),
					}
			INTRATES[digi][half][when]['num_comb'].SetDirectory(0)
			INTRATES[digi][half][when]['den_comb'].SetDirectory(0)
			INTRATES[digi][half][when]['rate_comb'].SetDirectory(0)
			INTRATES[digi][half][when]['num_sep'].SetDirectory(0)
			INTRATES[digi][half][when]['den_sep'].SetDirectory(0)
			INTRATES[digi][half][when]['rate_sep'].SetDirectory(0)
			for ec in ECLIST:
				for ring in RINGLIST:
					# Occupancy totals
					RATES['occ'][ec+ring][digi][half][when] = {
							'num':HISTS[ec+ring][digi][PLOT[digi][when]['bx'][0]][half]['rate'].Clone(),
							'den':0.,# counter not histogram
							'rate':HISTS[ec+ring][digi][PLOT[digi][when]['bx'][0]][half]['rate'].Clone(),
							}
					RATES['occ'][ec+ring][digi][half][when]['num'].SetDirectory(0)
					RATES['occ'][ec+ring][digi][half][when]['rate'].SetDirectory(0)
					# Global phi totals
					RATES['phi'][ec+ring][digi][half][when] = {
							'num':PHI[ec+ring][digi][PLOT[digi][when]['bx'][0]][half]['rate'].Clone(),
							'den':PHI[ec+ring][digi][PLOT[digi][when]['bx'][0]][half]['rate'].Clone(),
							'rate':PHI[ec+ring][digi][PLOT[digi][when]['bx'][0]][half]['rate'].Clone(),
							}
					RATES['phi'][ec+ring][digi][half][when]['num'].SetDirectory(0)
					RATES['phi'][ec+ring][digi][half][when]['den'].SetDirectory(0)
					RATES['phi'][ec+ring][digi][half][when]['rate'].SetDirectory(0)
					# rate vs. lumi totals
					RATES['lumi'][ec+ring][digi][half][when] = {
							'num':LUMI[ec+ring][digi][PLOT[digi][when]['bx'][0]][half]['rate'].Clone(),
							'den':LUMI[ec+ring][digi][PLOT[digi][when]['bx'][0]][half]['rate'].Clone(),
							'rate':LUMI[ec+ring][digi][PLOT[digi][when]['bx'][0]][half]['rate'].Clone(),
							}
					RATES['lumi'][ec+ring][digi][half][when]['num'].SetDirectory(0)
					RATES['lumi'][ec+ring][digi][half][when]['den'].SetDirectory(0)
					RATES['lumi'][ec+ring][digi][half][when]['rate'].SetDirectory(0)

### Normalize and combine Data histograms; then make plot
for ring in RINGLIST:
	for ec in ECLIST:
		for digi in BXDICT.keys():
			### Normalize each half ring individually then add
			# comp : 0 = 'l', 1 = 'r'
			# wire : 0 = 'l', 1 = 'u'
			for when in PLOT[digi].keys():
				for i in [0,1]:
					for bx in PLOT[digi][when]['bx']:
						#################################################################
						# Digi Occupancy
						#################################################################
						# Get number of looks in this BX after gap
						# Total looks in this BX after gap =  number of time bins looked in for this bx after gap * number of lcts in this bx after gap
						nTB = BXDICT[digi][bx]['upper'] - BXDICT[digi][bx]['lower'] + 1
						nLooks = nTB * HISTS[ec+ring][digi][bx][HALVES[digi][i]]['den'].GetEntries()
						# Divide this bx after gap num and den for rate in this bx only (not used at moment)
						HISTS[ec+ring][digi][bx][HALVES[digi][i]]['rate'] = HISTS[ec+ring][digi][bx][HALVES[digi][i]]['num'].Clone()
						HISTS[ec+ring][digi][bx][HALVES[digi][i]]['rate'].Scale(1./nLooks)
						# Add num and dens to totals for this half
						RATES['occ'][ec+ring][digi][HALVES[digi][i]][when]['num'].Add(HISTS[ec+ring][digi][bx][HALVES[digi][i]]['num'])
						RATES['occ'][ec+ring][digi][HALVES[digi][i]][when]['den'] += nLooks
						#################################################################
						# Global Phi
						#################################################################
						# Divide this bx after gap num and den for rate in this bx (den is looks per chamber, not used at moment)
						PHI[ec+ring][digi][bx][HALVES[digi][i]]['rate'] = PHI[ec+ring][digi][bx][HALVES[digi][i]]['num'].Clone()
						PHI[ec+ring][digi][bx][HALVES[digi][i]]['rate'].Divide(PHI[ec+ring][digi][bx][HALVES[digi][i]]['den'])
						# Add num and dens to totals for this half
						RATES['phi'][ec+ring][digi][HALVES[digi][i]][when]['num'].Add(PHI[ec+ring][digi][bx][HALVES[digi][i]]['num'])
						denPhi = PHI[ec+ring][digi][bx][HALVES[digi][i]]['den'].Clone()
						denPhi.Scale(nTB)
						RATES['phi'][ec+ring][digi][HALVES[digi][i]][when]['den'].Add(denPhi)
						#################################################################
						# Hit rate vs. luminosity
						#################################################################
						# Divide this bx after gap num and den for rate in this bx (den is looks per chamber per lumi bin, not used at moment)
						LUMI[ec+ring][digi][bx][HALVES[digi][i]]['rate'] = LUMI[ec+ring][digi][bx][HALVES[digi][i]]['num'].Clone()
						LUMI[ec+ring][digi][bx][HALVES[digi][i]]['rate'].Divide(LUMI[ec+ring][digi][bx][HALVES[digi][i]]['den'])
						# Add num and dens to totals for this half
						RATES['lumi'][ec+ring][digi][HALVES[digi][i]][when]['num'].Add(LUMI[ec+ring][digi][bx][HALVES[digi][i]]['num'])
						denLumi = LUMI[ec+ring][digi][bx][HALVES[digi][i]]['den'].Clone()
						denLumi.Scale(nTB)
						RATES['lumi'][ec+ring][digi][HALVES[digi][i]][when]['den'].Add(denLumi)
						# end bx loop

					#########################################################
					# Divide summed numerators and denomators for each half #
					#########################################################
					RATES['occ'][ec+ring][digi][HALVES[digi][i]][when]['rate'] = RATES['occ'][ec+ring][digi][HALVES[digi][i]][when]['num'].Clone()
					RATES['occ'][ec+ring][digi][HALVES[digi][i]][when]['rate'].Sumw2()
					RATES['occ'][ec+ring][digi][HALVES[digi][i]][when]['rate'].Scale(1./RATES['occ'][ec+ring][digi][HALVES[digi][i]][when]['den'])

					RATES['phi'][ec+ring][digi][HALVES[digi][i]][when]['rate'] = RATES['phi'][ec+ring][digi][HALVES[digi][i]][when]['num'].Clone()
					RATES['phi'][ec+ring][digi][HALVES[digi][i]][when]['rate'].Sumw2()
					RATES['phi'][ec+ring][digi][HALVES[digi][i]][when]['rate'].Divide(RATES['phi'][ec+ring][digi][HALVES[digi][i]][when]['den'])

					RATES['lumi'][ec+ring][digi][HALVES[digi][i]][when]['rate'] = RATES['lumi'][ec+ring][digi][HALVES[digi][i]][when]['num'].Clone()
					RATES['lumi'][ec+ring][digi][HALVES[digi][i]][when]['rate'].Sumw2()
					RATES['lumi'][ec+ring][digi][HALVES[digi][i]][when]['rate'].Divide(RATES['lumi'][ec+ring][digi][HALVES[digi][i]][when]['den'])
					# end half loop

				################################################################
				# Sum each half into total
				# HALVES[digi][0][0:2] = ['l','l'] : Left and Lower
				# HALVES[digi][1][0:2] = ['r','u'] : Right and Upper
				################################################################
				RATES['occ'][ec+ring][digi]['a'][when]['rate'] = RATES['occ'][ec+ring][digi][HALVES[digi][0]][when]['rate'].Clone()
				RATES['occ'][ec+ring][digi]['a'][when]['rate'].Add(RATES['occ'][ec+ring][digi][HALVES[digi][1]][when]['rate'])

				RATES['phi'][ec+ring][digi]['a'][when]['rate'] = RATES['phi'][ec+ring][digi][HALVES[digi][0]][when]['rate'].Clone()
				RATES['phi'][ec+ring][digi]['a'][when]['rate'].Add(RATES['phi'][ec+ring][digi][HALVES[digi][1]][when]['rate'])

				RATES['lumi'][ec+ring][digi]['a'][when]['rate'] = RATES['lumi'][ec+ring][digi][HALVES[digi][0]][when]['rate'].Clone()
				RATES['lumi'][ec+ring][digi]['a'][when]['rate'].Add(RATES['lumi'][ec+ring][digi][HALVES[digi][1]][when]['rate'])

				################
				## Make plots ##
				################
				# Hit Rate vs. Luminosity Plots
#				if MC=='':
#					fit = [False]
#					if DOFIT: fit.append(True)
#					for dofit in fit:
#						makeLuminosityPlot(RATES['lumi'][ec+ring][digi]['a'][when]['rate'].Clone(), digi, when, ec, ring, dofit)
#						makeSepLumiPlot(RATES['lumi'][ec+ring][digi][HALVES[digi][0]][when]['rate'].Clone(),
#							RATES['lumi'][ec+ring][digi][HALVES[digi][1]][when]['rate'].Clone(), digi, when, ec, ring, dofit)
				# Chamber Digi Occupancy and Global Phi Plots
				for mc in MCLIST:
					makeOccupancyPlot(RATES['occ'][ec+ring][digi]['a'][when]['rate'].Clone(),digi,when,ec,ring,mc)
					makePhiPlot(RATES['phi'][ec+ring][digi]['a'][when]['rate'].Clone(),digi,when,ec,ring,mc)
				# debug!
#				if DOLOG:
#					lumberjack.occLogger(occLog,RATES['occ'][ec+ring][digi]['a'][when]['rate'].Clone(),areaHists[digi][ring],digi,when,ec,ring,PILEUP)
#					lumberjack.lumiLogger(lumiLog,RATES['lumi'][ec+ring][digi]['a'][when]['rate'].Clone(),chamArea[digi][ring],digi,when,ec,ring,PILEUP)
#					lumberjack.lumiHalfLogger(lumiHalfLog,RATES['lumi'][ec+ring][digi][HALVES[digi][0]][when]['rate'].Clone(),
#							chamHalfArea[digi][HALVES[digi][0]][ring],digi,when,ec,ring,PILEUP,half=HALVES[digi][0])
#					lumberjack.lumiHalfLogger(lumiHalfLog,RATES['lumi'][ec+ring][digi][HALVES[digi][1]][when]['rate'].Clone(),
#							chamHalfArea[digi][HALVES[digi][1]][ring],digi,when,ec,ring,PILEUP,half=HALVES[digi][1])
#					lumberjack.phiLogger(phiLog,RATES['phi'][ec+ring][digi]['a'][when]['rate'].Clone(),chamArea[digi][ring],digi,when,ec,ring,PILEUP)
				# end when loop

##########################
### Make Integral Plot ###
##########################
for digi in PLOT.keys():
	for when in PLOT[digi].keys():
		for ectype in ectypelist:
			for half in HALVES[digi][0:2]:
				for bx in PLOT[digi][when]['bx']:
					# Combine numerator
					INTRATES[digi][half][when]['num_'+ectype].Add(INT[digi][bx][half]['num_'+ectype])
					# Scale by num_combber of time bins considered and combine
					nTB = BXDICT[digi][bx]['upper'] - BXDICT[digi][bx]['lower'] + 1
					denInt = INT[digi][bx][half]['den_'+ectype].Clone()
					denInt.Scale(nTB)
					INTRATES[digi][half][when]['den_'+ectype].Add(denInt)
				# Separate_combly normalize left-right and lower-upper
				INTRATES[digi][half][when]['rate_'+ectype] = INTRATES[digi][half][when]['num_'+ectype].Clone()
				INTRATES[digi][half][when]['rate_'+ectype].Divide(INTRATES[digi][half][when]['den_'+ectype])
			# Add halves together
			INTRATES[digi]['a'][when]['rate_'+ectype] = INTRATES[digi][HALVES[digi][0]][when]['rate_'+ectype].Clone()
			INTRATES[digi]['a'][when]['rate_'+ectype].Add(INTRATES[digi][HALVES[digi][1]][when]['rate_'+ectype])
			if DOLOG: lumberjack.intLogger(intLog,INTRATES[digi]['a'][when]['rate_'+ectype].Clone(),chamArea[digi],digi,when,ectype,PILEUP)
			for mc in MCLIST:
				makeIntegralPlot(INTRATES[digi]['a'][when]['rate_'+ectype].Clone(),digi,when,ectype,mc)
