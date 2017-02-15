import sys, os
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS

import itertools as it
LHC_BUNCHES = 3564

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'GIF' : '',
	'P5'  : 'gaps.root',
	'MC'  : ''
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.SetFileNames(CONFIG)
if TYPE != 'P5':
	print 'This script will only work for P5.'
	exit()

##### IMPLEMENT ANALYZERS #####
def analyze(self, t, PARAMS):
	for idx, entry in enumerate(t):
		print 'Event: ', idx, '\r',

		RUN = t.Event_RunNumber
		if RUN not in self.HISTS.keys():
			self.HISTS[RUN] = R.TH1F('h'+str(RUN), '', LHC_BUNCHES, 0, LHC_BUNCHES)
			self.HISTS[RUN].SetDirectory(0)

		self.HISTS[RUN].Fill(t.Event_BXCrossing)

	self.F_OUT.cd()
	for RUN in self.HISTS.keys():
		self.HISTS[RUN].Write()

def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	HNAMES = [i.GetName() for i in list(f.GetListOfKeys())]
	self.HISTS = {}
	for NAME in HNAMES:
		self.HISTS[int(NAME[1:])] = f.Get(NAME)
		self.HISTS[int(NAME[1:])].SetDirectory(0)

def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HISTS = {}

def cleanup(self, PARAMS):
	print ''
	pass

##### DECLARE ANALYZERS AND RUN ANALYSIS #####
R.gROOT.SetBatch(True)
METHODS = ['analyze', 'load', 'setup', 'cleanup']
ARGS = {\
	'PARAMS'     : [OFN, TYPE],
	'F_DATAFILE' : FDATA
}
Analyzer = getattr(MS, TYPE+'Analyzer')
for METHOD in METHODS:
	setattr(Analyzer, METHOD, locals()[METHOD])
data = Analyzer(**ARGS)

#### FIND BUNCH RANGES #####
for RUN in data.HISTS.keys():
	h = data.HISTS[RUN]
	#print 'RUN', RUN
	BXList = []
	Count = 0
	for BX in range(LHC_BUNCHES):
		if h.GetBinContent(BX+1) == 0:
			BXList.append(BX)
		else:
			Count += 1

	print RUN, Count
	continue
	print '  {:>5s} {:>5s} {:>5s}'.format('SIZE', 'START', 'END')
	for key, group in it.groupby(enumerate(BXList), lambda (idx, BX) : idx - BX):
		BXRange = [BX for idx, BX in list(group)]
		print '  {:5d} {:5d} {:5d}'.format(BXRange[-1]-BXRange[0]+1, BXRange[0], BXRange[-1])
