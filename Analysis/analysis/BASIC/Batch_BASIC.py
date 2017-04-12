import sys, os
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi

########################################################
# Batch version of an analyzer, uses GetEntry instead  #
# Imports setup, cleanup, and analysis loopFunction    #
from BASIC import setup, cleanup, loopFunction         #
# Adds extra parameters to handle file parallelization #
# Should not implement loading or plotter functions    #
########################################################

#########################
## IMPLEMENT ANALYZERS ##
#########################

# analysis function; runs once per tree
def analyze(self, t, PARAMS):
	START, END = PARAMS[2], PARAMS[3]
	#Primitives.SelectBranches(t, DecList=[], branches=['*'])
	for idx in xrange(START, END+1):
		#print 'Events:', idx+1, '\r',
		t.GetEntry(idx)
		loopFunction(self, t, PARAMS)

	self.F_OUT.cd()
	#self.HISTS[].Write()

# load function; loads the file specified in config instead of running analysis
def load(self, PARAMS):
	pass

########################
##  MAIN MODULE CODE  ##
########################

if __name__ == '__main__':
	#### SETUP SCRIPT #####
	# Output file names
	CONFIG = {
		'GIF' : 'BASIC_GIF.root',
		'P5'  : 'BASIC_P5.root',
		'MC'  : 'BASIC_MC.root'
	}
	# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
	TYPE, OFN, FDATA, REMAINDER = MS.ParseArguments(CONFIG, extraArgs=True)

	# Batch specific parameters
	NUM   = REMAINDER[0]
	START = int(REMAINDER[1])
	END   = int(REMAINDER[2])
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
	if TYPE == 'GIF':
		ARGS['ATTLIST'] = [float('inf')]
	Analyzer = getattr(MS, TYPE+'Analyzer')
	for METHOD in METHODS:
		setattr(Analyzer, METHOD, locals()[METHOD])
	data = Analyzer(**ARGS)
