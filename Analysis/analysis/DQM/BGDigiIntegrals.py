import os
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS

MS.F_MCDATA = '$WS/public/Neutron/hacktrees2/hacktree.root'

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'P5'  : 'Integrals_P5.root',
	'MC'  : 'Integrals_MC.root'
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

ringlist = ['-42', '-41', '-32', '-31', '-22', '-21', '-13', '-12', '-11', '+11', '+12', '+13', '+21', '+22', '+31', '+32', '+41', '+42']
ringmap  = range(-9,0) + range(1,10)
ringdict = dict(zip(ringlist, ringmap))

# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HISTS = {}
	self.HISTS['comp'] = R.TH1F('hComp', '', 20, -10, 10)
	self.HISTS['wire'] = R.TH1F('hWire', '', 20, -10, 10)
	for name in ['comp', 'wire']:
		self.HISTS[name].SetDirectory(0)

# once per file
def analyze(self, t, PARAMS):
	TYPE = PARAMS[1]
	if TYPE == 'P5':
		Primitives.SelectBranches(t, DecList=['LCT','COMP','WIRE'], branches=['Z_mass','Z_pT','nJets20'])
	elif TYPE == 'MC':
		Primitives.SelectBranches(t, DecList=['COMP','WIRE'])
	for idx, entry in enumerate(t):
		#if idx == 10000: break
		print 'Events:', idx+1, '\r',

		if TYPE == 'P5':
			if      t.Z_mass <= 98. and t.Z_mass >= 84.\
				and t.nJets20 == 0\
				and t.Z_pT <= 20.:
				pass
			else:
				continue

			if list(t.lct_id) == [] or list(t.comp_id) == []: continue
			E = Primitives.ETree(t, DecList=['LCT','COMP','WIRE'])
			lcts  = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham ))]
			comps = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham))]
			wires = [Primitives.Wire   (E, i) for i in range(len(E.wire_cham))]

			twolcts = list(set([i for i in E.lct_cham if E.lct_cham.count(i)>1]))
			for lct in lcts:
				if lct.cham in twolcts: continue
				nComp = 0
				cham = CH.Chamber(lct.cham)
				nHS = cham.nstrips*2
				nWG = cham.nwires
				if cham.station==1 and cham.ring==1:
					# ME1/1a and ME1/1b are separated by a cut in the strips.
					# Since wires are tilted use the a/b divider as a crude radial cut
					# on LCT position instead of wires.
					# ME1/1b : strips  1 to  64 (top)    | hs   0 to 127 (top)
					# ME1/1a : strips 65 to 112 (bottom) | hs 128 to 224 (bottom)
					# (remember strips are numbered from 1 while hs are numbered from 0!)
					#
					# For ME1/1 the +/- endcaps are 'flipped' wrt each other
					# (+,0) is (-,3) and vice versa
					# (+,1) is (-,2) and vice versa
					# Does not actually matter for what we are doing but important to keep in mind!
					#
					# -> LCTAreas are defined for ME+1/1
					# ME+1/1b - 1 : (  0, 31) , 2 : ( 95,127) (hs are numbered R to L - top)
					# ME+1/1a - 0 : (200,224) , 3 : (128,152) (hs are numbered L to R - bottom)
					#
					# For opposite area, the set of opposite half halfstrips are disjoint for LCT 
					# areas 2 and 3
					#
					# -> OppAreas are defined for ME+1/1
					#           (top) +   (bottom)
					# 0,1 : (64, 127) + (128, 171)
					# 2,3 : ( 0,  63) + (172, 223)
					LCTAreas = \
					{
						0 : {'wg0' : 0. , 'wg1' : nWG , 'hs0' : 200. , 'hs1' : 223},
						1 : {'wg0' : 0. , 'wg1' : nWG , 'hs0' : 0.   , 'hs1' : 31 },
						2 : {'wg0' : 0. , 'wg1' : nWG , 'hs0' : 96   , 'hs1' : 127},
						3 : {'wg0' : 0. , 'wg1' : nWG , 'hs0' : 128  , 'hs1' : 151},
					}
					OppAreas = \
					{
						0 : {'hs0' : 64 , 'hs1' : 127 , 'hs2' : 128 , 'hs3' : 171},
						1 : {'hs0' : 64 , 'hs1' : 127 , 'hs2' : 128 , 'hs3' : 171},
						2 : {'hs0' :  0 , 'hs1' :  63 , 'hs2' : 172 , 'hs3' : 223},
						3 : {'hs0' :  0 , 'hs1' :  63 , 'hs2' : 172 , 'hs3' : 223},
					}
				else:
					LCTAreas = \
					{
						0 : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : 0.          , 'hs1' : nHS*0.25},
						1 : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : 0.          , 'hs1' : nHS*0.25},
						2 : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
						3 : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
					}
					OppAreas = \
					{
						0 : {'hs0' : (1-0.50)*nHS, 'hs1' : nHS     },
						1 : {'hs0' : (1-0.50)*nHS, 'hs1' : nHS     },
						2 : {'hs0' : 0.          , 'hs1' : nHS*0.50},
						3 : {'hs0' : 0.          , 'hs1' : nHS*0.50},
					}
				# Loop on all areas (we've already forced there to be only one LCT in this chamber)
				for key in LCTAreas.keys():
					# If LCT in a corner
					if  lct.keyWireGroup >= LCTAreas[key]['wg0'] and lct.keyWireGroup <= LCTAreas[key]['wg1']\
					and lct.keyHalfStrip >= LCTAreas[key]['hs0'] and lct.keyHalfStrip <= LCTAreas[key]['hs1']:
						for comp in comps:
							if comp.cham != lct.cham: continue
							# For comparators in opposite half of LCT
							OPPAREA = False
							if cham.station==1 and cham.ring==1:
								if ((comp.staggeredHalfStrip >= OppAreas[key]['hs0'] and comp.staggeredHalfStrip <= OppAreas[key]['hs1'])\
										or \
									(comp.staggeredHalfStrip >= OppAreas[key]['hs2'] and comp.staggeredHalfStrip <= OppAreas[key]['hs3'])):
									OPPAREA = True
							else:
								if comp.staggeredHalfStrip >= OppAreas[key]['hs0'] and comp.staggeredHalfStrip <= OppAreas[key]['hs1']:
									OPPAREA = True
							if OPPAREA:
								if comp.timeBin >= 1 and comp.timeBin <= 5:
									self.HISTS['comp'].Fill(ringdict[cham.display('{E}{S}{R}')])

			for lct in lcts:
				if lct.cham in twolcts: continue
				nWire = 0
				cham = CH.Chamber(lct.cham)
				nHS = cham.nstrips*2
				nWG = cham.nwires
				if cham.station==1 and cham.ring==1:
					# ME1/1 has wires tilted at 29 degrees wrt local +x axis
					# Instead of requiring that the LCT is in a "corner", for 
					# ME1/1 we use "bottom" and "top" parts to look for an LCT
					# "Bottom" is defined as  1 <= kwg <= 12 (0,3)
					# "Top"    is defined as 37 <= kwg <= 48 (1,2)
					# (Only defined differently because in ME1/1 we don't 
					#  make any requirement on the HS of the LCT)
					LCTAreas = \
					{
						0 : {'wg0' :  1. , 'wg1' : 12. , 'hs0' : 0. , 'hs1' : nHS},
						1 : {'wg0' : 37. , 'wg1' : 48. , 'hs0' : 0. , 'hs1' : nHS},
						2 : {'wg0' : 37. , 'wg1' : 48. , 'hs0' : 0. , 'hs1' : nHS},
						3 : {'wg0' :  1. , 'wg1' : 12. , 'hs0' : 0. , 'hs1' : nHS},
					}
					# ME1/1 opposite areas are the other "half"
					# keys correspond to LCT location
					# "Bottom" LCTs -> Look for wgs in 25 <= wg <= 48 (0,3)
					#    "Top" LCTs -> Look for wgs in  1 <= wg <= 24 (1,2)
					# (Same for all other chambers but defined explicitly for ME1/1)
					OppAreas = \
					{
						0 : {'wg0' :  25 , 'wg1' : 48 },
						1 : {'wg0' :   1 , 'wg1' : 24 },
						2 : {'wg0' :   1 , 'wg1' : 24 },
						3 : {'wg0' :  25 , 'wg1' : 48 },
					}
				else:
					LCTAreas = \
					{
						0 : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : 0.          , 'hs1' : nHS*0.25},
						1 : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : 0.          , 'hs1' : nHS*0.25},
						2 : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
						3 : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
					}
					OppAreas = \
					{
						0 : {'wg0' : (1-0.50)*nWG, 'wg1' : nWG     },
						1 : {'wg0' : 0.          , 'wg1' : nWG*0.50},
						2 : {'wg0' : 0.          , 'wg1' : nWG*0.50},
						3 : {'wg0' : (1-0.50)*nWG, 'wg1' : nWG     },
					}
				for key in LCTAreas.keys():
					if  lct.keyWireGroup >= LCTAreas[key]['wg0'] and lct.keyWireGroup <= LCTAreas[key]['wg1']\
					and lct.keyHalfStrip >= LCTAreas[key]['hs0'] and lct.keyHalfStrip <= LCTAreas[key]['hs1']:
						for wire in wires:
							if wire.cham != lct.cham: continue
							if wire.number >= OppAreas[key]['wg0'] and wire.number <= OppAreas[key]['wg1']:
								if wire.timeBin >= 1 and wire.timeBin <= 5:
									self.HISTS['wire'].Fill(ringdict[cham.display('{E}{S}{R}')])

		elif TYPE == 'MC':
			E = Primitives.ETree(t, DecList=['COMP','WIRE'])
			comps = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham))]
			wires = [Primitives.Wire   (E, i) for i in range(len(E.wire_cham))]

			for comp in comps:
				cham = CH.Chamber(comp.cham)
				self.HISTS['comp'].Fill(ringdict[cham.display('{E}{S}{R}')])

			for wire in wires:
				cham = CH.Chamber(comp.cham)
				self.HISTS['wire'].Fill(ringdict[cham.display('{E}{S}{R}')])

	self.F_OUT.cd()
	for name in ['comp', 'wire']:
		self.HISTS[name].Write()

# if file is already made
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	self.HISTS['comp'] = f.Get('hComp')
	self.HISTS['wire'] = f.Get('hWire')
	for name in ['comp', 'wire']:
		self.HISTS[name].SetDirectory(0)

def cleanup(self, PARAMS):
	pass
	print ''

##### DECLARE ANALYZERS AND RUN ANALYSIS #####
R.gROOT.SetBatch(True)
METHODS = ['analyze', 'load', 'setup', 'cleanup']
ARGS = {\
	'PARAMS'     : [OFN, TYPE],
	'F_DATAFILE' : FDATA
}
if TYPE == 'GIF':
	ARGS['ATTLIST'] = [float('inf')]
Analyzer = getattr(MS, TYPE+'Analyzer')
for METHOD in METHODS:
	setattr(Analyzer, METHOD, locals()[METHOD])
data = Analyzer(**ARGS)

##### MAKEPLOT FUNCTIONS #####
def makePlot(h, NAME):
	plot = Plotter.Plot(h, option='hist')

	canvas = Plotter.Canvas(lumi='Background {NAME} by Ring, {TYPE}'.format(NAME='Comparators' if NAME=='comp' else 'Wires', TYPE=TYPE), cWidth=1000)

	canvas.addMainPlot(plot)

	canvas.makeTransparent()
	h.GetXaxis().SetRangeUser(-9,10)
	for ring in ringlist:
		bin_ = ringdict[ring] + 11
		h.GetXaxis().SetBinLabel(bin_, ring.replace('-','#minus'))
	plot.SetLineColor(0)
	plot.SetFillColor(R.kOrange)
	plot.scaleLabels(1.25, 'X')
	plot.setTitles(X='CSC Ring', Y='Counts')

	canvas.finishCanvas()
	canvas.save('pdfs/Integral_{NAME}_{TYPE}.pdf'.format(NAME=NAME,TYPE=TYPE))
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

for NAME in data.HISTS:
	makePlot(data.HISTS[NAME], NAME)
