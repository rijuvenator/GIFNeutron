'''
Quick script to compare the effect of 'hacking' the CSCDigitizer.
Plots comparator and wire group occupancies.
'''
import sys, os, argparse
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.roottools as roottools
import logging
R.gROOT.SetBatch(True)

RINGLIST = ['11', '12', '13', '21', '22', '31', '32', '41', '42']

# Set dictionary
mcDict = {
	'HP_Thermal_ON': {
		'hack' : {
			#'file' : '/afs/cern.ch/work/a/adasgupt/public/Neutron/hacktrees2/hacktree.root',
			'fwire'  : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/wire/BGWire_MC_bgdigitest.root',
			'fcomp'  : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/comp/BGComp_MC_lrNormTest.root',
			'nEvts' : 25000.,
			'hists' : {},
		},
		'nohack' : {
			#'file' : '/afs/cern.ch/work/a/adasgupt/public/Neutron/nomtrees2/nomtree.root',
			'fcomp' : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/comp/',
			'fwire' : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/wire/',
			'nEvts' : 25000.,
			'hists' : {},
		},
	},
	#'HP_Thermal_OFF': {
	#	'hack' : {
	#		#'file' : '/afs/cern.ch/work/a/adasgupt/public/Neutron/hacktrees2/hacktree.root',
	#		'fwire'  : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/wire/BGWire_MC_bgdigitest.root',
	#		'fcomp'  : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/comp/BGComp_MC_lrNormTest.root',
	#		'nEvts' : 25000.,
	#		'hists' : {},
	#	},
	#	'nohack' : {
	#		#'file' : '/afs/cern.ch/work/a/adasgupt/public/Neutron/nomtrees2/nomtree.root',
	#		'fcomp' : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/comp/',
	#		'fwire' : '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/wire/',
	#		'nEvts' : 25000.,
	#		'hists' : {},
	#	},
	#},
}

for RING in RINGLIST:
	for digi in ['comp','wire']:
		DIGI = 'Comp' if digi=='comp' else 'Wire'
		# Get Histogram 1
		fhname  = '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/'+digi+'/BG'+DIGI+'_MC_HP_ON_digi_all.root'
		print fhname
		#fhname  = '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/comp/BGComp_MC_bgdigitest.root'
		fh = R.TFile.Open(fhname)
		hist_1 = fh.Get('o'+RING)
		hist_1.SetDirectory(0)
		# Get Histogram 2
		fnhname = '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/'+digi+'/BG'+DIGI+'_MC_HP_OFF_digi_all.root'
		#fnhname = '/afs/cern.ch/user/c/cschnaib/Analysis/analysis/comp/BGComp_MC_bgdigitest_nohack.root'
		fnh = R.TFile.Open(fnhname)
		hist_2 = fnh.Get('o'+RING)
		hist_2.SetDirectory(0)

		# Scale histograms
		hist_1.Scale(100000./104950.)
		hist_2.Scale(100000./98250.)

		plot_1 = Plotter.Plot(hist_1,legName='HP Thermal ON',legType='l',option='hist')
		plot_2 = Plotter.Plot(hist_2,legName='HP Thermal OFF',legType='l',option='hist')
		
		canvas = Plotter.Canvas(lumi='ME'+RING+' MC '+DIGI+' Occupancy')

		canvas.addMainPlot(plot_1)
		plot_1.SetLineColor(R.kRed)
		canvas.addMainPlot(plot_2)
		plot_2.SetLineColor(R.kBlue)

		canvas.makeLegend(pos='tr')
		canvas.legend.moveLegend(X=-0.2)

		xaxis = 'Half Strip Number' if digi=='comp' else 'Wire Group Number'
		canvas.firstPlot.setTitles(X=xaxis,Y='Counts [au]')
		canvas.firstPlot.SetMinimum(0.)

		canvas.makeTransparent()
		canvas.finishCanvas('BOB')
		#canvas.save('pdfs/MCComp_digi_fix_comparison_hp_on_'+RING,['.pdf'])
		name = 'MC'+DIGI+'_hp_thermal_comparison_'+RING
		canvas.save('pdfs/'+name,['.pdf'])
		canvas.deleteCanvas()
