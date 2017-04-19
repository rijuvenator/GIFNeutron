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
from GOAT import setup, cleanup, loopFunction, SLW     #
# Adds extra parameters to handle file parallelization #
# Should not implement loading or plotter functions    #
########################################################

#########################
## IMPLEMENT ANALYZERS ##
#########################

# analysis function; runs once per tree
def analyze(self, t, PARAMS):
	START, END = PARAMS.START, PARAMS.END
	#Primitives.SelectBranches(t, DecList=[], branches=['*'])
	for idx in xrange(START, END+1):
		#print 'Events:', idx+1, '\r',
		t.GetEntry(idx)
		loopFunction(self, t, PARAMS)

	self.F_OUT.cd()
	SLW(self, PARAMS, 'WRITE')

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
		'GIF' : '$WS/public/goatees/GOAT_GIF.root',
		'P5'  : '$WS/public/goatees/GOAT_P5.root',
		'MC'  : '$WS/public/goatees/GOAT_MC.root'
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
		'START'   :START,
		'END'     :END,
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
