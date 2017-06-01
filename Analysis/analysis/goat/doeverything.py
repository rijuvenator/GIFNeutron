import sys, os, argparse, math
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
R.gROOT.SetBatch(True)
# area histograms calculated on the fly
import areas as areas
areaHists = areas.areaHists

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
if GEO=='' and MC!='':
	print 'Choose a geometry'
	exit()

# Which time bins to use in each BX
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
# Which BXs to use in each plot
# format:
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
# User input limits of plots
LIMITS = {
		'int':{
			'early':{
				'wire':0.0052,
				'comp':0.004,
			},
			'late':{
				'wire':0.0052,
				'comp':0.004,
			},
			'total':{
				'wire':0.0052,
				'comp':0.004,
			},
		},
		'occ':{
			'early':{
				'comp':{
					'11':50e-6,
					'12':12e-6,
					'13':15e-6,
					'21':45e-6,
					'22':10e-6,
					'31':30e-6,
					'32':15e-6,
					'41':30e-6,
					'42':25e-6,
					},
				'wire':{
					'11':0.2e-3,
					'12':12e-6,
					'13':16e-6,
					'21':0.08e-3,
					'22':26e-6,
					'31':0.08e-3,
					'32':40e-6,
					'41':0.06e-3,
					'42':0.05e-3,
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
					'22':0.0012,
					'32':0.001,
					'42':0.0025,
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

### Set permenant dictionaries
RINGLIST = ['42', '41', '32', '31', '22', '21', '13', '12', '11']
ERINGLIST = ['-42','-41','-32','-31','-22','-21','-13','-12','-11',
			 '+11','+12','+13','+21','+22','+31','+32','+41','+42']
ECLIST = ['','+','-']
HALVES = {
		'comp':['l','r','a'],
		'wire':['l','u','a'],
		}

#####################################
### Get/make occupancy histograms ###
#####################################

if RECREATE:
	# Get Tree
	if DOROADS:
		FILE = R.TFile.Open('/afs/cern.ch/work/a/adasgupt/public/goatees/GOAT_P5.root')
	else:
		FILE = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/goatees/GOAT_P5_noTrackRemoval_good.root')
	tree = FILE.Get('t')
	### Set Histograms
	FOUT = R.TFile('root/occupancy'+('_'+NAME if NAME != '' else '')+'.root','RECREATE')
	FOUT.cd()
	HISTS = {ec+ring:{digi:{bx:{half:{} for half in HALVES[digi]} for bx in BXDICT[digi].keys()} for digi in BXDICT.keys()} for ring in RINGLIST for ec in ECLIST}
	PHI = {ec+ring:{digi:{bx:{half:{} for half in HALVES[digi]} for bx in BXDICT[digi].keys()} for digi in BXDICT.keys()} for ring in RINGLIST for ec in ECLIST}
	LUMI = {ec+ring:{digi:{bx:{half:{} for half in HALVES[digi]} for bx in BXDICT[digi].keys()} for digi in BXDICT.keys()} for ring in RINGLIST for ec in ECLIST}
	lumiBins = 30
	maxLumi = 1.5e34
	for ring in RINGLIST:
		for ec in ECLIST:
			cham = CH.Chamber(CH.serialID(1, int(ring[0]), int(ring[1]), 1))
			nhs = cham.nstrips*2
			nwg = cham.nwires
			for digi in PLOT.keys():
				lim = nhs+2 if digi=='comp' else nwg+2
				for half in HALVES[digi]:
					for bx in BXDICT[digi].keys():
						# Set occupancy histograms
						HISTS[ec+ring][digi][bx][half] = {
								'num':R.TH1D('num_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx),'',  lim,0,lim),
								'den':R.TH1D('den_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx),'',  1,0,1),
								'rate':R.TH1D('rate_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx),'',  lim,0,lim),
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
					# weight each event by pileup to get per pp-collision
					pileup = 1./entry.PILEUP if PILEUP else 1.
					# area of each wg/hs for 6 layers in cm^2
					binnum = entry.D_POS[idigi] if digi=='wire' else entry.D_POS[idigi]+1 # add one for comp hs which count from 0
					area = 1./areaHists[digi][ring].GetBinContent(binnum) if AREA else 1.
					# convert per 25 ns to per s
					time = 1./(25.*10**(-9)) if TIME else 1.
					# weight
					weight = pileup*area*time
					# Fill occupancy numerator
					HISTS[ecr][digi][entry.BX][half]['num'].Fill(entry.D_POS[idigi],weight)
					HISTS[ring][digi][entry.BX][half]['num'].Fill(entry.D_POS[idigi],weight)
					# Fill global phi numerator
					PHI[ecr][digi][entry.BX][half]['num'].Fill(entry.CHAM,weight)
					PHI[ring][digi][entry.BX][half]['num'].Fill(entry.CHAM,weight)
					# Fill luminosity numerator
					LUMI[ecr][digi][entry.BX][half]['num'].Fill(entry.LUMI,weight)
					LUMI[ring][digi][entry.BX][half]['num'].Fill(entry.LUMI,weight)
			# Fill occupancy denominator
			HISTS[ecr][digi][entry.BX][half]['den'].Fill(0,1.)
			HISTS[ring][digi][entry.BX][half]['den'].Fill(0,1.)
			# Fill global phi denominator
			PHI[ecr][digi][entry.BX][half]['den'].Fill(entry.CHAM,1.)
			PHI[ring][digi][entry.BX][half]['den'].Fill(entry.CHAM,1.)
			# Fill luminosity denominator
			LUMI[ecr][digi][entry.BX][half]['den'].Fill(entry.LUMI,1.)
			LUMI[ring][digi][entry.BX][half]['den'].Fill(entry.LUMI,1.)

	# Write histograms to output file
	FOUT.cd()
	for ring in RINGLIST:
		for ec in ECLIST:
			for digi in BXDICT.keys():
				for half in HALVES[digi]:
					for bx in BXDICT[digi].keys():
						for TYPE in ['num','den','rate']:
							HISTS[ec+ring][digi][bx][half][TYPE].Write()
							PHI[ec+ring][digi][bx][half][TYPE].Write()
							LUMI[ec+ring][digi][bx][half][TYPE].Write()
else:
	# Get histograms from already created output file
	HISTS = {ec+ring:{digi:{bx:{half:{} for half in HALVES[digi]} for bx in BXDICT[digi].keys()} for digi in BXDICT.keys()} for ring in RINGLIST for ec in ECLIST}
	PHI = {ec+ring:{digi:{bx:{half:{} for half in HALVES[digi]} for bx in BXDICT[digi].keys()} for digi in BXDICT.keys()} for ring in RINGLIST for ec in ECLIST}
	LUMI = {ec+ring:{digi:{bx:{half:{} for half in HALVES[digi]} for bx in BXDICT[digi].keys()} for digi in BXDICT.keys()} for ring in RINGLIST for ec in ECLIST}
	FOUT = R.TFile.Open('root/occupancy'+('_'+NAME if NAME != '' else '')+'.root','READ')
	for ring in RINGLIST:
		for ec in ECLIST:
			for digi in BXDICT.keys():
				for half in HALVES[digi]:
					for bx in BXDICT[digi].keys():
						# Get occupancy histograms
						HISTS[ec+ring][digi][bx][half] = {
								'num' :FOUT.Get('num_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx)).Clone(),
								'den' :FOUT.Get('den_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx)).Clone(),
								'rate':FOUT.Get('rate_'+ec+ring+'_'+digi+'_'+half+'_'+str(bx)).Clone(),
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

### Normalize MC histograms
# Number of events in each MC file
# I make this to be user input, but it doesn't have to be
MCNORM = {
		'HP_Thermal_ON':102100.,
		'HP_Thermal_OFF':98250.,
		'XS_Thermal_ON':99000.,
		'XS_Thermal_OFF':100000.,
		'XS_ThermalOFF':100000.,
		}

# Set MC
if MC=='':
	MCLIST = ['']
elif MC=='all':
	MCLIST = ['XS_ThermalON','XS_ThermalOFF','HP_Thermal_ON','HP_ThermalOFF']
else:
	MCLIST = [MC]

if MC:
	MCHISTS = {mc:{ec+ring:{digi:{} for digi in PLOT.keys()} for ec in ECLIST for ring in RINGLIST} for mc in MCLIST}
	for mc in MCLIST:
		mcName = mc+'_TOF'+'_'+GEO+('_AREA' if AREA else '')+('_TIME' if TIME else '')+('_'+EXTRA if EXTRA!='' else '')
		FMC = R.TFile.Open('root/hists_'+mcName+'.root')
		print 'root/hists_'+mcName+'.root'
		for ring in RINGLIST:
			for ec in ECLIST:
				for digi in PLOT.keys():
					# Get histos
					MCHISTS[mc][ec+ring][digi] = {
							'occ' : FMC.Get(ec+ring+'_'+digi+'_occ').Clone(),
							'phi' : FMC.Get('phi_'+ec+ring+'_'+digi+'_occ').Clone(),
							}
					MCHISTS[mc][ec+ring][digi]['occ'].SetDirectory(0)
					MCHISTS[mc][ec+ring][digi]['phi'].SetDirectory(0)
					# Scale MC to the number of pp collisions generated in each MC
					MCHISTS[mc][ec+ring][digi]['occ'].Scale(1./MCNORM[mc])
					MCHISTS[mc][ec+ring][digi]['phi'].Scale(1./MCNORM[mc])
					# Scale to a single chamber 
					if ring in ['21','31','41']:
						if ec=='':
							ncham = 36.
						else:
							ncham = 18.
					else:
						if ec=='':
							ncham = 72.
						else:
							ncham = 36.
					MCHISTS[mc][ec+ring][digi]['occ'].Scale(1./ncham)
					if ec=='':
						MCHISTS[mc][ec+ring][digi]['phi'].Scale(1./2)
					else:
						MCHISTS[mc][ec+ring][digi]['phi'].Scale(1.)

###########################
### Make plot functions ###
###########################

def makeOccupancyPlot(dataHist,digi,when,ec,ring,mc):
	# Make occupancy plot for each digi and plot type
	dataPlot = Plotter.Plot(dataHist.Clone(),option='p',legType='p',legName='Data')
	title = 'ME'+ec+ring+' '+('Comparator ' if digi=='comp' else 'Wire Group ')+'Occupancy'
	# Make MC plot
	if mc!='':
		mcname = mc.replace('_',' ')
		mchist = MCHISTS[mc][ec+ring][digi]['occ'].Clone()
		mcPlot = Plotter.Plot(mchist,legType='f',option='hist',legName=mcname)
	for LOGY in [False]:#,True]:
		if mc!='':
			mcname = mc.replace('_',' ')
			TITLE = mcname
		else:
			TITLE = title
		canvas = Plotter.Canvas(lumi=TITLE,logy=LOGY)
		if mc!='':
			canvas.addMainPlot(mcPlot)
			mcPlot.SetFillColor(R.kOrange)
		canvas.addMainPlot(dataPlot)
		if mc!='':
			canvas.makeLegend(pos='tr')
			canvas.legend.moveLegend(X=-0.2)
			canvas.legend.resizeHeight()
			canvas.drawText('MC integral : {:1.4f}'.format(mcPlot.Integral()),pos=(0.6,0.7))
		mcMax = mcPlot.GetMaximum() if mc!='' else 0.
		maximum = max(dataPlot.GetMaximum(),mcMax)
		if ring in LIMITS['occ'][when][digi].keys():
			canvas.firstPlot.SetMaximum(LIMITS['occ'][when][digi][ring])
		else: # set maximum dynamically
			canvas.firstPlot.SetMaximum(maximum * 1.2)
		canvas.firstPlot.SetMinimum(1e-2 if LOGY else 0.)
		x = 'Comparator Half Strip' if digi=='comp' else 'Wire Group Number'
		y = 'Counts'
		if AREA:
			y += '/cm^{2}'
		if TIME:
			y += '/s'
		else:
			y += '/BX'
		canvas.firstPlot.setTitles(X=x, Y=y)
		canvas.drawText('Data integral : {:1.4f}'.format(dataPlot.Integral()),pos=(0.6,0.6))
		canvas.firstPlot.scaleTitleOffsets(1.2,'Y')
		canvas.makeTransparent()
		canvas.finishCanvas('BOB')
		name = 'occupancy_'+ec+ring+'_'+digi+'_'+when+('_'+HISTNAME if HISTNAME!= '' else '')+('_logy' if LOGY else '')+('_'+mc if mc!='' else '')
		name = name.replace('+','p')
		name = name.replace('-','m')
		canvas.save('pdfs/'+name+'.pdf')
		canvas.deleteCanvas()

def makePhiPlot(dataHist,digi,when,ec,ring,mc):
	# Make occupancy plot for each digi and plot type
	dataPlot = Plotter.Plot(dataHist.Clone(),option='p',legName='Data',legType='p')
	TITLE = 'ME'+ec+ring+' '+('Comparator ' if digi=='comp' else 'Wire Group ')+'Occupancy per Chamber'
	# Make MC plot
	if mc!='':
		mcname = mc.replace('_',' ')
		mchist = MCHISTS[mc][ec+ring][digi]['phi'].Clone()
		mcPlot = Plotter.Plot(mchist,legType='f',option='hist',legName=mcname)
	for LOGY in [False]:#,True]:
		canvas = Plotter.Canvas(lumi=TITLE,logy=LOGY)
		if mc!='':
			canvas.addMainPlot(mcPlot)
			mcPlot.SetFillColor(R.kOrange)
		canvas.addMainPlot(dataPlot,addToPlotList=False)
		if mc!='':
			canvas.makeLegend(pos='tr')
			canvas.legend.moveLegend(X=-0.2)
			canvas.legend.resizeHeight()
			canvas.drawText('MC integral : {:1.4f}'.format(mcPlot.Integral()),pos=(0.6,0.7))
		mcMax = mcPlot.GetMaximum() if mc!='' else 0.
		maximum = max(dataPlot.GetMaximum(),mcMax)
		if ring in LIMITS['phi'][when][digi].keys():
				canvas.firstPlot.SetMaximum(LIMITS['phi'][when][digi][ring])
		else: # set maximum dynamically
			canvas.firstPlot.SetMaximum(maximum * 1.2)
		canvas.firstPlot.SetMinimum(1e-2 if LOGY else 0.)
		x = 'CSC Chamber'
		y = 'Counts/cm^{2}/s' if AREA else 'Counts/BX'
		canvas.firstPlot.setTitles(X=x, Y=y)
		canvas.firstPlot.scaleTitleOffsets(1.2,'Y')
		canvas.drawText('Data integral : {:1.4f}'.format(dataPlot.Integral()),pos=(0.6,0.6))
		canvas.makeTransparent()
		canvas.finishCanvas('BOB')
		name = 'phi_'+ec+ring+'_'+digi+'_'+when+('_'+HISTNAME if HISTNAME != '' else '')+('_logy' if LOGY else '')+('_'+mc if mc!='' else '')
		name = name.replace('+','p')
		name = name.replace('-','m')
		canvas.save('pdfs/'+name+'.pdf')
		canvas.deleteCanvas()

def makeIntegralPlot(dataHist,digi,when,mc):
	# Make integral plot for each digi and plot type
	dataPlot = Plotter.Plot(dataHist.Clone(),option='p',legType='p',legName='Data')
	title = ('Comparator ' if digi=='comp' else 'Wire Group ')+'Integral Occupancy'
	# Make MC Plot
	if mc!='':
		integralMC   = R.TH1D('integralMC_'+digi+'_mc','',18,0,18)
		for b,ering in enumerate(ERINGLIST):
			# MC
			totalMC = MCHISTS[mc][ering][digi]['occ'].Clone()
			integralMC.SetBinContent(b+1,totalMC.Integral())
			integralMC.GetXaxis().SetBinLabel(b+1,ering.replace('-','#minus'))
		mcname = mc.replace('_',' ')
		mcPlot = Plotter.Plot(integralMC,option='hist',legName=mcname,legType='f')
	for LOGY in [False]:#True]:
		if mc!='':
			mcname = mc.replace('_',' ')
			TITLE = mcname
		else:
			TITLE = title
		canvas = Plotter.Canvas(lumi=TITLE,logy=LOGY)
		if mc!='': 
			canvas.addMainPlot(mcPlot)
			mcPlot.SetFillColor(R.kOrange)
		canvas.addMainPlot(dataPlot)
		if mc!='':
			canvas.makeLegend(pos='tr')
			canvas.legend.moveLegend(X=-0.2)
			canvas.legend.resizeHeight()
		#canvas.firstPlot.SetMaximum(0.0052 if digi=='wire' else 0.004)
		if digi in LIMITS['int'][when].keys():
			canvas.firstPlot.SetMaximum(LIMITS['int'][when][digi])
		else: # set maximum dynamically
			mcMax = mcPlot.GetMaximum() if mc!='' else 0.
			maximum = max(dataPlot.GetMaximum(),mcMax)
			canvas.firstPlot.SetMaximum(maximum * 1.1)
		canvas.firstPlot.SetMinimum(1e-2 if LOGY else 0.)
		x = 'CSC Ring'
		for ibin,ring in enumerate(ERINGLIST):
			canvas.firstPlot.GetXaxis().SetBinLabel(ibin+1, ring.replace('-','#minus'))
		y = 'Counts/cm^{2}/s' if AREA else 'Counts/BX'
		canvas.firstPlot.setTitles(Y=y)
		canvas.firstPlot.scaleTitleOffsets(1.2,'Y')
		canvas.makeTransparent()
		canvas.finishCanvas('BOB')
		name = 'integral_'+digi+'_'+when+('_'+HISTNAME if HISTNAME != '' else '')+('_logy' if LOGY else '')+('_'+mc if mc!='' else '')
		canvas.save('pdfs/'+name+'.pdf')
		canvas.deleteCanvas()

def makeLuminosityPlot(dataHist,digi,when,ec,ring):
	# Make occupancy plot for each digi and plot type
	dataPlot = Plotter.Plot(dataHist.Clone(),option='p')
	TITLE = 'ME'+ec+ring+' '+('Comparator ' if digi=='comp' else 'Wire Group ')+'Occupancy'
	for LOGY in [False]:#,True]:
		canvas = Plotter.Canvas(lumi=TITLE,logy=LOGY)
		canvas.addMainPlot(dataPlot,addToPlotList=False)
		canvas.firstPlot.SetMinimum(1e-2 if LOGY else 0.)
		x = 'Luminosity [cm^{-2}s^{-1}]'
		y = 'Counts/cm^{2}/s' if AREA else 'Counts/BX'
		canvas.firstPlot.setTitles(X=x, Y=y)
		canvas.firstPlot.scaleTitleOffsets(1.2,'Y')
		canvas.makeTransparent()
		canvas.finishCanvas('BOB')
		name = 'luminosity_'+ec+ring+'_'+digi+'_'+when+('_'+HISTNAME if HISTNAME != '' else '')+('_logy' if LOGY else '')
		name = name.replace('+','p')
		name = name.replace('-','m')
		canvas.save('pdfs/'+name+'.pdf')
		canvas.deleteCanvas()

def makeSepPlot(hist1,hist2,digi,when,ec,ring):
	# Make counts vs. luminosity plots for each half separately and plot them on 
	# the same axis
	plot1 = Plotter.Plot(hist1,legType='p',legName='Upper half' if digi=='wire' else 'Right half',option='p')
	plot2 = Plotter.Plot(hist2,legType='p',legName='Lower half' if digi=='wire' else 'Left half',option='p')
	TITLE = 'ME'+ring+(' Wire Group Rate ' if digi=='wire' else ' Comparator Rate ')+'vs. Luminosity'
	for LOGY in [False]:#,True]:
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
		name = 'luminosity_sep_'+ec+ring+'_'+digi+'_'+when+('_'+HISTNAME if HISTNAME != '' else '')+('_logy' if LOGY else '')
		name = name.replace('+','p')
		name = name.replace('-','m')
		canvas.save('pdfs/'+name+'.pdf')
		canvas.deleteCanvas()

#####################
#### Make Plots! ####
#####################

### Normalize and combine Data histograms; then make plot
for ring in RINGLIST:
	for ec in ECLIST:
		for digi in BXDICT.keys():
			for bx in BXDICT[digi].keys():
				################################
				### Normalize occupancy plot ###
				################################
				for i in [0,1]:
					### Normalize each half ring individually then add
					# comp : 0 = 'l', 1 = 'r'
					# wire : 0 = 'l', 1 = 'u'
					#################################################################
					HISTS[ec+ring][digi][bx][HALVES[digi][i]]['num'].Sumw2()
					HISTS[ec+ring][digi][bx][HALVES[digi][i]]['den'].Sumw2()
					# Normalize each half individually
					HISTS[ec+ring][digi][bx][HALVES[digi][i]]['rate'].Add(HISTS[ec+ring][digi][bx][HALVES[digi][i]]['num'])
					HISTS[ec+ring][digi][bx][HALVES[digi][i]]['rate'].Scale(1./HISTS[ec+ring][digi][bx][HALVES[digi][i]]['den'].GetEntries())
					# Add to normalized histogram to total
					HISTS[ec+ring][digi][bx]['a']['rate'].Add(HISTS[ec+ring][digi][bx][HALVES[digi][i]]['rate'])
					#################################################################
					PHI[ec+ring][digi][bx][HALVES[digi][i]]['num'].Sumw2()
					PHI[ec+ring][digi][bx][HALVES[digi][i]]['den'].Sumw2()
					# Normalize each half individually
					PHI[ec+ring][digi][bx][HALVES[digi][i]]['rate'].Add(PHI[ec+ring][digi][bx][HALVES[digi][i]]['num'])
					PHI[ec+ring][digi][bx][HALVES[digi][i]]['rate'].Divide(PHI[ec+ring][digi][bx][HALVES[digi][i]]['den'])
					# Add to normalized histogram to total
					PHI[ec+ring][digi][bx]['a']['rate'].Add(PHI[ec+ring][digi][bx][HALVES[digi][i]]['rate'])
					#################################################################
					LUMI[ec+ring][digi][bx][HALVES[digi][i]]['num'].Sumw2()
					LUMI[ec+ring][digi][bx][HALVES[digi][i]]['den'].Sumw2()
					# Normalize each half individually
					LUMI[ec+ring][digi][bx][HALVES[digi][i]]['rate'].Add(LUMI[ec+ring][digi][bx][HALVES[digi][i]]['num'])
					LUMI[ec+ring][digi][bx][HALVES[digi][i]]['rate'].Divide(LUMI[ec+ring][digi][bx][HALVES[digi][i]]['den'])
					# Add to normalized histogram to total
					LUMI[ec+ring][digi][bx]['a']['rate'].Add(LUMI[ec+ring][digi][bx][HALVES[digi][i]]['rate'])
					#################################################################
			################
			## Make plots ##
			################
			for when in PLOT[digi].keys():
				# Clone the first bx for this plot type
				total  = HISTS[ec+ring][digi][PLOT[digi][when]['bx'][0]]['a']['rate'].Clone()
				totalphi = PHI[ec+ring][digi][PLOT[digi][when]['bx'][0]]['a']['rate'].Clone()
				totallumi =   LUMI[ec+ring][digi][PLOT[digi][when]['bx'][0]]['a']['rate'].Clone()
				totallumiLL = LUMI[ec+ring][digi][PLOT[digi][when]['bx'][0]][HALVES[digi][0]]['rate'].Clone()
				totallumiRU = LUMI[ec+ring][digi][PLOT[digi][when]['bx'][0]][HALVES[digi][1]]['rate'].Clone()
				# Add in the rest of the bx
				if len(PLOT[digi][when]['bx'])>1:
					for i,bx in enumerate(PLOT[digi][when]['bx'][1:]):
						total.Add( HISTS[ec+ring][digi][bx]['a']['rate'])
						totalphi.Add(PHI[ec+ring][digi][bx]['a']['rate'])
						totallumi.Add(LUMI[ec+ring][digi][bx]['a']['rate'])
						totallumiLL.Add(LUMI[ec+ring][digi][bx][HALVES[digi][0]]['rate'])
						totallumiRU.Add(LUMI[ec+ring][digi][bx][HALVES[digi][1]]['rate'])
				# Scale by number of time bins added together
				total.Scale(   1./PLOT[digi][when]['tb'])
				totalphi.Scale(1./PLOT[digi][when]['tb'])
				totallumi.Scale(1./PLOT[digi][when]['tb'])
				totallumiLL.Scale(1./PLOT[digi][when]['tb'])
				totallumiRU.Scale(1./PLOT[digi][when]['tb'])
				###########################
				## Make Luminosity Plots ##
				###########################
				if MC=='':
					makeLuminosityPlot(totallumi,digi,when,ec,ring)
					makeSepPlot(totallumiRU,totallumiLL,digi,when,ec,ring)
				##############################
				## Make Occupancy/Phi Plots ##
				##############################
				for mc in MCLIST:
					makeOccupancyPlot(total,digi,when,ec,ring,mc)
					makePhiPlot(totalphi,digi,when,ec,ring,mc)

##########################
### Make Integral Plot ###
##########################
for digi in PLOT.keys():
	for when in PLOT[digi].keys():
		integralData = R.TH1D('integralData_'+digi+'_'+when,'',18,0,18)
		print '***', when
		for b,ring in enumerate(ERINGLIST):
			### Clone the first bx for this plot
			total   = HISTS[ring][digi][PLOT[digi][when]['bx'][0]]['a']['rate'].Clone()
			totalLL = HISTS[ring][digi][PLOT[digi][when]['bx'][0]][HALVES[digi][0]]['rate'].Clone()
			totalRU = HISTS[ring][digi][PLOT[digi][when]['bx'][0]][HALVES[digi][1]]['rate'].Clone()
			# Add in the rest
			if len(PLOT[digi][when]['bx'])>1:
				for i,bx in enumerate(PLOT[digi][when]['bx'][1:]):
					total.Add(HISTS[ring][digi][bx]['a']['rate'])
					totalLL.Add(HISTS[ring][digi][bx][HALVES[digi][0]]['rate'])
					totalRU.Add(HISTS[ring][digi][bx][HALVES[digi][1]]['rate'])
			# Scale by number of time bins added together
			total.Scale(1./PLOT[digi][when]['tb'])
			# Set integralData contents and labels
			integ = total.Integral()
			integralData.SetBinContent(b+1,integ)
			errLL2 = 1./totalLL.GetEntries() if totalLL.GetEntries()>0 else 0
			errRU2 = 1./totalRU.GetEntries() if totalRU.GetEntries()>0 else 0
			err = integ * math.sqrt( errLL2 + errRU2 )
			integralData.SetBinError(b+1,err)
			integralData.GetXaxis().SetBinLabel(b+1,ring.replace('-','#minus'))
			print '***', ring, integ, err
		for mc in MCLIST:
			makeIntegralPlot(integralData,digi,when,mc)
