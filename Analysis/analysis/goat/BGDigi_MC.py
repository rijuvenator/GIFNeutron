'''
Analysis of comparator hits from MC
Output is
	- Comparator hit occupancy
	- Comparator hit timing
No attempt is made to clean comparator hits to include only neutron-
induced hits. All comparator hit are considered.
'''
import sys, os
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS

#MS.F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/hacktrees2/hacktree.root'
#MS.F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/nomtrees2/nomtree.root'
# old XS, Thermal OFF w/o digi hack
#MS.F_MCDATA = '/afs/cern.ch/user/c/cschnaib/Analysis/trees_mc/ana_neutronMC.root'

# XS Thermal OFF
#MS.F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_OFF/ana_neutronMC_XS_Thermal_OFF.root'
# XS Thermal ON
#MS.F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_ON/ana_neutronMC_XS_ThermalON.root'
# HP Thermal OFF
#MS.F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/HP_Thermal_OFF/ana_neutronMC_HPThermalOFF_digi_all.root'
# HP Thermal ON
#MS.F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/HP_Thermal_ON/ana_neutronMC_HPThermalON_105k_digi_hack.root'
# HP Thermal ON, + TOF Hack
#MS.F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/ana_Neutron_MC_25000_Hack3.root'

# HP Thermal ON, + TOF Hack, No Short Hack
#MS.F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/ana_Neutron_MC_25000_NomTOF.root'

# HP Thermal ON + TOF Hack
MS.F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/ana_Neutron_MC_102100_NomTOF.root'
# HP Thermal OFF, + TOF Hack
#MS.F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/HP_Thermal_OFF/tree_HP_ThermalOFF_tof.root'
# XS Thermal ON, + TOF Hack
#MS.F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_ON/ana_neutronMC_XS_ThermalON_tof.root'
# XS Thermal OFF, + TOF Hack
#MS.F_MCDATA = '/afs/cern.ch/work/c/cschnaib/public/NeutronSim/XS_Thermal_OFF/ana_neutronMC_XS_Thermal_OFF_tof.root'

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
	'MC' : 'root/hists_HP_Thermal_ON.root',
	#'MC' : 'root/hists_HP_Thermal_OFF.root',
	#'MC' : 'root/hists_XS_Thermal_ON.root',
	#'MC' : 'root/hists_XS_Thermal_OFF.root',
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

##### IMPLEMENT ANALYZERS #####
def analyze(self, t, PARAMS):
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
			self.HISTS[cham.display('{E}{S}{R}')]['comp'].Fill(comp.halfStrip)
			self.HISTS[cham.display('{S}{R}')]['comp'].Fill(comp.halfStrip)
			self.PHI[cham.display('{E}{S}{R}')]['comp'].Fill(int(cham.display('{C}')))
			self.PHI[cham.display('{S}{R}')]['comp'].Fill(int(cham.display('{C}')))
		for wire in wires:
			cham = CH.Chamber(wire.cham)
			# thermal neutron wire group hits are in time bins 12 or later
			if wire.timeBin < 12: continue
			self.HISTS[cham.display('{E}{S}{R}')]['wire'].Fill(wire.number)
			self.HISTS[cham.display('{S}{R}')]['wire'].Fill(wire.number)
			self.PHI[cham.display('{E}{S}{R}')]['wire'].Fill(int(cham.display('{C}')))
			self.PHI[cham.display('{S}{R}')]['wire'].Fill(int(cham.display('{C}')))



	self.F_OUT.cd()
	for ring in RINGLIST:
		for E in ['+','-','']:
			self.HISTS[E+ring]['wire'].Write()
			self.HISTS[E+ring]['comp'].Write()
			self.PHI[E+ring]['wire'].Write()
			self.PHI[E+ring]['comp'].Write()

def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	self.PHI= {}
	for ring in RINGLIST:
		for E in ['+','-','']:
			self.HISTS[E+ring] = {
				'comp'  : f.Get(E+ring+'_comp_occ'),
				'wire'  : f.Get(E+ring+'_wire_occ'),
			}
			self.HISTS[E+ring]['comp' ].SetDirectory(0)
			self.HISTS[E+ring]['wire' ].SetDirectory(0)
			self.PHI[E+ring] = {
				'comp'  : f.Get('phi_'+E+ring+'_comp_occ'),
				'wire'  : f.Get('phi_'+E+ring+'_wire_occ'),
			}
			self.PHI[E+ring]['comp' ].SetDirectory(0)
			self.PHI[E+ring]['wire' ].SetDirectory(0)

def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HISTS = {}
	self.PHI= {}
	for ring in RINGLIST:
		for E in ['+','-','']:
			cham = CH.Chamber(CH.serialID(1, int(ring[0]), int(ring[1]), 1))
			nhs = cham.nstrips*2
			nwires = cham.nwires
			self.HISTS[E+ring] = {
				'wire' : R.TH1F(E+ring+'_wire_occ', '', nwires+2, 0., nwires+2),
				'comp' : R.TH1F(E+ring+'_comp_occ', '', nhs+2, 0., nhs+2),
			}
			self.HISTS[E+ring]['comp'].SetDirectory(0)
			self.HISTS[E+ring]['wire'].SetDirectory(0)
			if ring=='21' or ring=='31' or ring=='41':
				ncham = 18
			else:
				ncham = 36
			self.PHI[E+ring] = {
					'wire' : R.TH1F('phi_'+E+ring+'_wire_occ','',ncham,1,ncham+1),
					'comp' : R.TH1F('phi_'+E+ring+'_comp_occ','',ncham,1,ncham+1),
					}
			self.PHI[E+ring]['comp'].SetDirectory(0)
			self.PHI[E+ring]['wire'].SetDirectory(0)

def cleanup(self, PARAMS):
	pass
	print ''

##### DECLARE ANALYZERS AND RUN ANALYSIS #####
R.gROOT.SetBatch(True)
METHODS = ['analyze', 'load', 'setup', 'cleanup']
ARGS = {
	'PARAMS'     : [OFN, TYPE],
	'F_DATAFILE' : FDATA
}
if TYPE == 'GIF':
	ARGS['ATTLIST'] = [float('inf')]
Analyzer = getattr(MS, TYPE+'Analyzer')
for METHOD in METHODS:
	setattr(Analyzer, METHOD, locals()[METHOD])
data = Analyzer(**ARGS)

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
