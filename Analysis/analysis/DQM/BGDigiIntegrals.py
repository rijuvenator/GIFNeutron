import os
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi

MS.F_MCDATA = '$WS/public/Neutron/hacktrees2/hacktree.root'

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'P5'  : 'Integrals_P5_test.root',
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
		if idx == 10000: break
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

			DOROAD = False

			bgLCTs, bgComps = BGDigi.getBGCompCandList(lcts, comps)
			if len(bgLCTs) == 0: continue # skip event if there were no isolated LCTs
			if DOROAD:
				roadChams = BGDigi.removeDigiRoads(bgComps)
			else:
				roadChams = []

			for lct in bgLCTs:
				# Skip Chamber if there's a background road
				if lct.cham in roadChams and DOROAD: continue
				cham = CH.Chamber(lct.cham)
				for comp in bgComps:
					if comp.cham!=lct.cham: continue
					if comp.timeBin >= 1 and comp.timeBin <= 5:
						self.HISTS['comp'].Fill(ringdict[cham.display('{E}{S}{R}')])

			bgLCTs, bgWires = BGDigi.getBGWireCandList(lcts,wires)
			if len(bgLCTs) == 0: continue # skip event if no isolated LCTs
			if DOROAD:
				roadChams = BGDigi.removeDigiRoads(bgWires)
			else:
				roadChams = []
				
			for lct, half in bgLCTs:
				# skip chamber if there's a background track
				if lct.cham in roadChams and DOROAD: continue
				cham = CH.Chamber(lct.cham)
				for wire in bgWires:
					if wire.cham != lct.cham: continue
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
