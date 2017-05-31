'''
Analysis of comparator hits from MC
Output is
	- Comparator hit occupancy
	- Comparator hit timing
No attempt is made to clean comparator hits to include only neutron-
induced hits. All comparator hit are considered.
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
parser.add_argument('-tof','--TOF',action='store_false',dest='TOF',
		default=True,help='Use SH time of flight hack')
# Weight by area
parser.add_argument('-a','--area',action='store_true',dest='AREA',
		default=False,help='Weight digis by area')
# Weight by time
parser.add_argument('-t','--time',action='store_true',dest='TIME',
		default=False,help='Convert to rate per second')

args = parser.parse_args()

HP = args.HP
XS = args.XS
THERMAL = args.THERMAL
TOF = args.TOF
AREA = args.AREA
TIME = args.TIME

# Choose MC to use
if HP and XS:
	print 'Can\'t have XS and HP!'
	exit()

if HP:
	if THERMAL:
		if TOF:
			# HP Thermal ON + TOF Hack
			F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/ana_Neutron_MC_102100_NomTOF.root'
			#MS.F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/ana_Neutron_MC_25000_Hack3.root'
			outfile = 'hists_HP_Thermal_ON_TOF'+('_AREA' if AREA else '')+('_TIME' if TIME else '')+'.root'
		else:
			# HP Thermal ON
			F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/HP_Thermal_ON/ana_neutronMC_HPThermalON_105k_digi_hack.root'
			outfile = 'hists_HP_Thermal_ON'+('_AREA' if AREA else '')+('_TIME' if TIME else '')+'.root'
	else:
		if TOF:
			# HP Thermal OFF, + TOF Hack
			F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/HP_Thermal_OFF/tree_HP_ThermalOFF_tof.root'
			outfile = 'hists_HP_Thermal_OFF_TOF'+('_AREA' if AREA else '')+('_TIME' if TIME else '')+'.root'
		else:
			# HP Thermal OFF
			F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/HP_Thermal_OFF/ana_neutronMC_HPThermalOFF_digi_all.root'
			outfile = 'hists_HP_Thermal_OFF'+('_AREA' if AREA else '')+('_TIME' if TIME else '')+'.root'

elif XS:
	if THERMAL:
		if TOF:
			# XS Thermal ON, + TOF Hack
			F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_ON/ana_neutronMC_XS_ThermalON_tof.root'
			outfile = 'hists_XS_Thermal_ON_TOF'+('_AREA' if AREA else '')+('_TIME' if TIME else '')+'.root'
		else:
			# XS Thermal ON
			F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_ON/ana_neutronMC_XS_ThermalON.root'
			outfile = 'hists_XS_Thermal_ON'+('_AREA' if AREA else '')+('_TIME' if TIME else '')+'.root'
	else:
		if TOF:
			# XS Thermal OFF, + TOF Hack
			F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_OFF/ana_neutronMC_XS_Thermal_OFF_tof.root'
			outfile = 'hists_XS_Thermal_OFF_TOF'+('_AREA' if AREA else '')+('_TIME' if TIME else '')+'.root'
		else:
			# XS Thermal OFF
			F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_OFF/ana_neutronMC_XS_Thermal_OFF.root'
			outfile = 'hists_XS_Thermal_OFF'+('_AREA' if AREA else '')+('_TIME' if TIME else '')+'.root'
else:
	print 'Need to specify XS or HP'
	exit()



# Special MC files, not normally to be used

#MS.F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/hacktrees2/hacktree.root'
#MS.F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/nomtrees2/nomtree.root'

# old XS, Thermal OFF w/o digi hack
#MS.F_MCDATA = '/afs/cern.ch/user/c/cschnaib/Analysis/trees_mc/ana_neutronMC.root'

# HP Thermal ON, + TOF Hack, No Short Hack
#MS.F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/ana_Neutron_MC_25000_NomTOF.root'


RINGLIST = ['11', '12', '13', '21', '22', '31', '32', '41', '42']
#RINGLIST = ['-42', '-41', '-32', '-31', '-22', '-21', '-13', '-12', '-11', '+11', '+12', '+13', '+21', '+22', '+31', '+32', '+41', '+42']

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	#'MC'  : 'BGComp_MC.root'
	#'MC'  : 'BGComp_MC_XS_OFF.root'
	#'MC'  : 'BGComp_MC_XS_ON.root'
	#'MC'  : 'BGComp_MC_HP_OFF.root'
	#'MC'  : 'BGComp_MC_HP_ON.root'
	#'MC'  : 'BGComp_MC_HP_ON_Hack3.root'
	#'MC'  : 'BGComp_MC_HP_ON_NomTOF.root'
	#'MC' : 'root/hists_HP_Thermal_ON.root',
	#'MC' : 'root/hists_HP_Thermal_OFF.root',
	#'MC' : 'root/hists_XS_Thermal_ON.root',
	#'MC' : 'root/hists_XS_Thermal_OFF.root',
	'MC' : 'root/'+outfile
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
#TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)
FN = R.TFile.Open(F_MCDATA)
t = FN.Get('GIFTree/GIFDigiTree')
F_OUT = R.TFile('root/'+outfile,'RECREATE')
F_OUT.cd()
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

##### IMPLEMENT ANALYZERS #####

Primitives.SelectBranches(t, DecList=['COMP','WIRE'])
for idx, entry in enumerate(t):
	print 'Events:', idx+1, '\r',
	E = Primitives.ETree(t, DecList=['COMP','WIRE'])
	comps = [Primitives.Comp(E, i) for i in range(len(E.comp_cham))]
	wires = [Primitives.Wire(E, i) for i in range(len(E.wire_cham))]

	for comp in comps:
		cham = CH.Chamber(comp.cham)
		# thermal neutron comparator hits are in time bins 10 or later
		if comp.timeBin < 10: continue
		area = areaHists['comp'][cham.display('{S}{R}')].GetBinContent(comp.halfStrip) if AREA else 1.
		time = 25. * 10**(-9) if TIME else 1.
		weight = 1./(area*time)
		HISTS[cham.display('{E}{S}{R}')]['comp'].Fill(comp.halfStrip)
		HISTS[cham.display('{S}{R}')]['comp'].Fill(comp.halfStrip)
		PHI[cham.display('{E}{S}{R}')]['comp'].Fill(int(cham.display('{C}')))
		PHI[cham.display('{S}{R}')]['comp'].Fill(int(cham.display('{C}')))
	for wire in wires:
		cham = CH.Chamber(wire.cham)
		# thermal neutron wire group hits are in time bins 12 or later
		if wire.timeBin < 12: continue
		area = areaHists['wire'][cham.display('{S}{R}')].GetBinContent(wire.number) if AREA else 1.
		time = 25. * 10**(-9) if TIME else 1.
		weight = 1./(area*time)
		HISTS[cham.display('{E}{S}{R}')]['wire'].Fill(wire.number,weight)
		HISTS[cham.display('{S}{R}')]['wire'].Fill(wire.number,weight)
		PHI[cham.display('{E}{S}{R}')]['wire'].Fill(int(cham.display('{C}')),weight)
		PHI[cham.display('{S}{R}')]['wire'].Fill(int(cham.display('{C}')),weight)



F_OUT.cd()
for ring in RINGLIST:
	for E in ['+','-','']:
		HISTS[E+ring]['wire'].Write()
		HISTS[E+ring]['comp'].Write()
		PHI[E+ring]['wire'].Write()
		PHI[E+ring]['comp'].Write()

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
