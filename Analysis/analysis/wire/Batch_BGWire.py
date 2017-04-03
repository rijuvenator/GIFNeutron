'''
Analysis of candidate neutron-induced background wire group hits
Uses the usual tricks:
	- Z->mumu events in Run2016H
	- 1st BX after a gap in LHC BX structure
	- Requires LCT in 1/16th corner of a chamber and counts
	  wire group hits in the opposite half in selected early-time
	  background time-bins
	- Skips chambers with extra background tracks
	  (tracks found with a road method)
Output plots are
	- Background wire group hit rate vs inst. lumi.
	- Background wire group hit occupancy
	- (other plots used to generate/normalize first two)
	- Background wire group hit BX
'''
import sys, os, argparse
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi
from BGWire import setup, loopFunction

RINGLIST = ['11', '12', '13', '21', '22', '31', '32', '41', '42']
ULRINGLIST = [i+'u' for i in RINGLIST] + [i+'l' for i in RINGLIST]

##### IMPLEMENT ANALYZERS #####

def analyze(self, t, PARAMS):
	DOGAP   = PARAMS[2]
	DOZJETS = PARAMS[3]
	GAP     = PARAMS[4]
	DOROAD  = PARAMS[5]
	START   = PARAMS[6]
	END     = PARAMS[7]
	Primitives.SelectBranches(t, DecList=['LCT', 'WIRE'], branches=['Event_RunNumber','Event_BXCrossing','Event_LumiSection'])
	#for idx, entry in enumerate(t):
	for idx in xrange(START, END+1):
		#if idx == 1000: break
		t.GetEntry(idx)
		#print 'Events    :', idx+1, '\r',

		loopFunction(self, t, PARAMS)

	self.F_OUT.cd()
	for ring in ULRINGLIST:
		self.HISTS[ring]['time'].Write()
		self.HISTS[ring]['lumi'].Write()
		self.HISTS[ring]['totl'].Write()
		self.HISTS[ring]['occ'].Write()
		self.HISTS[ring]['lct'].Write()
	for ring in RINGLIST:
		self.HISTS[ring]['occ'].Write()
		self.HISTS[ring]['lct'].Write()

	if DOGAP:
		print ''
		analyzed = 0
		for size in sorted(self.COUNTS.keys()):
			analyzed += self.COUNTS[size]
			print 'Gaps ({:3d}):'.format(size) if size > 0 else 'Not Gap   :', self.COUNTS[size]
		print 'Analyzed  :', analyzed

# if file is already made
def load(self, PARAMS):
	pass

# runs before file loop; open a file, declare a hist dictionary
# def setup(self, PARAMS):

def cleanup(self, PARAMS):
	print ''
	pass

if __name__ == '__main__':
	#### SETUP SCRIPT #####
	# Output file names
	CONFIG = {
		'P5'  : 'BGWire_P5_bgdigitest.root',
	}
	# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
	TYPE, OFN, FDATA, REMAINDER = MS.ParseArguments(CONFIG, extraArgs=True)

	parser = argparse.ArgumentParser()
	parser.add_argument('-ng', '--nogap'     , action='store_false' , dest='NOGAP')
	parser.add_argument('-nz', '--nozjetcuts', action='store_false' , dest='NOZJETS')
	parser.add_argument('-f' , '--file'      , default=''           , dest='FILE')
	parser.add_argument('-g' , '--gapsize'   , default=35, type=int , dest='GAP')
	parser.add_argument('-fr', '--findroads' , action='store_true'  , dest='DOROAD')
	parser.add_argument('--batchconfig', nargs=3)
	args = parser.parse_args(REMAINDER)

	DOROAD  = args.DOROAD
	DOGAP   = args.NOGAP
	DOZJETS = args.NOZJETS
	GAP     = args.GAP
	OFN = 'BGWire_P5' + ('' if args.FILE == '' else '_') + args.FILE + '.root'
	if FDATA is not None: FDATA = OFN

	NUM = args.batchconfig[0]
	START = int(args.batchconfig[1])
	END = int(args.batchconfig[2])

	OFN = OFN.replace('.root', '_'+NUM+'.root')
	FDATA = OFN if FDATA is not None else None

	if FDATA is not None:
		print 'Use the other script!!'
		exit()

	##### DECLARE ANALYZERS AND RUN ANALYSIS #####
	R.gROOT.SetBatch(True)
	METHODS = ['analyze', 'load', 'setup', 'cleanup']
	ARGS = {
		'PARAMS'     : [OFN, TYPE, DOGAP, DOZJETS, GAP, DOROAD, START, END],
		'F_DATAFILE' : FDATA
	}
	Analyzer = getattr(MS, TYPE+'Analyzer')
	for METHOD in METHODS:
		setattr(Analyzer, METHOD, locals()[METHOD])
	data = Analyzer(**ARGS)
