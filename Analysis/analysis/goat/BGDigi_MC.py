'''
Analysis of comparator hits from MC
Output is
	- Comparator hit occupancy
	- Comparator hit timing
'''
import sys, os, argparse
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
R.gROOT.SetBatch(True)
# area histograms calculated on the fly
import areas as areas
areaHists = areas.areaHists

parser = argparse.ArgumentParser()

# HP/XS (necessary)
parser.add_argument('-hp','--HP',action='store_true',dest='HP',
		default=False,help='Use HP neutron library')
parser.add_argument('-xs','--XS',action='store_true',dest='XS',
		default=False,help='Use XS neutron library')
# Thermal ON/OFF
parser.add_argument('-therm','--thermal',action='store_true',dest='THERMAL',
		default=False,help='Use neutron thermalization')
# SimHit time of flight hack (default is true)
parser.add_argument('-tof','--TOF',action='store_true',dest='TOF',
		default=False,help='Use SH time of flight hack')
# Weight by area
parser.add_argument('-a','--area',action='store_true',dest='AREA',
		default=False,help='Weight digis by area')
# Weight by time
parser.add_argument('-t','--time',action='store_true',dest='TIME',
		default=False,help='Convert to rate per second')
# Which Geometry to use
parser.add_argument('-geo','--GEO',dest='GEO',
		default='',help='Use 2016 Geometry')
# add an extra input root file name for special tests
parser.add_argument('-in','--inname',dest='INNAME',
		default='',help='Add an extra optional input root filename for speicial tests')
# add an extra output root file name for special tests
parser.add_argument('-out','--outname',dest='OUTNAME',
		default='',help='Add an extra optional output root filename for speicial tests')

args = parser.parse_args()

HP = args.HP
XS = args.XS
THERMAL = args.THERMAL
TOF = args.TOF
AREA = args.AREA
TIME = args.TIME
GEO = args.GEO
INNAME = args.INNAME
OUTNAME = args.OUTNAME
 
if GEO=='':
	print 'Need to specify geometry'

# Choose MC to use
if HP and XS:
	print 'Can\'t have XS and HP!'
	exit()

# HP Thermal ON + TOF Hack
#/afs/cern.ch/work/a/adasgupt/public/Neutron/ana_Neutron_MC_102100_NomTOF.root
#MS./afs/cern.ch/work/a/adasgupt/public/Neutron/ana_Neutron_MC_25000_Hack3.root
# HP Thermal ON
#/afs/cern.ch/work/c/cschnaib/public/NeutronSim/HP_Thermal_ON/ana_neutronMC_HPThermalON_105k_digi_hack.root
# HP Thermal OFF, + TOF Hack
#/afs/cern.ch/work/c/cschnaib/public/NeutronSim/HP_Thermal_OFF/tree_HP_ThermalOFF_tof.root
# HP Thermal OFF
#/afs/cern.ch/work/c/cschnaib/public/NeutronSim/HP_Thermal_OFF/ana_neutronMC_HPThermalOFF_digi_all.root
# XS Thermal ON, + TOF Hack
#/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_ON/ana_neutronMC_XS_ThermalON_tof.root
# XS Thermal ON
#/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_ON/ana_neutronMC_XS_ThermalON.root
# XS Thermal OFF + TOF Hack + 2016CavernGeo
#/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_OFF/MinBias_XSThermalOFF_2016CavernGeo_TREE.root
# XS Thermal OFF + TOF Hack + 2016Geo
#/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_OFF/MinBias_XSThermalOFF_2016Geo_TREE.root
# XS Thermal OFF + TOF Hack + 2015Geo
#/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_OFF/ana_neutronMC_XS_Thermal_OFF_tof.root
# XS Thermal OFF, NO TOF Hack, 2015Geo
#/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_OFF/ana_neutronMC_XS_Thermal_OFF.root
# Special MC files, not normally to be used
#MS.F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/hacktrees2/hacktree.root'
#MS.F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/nomtrees2/nomtree.root'
# old XS, Thermal OFF w/o digi hack
#MS.F_MCDATA = '/afs/cern.ch/user/c/cschnaib/Analysis/trees_mc/ana_neutronMC.root'
# HP Thermal ON, + TOF Hack, No Short Hack
#MS.F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/ana_Neutron_MC_25000_NomTOF.root'

# Generate input/output MC file
CHRISPUBLIC = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/'
F_MCDATA = CHRISPUBLIC+'MinBias'+('_XS' if XS else '_HP')+('_ThermalON' if THERMAL else '_ThermalOFF')+('_TOF' if TOF else '')+('_'+GEO if GEO!='' else '')+('_'+INNAME if INNAME!='' else '')+'.root'
outfile = 'root/hists_'+('XS' if XS else 'HP')\
		+('_ThermalON' if THERMAL else '_ThermalOFF')\
		+('_TOF' if TOF else '')\
		+('_'+GEO if GEO!='' else '')\
		+('_AREA' if AREA else '')\
		+('_TIME' if TIME else '')\
		+('_'+OUTNAME if OUTNAME!='' else '')\
		+'.root'

#### SETUP SCRIPT #####
FN = R.TFile.Open(F_MCDATA)
t = FN.Get('GIFTree/GIFDigiTree')
F_OUT = R.TFile(outfile,'RECREATE')
print '''
INPUT : {F_MCDATA}
OUTPUT : {outfile}
'''.format(**locals())
F_OUT.cd()

RINGLIST = ['11','21','31','41','12','13','22','32','42']
ERINGLIST = ['+11','-11','+21','-21','+31','-31','+41','-41',
			 '+12','-12','+13','-13','+22','-22','+32','-32','+42','-42']
ringMap = {ring:i for i,ring in enumerate(RINGLIST)}
eringMap = {ring:i for i,ring in enumerate(ERINGLIST)}

HISTS = {}
PHI= {}
for ring in RINGLIST:
	for E in ['+','-','']:
		cham = CH.Chamber(CH.serialID(1, int(ring[0]), int(ring[1]), 1))
		nhs = cham.nstrips*2
		nwires = cham.nwires
		HISTS[E+ring] = {
			'wire' : R.TH1F(E+ring+'_wire_occ', '', nwires+2, 0., nwires+2),
			'comp' : R.TH1F(E+ring+'_comp_occ', '', nhs+2, 0., nhs+2),
		}
		HISTS[E+ring]['comp'].SetDirectory(0)
		HISTS[E+ring]['wire'].SetDirectory(0)
		if ring=='21' or ring=='31' or ring=='41':
			ncham = 18
		else:
			ncham = 36
		PHI[E+ring] = {
				'wire' : R.TH1F('phi_'+E+ring+'_wire_occ','',ncham,1,ncham+1),
				'comp' : R.TH1F('phi_'+E+ring+'_comp_occ','',ncham,1,ncham+1),
				}
		PHI[E+ring]['comp'].SetDirectory(0)
		PHI[E+ring]['wire'].SetDirectory(0)

INTHISTS = {digi:{} for digi in ['comp','wire']}
for digi in ['comp','wire']:
	INTHISTS[digi]['sep'] = R.TH1D(digi+'_int_sep','',18,0,18)
	INTHISTS[digi]['comb'] = R.TH1D(digi+'_int_comb','',9,0,9)
	INTHISTS[digi]['sep'].SetDirectory(0)
	INTHISTS[digi]['comb'].SetDirectory(0)

##### IMPLEMENT ANALYZERS #####

Primitives.SelectBranches(t, DecList=['COMP','WIRE'])
eventWeight = 1./t.GetEntries()
for idx, entry in enumerate(t):
	print 'Events:', idx+1, '\r',
	E = Primitives.ETree(t, DecList=['COMP','WIRE'])
	comps = [Primitives.Comp(E, i) for i in range(len(E.comp_cham))]
	wires = [Primitives.Wire(E, i) for i in range(len(E.wire_cham))]

	for comp in comps:
		cham = CH.Chamber(comp.cham)
		# comp.halfStrip0 counts hs from 0 to 2*(s-1)+c
		# thermal neutron comparator hits are in time bins 10 or later
		if comp.timeBin < 10: continue
		# Set event weights (per area per time done elsewhere)
		if cham.display('{S}{R}') in ['21','31','41']:
			ncham = 18.
		else:
			ncham = 36.
		ecWeight = eventWeight/ncham # weight for a singe endcap
		weight = eventWeight/ncham/2. # weight for combined endcaps
		# Fill histograms
		HISTS[cham.display('{E}{S}{R}')]['comp'].Fill(comp.halfStrip0+2,ecWeight)
		HISTS[cham.display('{S}{R}')]['comp'].Fill(comp.halfStrip0+2,weight)
		PHI[cham.display('{E}{S}{R}')]['comp'].Fill(int(cham.display('{C}')),eventWeight)
		PHI[cham.display('{S}{R}')]['comp'].Fill(int(cham.display('{C}')),eventWeight/2.)
		INTHISTS['comp']['sep'].Fill(eringMap[cham.display('{E}{S}{R}')],ecWeight)
		INTHISTS['comp']['comb'].Fill(ringMap[cham.display('{S}{R}')],weight)
	for wire in wires:
		cham = CH.Chamber(wire.cham)
		# thermal neutron wire group hits are in time bins 12+ for 2015 and 11+ for 2016 geometries
		TCUT = 12 if GEO=='2015Geo' else 11
		if wire.timeBin < TCUT: continue
		# Set event weights (per area per time done elsewhere)
		if cham.display('{S}{R}') in ['21','31','41']:
			ncham = 18.
		else:
			ncham = 36.
		ecWeight = eventWeight/ncham # weight for a singe endcap
		weight = eventWeight/ncham/2. # weight for combined endcaps
		# Fill histograms
		HISTS[cham.display('{E}{S}{R}')]['wire'].Fill(wire.number,ecWeight)
		HISTS[cham.display('{S}{R}')]['wire'].Fill(wire.number,weight)
		PHI[cham.display('{E}{S}{R}')]['wire'].Fill(int(cham.display('{C}')),eventWeight)
		PHI[cham.display('{S}{R}')]['wire'].Fill(int(cham.display('{C}')),eventWeight/2.)
		INTHISTS['wire']['sep'].Fill(eringMap[cham.display('{E}{S}{R}')],ecWeight)
		INTHISTS['wire']['comb'].Fill(ringMap[cham.display('{S}{R}')],weight)



F_OUT.cd()
for ring in RINGLIST:
	for E in ['+','-','']:
		HISTS[E+ring]['wire'].Write()
		HISTS[E+ring]['comp'].Write()
		PHI[E+ring]['wire'].Write()
		PHI[E+ring]['comp'].Write()
for digi in ['comp','wire']:
	for pType in ['sep','comb']:
		INTHISTS[digi][pType].Write()

##### MAKE PLOTS #####
def makePlot(hist, ring, tag):
	plot = Plotter.Plot(hist, legName='', legType='l', option='hist')
	canvas = Plotter.Canvas(lumi='ME'+ring)
	canvas.addMainPlot(plot)
	canvas.finishCanvas()
	canvas.save('pdfs/BGCompMC'+tag+'_'+ring+'.pdf')

#for digi in ['comp','wire']:
#	for ring in RINGLIST:
#		makePlot(data.HISTS[ring][digi], ring, digi )
