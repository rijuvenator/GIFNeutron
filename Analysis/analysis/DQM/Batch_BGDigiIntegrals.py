import os
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi
from BGDigiIntegrals import setup, loopFunction, writeHistos, RINGLIST, ERINGLIST, RINGDICT, DOZJETS, DOROAD, DOGAP, GAP

##### FUNCTIONS #####
# runs before file loop; open a file, declare a hist dictionary
# def setup(self, PARAMS):

# once per file
def analyze(self, t, PARAMS):
	TYPE = PARAMS['TYPE']
	START = PARAMS['START']
	END = PARAMS['END']
	if TYPE == 'P5':
		Primitives.SelectBranches(t, DecList=['LCT','COMP','WIRE'], branches=['Z_mass','Z_pT','nJets20', 'Event_RunNumber', 'Event_BXCrossing'])
#	elif TYPE == 'MC':
#		Primitives.SelectBranches(t, DecList=['COMP','WIRE'])
	#for idx, entry in enumerate(t):
	for idx in xrange(START, END+1):
		#if idx == 1000: break
		t.GetEntry(idx)
		#print 'Events:', idx+1, '\r',
		loopFunction(self, t, PARAMS)

	writeHistos(self, PARAMS)

# if file is already made
def load(self, PARAMS):
	pass

def cleanup(self, PARAMS):
	pass
	#print ''

##### ACTUAL CODE TO RUN #####
if __name__ == '__main__':
	#### SETUP SCRIPT #####
	# Output file names
	CONFIG = {
		'P5'  : 'Integrals_P5.root',
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
		'PARAMS' : {
			'OFN':OFN,
			'TYPE':TYPE,
			'DOZJETS':DOZJETS,
			'DOROAD':DOROAD,
			'DOGAP':DOGAP,
			'GAP':GAP,
			'RINGLIST':RINGLIST,
			'RINGDICT':RINGDICT,
			'START':START,
			'END':END
		},

		'F_DATAFILE' : FDATA
	}
	Analyzer = getattr(MS, TYPE+'Analyzer')
	for METHOD in METHODS:
		setattr(Analyzer, METHOD, locals()[METHOD])
	data = Analyzer(**ARGS)
