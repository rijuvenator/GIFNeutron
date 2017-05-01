import os, math, sys
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi
from BGCompPatterns import setup, loopFunction

##### ANALYZER FUNCTIONS #####
# runs before file loop; open a file, declare a hist dictionary
# def setup(self, PARAMS):

# once per file
def analyze(self, t, PARAMS):
	TYPE = PARAMS[1]
	START = PARAMS[2]
	END = PARAMS[3]
	Primitives.SelectBranches(t, DecList=['LCT','COMP','WIRE'], branches=['Event_RunNumber', 'Event_BXCrossing'])
	#for idx, entry in enumerate(t):
	for idx in xrange(START, END+1):
		#if idx == 1000: break
		t.GetEntry(idx)
		#print 'Events:', idx, '\r',

		loopFunction(self, t, TYPE)

	self.F_OUT.cd()
	self.HIST.Write()

def cleanup(self, PARAMS):
	print ''

# if file is already made
def load(self, PARAMS):
	pass

if __name__ == '__main__':
	#### SETUP SCRIPT #####
	# Output file names
	CONFIG = {
		'P5'  : '$WS/public/patterns/bgpatterns_P5.root',
	}
	# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
	TYPE, OFN, FDATA, REMAINDER = MS.ParseArguments(CONFIG, extraArgs=True)

	NUM = REMAINDER[0]
	START = int(REMAINDER[1])
	END = int(REMAINDER[2])

	OFN = OFN.replace('.root', '_'+NUM+'.root')
	FDATA = OFN if FDATA is not None else None

	if FDATA is not None:
		print 'Use the other script!!'
		exit()

	##### DECLARE ANALYZERS AND RUN ANALYSIS #####
	R.gROOT.SetBatch(True)
	METHODS = ['analyze', 'load', 'setup', 'cleanup']
	ARGS = {
		'PARAMS'     : [OFN, TYPE, START, END],
		'F_DATAFILE' : FDATA
	}
	Analyzer = getattr(MS, TYPE+'Analyzer')
	for METHOD in METHODS:
		setattr(Analyzer, METHOD, locals()[METHOD])
	data = Analyzer(**ARGS)
