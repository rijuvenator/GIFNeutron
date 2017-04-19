import sys, os
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi

###################################################
# A skeleton analyzer template to be used with MS #
# Setup involves specifying a CONFIG of filenames #
# Defines analyze, load, setup, cleanup for a     #
# MS class; declares the analyzer which runs it   #
# Plotting functions at the bottom                #
###################################################

#########################
## IMPLEMENT ANALYZERS ##
#########################

# analysis function; runs once per tree
def analyze(self, t, PARAMS):
	#Primitives.SelectBranches(t, DecList=[], branches=['*'])
	for idx, entry in enumerate(t):
		#if idx == 50000: break
		print 'Events:', idx+1, '\r',
		loopFunction(self, t, PARAMS)

	self.F_OUT.cd()
	SLW(self, PARAMS, 'WRITE')

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
			self.HISTS[endcap][ring][digiName][half][BX]['nLCT'].Fill(LUMI, getattr(lct, lctpos))
			for digi in oppDigis:
				self.HISTS[endcap][ring][digiName][half][BX][digi.timeBin][digi.layer]['nDigi'].Fill(LUMI, getattr(digi, digipos))

def SLW(self, PARAMS, WHICH):
	if WHICH in ('SETUP', 'LOAD'): self.HISTS = {'+':{}, '-':{}}
	for endcap in ('+', '-'):
		if WHICH in ('SETUP', 'LOAD'): self.HISTS[endcap] = {}
		for ring in PARAMS.RINGLIST:
			if WHICH in ('SETUP', 'LOAD'): self.HISTS[endcap][ring] = {}
			cham = CH.Chamber(CH.serialID(1, int(ring[0]), int(ring[1]), 1))
			binsComp = cham.nstrips*2+2
			binsWire = cham.nwires+2
			DIGIDICT = {
				'comp' : ('Comp', ('l', 'r'), 10, binsComp),
				'wire' : ('Wire', ('u', 'l'), 16, binsWire),
			}
			for digi, (Digi, halflist, tbmax, bins) in DIGIDICT.iteritems():
				AXES = (30, 0, 15.e33, bins, 0, bins)
				if WHICH in ('SETUP', 'LOAD'): self.HISTS[endcap][ring][digi] = {}
				for half in halflist:
					if WHICH in ('SETUP', 'LOAD'): self.HISTS[endcap][ring][digi][half] = {}
					for BX in xrange(1, 50):
						if WHICH in ('SETUP', 'LOAD'): self.HISTS[endcap][ring][digi][half][BX] = {}
						NAME_LCT  = '_'.join([digi, endcap, ring, half, str(BX), 'nLCT' ])
						if WHICH == 'SETUP':
							self.HISTS[endcap][ring][digi][half][BX]['nLCT'] = R.TH2F(NAME_LCT, '', *AXES)
							self.HISTS[endcap][ring][digi][half][BX]['nLCT'].SetDirectory(0)
						elif WHICH == 'LOAD':
							self.HISTS[endcap][ring][digi][half][BX]['nLCT'] = f.Get(NAME_LCT)
							self.HISTS[endcap][ring][digi][half][BX]['nLCT'].SetDirectory(0)
						elif WHICH == 'WRITE':
							self.HISTS[endcap][ring][digi][half][BX]['nLCT'].Write()
						for timeBin in xrange(0, tbmax):
							if WHICH in ('SETUP', 'LOAD'): self.HISTS[endcap][ring][digi][half][BX][timeBin] = {}
							for layer in xrange(1, 7):
								if WHICH in ('SETUP', 'LOAD'): self.HISTS[endcap][ring][digi][half][BX][timeBin][layer] = {}
								NAME_DIGI = '_'.join([digi, endcap, ring, half, str(BX), str(timeBin), str(layer), 'nDigi'])
								if WHICH == 'SETUP':
									self.HISTS[endcap][ring][digi][half][BX][timeBin][layer]['nDigi'] = R.TH2F(NAME_DIGI, '', *AXES)
									self.HISTS[endcap][ring][digi][half][BX][timeBin][layer]['nDigi'].SetDirectory(0)
								elif WHICH == 'LOAD':
									self.HISTS[endcap][ring][digi][half][BX][timeBin][layer]['nDigi'] = f.Get(NAME_DIGI)
									self.HISTS[endcap][ring][digi][half][BX][timeBin][layer]['nDigi'].SetDirectory(0)
								elif WHICH == 'WRITE':
									self.HISTS[endcap][ring][digi][half][BX][timeBin][layer]['nDigi'].Write()

# load function; loads the file specified in config instead of running analysis
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	SLW(self, PARAMS, 'LOAD')

# pre-analysis function; declare histograms, etc.
def setup(self, PARAMS):
	self.COUNTS = {}
	self.F_OUT = R.TFile(PARAMS.OFN,'RECREATE')
	self.F_OUT.cd()
	SLW(self, PARAMS, 'SETUP')

# post-analysis function; print extra lines, etc.
def cleanup(self, PARAMS):
	print ''

########################
## PLOTTING FUNCTIONS ##
########################

def makePlot(hist):
	plot = Plotter.Plot(hist, legName='', legType='felp', option='hist')
	canvas = Plotter.Canvas(lumi='')
	canvas.addMainPlot(plot)
	canvas.makeLegend()
	canvas.finishCanvas()
	canvas.save('plot', ['.pdf', '.png'])

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
