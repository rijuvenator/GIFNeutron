'''
Analysis of wire group hits from MC
Output is
	- Comparator hit occupancy
	- Comparator hit timing
No attempt is made to clean wire group hits to include only neutron-
induced hits. All wire group hit are considered.
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
# HP Thermal ON, + TOF Hack
MS.F_MCDATA = '/afs/cern.ch/work/a/adasgupt/public/Neutron/ana_Neutron_MC_102100_NomTOF.root'
RINGLIST = ['11', '12', '13', '21', '22', '31', '32', '41', '42']

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	#'MC'  : 'BGWire_MC_XS_OFF.root'
	#'MC'  : 'BGWire_MC_XS_ON.root'
	#'MC'  : 'BGWire_MC_HP_OFF.root'
	#'MC'  : 'BGWire_MC_HP_ON.root'
	#'MC'  : 'BGWire_MC_HP_ON_Hack3.root'
	'MC'  : 'BGWire_MC_HP_ON_NomTOF.root'
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

##### IMPLEMENT ANALYZERS #####
def analyze(self, t, PARAMS):
	Primitives.SelectBranches(t, DecList=['WIRE'])
	for idx, entry in enumerate(t):
		print 'Events:', idx+1, '\r',
		E = Primitives.ETree(t, DecList=['WIRE'])
		wires = [Primitives.Wire(E, i) for i in range(len(E.wire_cham))]

		for wire in wires:
			cham = CH.Chamber(wire.cham)
			self.HISTS[cham.display('{E}{S}{R}')]['time'].Fill(wire.timeBin)
			self.HISTS[cham.display('{E}{S}{R}')]['occ' ].Fill(wire.number)
			self.HISTS[cham.display('{S}{R}')]['time'].Fill(wire.timeBin)
			if wire.timeBin < 12: continue
			self.HISTS[cham.display('{S}{R}')]['occ' ].Fill(wire.number)

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
			self.HISTS[E+ring] = {
				'time': R.TH1F('t'+E+ring, '', 10, 0., 10.),
				'occ' : R.TH1F('o'+E+ring, '', cham.nwires+10, 0., cham.nwires+10),
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
	canvas.save('pdfs/BGWireMC'+tag+'_'+ring+'.pdf')

#for ring in RINGLIST:
#	makePlot(data.HISTS[ring]['time'], ring, 'time')
#	makePlot(data.HISTS[ring]['occ' ], ring, 'occ' )
