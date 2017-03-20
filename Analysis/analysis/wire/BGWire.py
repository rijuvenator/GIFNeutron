import sys, os, argparse
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi
import logging

logging.basicConfig(filename='eventlist.log',format='%(asctime)s %(message)s')

MS.F_P5DATA = '$WS/public/Neutron/ana_Neutron_P5_ALL.root'
MS.F_RUNGRID = '../datafiles/runlumigrid_all'
MS.F_GAPDATA = '../datafiles/gapdata_ALL'
RINGLIST = ['11', '12', '13', '21', '22', '31', '32', '41', '42']
ULRINGLIST = [i+'u' for i in RINGLIST] + [i+'l' for i in RINGLIST]

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
args = parser.parse_args(REMAINDER)

DOROAD  = args.DOROAD
DOGAP   = args.NOGAP
DOZJETS = args.NOZJETS
GAP     = args.GAP
OFN = 'BGWire_P5' + ('' if args.FILE == '' else '_') + args.FILE + '.root'
if FDATA is not None: FDATA = OFN

elist = []
EFILE = open('eventlist.log')
for line in EFILE:
	event = line.strip('\n').split()[-1]
	elist.append(int(event))
print len(elist)

##### IMPLEMENT ANALYZERS #####
def analyze(self, t, PARAMS):
	DOGAP = PARAMS[2]
	DOZJETS = PARAMS[3]
	GAP = PARAMS[4]
	Primitives.SelectBranches(t, DecList=['LCT', 'WIRE'], branches=['Event_RunNumber','Event_BXCrossing','Event_LumiSection'])
#	for idx, entry in enumerate(t):
#		if idx == 42732: break
	for idx in elist:
		t.GetEntry(idx)
		print 'Events    :', idx+1, '\r',

		# Z and jet cuts
		if DOZJETS:
			if      t.Z_mass <= 98. and t.Z_mass >= 84.\
				and t.nJets20 == 0\
				and t.Z_pT <= 20.:
				pass
			else:
				continue

		if DOGAP:
			# Only after gap BXs
			size = self.afterGapSize(t.Event_RunNumber, t.Event_BXCrossing, minSize=GAP)
			if size not in self.COUNTS.keys():
				self.COUNTS[size] = 0
			self.COUNTS[size] += 1

			if size == 0: continue

		#logging.warning('Event '+str(idx))

		# Background wire groups
		if list(t.lct_id) == [] or list(t.wire_id) == []: continue
		E = Primitives.ETree(t, DecList=['LCT','WIRE'])
		lcts  = [Primitives.LCT (E, i) for i in range(len(E.lct_cham ))]
		wires = [Primitives.Wire(E, i) for i in range(len(E.wire_cham))]

		bgLCTs, bgWires = BGDigi.getBGWireCandList(lcts,wires)
		if len(bgLCTs) == 0: continue # skip event if no isolated lcts
		if DOROAD:
			roadChams = BGDigi.removeDigiRoads(bgWires)
		else:
			roadChams = []
		for lct, half in bgLCTs:
			nWire = 0.
			# skip chamber if there's a background track
			if lct.cham in roadChams and DOROAD: continue
			cham = CH.Chamber(lct.cham)
			for wire in bgWires:
				if wire.cham != lct.cham: continue
				self.HISTS[cham.display('{S}{R}')+half]['time'].Fill(wire.timeBin)
				if wire.timeBin >= 1 and wire.timeBin <= 5:
					self.HISTS[cham.display('{S}{R}')+half]['occ'].Fill(wire.number)
					self.HISTS[cham.display('{S}{R}')]['occ'].Fill(wire.number)
					nWire += 1
			self.HISTS[cham.display('{S}{R}')+half]['lumi'].Fill(self.lumi(t.Event_RunNumber, t.Event_LumiSection), float(nWire))
			self.HISTS[cham.display('{S}{R}')+half]['totl'].Fill(self.lumi(t.Event_RunNumber, t.Event_LumiSection), float(1.   ))

	self.F_OUT.cd()
	for ring in ULRINGLIST:
		self.HISTS[ring]['time'].Write()
		self.HISTS[ring]['lumi'].Write()
		self.HISTS[ring]['totl'].Write()
		self.HISTS[ring]['occ'].Write()
	for ring in RINGLIST:
		self.HISTS[ring]['occ'].Write()

	if DOGAP:
		print ''
		analyzed = 0
		for size in sorted(self.COUNTS.keys()):
			analyzed += self.COUNTS[size]
			print 'Gaps ({:3d}):'.format(size) if size > 0 else 'Not Gap   :', self.COUNTS[size]
		print 'Analyzed  :', analyzed

# if file is already made
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	for ring in ULRINGLIST:
		self.HISTS[ring] = {
			'time' : f.Get('t'+ring),
			'lumi' : f.Get('l'+ring),
			'totl' : f.Get('a'+ring),
			'occ'  : f.Get('o'+ring),
		}
		self.HISTS[ring]['time'].SetDirectory(0)
		self.HISTS[ring]['lumi'].SetDirectory(0)
		self.HISTS[ring]['totl'].SetDirectory(0)
		self.HISTS[ring]['occ'].SetDirectory(0)
	for ring in RINGLIST:
		self.HISTS[ring] = {
			'occ'  : f.Get('o'+ring),
		}
		self.HISTS[ring]['occ'].SetDirectory(0)

# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	self.COUNTS = {}
	self.HISTS = {}
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	for ring in ULRINGLIST:
		cham = CH.Chamber(CH.serialID(1, int(ring[0]), int(ring[1]), 1))
		bins = cham.nwires+2
		self.HISTS[ring] = {
			'time': R.TH1F('t'+ring, '', 10, 0., 16.),
			'lumi': R.TH1F('l'+ring, '', 30, 0., 15.e33),
			'totl': R.TH1F('a'+ring, '', 30, 0., 15.e33),
			'occ' : R.TH1F('o'+ring, '', bins, 0, bins),
		}
		self.HISTS[ring]['time'].SetDirectory(0)
		self.HISTS[ring]['lumi'].SetDirectory(0)
		self.HISTS[ring]['totl'].SetDirectory(0)
		self.HISTS[ring]['occ'].SetDirectory(0)
	for ring in RINGLIST:
		cham = CH.Chamber(CH.serialID(1, int(ring[0]), int(ring[1]), 1))
		bins = cham.nwires+2
		self.HISTS[ring] = {
			'occ' : R.TH1F('o'+ring, '', bins, 0, bins),
		}
		self.HISTS[ring]['occ'].SetDirectory(0)

def cleanup(self, PARAMS):
	print ''
	pass

##### DECLARE ANALYZERS AND RUN ANALYSIS #####
R.gROOT.SetBatch(True)
METHODS = ['analyze', 'load', 'setup', 'cleanup']
ARGS = {
	'PARAMS'     : [OFN, TYPE, DOGAP, DOZJETS, GAP],
	'F_DATAFILE' : FDATA
}
if TYPE == 'GIF':
	ARGS['ATTLIST'] = [float('inf')]
Analyzer = getattr(MS, TYPE+'Analyzer')
for METHOD in METHODS:
	setattr(Analyzer, METHOD, locals()[METHOD])
data = Analyzer(**ARGS)

##### MAKEPLOT FUNCTIONS #####
def makeTimePlot(h, ring):
	if h.Integral() == 0: return
	plot = Plotter.Plot(h, option='hist')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.addMainPlot(plot)
	canvas.makeTransparent()
	#canvas.firstPlot.plot.SetMaximum(1.05)
	canvas.firstPlot.plot.SetMinimum(0)
	#canvas.firstPlot.plot.SetMinimum(0.00001)
	canvas.finishCanvas()
	canvas.SaveAs('pdfs/BGWireTime'+'_'+ring+'.pdf')
	R.SetOwnership(canvas, False)

def makeLumiPlotFull(h1u, h1l, h2u, h2l, ring):
	binit = range(1, h1u.GetNbinsX()+1)
	nwiresu = [h1u.GetBinContent(i) for i in binit]
	nwiresl = [h1l.GetBinContent(i) for i in binit]
	totalsu = [h2u.GetBinContent(i) for i in binit]
	totalsl = [h2l.GetBinContent(i) for i in binit]
	#lumi = np.array([])
	#lumi = h1.GetXaxis().GetCenter(lumi)
	#lumi = np.array(lumi)
	lumiA = np.array([(15.e33)/30 * (i+0.5) for i in range(30)])
	dataAu = np.array([nwire/float(total) if total != 0 else 0. for nwire,total in zip(nwiresu,totalsu)])
	dataAl = np.array([nwire/float(total) if total != 0 else 0. for nwire,total in zip(nwiresl,totalsl)])
	lumi = np.array(lumiA[10:26])
	datau = np.array(dataAu[10:26])
	datal = np.array(dataAl[10:26])
	hu = R.TGraph(len(lumi), lumi, datau)
	hl = R.TGraph(len(lumi), lumi, datal)
	#print lumi, data
	plotu = Plotter.Plot(hu, legName = ring+' upper', option='PE', legType = 'P')
	plotl = Plotter.Plot(hl, legName = ring+' lower', option='PE', legType = 'P')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.addMainPlot(plotu)
	canvas.addMainPlot(plotl)
	canvas.makeTransparent()
	canvas.scaleMargins(1.25, 'R')
	canvas.firstPlot.setTitles(X='Luminosity [cm^{-2}s^{-1}]', Y='#LT Number of Background Wire Groups#GT')
	canvas.firstPlot.GetXaxis().SetLimits(0., 15.e33)
	canvas.firstPlot.SetMinimum(0. )
	canvas.firstPlot.SetMaximum(1.0)
	canvas.firstPlot.scaleTitleOffsets(1.2)
	plotu.SetMarkerColor(R.kRed)
	plotl.SetMarkerColor(R.kBlue)
	canvas.makeLegend(pos='tl')
	canvas.finishCanvas()
	canvas.SaveAs('pdfs/BGWireAvgN'+'_'+ring+'.pdf')
	R.SetOwnership(canvas, False)

def makeLumiPlot(h1, h2, ring):
	binit = range(1, h1.GetNbinsX()+1)
	nwires = [h1.GetBinContent(i) for i in binit]
	totals = [h2.GetBinContent(i) for i in binit]
	#lumi = np.array([])
	#lumi = h1.GetXaxis().GetCenter(lumi)
	#lumi = np.array(lumi)
	lumiA = np.array([(15.e33)/30 * (i+0.5) for i in range(30)])
	dataA = np.array([nwire/float(total) if total != 0 else 0. for nwire,total in zip(nwires,totals)])
	lumi = np.array(lumiA[10:26])
	data = np.array(dataA[10:26])
	h = R.TGraph(len(lumi), lumi, data)
	#print lumi, data
	plot = Plotter.Plot(h, option='PE')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.addMainPlot(plot)
	canvas.makeTransparent()
	canvas.scaleMargins(1.25, 'R')
	canvas.firstPlot.setTitles(X='Luminosity [cm^{-2}s^{-1}]', Y='#LT Number of Background Wire Groups#GT')
	canvas.firstPlot.GetXaxis().SetLimits(0., 15.e33)
	canvas.firstPlot.SetMinimum(0. )
	canvas.firstPlot.SetMaximum(1.0)
	canvas.firstPlot.scaleTitleOffsets(1.2)
	canvas.finishCanvas()
	canvas.SaveAs('pdfs/BGWireAvgN'+'_'+ring+'.pdf')
	R.SetOwnership(canvas, False)

def makeNumDum(h, ring, which):
	plot = Plotter.Plot(h, option='P')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.addMainPlot(plot)
	canvas.makeTransparent()
	canvas.scaleMargins(1.25, 'R')
	canvas.firstPlot.setTitles(X='Luminosity [cm^{-2}s^{-1}]', Y='Number of Background Wire Groups' if which == 'nwire' else 'Counts')
	canvas.finishCanvas()
	canvas.SaveAs('pdfs/BGWireAvgN'+'_'+ring+'_'+which+'.pdf')
	R.SetOwnership(canvas, False)

def makeOccPlot(h,ring):
	for logy in [True,False]:
		plot = Plotter.Plot(h,option='hist')
		canvas = Plotter.Canvas(lumi='ME'+ring+' WG Occupancy',logy=logy)
		canvas.addMainPlot(plot)
		canvas.makeTransparent()
		plot.setTitles(X='Wire Group Number',Y='Counts')
		#canvas.finishCanvas('bob')
		canvas.finishCanvas()
		canvas.save('pdfs/BGWireOcc_'+ring,['.pdf'])
		canvas.deleteCanvas()

for ring in ULRINGLIST:
	makeTimePlot(data.HISTS[ring]['time'], ring)
	makeLumiPlot(data.HISTS[ring]['lumi'], data.HISTS[ring]['totl'], ring)
	makeNumDum(data.HISTS[ring]['lumi'], ring, 'nwire')
	makeNumDum(data.HISTS[ring]['totl'], ring, 'lumi')
	makeOccPlot(data.HISTS[ring]['occ'], ring)
for ring in RINGLIST:
	makeLumiPlotFull(data.HISTS[ring+'u']['lumi'],data.HISTS[ring+'l']['lumi'], data.HISTS[ring+'u']['totl'], data.HISTS[ring+'l']['totl'],ring)
	makeOccPlot(data.HISTS[ring]['occ'],ring)
