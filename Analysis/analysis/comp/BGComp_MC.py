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
MS.F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/ana_Neutron_MC_25000_NomTOF.root'

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
	'MC'  : 'BGComp_MC_HP_ON_NomTOF.root'
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

##### IMPLEMENT ANALYZERS #####
def analyze(self, t, PARAMS):
	Primitives.SelectBranches(t, DecList=['COMP'])
	for idx, entry in enumerate(t):
		print 'Events:', idx+1, '\r',
		E = Primitives.ETree(t, DecList=['COMP'])
		comps = [Primitives.Comp(E, i) for i in range(len(E.comp_cham))]

		for comp in comps:
			cham = CH.Chamber(comp.cham)
			self.HISTS[cham.display('{E}{S}{R}')]['time'].Fill(comp.timeBin)
			self.HISTS[cham.display('{E}{S}{R}')]['occ' ].Fill(comp.halfStrip)
			self.HISTS[cham.display('{S}{R}')]['time'].Fill(comp.timeBin)
			#self.HISTS[cham.display('{S}{R}')]['occ' ].Fill(comp.staggeredHalfStrip)
			#if comp.timeBin < 10: continue
			self.HISTS[cham.display('{S}{R}')]['occ' ].Fill(comp.halfStrip)

	self.F_OUT.cd()
	for ring in RINGLIST:
		for E in ['+','-','']:
			self.HISTS[E+ring]['time'].Write()
			self.HISTS[E+ring]['occ' ].Write()

def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	for ring in RINGLIST:
		for E in ['+','-','']:
			self.HISTS[E+ring] = {
				'time' : f.Get('t'+E+ring),
				'occ'  : f.Get('o'+E+ring),
			}
			self.HISTS[E+ring]['time'].SetDirectory(0)
			self.HISTS[E+ring]['occ' ].SetDirectory(0)

def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HISTS = {}
	for ring in RINGLIST:
		for E in ['+','-','']:
			cham = CH.Chamber(CH.serialID(1, int(ring[0]), int(ring[1]), 1))
			bins = cham.nstrips*2+2
			self.HISTS[E+ring] = {
				'time': R.TH1F('t'+E+ring, '', 10, 0., 10.),
				'occ' : R.TH1F('o'+E+ring, '', bins, 0., bins),
			}
			self.HISTS[E+ring]['time'].SetDirectory(0)
			self.HISTS[E+ring]['occ' ].SetDirectory(0)

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

#for ring in RINGLIST:
#	makePlot(data.HISTS[ring]['time'], ring, 'time')
#	makePlot(data.HISTS[ring]['occ' ], ring, 'occ' )
