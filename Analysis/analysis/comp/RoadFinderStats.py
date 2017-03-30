import os, math, sys
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'GIF' : 'bgpatterns_GIF.root',
	'P5'  : 'bgpatterns_P5.root',
	'MC'  : 'bgpatterns_MC.root'
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

##### ANALYZER FUNCTIONS #####
# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	pass

# once per file
def analyze(self, t, PARAMS):
	TYPE = PARAMS[1]
	DATA = {
		'passZ'   : {'elim' : 0, 'tot' : 0},
		'passBX'  : {'elim' : 0, 'tot' : 0},
		'passZBX' : {'elim' : 0, 'tot' : 0},
	}
	for idx, entry in enumerate(t):
		if idx%1000 == 0: print 'Events:', idx, '\r',

		passZ, passBX, passZBX = False, False, False

		if      t.Z_mass <= 98. and t.Z_mass >= 84.\
			and t.nJets20 == 0\
			and t.Z_pT <= 20.:
				passZ = True

		size, diff, train = self.getBunchInfo(t.Event_RunNumber, t.Event_BXCrossing, minSize=35)
		if size != 0:
			passBX = True

		passZBX = passZ and passBX


		if list(t.lct_id) == [] or list(t.comp_id) == []: continue
		E = Primitives.ETree(t, DecList=['LCT','COMP','WIRE'])
		lcts  = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham ))]
		comps = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham))]

		twolcts = list(set([i for i in E.lct_cham if E.lct_cham.count(i)>1]))
		for lct in lcts:
			if lct.cham in twolcts: continue

			DATA['passZ'  ]['tot'] += passZ
			DATA['passBX' ]['tot'] += passBX
			DATA['passZBX']['tot'] += passZBX

			cham = CH.Chamber(lct.cham)
			nHS = cham.nstrips*2
			nWG = cham.nwires
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

			BGCompList = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[]}
			for key in LCTAreas.keys():
				if  lct.keyWireGroup >= LCTAreas[key]['wg0'] and lct.keyWireGroup <= LCTAreas[key]['wg1']\
				and lct.keyHalfStrip >= LCTAreas[key]['hs0'] and lct.keyHalfStrip <= LCTAreas[key]['hs1']:
					for comp in comps:
						if comp.cham != lct.cham: continue
						if comp.staggeredHalfStrip >= OppAreas[key]['hs0'] and comp.staggeredHalfStrip <= OppAreas[key]['hs1']:
							BGCompList[comp.layer].append(comp)

			minRoadLength = 4 # minimum 4 layers in a road
			roadWidth     = 3 # size away from central road hs
			roads = []
			sortFunc = lambda road: len(set([comp.layer for comp in road]))
			# Loop through outer layers
			for (beginLay,endLay) in [(1,6),(1,5),(2,6),(1,4),(2,5),(3,6)]:
				# Calculate hs difference between comparators in outer layer and inner layer
				layDiff = endLay - beginLay
				for beginComp in BGCompList[beginLay]:
					for endComp in BGCompList[endLay]:
						# Make road and count comparators
						road = []
						xDiff = endComp.staggeredHalfStrip - beginComp.staggeredHalfStrip
						road.append(beginComp)
						for lay in range(beginLay+1, endLay):
							xpos = (float(xDiff)/layDiff)*(lay-beginLay) + beginComp.staggeredHalfStrip
							for c in BGCompList[lay]:
								if c.cham != beginComp.cham: continue
								if c.staggeredHalfStrip >= xpos-roadWidth and c.staggeredHalfStrip <= xpos+roadWidth:
									road.append(c)
						road.append(endComp)

						if sortFunc(road) < minRoadLength: continue
						roads.append(road)

			if roads != []:
				DATA['passZ'  ]['elim'] += passZ
				DATA['passBX' ]['elim'] += passBX
				DATA['passZBX']['elim'] += passZBX
	for key, frac in DATA.iteritems():
		print '{:7s} {:6d} {:6d}'.format(key, frac['elim'], frac['tot'])

def cleanup(self, PARAMS):
	print ''

# if file is already made
def load(self, PARAMS):
	pass

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
