'''
Script meant to combine the outputs of :
	- wire/BGWire.py and wire/BGWire_MC.py
	- comp/BGComp.py and comp/BGComp_MC.py

Wire group and comparator hit occupancy plots are normalized in this script
as well. Comparator hit cumulative occupancy plots are also made.

Current normalization procedure is to normalize the l/r comparator hit 
and t/b wire group hit plots to the number of "looks" in each half 
chamber individually. This produces a per BX rate.

The MC is normalized to the number of events generated in the sample
which is equivalent to being a per BX rate. (Number of generated
events must be put in by hand.)

Plots are made for each ring individually.

Usage : python mcdata.py
'''
import sys, os, argparse
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi
import Gif.Analysis.roottools as roottools
import logging
R.gROOT.SetBatch(True)

RINGLIST = ['11', '12', '13', '21', '22', '31', '32', '41', '42']
ULRINGLIST = [i+'u' for i in RINGLIST] + [i+'l' for i in RINGLIST]

dataDict = {
		'comp': {
			#'file' : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/comp/BGComp_P5_bgdigitest.root',
			'file' : '../comp/BGComp_P5.root',
			'hists' : {},
		},
		'wire' : {
			'file' : '../wire/BGWire_P5.root',
			'hists' : {},
		}
}
mcDict = {
	'comp': {
		#'HP_ThermalON' : {
		#	'file'  : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/comp/BGComp_MC_bgdigitest.root',
		#	'nEvts' : 25000.,
		#	'hists' : {},
		#},
#		'HP_ThermalON' : {
#			'file'  : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/comp/BGComp_MC_HP_ON.root',
#			'nEvts' : 102100.,
#			'hists' : {},
#		},
#		'HP_ThermalOFF' : {
#			'file'  : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/comp/BGComp_MC_HP_OFF.root',
#			'nEvts' : 96250.,
#			'hists' : {},
#		},
#		'XS_ThermalON' : {
#			'file'  : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/comp/BGComp_MC_XS_ON.root',
#			'nEvts' : 100000.,
#			'hists' : {},
#		},
#		'XS_ThermalOFF' : {
#			'file'  : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/comp/BGComp_MC_XS_OFF.root',
#			'nEvts' : 99000.,
#			'hists' : {},
#		},
		'DigiHack' : {
			'file'  : '../comp/BGComp_MC_HP_ON_NomTOF.root',
			'nEvts' : 25000.,
			'hists' : {},
		},
	},
	'wire': {
		#'HP_ThermalON' : {
		#	'file'  : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/wire/BGWire_MC_bgdigitest.root',
		#	'nEvts' : 25000.,
		#	'hists' : {},
		#},
#		'HP_ThermalON' : {
#			'file'  : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/wire/BGWire_MC_HP_ON.root',
#			'nEvts' : 102100.,
#			'hists' : {},
#		},
#		'HP_ThermalOFF' : {
#			'file'  : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/wire/BGWire_MC_HP_OFF.root',
#			'nEvts' : 96250.,
#			'hists' : {},
#		},
#		'XS_ThermalON' : {
#			'file'  : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/wire/BGWire_MC_XS_ON.root',
#			'nEvts' : 100000.,
#			'hists' : {},
#		},
#		'XS_ThermalOFF' : {
#			'file'  : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/wire/BGWire_MC_XS_OFF.root',
#			'nEvts' : 100000.,
#			'hists' : {},
#		},
		'DigiHack' : {
			'file'  : '../wire/BGWire_MC_HP_ON_NomTOF.root',
			'nEvts' : 25000.,
			'hists' : {},
		}
	},
}

########################
# Load Data Histograms #
########################

def loadCompData(dataDict):
	''' Load in comparator hit data histograms
		- assumes that dataDict is dataDict['comp']
	'''
	fdata = R.TFile.Open(dataDict['file'])
	for ring in RINGLIST:
		for half in ['l','r','']:
			dataDict['hists'][ring+half] = {
				#'time' : fdata.Get('t'+ring+half),
				#'lumi' : fdata.Get('l'+ring+half),
				#'totl' : fdata.Get('a'+ring+half),
				'occ'  : fdata.Get('o'+ring+half),
				'lct'  : fdata.Get('lct'+ring+half),
			}
			#dataDict['hists'][ring+half]['time'].SetDirectory(0)
			#dataDict['hists']['lumi'].SetDirectory(0)
			#dataDict['hists']['totl'].SetDirectory(0)
			dataDict['hists'][ring+half]['occ'].SetDirectory(0)
			dataDict['hists'][ring+half]['lct'].SetDirectory(0)

def loadWireData(dataDict):
	''' Load in wire group data histograms
		- assumes that dataDict is dataDict['wire']
	'''
	fdata = R.TFile.Open(dataDict['file'])
	for ring in ULRINGLIST:
		dataDict['hists'][ring] = {
			#'time' : fdata.Get('t'+ring),
			#'lumi' : fdata.Get('l'+ring),
			#'totl' : fdata.Get('a'+ring),
			'occ'  : fdata.Get('o'+ring),
			'lct'  : fdata.Get('lct'+ring),
		}
		#dataDict['hists'][ring]['time'].SetDirectory(0)
		#dataDict['hists']['lumi'].SetDirectory(0)
		#dataDict['hists']['totl'].SetDirectory(0)
		dataDict['hists'][ring]['occ'].SetDirectory(0)
		dataDict['hists'][ring]['lct'].SetDirectory(0)
	for ring in RINGLIST:
		dataDict['hists'][ring] = {
			'occ'  : fdata.Get('o'+ring),
			'lct'  : fdata.Get('lct'+ring),
		}
		dataDict['hists'][ring]['occ'].SetDirectory(0)
		dataDict['hists'][ring]['lct'].SetDirectory(0)

######################
# Load MC Histograms #
######################

def loadCompMC(mcDict):
	''' Load in comparator MC histograms
		- assumes that mcDict is mcDict['comp']
	'''
	for mcType in mcDict.keys():
		fmc = R.TFile.Open(mcDict[mcType]['file'])
		for ring in RINGLIST:
			mcDict[mcType]['hists'][ring] = {
				#'time' : fmc.Get('t'+ring),
				'occ'  : fmc.Get('o'+ring),
			}
			#mcDict[mcType]['hists'][ring]['time'].SetDirectory(0)
			mcDict[mcType]['hists'][ring]['occ' ].SetDirectory(0)

def loadWireMC(mcDict):
	''' Load in wire group MC histograms
		- assumes that mcDict is mcDict['wire']
	'''
	for mcType in mcDict.keys():
		fmc = R.TFile.Open(mcDict[mcType]['file'])
		for ring in RINGLIST:
			mcDict[mcType]['hists'][ring] = {
				#'time' : fmc.Get('t'+ring),
				'occ'  : fmc.Get('o'+ring),
			}
			#mcDict[mcType]['hists'][ring]['time'].SetDirectory(0)
			mcDict[mcType]['hists'][ring]['occ' ].SetDirectory(0)

########################
# Occupancy Histograms #
########################

def doCompOcc(dataDict,mcDict):
	''' Plots comparator hit occupancy
		- Normalizes left and right histograms to combined l+r lct count then draws
		  them on the same canvas
		- Plots each MC individually
	'''
	for mcType in mcDict.keys():
		for ring in RINGLIST:
			for logy in [True,False]:
				# Gather data histograms
				compDataHist = dataDict['hists'][ring]['occ'].Clone()
				compDataHist.Sumw2()
				lctDataHist = dataDict['hists'][ring]['lct'].Clone()
				lctDataHist.Sumw2()

				# Divide comparator hit occupancy histograms by the number of times
				# we "looked" in a ring and counted background comparator hits
				compDataHist.Scale(1./lctDataHist.Integral() if lctDataHist.GetEntries() > 0 else 0.)

				# Gather MC histograms
				compMCHist = mcDict[mcType]['hists'][ring]['occ'].Clone()

				# Divide MC comp group occupancy by the number of MC events 
				# generated (i.e. number of evts used to fill original histogram)
				compMCHist.Scale(1./mcDict[mcType]['nEvts'])

				# Make plots
				compDataPlot = Plotter.Plot(compDataHist,option='p')
				compMCPlot = Plotter.Plot(compMCHist,option='hist')
				canvas = Plotter.Canvas(lumi='ME'+ring+' Comparator Hit Occupancy',logy=logy)
				canvas.addMainPlot(compDataPlot)
				canvas.addMainPlot(compMCPlot)
				canvas.firstPlot.setTitles(X='Half Strip Number',Y='Counts per BX')
				canvas.firstPlot.SetMinimum(1E-5 if logy else 0.)
				maximum = max(compDataPlot.GetMaximum(),compMCPlot.GetMaximum())
				canvas.firstPlot.SetMaximum(maximum*1.05)
				canvas.makeTransparent()
				canvas.finishCanvas('BOB')
				canvas.save('pdfs/BGCompOcc_DataMC_'+ring+('_logy_' if logy else '_')+mcType,['.pdf'])
				canvas.deleteCanvas()

def doCompOccSep(dataDict,mcDict):
	''' Plots comparator hit occupancy
		- Normalizes left and right histograms separately then draws them on
		  the same canvas
		- Plots each MC individually
	'''
	for mcType in mcDict.keys():
		for ring in RINGLIST:
			for logy in [True,False]:
				# Gather data histograms
				compDataHist_l = dataDict['hists'][ring+'l']['occ'].Clone()
				compDataHist_l.Sumw2()
				compDataHist_r = dataDict['hists'][ring+'r']['occ'].Clone()
				compDataHist_r.Sumw2()
				lctDataHist_l = dataDict['hists'][ring+'l']['lct'].Clone()
				lctDataHist_l.Sumw2()
				lctDataHist_r = dataDict['hists'][ring+'r']['lct'].Clone()
				lctDataHist_r.Sumw2()

				# Divide comparator hit occupancy histograms by the number of times
				# we "looked" in a ring and counted background comparator hits
				compDataHist_l.Scale(1./lctDataHist_l.Integral() if lctDataHist_l.GetEntries() > 0 else 0.)
				compDataHist_r.Scale(1./lctDataHist_r.Integral() if lctDataHist_r.GetEntries() > 0 else 0.)

				# Gather MC histograms
				compMCHist = mcDict[mcType]['hists'][ring]['occ'].Clone()

				# Divide MC comp group occupancy by the number of MC events 
				# generated (i.e. number of evts used to fill original histogram)
				compMCHist.Scale(1./mcDict[mcType]['nEvts'])

				# Make plots
				compDataPlot_l = Plotter.Plot(compDataHist_l,option='p')
				compDataPlot_r = Plotter.Plot(compDataHist_r,option='p')
				compMCPlot = Plotter.Plot(compMCHist,option='hist')
				canvas = Plotter.Canvas(lumi='ME'+ring+' Comparator Hit Occupancy',logy=logy)
				canvas.addMainPlot(compDataPlot_l)
				compDataPlot_l.SetMarkerColor(R.kRed)
				canvas.addMainPlot(compDataPlot_r)
				compDataPlot_r.SetMarkerColor(R.kBlue)
				canvas.addMainPlot(compMCPlot)
				canvas.firstPlot.setTitles(X='Half Strip Number',Y='Counts per BX')
				canvas.firstPlot.SetMinimum(1E-5 if logy else 0.)
				maximum = max(compDataPlot_l.GetMaximum(),compDataPlot_r.GetMaximum(),compMCPlot.GetMaximum())
				canvas.firstPlot.SetMaximum(maximum*1.05)
				canvas.makeTransparent()
				canvas.finishCanvas('BOB')
				canvas.save('pdfs/BGCompOcc_DataMC_'+ring+('_logy_' if logy else '_')+mcType+'_sep',['.pdf'])
				canvas.deleteCanvas()

def doWireOcc(dataDict,mcDict):
	''' Plots wire group hit occupancy
		- Normalizes upper and lower histograms separately then draws them on
		  the same canvas
		- Plots each MC individually
	'''
	for mcType in mcDict.keys():
		for ring in RINGLIST:
			for logy in [True,False]:
				# Gather data histograms
				wireDataHist_l = dataDict['hists'][ring+'l']['occ'].Clone()
				wireDataHist_l.Sumw2()
				lctDataHist_l = dataDict['hists'][ring+'l']['lct'].Clone()
				lctDataHist_l.Sumw2()
				wireDataHist_u = dataDict['hists'][ring+'u']['occ'].Clone()
				wireDataHist_u.Sumw2()
				lctDataHist_u = dataDict['hists'][ring+'u']['lct'].Clone()
				lctDataHist_u.Sumw2()

				# Divide wire group occupancy histograms by the number of times
				# we "looked" in a ring and counted background wire groups
				wireDataHist_u.Scale(1./lctDataHist_u.Integral() if lctDataHist_u.GetEntries() > 0 else 0.)
				wireDataHist_l.Scale(1./lctDataHist_l.Integral() if lctDataHist_l.GetEntries() > 0 else 0.)

				# Gather MC histograms
				wireMCHist = mcDict[mcType]['hists'][ring]['occ'].Clone()

				# Divide MC wire group occupancy by the number of MC events 
				# generated (i.e. number of evts used to fill original histogram)
				wireMCHist.Scale(1./mcDict[mcType]['nEvts'])

				# Make plots
				wireDataPlot_l = Plotter.Plot(wireDataHist_l,option='p')
				wireDataPlot_u = Plotter.Plot(wireDataHist_u,option='p')
				wireMCPlot = Plotter.Plot(wireMCHist,option='hist')
				canvas = Plotter.Canvas(lumi='ME'+ring+' Wire Group Occupancy',logy=logy)
				canvas.addMainPlot(wireDataPlot_l)
				wireDataPlot_l.SetMarkerColor(R.kBlue)
				canvas.addMainPlot(wireDataPlot_u)
				wireDataPlot_u.SetMarkerColor(R.kRed)
				canvas.addMainPlot(wireMCPlot)
				canvas.firstPlot.setTitles(X='Wire Group Number',Y='Counts per BX')
				canvas.firstPlot.SetMinimum(1E-5 if logy else 0.)
				maximum = max(wireDataPlot_u.GetMaximum(),wireDataPlot_l.GetMaximum(),wireMCPlot.GetMaximum())
				canvas.firstPlot.SetMaximum(maximum*1.05)
				canvas.makeTransparent()
				canvas.finishCanvas('BOB')
				canvas.save('pdfs/BGWireOcc_DataMC_'+ring+('_logy_' if logy else '_')+mcType,['.pdf'])
				canvas.deleteCanvas()

##############################################
# Comparator Cumulative Occupancy Histograms #
##############################################

def doCompCum(dataDict,mcDict):
	''' Plot cumulative comparator occupancy histograms
		- Plots both greater than (ge) and less than (le) cumulative distrubutions
		- Uses the comparator occupancy histograms that are normalized to l+r lct counts
	'''
	for mcType in mcDict.keys():
		for ring in RINGLIST:
			for logy in [True,False]:
				for itype in ['le','ge']:
					cumDataHist = roottools.cumulative_histogram(dataDict['hists'][ring]['occ'].Clone(),itype)
					cumDataHist.Sumw2()
					lctDataHist = dataDict['hists'][ring]['lct'].Clone()
					lctDataHist.Sumw2()

					cumDataHist.Scale(1./lctDataHist.Integral() if lctDataHist.GetEntries() > 0 else 0.)

					cumMCHist = roottools.cumulative_histogram(mcDict[mcType]['hists'][ring]['occ'],itype)
					cumMCHist.Scale(1./mcDict[mcType]['nEvts'])

					cumDataPlot = Plotter.Plot(cumDataHist,option='p')
					cumMCPlot = Plotter.Plot(cumMCHist,option='hist')

					canvas = Plotter.Canvas(lumi='ME'+ring+' Cumulative Comparator Hit Occupancy',logy=logy)
					canvas.addMainPlot(cumDataPlot)
					canvas.addMainPlot(cumMCPlot)
					canvas.firstPlot.setTitles(X='Half Strip Number',Y='N(comp) < HS')
					canvas.makeTransparent()
					canvas.finishCanvas('BOB')
					canvas.firstPlot.setTitles(X='Half Strip Number',Y='N(comp)'+('>' if itype=='ge' else '<')+' HS(comp)')
					canvas.deleteCanvas()


def doCompCumSep(dataDict,mcDict):
	''' Plot cumulative comparator occupancy separate l/r normalizations
		- Not finished
	'''
	for mcType in mcDict.keys():
		for ring in RINGLIST:
			for logy in [True,False]:
				for itype in ['le','ge']:
					cumDataHist = roottools.cumulative_histogram(dataDict['hists'][ring]['occ'].Clone(),itype)
					cumDataHist.Sumw2()
					lctDataHist = dataDict['hists'][ring]['lct'].Clone()
					lctDataHist.Sumw2()

					cumDataHist.Scale(1./lctDataHist.Integral() if lctDataHist.GetEntries() > 0 else 0.)

					cumMCHist = roottools.cumulative_histogram(mcDict[mcType]['hists'][ring]['occ'],itype)
					cumMCHist.Scale(1./mcDict[mcType]['nEvts'])

					cumDataPlot = Plotter.Plot(cumDataHist,option='p')
					cumMCPlot = Plotter.Plot(cumMCHist,option='hist')

					canvas = Plotter.Canvas(lumi='ME'+ring+' Cumulative Comparator Hit Occupancy',logy=logy)
					canvas.addMainPlot(cumDataPlot)
					canvas.addMainPlot(cumMCPlot)
					canvas.firstPlot.setTitles(X='Half Strip Number',Y='N(comp)'+('>' if itype=='ge' else '<')+' HS(comp)')
					canvas.makeTransparent()
					canvas.finishCanvas('BOB')
					canvas.save('pdfs/BGCompCum_DataMC_'+ring+('_logy_' if logy else '_')+itype+'_'+mcType,['.pdf'])
					canvas.deleteCanvas()


# Make Wire Group Histograms
wireDataDict = dataDict['wire']
wireMCDict = mcDict['wire']
loadWireData(wireDataDict)
loadWireMC(wireMCDict)
doWireOcc(wireDataDict,wireMCDict)

# Make Comparator Histograms
compDataDict = dataDict['comp']
compMCDict = mcDict['comp']
loadCompData(compDataDict)
loadCompMC(compMCDict)
#doCompOcc(compDataDict,compMCDict)
doCompOccSep(compDataDict,compMCDict) # current comparator occupancy money plot
#doCompCum(compDataDict,compMCDict)
