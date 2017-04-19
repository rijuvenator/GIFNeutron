import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi
import array

#########################################################
## SINATRA: the successor to GOAT which makes a tree   ##
## instead of 250k histograms. It runs the analysis.   ##
## It is now very easy to make any kind of histogram   ##
## by requiring various cuts on this tree.             ##
##                                                     ##
## Each entry is an LCT that led to background digis   ##
## POS is the LCT's position; HS or WG defined by DIGI ##
## D_* are the lists of digi info for that LCT         ##
#########################################################

#########################
## IMPLEMENT ANALYZERS ##
#########################

# analysis function; runs once per tree
def analyze(self, t, PARAMS):
	#Primitives.SelectBranches(t, DecList=[], branches=['*'])
	for idx, entry in enumerate(t):
		print 'Events:', idx+1, '\r',
		loopFunction(self, t, PARAMS)

	self.F_OUT.cd()
	self.TREE.Write()

# loop function; runs once per event
def loopFunction(self, t, PARAMS):
	if PARAMS.DOZJETS:
		if      t.Z_mass <= 98. and t.Z_mass >= 84.\
			and t.nJets20 == 0\
			and t.Z_pT <= 20.:
			pass
		else:
			return

	if PARAMS.DOGAP:
		# Only after gap BXs
		size, BX, train = self.getBunchInfo(t.Event_RunNumber, t.Event_BXCrossing, minSize=PARAMS.GAP)
		if not size: return
		if BX > 48: BX = 49

	# Background digis
	if list(t.lct_id) == [] or list(t.comp_id) == []: return
	E = Primitives.ETree(t, DecList=['LCT','COMP','WIRE'])
	lcts  = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham ))]
	comps = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham))]
	wires = [Primitives.Wire   (E, i) for i in range(len(E.wire_cham))]

	LUMI = self.lumi(t.Event_RunNumber, t.Event_LumiSection)

	DIGIDICT = {
		'comp': ('Comp', comps, 'halfStrip', 'keyHalfStrip'),
		'wire': ('Wire', wires, 'number'   , 'keyWireGroup'),
	}

	for digiName, (DigiName, digilist, digipos, lctpos) in DIGIDICT.iteritems():
		bgLCTs, oppDigis = getattr(BGDigi, 'getBG'+DigiName+'CandList')(lcts, digilist)
		if len(bgLCTs) == 0: continue

		if PARAMS.DOROAD:
			roadChams = BGDigi.removeDigiRoads(oppDigis)
		else:
			roadChams = []
	
		for lct, half in bgLCTs:
			nDigi = 0
			if lct.cham in roadChams and PARAMS.DOROAD: continue
			cham = CH.Chamber(lct.cham)
			endcap, ring = cham.display('{E}'), cham.display('{S}{R}')
			self.VARS['ENDCAP' ].assign(endcap)
			self.VARS['RING'   ].assign(ring)
			self.VARS['DIGI'   ].assign(digiName)
			self.VARS['HALF'   ].assign(half)
			self.VARS['BX'     ][0] = BX
			self.VARS['LUMI'   ][0] = LUMI
			self.VARS['POS'    ][0] = getattr(lct, lctpos)
			self.VARS['D_TIME' ].clear()
			self.VARS['D_LAYER'].clear()
			self.VARS['D_POS'  ].clear()
			for digi in oppDigis:
				self.VARS['D_TIME' ].push_back(digi.timeBin)
				self.VARS['D_LAYER'].push_back(digi.layer)
				self.VARS['D_POS'  ].push_back(getattr(digi, digipos))
			self.TREE.Fill()

# load function; loads the file specified in config instead of running analysis
def load(self, PARAMS):
	pass

# pre-analysis function; declare histograms, etc.
def setup(self, PARAMS):
	self.COUNTS = {}
	self.F_OUT = R.TFile(PARAMS.OFN,'RECREATE')
	self.F_OUT.cd()
	self.TREE = R.TTree('t', 't')

	self.VARS = {
		'ENDCAP' : R.string(),
		'RING'   : R.string(),
		'DIGI'   : R.string(),
		'HALF'   : R.string(),
		'BX'     : array.array('i', [-1]),
		'LUMI'   : array.array('d', [-1]),
		'POS'    : array.array('i', [-1]),
		'D_TIME' : R.vector('int')(),
		'D_LAYER': R.vector('int')(),
		'D_POS'  : R.vector('int')()
	}

	self.TREE.Branch('ENDCAP' ,self.VARS['ENDCAP' ])
	self.TREE.Branch('RING'   ,self.VARS['RING'   ])
	self.TREE.Branch('DIGI'   ,self.VARS['DIGI'   ])
	self.TREE.Branch('HALF'   ,self.VARS['HALF'   ])
	self.TREE.Branch('BX'     ,self.VARS['BX'     ], 'BX/I')
	self.TREE.Branch('LUMI'   ,self.VARS['LUMI'   ], 'LUMI/D')
	self.TREE.Branch('POS'    ,self.VARS['POS'    ], 'POS/I')
	self.TREE.Branch('D_TIME' ,self.VARS['D_TIME' ])
	self.TREE.Branch('D_LAYER',self.VARS['D_LAYER'])
	self.TREE.Branch('D_POS'  ,self.VARS['D_POS'  ])

# post-analysis function; print extra lines, etc.
def cleanup(self, PARAMS):
	print ''

########################
##  MAIN MODULE CODE  ##
########################

if __name__ == '__main__':

	#### SETUP SCRIPT #####
	# Output file names
	CONFIG = {
		'GIF' : 'GOAT_GIF.root',
		'P5'  : 'GOAT_P5.root',
		'MC'  : 'GOAT_MC.root'
	}
	# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
	TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

	# External Parameters
	class Namespace(object):
		def __init__(self, dict_):
			self.__dict__.update(dict_)
	PARAMS = {
		'OFN'     :OFN,
		'TYPE'    :TYPE,
		'DOZJETS' :False,
		'DOROAD'  :True,
		'DOGAP'   :True,
		'GAP'     :35,
		'RINGLIST':['11', '12', '13', '21', '22', '31', '32', '41', '42'],
	}
	PARAMS['ERINGLIST' ] = ['-'+r for r in reversed(PARAMS['RINGLIST'])]+['+'+r for r in PARAMS['RINGLIST']]
	PARAMS['RINGDICT'  ] = dict(zip(PARAMS['ERINGLIST'], range(-9, 0) + range(1, 10))),
	PARAMS = Namespace(PARAMS)

	##### DECLARE ANALYZERS AND RUN ANALYSIS #####
	R.gROOT.SetBatch(True)
	METHODS = ['analyze', 'load', 'setup', 'cleanup']
	ARGS = {
		'PARAMS'     : PARAMS,
		'F_DATAFILE' : FDATA
	}
	if TYPE == 'GIF':
		ARGS['ATTLIST'] = [float('inf')]
	Analyzer = getattr(MS, TYPE+'Analyzer')
	for METHOD in METHODS:
		setattr(Analyzer, METHOD, locals()[METHOD])
	data = Analyzer(**ARGS)
