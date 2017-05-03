import sys, os, argparse, math
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi
R.gROOT.SetBatch(True)
# area histograms calculated on the fly
import areas as areas
areaHists = areas.areaHists

# parse arguments
parser = argparse.ArgumentParser()
# recreate
parser.add_argument('-r','--recreate',action='store_true',dest='RECREATE',
		default=False,help='whether or not to (re)create an output data file')
# name
parser.add_argument('-n','--name',dest='NAME',default='',help='extra name to output data file')
# scale
parser.add_argument('-s','--scale',dest='SCALE',action='store_true',
		default=False,help='whether or not to scale to counts/cm^2/s')
args = parser.parse_args()
RECREATE = args.RECREATE
NAME = args.NAME
SCALE = args.SCALE

# Which time bins to use in each BX
BXDICT = {
		'wire':{
			1:{'lower':1,'upper':5},
			2:{'lower':1,'upper':4},
			3:{'lower':1,'upper':3},
			4:{'lower':1,'upper':2},
			5:{'lower':1,'upper':1},
			46:{'lower':13,'upper':15},
			47:{'lower':14,'upper':15},
			48:{'lower':15,'upper':15},
			},
		'comp':{
			1:{'lower':2,'upper':4},
			2:{'lower':2,'upper':3},
			3:{'lower':2,'upper':2},
			48:{'lower':9,'upper':9},
			},
		}
# Which BXs to use in each plot
PLOT = {
		'wire':{
			'early':{'bx':[1,2,3,4,5],'tb':15.},
			'bx1':{'bx':[1],'tb':5.},
			'bx2':{'bx':[2],'tb':4.},
			'bx3':{'bx':[3],'tb':3.},
			'bx4':{'bx':[4],'tb':2.},
			'bx5':{'bx':[5],'tb':1.},
			'late':{'bx':[46,47,48],'tb':6.},
			'bx46':{'bx':[46],'tb':1.},
			'bx47':{'bx':[47],'tb':2.},
			'bx48':{'bx':[48],'tb':3.},
			},
		'comp':{
			'early':{'bx':[1,2,3],'tb':6.},
			'bx1':{'bx':[1],'tb':3.},
			'bx2':{'bx':[2],'tb':2.},
			'bx3':{'bx':[3],'tb':1.},
			'late':{'bx':[48],'tb':1.},
			},
		}
LIMITS = {
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
					'11':0.25e-3,
					'12':12e-6,
					'13':16e-6,
					'21':0.1e-3,
					'22':26e-6,
					'31':0.08e-3,
					'32':40e-6,
					'41':0.06e-3,
					'42':0.06e-3,
					},
				},
			},
		'int':{
			'early':{
				'comp':0.005,
				'wire':0.007,
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
MCLIST = ['XS_Thermal_ON','XS_Thermal_OFF','HP_Thermal_ON','HP_Thermal_OFF']

#####################################
### Get/make occupancy histograms ###
#####################################

if RECREATE:
	# Get Tree
	FILE = R.TFile.Open('/afs/cern.ch/work/a/adasgupt/public/goatees/GOAT_P5.root')
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
		weight = 1./entry.PILEUP
		if entry.BX in BXDICT[digi].keys():
			for idigi,time in enumerate(entry.D_TIME):
				if time >= BXDICT[digi][entry.BX]['lower'] and \
				   time <= BXDICT[digi][entry.BX]['upper']:
					# Fill occupancy numerator
					HISTS[ecr][digi][entry.BX][half]['num'].Fill(entry.D_POS[idigi],weight)
					HISTS[ring][digi][entry.BX][half]['num'].Fill(entry.D_POS[idigi],weight)
					# Fill global phi numerator
					PHI[ecr][digi][entry.BX][half]['num'].Fill(entry.CHAM,weight)
					PHI[ring][digi][entry.BX][half]['num'].Fill(entry.CHAM,weight)
					# Fill luminosity numerator
					LUMI[ecr][digi][entry.BX][half]['num'].Fill(entry.LUMI,1.)
					LUMI[ring][digi][entry.BX][half]['num'].Fill(entry.LUMI,1.)
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
MCHISTS = {mc:{ec+ring:{digi:{} for digi in PLOT.keys()} for ec in ECLIST for ring in RINGLIST} for mc in MCLIST}
for mc in MCLIST:
	FMC = R.TFile.Open('root/hists_'+mc+'.root')
	for ring in RINGLIST:
		for ec in ECLIST:
			for digi in PLOT.keys():
				MCHISTS[mc][ec+ring][digi] = {
						'occ' : FMC.Get(ec+ring+'_'+digi+'_occ').Clone(),
						'phi' : FMC.Get('phi_'+ec+ring+'_'+digi+'_occ').Clone(),
						}
				MCHISTS[mc][ec+ring][digi]['occ'].SetDirectory(0)
				MCHISTS[mc][ec+ring][digi]['phi'].SetDirectory(0)

###########################
### Make plot functions ###
###########################

def makeOccupancyPlot(dataHist,digi,when,ec,ring,mc):
	# Make occupancy plot for each digi and plot type
	dataPlot = Plotter.Plot(dataHist.Clone(),option='p')
	TITLE = 'ME'+ec+ring+' '+('Comparator ' if digi=='comp' else 'Wire Group ')+'Occupancy'
	# Make MC plot
	if mc!='':
		mcname = mc.replace('_',' ')
		mchist = MCHISTS[mc][ec+ring][digi]['occ'].Clone()
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
			canvas.drawText('MC : {:1.4f}'.format(mcPlot.Integral()),pos=(0.6,0.7))
		mcMax = mcPlot.GetMaximum() if mc!='' else 0.
		maximum = max(dataPlot.GetMaximum(),mcMax)
		if when=='early':
			if ring in ['11','12','13','21','22','31','32','41','42']:
				canvas.firstPlot.SetMaximum(LIMITS['occ']['early'][digi][ring])
			else:
				canvas.firstPlot.SetMaximum(maximum * 1.2)
		else:
			canvas.firstPlot.SetMaximum(maximum * 1.2)
		canvas.firstPlot.SetMinimum(1e-2 if LOGY else 0.)
		x = 'Comparator Half Strip' if digi=='comp' else 'Wire Group Number'
		y = 'Counts/cm^{2}/s' if SCALE else 'Counts/BX'
		canvas.firstPlot.setTitles(X=x, Y=y)
		canvas.drawText('Data : {:1.4f}'.format(dataPlot.Integral()),pos=(0.6,0.6))
		canvas.firstPlot.scaleTitleOffsets(1.2,'Y')
		canvas.makeTransparent()
		canvas.finishCanvas('BOB')
		name = 'occupancy_'+ec+ring+'_'+digi+'_'+when+('_'+NAME if NAME != '' else '')+('_logy' if LOGY else '')+('_'+mc if mc!='' else '')
		name = name.replace('+','p')
		name = name.replace('-','m')
		canvas.save('pdfs/'+name+'.pdf')
		canvas.deleteCanvas()

def makePhiPlot(dataHist,digi,when,ec,ring,mc):
	# Make occupancy plot for each digi and plot type
	dataPlot = Plotter.Plot(dataHist.Clone(),option='p')
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
		mcMax = mcPlot.GetMaximum() if mc!='' else 0.
		maximum = max(dataPlot.GetMaximum(),mcMax)
		canvas.firstPlot.SetMaximum(maximum * 1.2)
		canvas.firstPlot.SetMinimum(1e-2 if LOGY else 0.)
		x = 'CSC Chamber'
		y = 'Counts/cm^{2}/s' if SCALE else 'Counts/BX'
		canvas.firstPlot.setTitles(X=x, Y=y)
		canvas.firstPlot.scaleTitleOffsets(1.2,'Y')
		canvas.makeTransparent()
		canvas.finishCanvas('BOB')
		name = 'phi_'+ec+ring+'_'+digi+'_'+when+('_'+NAME if NAME != '' else '')+('_logy' if LOGY else '')+('_'+mc if mc!='' else '')+'_test'
		name = name.replace('+','p')
		name = name.replace('-','m')
		canvas.save('pdfs/'+name+'.pdf')
		canvas.deleteCanvas()

def makeIntegralPlot(dataHist,digi,when,mc):
	# Make integral plot for each digi and plot type
	dataPlot = Plotter.Plot(dataHist.Clone(),option='p')
	TITLE = ('Comparator ' if digi=='comp' else 'Wire Group ')+'Integral Occupancy'
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
		canvas = Plotter.Canvas(lumi=TITLE,logy=LOGY)
		if mc!='': 
			canvas.addMainPlot(mcPlot)
			mcPlot.SetFillColor(R.kOrange)
		canvas.addMainPlot(dataPlot,addToPlotList=False)
		if mc!='':
			canvas.makeLegend(pos='tr')
			canvas.legend.moveLegend(X=-0.2)
			canvas.legend.resizeHeight()
		if when=='early':
			canvas.firstPlot.SetMaximum(LIMITS['int']['early'][digi])
		else:
			mcMax = mcPlot.GetMaximum() if mc!='' else 0.
			maximum = max(dataPlot.GetMaximum(),mcMax)
			canvas.firstPlot.SetMaximum(maximum * 1.1)
		canvas.firstPlot.SetMinimum(1e-2 if LOGY else 0.)
		x = 'CSC Ring'
		for ibin,ring in enumerate(ERINGLIST):
			canvas.firstPlot.GetXaxis().SetBinLabel(ibin+1, ring.replace('-','#minus'))
		y = 'Counts/cm^{2}/s' if SCALE else 'Counts/BX'
		canvas.firstPlot.setTitles(Y=y)
		canvas.firstPlot.scaleTitleOffsets(1.2,'Y')
		canvas.makeTransparent()
		canvas.finishCanvas('BOB')
		name = 'integral_'+digi+'_'+when+('_'+NAME if NAME != '' else '')+('_logy' if LOGY else '')+('_'+mc if mc!='' else '')
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
		y = 'Counts/cm^{2}/s' if SCALE else 'Counts/BX'
		canvas.firstPlot.setTitles(X=x, Y=y)
		canvas.firstPlot.scaleTitleOffsets(1.2,'Y')
		canvas.makeTransparent()
		canvas.finishCanvas('BOB')
		name = 'luminosity_'+ec+ring+'_'+digi+'_'+when+('_'+NAME if NAME != '' else '')+('_logy' if LOGY else '')
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
		name = 'luminosity_sep_'+ec+ring+'_'+digi+'_'+when+('_'+NAME if NAME != '' else '')+('_logy' if LOGY else '')
		name = name.replace('+','p')
		name = name.replace('-','m')
		canvas.save('pdfs/'+name+'.pdf')
		canvas.deleteCanvas()

#####################
#### Make Plots! ####
#####################

### Normalize MC histograms
# Number of events in each MC file
# I make this to be user input, but it doesn't have to be
MCNORM = {
		'HP_Thermal_ON':102100.,
		'HP_Thermal_OFF':98250.,
		'XS_Thermal_ON':99000.,
		'XS_Thermal_OFF':100000.,
		}
for mc in MCLIST:
	for ring in RINGLIST:
		for ec in ECLIST:
			for digi in PLOT.keys():
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
				MCHISTS[mc][ec+ring][digi]['phi'].Scale(1./ncham)
				if SCALE:
					# Scale by area
					MCHISTS[mc][ec+ring][digi]['occ'].Divide(areaHists[digi][ring])
					# Scale by time
					time = 25.*10**(-9)
					MCHISTS[mc][ec+ring][digi]['occ'].Scale(1./time)

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
					PHI[ec+ring][digi][bx][HALVES[digi][i]]['rate'].Scale(1./PHI[ec+ring][digi][bx][HALVES[digi][i]]['den'].GetEntries())
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
			#########################
			## Make Occupancy plot ##
			#########################
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
				if SCALE:
					# Convert the per time bin number into per seconds
					# 25 ns/bx * 10(-9) s/ns
					bxtosecconv = 25. * 10**(-9)
					total.Scale(1./bxtosecconv)
					totalphi.Scale(1./bxtosecconv)
					totallumi.Scale(1./bxtosecconv)
					totallumiRU.Scale(1./bxtosecconv)
					totallumiLL.Scale(1./bxtosecconv)
					# Convert into per cm^2
					total.Divide(areaHists[digi][ring])
					#totalphi.Divide(areaHists[digi][ring]) # hmmm... maybe need to fill with a weight of the digi area
					#totallumi{,RU,LL} same here.. need to fill with the weight of the area
				makeLuminosityPlot(totallumi,digi,when,ec,ring)
				makeSepPlot(totallumiRU,totallumiLL,digi,when,ec,ring)
				### Make Plot
				for mc in MCLIST+['']:
					makeOccupancyPlot(total,digi,when,ec,ring,mc)
					makePhiPlot(totalphi,digi,when,ec,ring,mc)

##########################
### Make Integral Plot ###
##########################
for digi in PLOT.keys():
	for when in PLOT[digi].keys():
		integralData = R.TH1D('integralData_'+digi+'_'+when,'',18,0,18)
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
			if SCALE:
				# Convert the per time bin number into per seconds
				bxtosecconv = 25.*10**(-9)
				integralData.Scale(1./bxtosecconv)
				# scale to per cm^2
				total.Divide(areaHists[digi][ring])
			# Set integralData contents and labels
			integralData.SetBinContent(b+1,total.Integral())
			errLL2 = 1./totalLL.GetEntries() if totalLL.GetEntries()>0 else 0
			errRU2 = 1./totalRU.GetEntries() if totalRU.GetEntries()>0 else 0
			err = total.Integral() * math.sqrt( errLL2 + errRU2 )
			integralData.SetBinError(b+1,err)
			integralData.GetXaxis().SetBinLabel(b+1,ring.replace('-','#minus'))
		for mc in MCLIST+['']:
			makeIntegralPlot(integralData,digi,when,mc)
