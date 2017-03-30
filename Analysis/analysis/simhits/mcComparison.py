'''
Purpose of this script is to combine simhit distributions from different 
MC samples onto a single canvas
- Requires the number of events in each MC sample for proper normalization
- Includes option to require < or > 300 ns simhit time of flight
- Output is a ROOT file and pdfs of different occupancy distributions

- Plots are separated by station and particle type
	- Stations  : 1,2,3,4,all
	- Particles : muon,pion,e+/-,proton,other,all

	hist key   : description
	------------------------
	- tof      : time of flight
	- radial2  : radial position squared
	- radial   : radial position
	- phi      : phi
	- z        : z position
	- id       : particle id
	- nSimHits : number of simhits in event
	- xy       : 2d y vs x
	- rz       : 2d r vs z
	- rphi     : 2d r vs phi
	- rtof     : 2d r vs time of flight
	- ztof     : 2d z vs time of flight
	- phitof   : 2d phi vs time of flight

'''

import os, math, sys
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.roottools as roottools
#import Gif.Analysis.MegaStruct as MS
R.gROOT.SetBatch(True)


TITLE = ''
#TITLE = '_tGT300'
#TITLE = '_tLT300'

RECREATE=True
outputROOT = R.TFile('mcComparison'+TITLE+'.root','recreate')
#RECREATE=False
#outputROOT = R.TFile.Open('mcComparison'+TITLE+'.root','read')


fileDict = {
	'HP_Thermal_ON':{
		'file':'/afs/cern.ch/work/c/cschnaib/public/NeutronSim/HP_Thermal_ON/ana_neutronMC_HPThermalON_105k_digi_hack.root',
		'color':R.kBlue,
		'nEvts':102100.,
		},
	'HP_Thermal_OFF':{
		'file':'/afs/cern.ch/work/c/cschnaib/public/NeutronSim/HP_Thermal_OFF/ana_neutronMC_HPThermalOFF_digi_all.root',
		'color':R.kOrange+1,
		'nEvts':96250.,
		#'nEvts':0.,
		},
	'XS_Thermal_ON':{
		'file':'/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_ON/ana_neutronMC_XS_ThermalON.root',
		'color':R.kGreen,
		'nEvts':100000.,
		#'nEvts':0.,
		},
	'XS_Thermal_OFF':{
		'file':'/afs/cern.ch/user/c/cschnaib/Analysis/trees_mc/ana_neutronMC.root',
		'color':R.kRed,
		'nEvts':100000.,
		#'nEvts':0.,
		},
}

stations = [1,2,3,4,'all']
particles = ['muon','e','pion','proton','other','all']
hists = ['tof','radial','radial2','phi','nSimHits','z','id']
hists2d = ['xy','rz','rphi','rtof','phitof','ztof']

HISTS = {
		'HP_Thermal_ON':{station:{hist:{particle:{} for particle in particles} for hist in hists} for station in stations},
		'HP_Thermal_OFF':{station:{hist:{particle:{} for particle in particles} for hist in hists} for station in stations},
		'XS_Thermal_ON':{station:{hist:{particle:{} for particle in particles} for hist in hists} for station in stations},
		'XS_Thermal_OFF':{station:{hist:{particle:{} for particle in particles} for hist in hists} for station in stations},
}
HISTS2D = {
		'HP_Thermal_ON':{station:{hist:{particle:{} for particle in particles} for hist in hists2d} for station in stations},
		'HP_Thermal_OFF':{station:{hist:{particle:{} for particle in particles} for hist in hists2d} for station in stations},
		'XS_Thermal_ON':{station:{hist:{particle:{} for particle in particles} for hist in hists2d} for station in stations},
		'XS_Thermal_OFF':{station:{hist:{particle:{} for particle in particles} for hist in hists2d} for station in stations},
}

if RECREATE:
	outputROOT.cd()
	for sim in HISTS.keys():
		name = 'h_'+sim
		for station in HISTS[sim].keys():
			# 1D histograms
			for particle in particles:
				HISTS[sim][station]['tof'][particle]       = R.TH1F(name+'_'+str(station)+'_tof_'+particle,      '',100,np.logspace(0.,10.,101))
				HISTS[sim][station]['radial'][particle]    = R.TH1F(name+'_'+str(station)+'_radial_'+particle,   '',100,0,800)
				HISTS[sim][station]['radial2'][particle]   = R.TH1F(name+'_'+str(station)+'_radial2_'+particle,  '',100,0,640000)
				HISTS[sim][station]['phi'][particle]       = R.TH1F(name+'_'+str(station)+'_phi_'+particle,      '',50,-3.14,3.14)
				HISTS[sim][station]['nSimHits'][particle]  = R.TH1F(name+'_'+str(station)+'_nSimHits_'+particle, '',25,0,25)
				HISTS[sim][station]['z'][particle]         = R.TH1F(name+'_'+str(station)+'_z_'+particle,        '',100,-1100,1100)
				HISTS[sim][station]['id'][particle]        = R.TH1F(name+'_'+str(station)+'_id_'+particle,       '',6,0,6)
				# 2D histograms
				HISTS2D[sim][station]['xy'][particle]     = R.TH2F(name+'_'+str(station)+'_xy_'+particle,     '',100,-700,700,100,-700,700)
				HISTS2D[sim][station]['rz'][particle]     = R.TH2F(name+'_'+str(station)+'_rz_'+particle,     '',100,0,1100,100,0,700)
				HISTS2D[sim][station]['rphi'][particle]   = R.TH2F(name+'_'+str(station)+'_rphi_'+particle,   '',50,-3.14,3.14,100,0,700)
				HISTS2D[sim][station]['rtof'][particle]   = R.TH2F(name+'_'+str(station)+'_rtof_'+particle,   '',100,np.logspace(-1.,10.,101),100,0,700)
				HISTS2D[sim][station]['phitof'][particle] = R.TH2F(name+'_'+str(station)+'_phitof_'+particle, '',100,np.logspace(-1.,10.,101),50,-3.14,3.14)
				HISTS2D[sim][station]['ztof'][particle]   = R.TH2F(name+'_'+str(station)+'_ztof_'+particle,   '',100,np.logspace(-1.,10.,101),100,0,1100)

	for neutronSim in fileDict.keys():
		neutronFile = R.TFile.Open(fileDict[neutronSim]['file'])
		t = neutronFile.Get('GIFTree/GIFDigiTree')
		#fileDict[neutronSim]['nEvts'] += t.GetEntries()
		#print
		#print neutronSim
		#print t.GetEntries()
		#print fileDict[neutronSim]['nEvts']
		for idx,entry in enumerate(t):
			print 'Events:', idx, '\r',

			E = Primitives.ETree(t, DecList=['SIMHIT'])
			# Total
			simhits = [Primitives.SimHit(E,i) for i in range(len(E.sim_cham))]
			# t > 300 ns
			#simhits = [Primitives.SimHit(E,i) for i in range(len(E.sim_cham)) if E.sim_tof[i] > 300]
			# t < 300 ns
			#simhits = [Primitives.SimHit(E,i) for i in range(len(E.sim_cham)) if E.sim_tof[i] < 300]


			# Fill N(SH) for each station for all particle types
			stationlist = [CH.Chamber(sh.cham).station for sh in simhits]
			for station in [1,2,3,4]:
				HISTS[neutronSim][station]['nSimHits']['all'].Fill(stationlist.count(station))
			HISTS[neutronSim]['all']['nSimHits']['all'].Fill(len(simhits))
			# Fill N(SH) for each station for each particle type
			for particle in particles:
				if particle == 'all': continue
				plist = []
				if particle=='muon':
					plist = plist + [sh for sh in simhits if abs(sh.particleID)==13]
				elif particle=='e':
					plist = plist + [sh for sh in simhits if abs(sh.particleID)==11]
				elif particle=='pion':
					plist = plist + [sh for sh in simhits if abs(sh.particleID)==211]
				elif particle=='proton':
					plist = plist + [sh for sh in simhits if abs(sh.particleID)==2212]
				else: # other
					plist = plist + [sh for sh in simhits \
						if abs(sh.particleID)!=13 and abs(sh.particleID)!=11 and abs(sh.particleID)!=211 and abs(sh.particleID)!=2212]
				for station in [1,2,3,4]:
					stationlistp = [CH.Chamber(sh.cham).station for sh in plist]
					HISTS[neutronSim][station]['nSimHits'][particle].Fill(stationlistp.count(station))
				HISTS[neutronSim]['all']['nSimHits'][particle].Fill(len(plist))
			for simhit in simhits:
				# Get station
				ch = CH.Chamber(simhit.cham)
				station = ch.station
				# Get r,phi,etc. (g for global, no prefix letter for local variables)
				gx = simhit.globalPos['x']
				gy = simhit.globalPos['y']
				gz = simhit.globalPos['z']
				gr2 = simhit.globalPos['x']**2 + simhit.globalPos['y']**2
				gr = math.sqrt( gr2 )
				gphi = math.atan2(simhit.globalPos['y'],simhit.globalPos['x'])
				tof = simhit.tof
				if abs(simhit.particleID)==13:
					particle = 'muon'
					fill = 0
				elif abs(simhit.particleID)==11:
					particle = 'e'
					if simhit.particleID==11:
						fill = 1
					else:
						fill = 2
				elif abs(simhit.particleID)==211:
					particle = 'proton'
					fill = 3
				elif abs(simhit.particleID)==2212:
					particle = 'pion'
					fill = 4
				else: # deuteron, oxygen, other nuclei, etc.
					particle = 'other'
					fill = 5
				# Fill for all particle types
				# Fill 1D histograms (per station)
				HISTS[neutronSim][station]['tof']['all'].Fill(tof)
				HISTS[neutronSim][station]['radial']['all'].Fill(gr)
				HISTS[neutronSim][station]['radial2']['all'].Fill(gr2)
				HISTS[neutronSim][station]['phi']['all'].Fill(gphi)
				HISTS[neutronSim][station]['z']['all'].Fill(gz)
				HISTS[neutronSim][station]['id']['all'].Fill(fill)
				# Fill 1D histograms (all stations)
				HISTS[neutronSim]['all']['tof']['all'].Fill(tof)
				HISTS[neutronSim]['all']['radial']['all'].Fill(gr)
				HISTS[neutronSim]['all']['radial2']['all'].Fill(gr2)
				HISTS[neutronSim]['all']['phi']['all'].Fill(gphi)
				HISTS[neutronSim]['all']['z']['all'].Fill(gz)
				HISTS[neutronSim]['all']['id']['all'].Fill(fill)
				# Fill for each particle type
				# Fill 1D histograms (per station)
				HISTS[neutronSim][station]['tof'][particle].Fill(tof)
				HISTS[neutronSim][station]['radial'][particle].Fill(gr)
				HISTS[neutronSim][station]['radial2'][particle].Fill(gr2)
				HISTS[neutronSim][station]['phi'][particle].Fill(gphi)
				HISTS[neutronSim][station]['z'][particle].Fill(gz)
				HISTS[neutronSim][station]['id'][particle].Fill(fill)
				# Fill 1D histograms (all stations)
				HISTS[neutronSim]['all']['tof'][particle].Fill(tof)
				HISTS[neutronSim]['all']['radial'][particle].Fill(gr)
				HISTS[neutronSim]['all']['radial2'][particle].Fill(gr2)
				HISTS[neutronSim]['all']['phi'][particle].Fill(gphi)
				HISTS[neutronSim]['all']['z'][particle].Fill(gz)
				HISTS[neutronSim]['all']['id'][particle].Fill(fill)

				# Fill for each particle type
				# Fill 2D histograms (per station)
				HISTS2D[neutronSim][station]['xy'][particle].Fill(gx,gy)
				HISTS2D[neutronSim][station]['rz'][particle].Fill(gz,gr)
				HISTS2D[neutronSim][station]['rphi'][particle].Fill(gphi,gr)
				HISTS2D[neutronSim][station]['rtof'][particle].Fill(tof,gr)
				HISTS2D[neutronSim][station]['phitof'][particle].Fill(tof,gphi)
				HISTS2D[neutronSim][station]['ztof'][particle].Fill(tof,gz)
				# Fill 2D histograms (all stations)
				HISTS2D[neutronSim]['all']['xy'][particle].Fill(gx,gy)
				HISTS2D[neutronSim]['all']['rz'][particle].Fill(gz,gr)
				HISTS2D[neutronSim]['all']['rphi'][particle].Fill(gphi,gr)
				HISTS2D[neutronSim]['all']['rtof'][particle].Fill(tof,gr)
				HISTS2D[neutronSim]['all']['phitof'][particle].Fill(tof,gphi)
				HISTS2D[neutronSim]['all']['ztof'][particle].Fill(tof,gz)
				# Fill for all particle types
				# Fill 2D histograms (per station)
				HISTS2D[neutronSim][station]['xy']['all'].Fill(gx,gy)
				HISTS2D[neutronSim][station]['rz']['all'].Fill(gz,gr)
				HISTS2D[neutronSim][station]['rphi']['all'].Fill(gphi,gr)
				HISTS2D[neutronSim][station]['rtof']['all'].Fill(tof,gr)
				HISTS2D[neutronSim][station]['phitof']['all'].Fill(tof,gphi)
				HISTS2D[neutronSim][station]['ztof']['all'].Fill(tof,gz)
				# Fill 2D histograms (all)
				HISTS2D[neutronSim]['all']['xy']['all'].Fill(gx,gy)
				HISTS2D[neutronSim]['all']['rz']['all'].Fill(gz,gr)
				HISTS2D[neutronSim]['all']['rphi']['all'].Fill(gphi,gr)
				HISTS2D[neutronSim]['all']['rtof']['all'].Fill(tof,gr)
				HISTS2D[neutronSim]['all']['phitof']['all'].Fill(tof,gphi)
				HISTS2D[neutronSim]['all']['ztof']['all'].Fill(tof,gz)

		outputROOT.cd()
		for station in stations:
			for particle in particles:
				HISTS[neutronSim][station]['tof'][particle].Write()
				HISTS[neutronSim][station]['radial'][particle].Write()
				HISTS[neutronSim][station]['radial2'][particle].Write()
				HISTS[neutronSim][station]['phi'][particle].Write()
				HISTS[neutronSim][station]['z'][particle].Write()
				HISTS[neutronSim][station]['id'][particle].Write()
				HISTS[neutronSim][station]['nSimHits'][particle].Write()
				HISTS2D[neutronSim][station]['xy'][particle].Write()
				HISTS2D[neutronSim][station]['rz'][particle].Write()
				HISTS2D[neutronSim][station]['rphi'][particle].Write()
				HISTS2D[neutronSim][station]['rtof'][particle].Write()
				HISTS2D[neutronSim][station]['phitof'][particle].Write()
				HISTS2D[neutronSim][station]['ztof'][particle].Write()
else:
	for neutronSim in HISTS.keys():
		name = 'h_'+neutronSim
		for station in stations:
			for particle in particles:
				HISTS[neutronSim][station]['tof'][particle]      = outputROOT.Get(name+'_'+str(station)+'_tof_'+particle)
				HISTS[neutronSim][station]['radial'][particle]   = outputROOT.Get(name+'_'+str(station)+'_radial_'+particle)
				HISTS[neutronSim][station]['radial2'][particle]  = outputROOT.Get(name+'_'+str(station)+'_radial2_'+particle)
				HISTS[neutronSim][station]['phi'][particle]      = outputROOT.Get(name+'_'+str(station)+'_phi_'+particle)
				HISTS[neutronSim][station]['z'][particle]        = outputROOT.Get(name+'_'+str(station)+'_z_'+particle)
				HISTS[neutronSim][station]['id'][particle]       = outputROOT.Get(name+'_'+str(station)+'_id_'+particle)
				HISTS[neutronSim][station]['nSimHits'][particle] = outputROOT.Get(name+'_'+str(station)+'_nSimHits_'+particle)
				HISTS2D[neutronSim][station]['xy'][particle]     = outputROOT.Get(name+'_'+str(station)+'_xy_'+particle)
				HISTS2D[neutronSim][station]['rz'][particle]     = outputROOT.Get(name+'_'+str(station)+'_rz_'+particle)
				HISTS2D[neutronSim][station]['rphi'][particle]   = outputROOT.Get(name+'_'+str(station)+'_rphi_'+particle)
				HISTS2D[neutronSim][station]['rtof'][particle]   = outputROOT.Get(name+'_'+str(station)+'_rtof_'+particle)
				HISTS2D[neutronSim][station]['phitof'][particle] = outputROOT.Get(name+'_'+str(station)+'_phitof_'+particle)
				HISTS2D[neutronSim][station]['ztof'][particle]   = outputROOT.Get(name+'_'+str(station)+'_ztof_'+particle)

def makePlots1D(HISTS,plotDict,particleTitles):
	for particle in particles:
		for name in ['tof','radial','radial2','phi','z','id','nSimHits']:
			for station in stations:
				for logy in [True,False]:

					# Normalize to 100k generated events
					SCALE = 100000.

					histHP_ON = HISTS['HP_Thermal_ON'][station][name][particle].Clone()
					if name=='nSimHits':
						histHP_ON = roottools.DrawOverflow(histHP_ON)
					histHP_ON.Scale(SCALE/fileDict['HP_Thermal_ON']['nEvts'])
					plotHP_ON = Plotter.Plot(histHP_ON,'HP Thermal ON',legType='l',option='hist')

					histHP_OFF = HISTS['HP_Thermal_OFF'][station][name][particle].Clone()
					if name=='nSimHits':
						histHP_OFF = roottools.DrawOverflow(histHP_OFF)
					histHP_OFF.Scale(SCALE/fileDict['HP_Thermal_OFF']['nEvts'])
					plotHP_OFF = Plotter.Plot(histHP_OFF,'HP Thermal OFF',legType='l',option='hist')

					histXS_ON = HISTS['XS_Thermal_ON'][station][name][particle].Clone()
					if name=='nSimHits':
						histXS_ON = roottools.DrawOverflow(histXS_ON)
					histXS_ON.Scale(SCALE/fileDict['XS_Thermal_ON']['nEvts'])
					plotXS_ON = Plotter.Plot(histXS_ON,'XS Thermal ON',legType='l',option='hist')
					
					histXS_OFF = HISTS['XS_Thermal_OFF'][station][name][particle].Clone()
					if name=='nSimHits':
						histXS_OFF = roottools.DrawOverflow(histXS_OFF)
					histXS_OFF.Scale(SCALE/fileDict['XS_Thermal_OFF']['nEvts'])
					plotXS_OFF = Plotter.Plot(histXS_OFF,'XS Thermal OFF',legType='l',option='hist')

					if name=='id':
						for plot in [plotXS_ON,plotXS_OFF,plotHP_ON,plotHP_OFF]:
							plot.GetXaxis().SetBinLabel(1,'#mu^{#pm}')
							plot.GetXaxis().SetBinLabel(2,'e^{-}')
							plot.GetXaxis().SetBinLabel(3,'e^{+}')
							plot.GetXaxis().SetBinLabel(4,'proton')
							plot.GetXaxis().SetBinLabel(5,'#pi^{#pm}')
							plot.GetXaxis().SetBinLabel(6,'other')
					canvas = Plotter.Canvas(lumi=particleTitles[particle]+' '+plotDict[name]['title']+' Station '+str(station),logy=logy)
					if 'tof' in name:
						canvas.mainPad.SetLogx(True)
					canvas.addMainPlot(plotXS_ON)
					canvas.addMainPlot(plotXS_OFF)
					canvas.addMainPlot(plotHP_OFF)
					canvas.addMainPlot(plotHP_ON)
					plotHP_ON.SetLineColor(fileDict['HP_Thermal_ON']['color'])
					plotHP_OFF.SetLineColor(fileDict['HP_Thermal_OFF']['color'])
					plotXS_ON.SetLineColor(fileDict['XS_Thermal_ON']['color'])
					plotXS_OFF.SetLineColor(fileDict['XS_Thermal_OFF']['color'])
					factor = 1.05
					maximum = max( plotHP_ON.GetMaximum(), plotHP_OFF.GetMaximum(), plotXS_ON.GetMaximum(), plotXS_OFF.GetMaximum() )
					canvas.firstPlot.SetMaximum(maximum*factor)
					plotHP_ON.setTitles(X=plotDict[name]['X'],Y=plotDict[name]['Y'])
					plotHP_OFF.setTitles(X=plotDict[name]['X'],Y=plotDict[name]['Y'])
					plotXS_OFF.setTitles(X=plotDict[name]['X'],Y=plotDict[name]['Y'])
					plotXS_ON.setTitles(X=plotDict[name]['X'],Y=plotDict[name]['Y'])
					canvas.makeLegend(pos='tr')
					if name=='z':
						canvas.legend.moveLegend(X=-0.4)
					else:
						canvas.legend.moveLegend(X=-0.1)
					canvas.makeTransparent()
					canvas.moveExponent()
					canvas.finishCanvas()
					canvas.save('pdfs/'+name+'_'+particle+'_'+str(station)+('_logy' if logy else '')+TITLE,['.pdf'])
					canvas.deleteCanvas()
				

def makePlots2D(HISTS2D,plotDict,particleTitles):
	for particle in particles:
		for name in ['xy','rz','rphi','rtof','phitof','ztof']:
			for station in stations:
				for neutronSim in HISTS2D.keys():
					hist = HISTS2D[neutronSim][station][name][particle]
					plot = Plotter.Plot(hist,option='colz')
					plot.setTitles(X=plotDict[name]['X'],Y=plotDict[name]['Y'])
					canvas = Plotter.Canvas(lumi=particleTitles[particle]+' '+plotDict[name]['title']+' Station '+str(station))
					if name in ['rtof','phitof','ztof']:
						canvas.mainPad.SetLogx(True)
					canvas.addMainPlot(plot)
					canvas.makeTransparent()
					canvas.finishCanvas()
					canvas.save('pdfs/'+neutronSim+'_'+name+'_'+particle+'_'+str(station)+TITLE,['.pdf'])
					canvas.deleteCanvas()

particleTitles = {
		'muon':'#mu^{#pm}',
		'e':'e^{#pm}',
		'pion':'#pi^{#pm}',
		'proton':'p',
		'other':'Other',
		'all':'All Particles',
}
plotDict = {
		'tof'   :{
			'X':'Time of Flight [ns]',
			'Y':'Counts',
			'title':'SimHit Time of Flight'},
		'radial2':{
			'X':'radius^{2} [cm^{2}]',
			'Y':'Counts',
			'title':'SimHit Squared Radial Position'},
		'radial':{
			'X':'radius [cm]',
			'Y':'Counts',
			'title':'SimHit Radial Position'},
		'phi'   :{
			'X':'#phi',
			'Y':'Counts',
			'title':'SimHit #phi'},
		'z'     :{
			'X':'z [cm]',
			'Y':'Counts',
			'title':'SimHit Z Position'},
		'id'    :{
			'X':'',
			'Y':'Counts',
			'title':'SimHit Particle Type'},
		'nSimHits':{
			'X':'N(SimHits)',
			'Y':'Counts',
			'title':'Number of SimHits per event'},
		'xy'    :{
			'X':'x position [cm]',
			'Y':'y position [cm]',
			'title':'SimHit Occupancy y vs. x'},
		'rz'    :{
			'X':'z position [cm]',
			'Y':'radial position [cm]',
			'title':'SimHit Occupancy r vs. z'},
		'rphi'  :{
			'X':'#phi',
			'Y':'radial position [cm]',
			'title':'SimHit Occupancy r vs. #phi'},
		'rtof'  :{
			'X':'Time of Flight [ns]',
			'Y':'radial position [cm]',
			'title':'SimHit r vs. tof'},
		'ztof'  :{
			'X':'Time of Flight [ns]',
			'Y':'z position [cm]',
			'title':'SimHit Z vs tof'},
		'phitof':{
			'X':'Time of Flight [ns]',
			'Y':'#phi',
			'title':'SimHit #phi vs tof'},
}

makePlots1D(HISTS,plotDict,particleTitles)
makePlots2D(HISTS2D,plotDict,particleTitles)

