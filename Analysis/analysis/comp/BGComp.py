'''
Analysis of candidate neutron-induced background comparator hits
Uses the usual tricks:
	- Z->mumu events in Run2016H
	- 1st BX after a gap in LHC BX structure
	- Requires LCT in 1/16th corner of a chamber and counts
	  comparator hits in the opposite half in selected early-time
	  background time-bins
	- Skips chambers with extra background tracks
	  (tracks found with a road method)
Output plots are
	- Background comparator hit rate vs inst. lumi.
	- Background comparator hit occupancy
	- (other plots used to generate/normalize first two)
	- Background comparator hit BX
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

RINGLIST = ['11', '12', '13', '21', '22', '31', '32', '41', '42']

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'P5'  : 'BGComp_P5_bgdigitest.root'
	#'P5'  : 'BGComp_P5_me11fix.root'
	#'P5'  : 'BGComp_P5.root'
	#'P5'  : 'BGComp_P5_noGap.root',
	#'P5'  : 'BGComp_P5_Gap8.root',
	#'P5'  : 'BGComp_P5_Gap11.root',
	#'P5'  : 'BGComp_P5_Gap35.root',
	#'P5'  : 'BGComp_P5_Gap35_NoZJetCut.root',
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
OFN = 'BGComp_P5' + ('' if args.FILE == '' else '_') + args.FILE + '.root'
if FDATA is not None: FDATA = OFN

##### IMPLEMENT ANALYZERS #####
def analyze(self, t, PARAMS):
	DOGAP = PARAMS[2]
	DOZJETS = PARAMS[3]
	GAP = PARAMS[4]
	Primitives.SelectBranches(t, DecList=['LCT', 'COMP'], branches=['Event_RunNumber','Event_BXCrossing','Event_LumiSection'])
	for idx, entry in enumerate(t):
		#if idx == 1000: break
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
			size, diff, train = self.getBunchInfo(t.Event_RunNumber, t.Event_BXCrossing, minSize=GAP)
			if size not in self.COUNTS.keys():
				self.COUNTS[size] = 0
			self.COUNTS[size] += 1

			if size == 0: continue

		# Background comparators
		if list(t.lct_id) == [] or list(t.comp_id) == []: continue
		E = Primitives.ETree(t, DecList=['LCT','COMP'])
		lcts  = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham ))]
		comps = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham))]

		bgLCTs,oppHalfComps = BGDigi.getBGCompCandList(lcts,comps)
		if len(bgLCTs)==0: continue # skip event if there were no isolated LCTs
		if DOROAD:
			roadChams = BGDigi.removeDigiRoads(oppHalfComps)
		else:
			roadChams = []
		for lct, half in bgLCTs:
			nComp = 0.
			# Skip Chamber if there's a background road
			if lct.cham in roadChams and DOROAD: continue
			cham = CH.Chamber(lct.cham)
			# FILLLCT
			self.HISTS[cham.display('{S}{R}')+half]['lct'].Fill(lct.keyHalfStrip)
			self.HISTS[cham.display('{S}{R}')]['lct'].Fill(lct.keyHalfStrip)
			for comp in oppHalfComps:
				if comp.cham!=lct.cham: continue
				self.HISTS[cham.display('{S}{R}')+half]['time'].Fill(comp.timeBin)
				self.HISTS[cham.display('{S}{R}')]['time'].Fill(comp.timeBin)
				if comp.timeBin >= 1 and comp.timeBin <= 5:
					self.HISTS[cham.display('{S}{R}')+half]['occ'].Fill(comp.halfStrip)
					self.HISTS[cham.display('{S}{R}')]['occ'].Fill(comp.halfStrip)
					nComp += 1
				if comp.timeBin == 0:
					self.HISTS[cham.display('{S}{R}')+half]['comp_t0'].Fill(comp.comp)
					self.HISTS[cham.display('{S}{R}')]['comp_t0'].Fill(comp.comp)
				if comp.timeBin == 1:
					self.HISTS[cham.display('{S}{R}')+half]['comp_t1'].Fill(comp.comp)
					self.HISTS[cham.display('{S}{R}')]['comp_t1'].Fill(comp.comp)
				if comp.timeBin == 2:
					self.HISTS[cham.display('{S}{R}')+half]['comp_t2'].Fill(comp.comp)
					self.HISTS[cham.display('{S}{R}')]['comp_t2'].Fill(comp.comp)
			self.HISTS[cham.display('{S}{R}')+half]['lumi'].Fill(self.lumi(t.Event_RunNumber, t.Event_LumiSection), float(nComp))
			self.HISTS[cham.display('{S}{R}')+half]['totl'].Fill(self.lumi(t.Event_RunNumber, t.Event_LumiSection), float(1.   ))
			self.HISTS[cham.display('{S}{R}')]['lumi'].Fill(self.lumi(t.Event_RunNumber, t.Event_LumiSection), float(nComp))
			self.HISTS[cham.display('{S}{R}')]['totl'].Fill(self.lumi(t.Event_RunNumber, t.Event_LumiSection), float(1.   ))

	self.F_OUT.cd()
	for ring in RINGLIST:
		for half in ['l','r','']:
			self.HISTS[ring+half]['time'].Write()
			self.HISTS[ring+half]['lumi'].Write()
			self.HISTS[ring+half]['totl'].Write()
			self.HISTS[ring+half]['occ'].Write()
			self.HISTS[ring+half]['lct'].Write()
			self.HISTS[ring+half]['comp_t0'].Write()
			self.HISTS[ring+half]['comp_t1'].Write()
			self.HISTS[ring+half]['comp_t2'].Write()

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
	for ring in RINGLIST:
		for half in ['l','r','']:
			self.HISTS[ring+half] = {
				'time' : f.Get('t'+ring+half),
				'lumi' : f.Get('l'+ring+half),
				'totl' : f.Get('a'+ring+half),
				'occ'  : f.Get('o'+ring+half),
				'lct'  : f.Get('lct'+ring+half),
				'comp' : f.Get('comp'+ring+half),
				'comp_t0' : f.Get('comp_t0'+ring+half),
				'comp_t1' : f.Get('comp_t1'+ring+half),
				'comp_t2' : f.Get('comp_t2'+ring+half),
			}
			self.HISTS[ring+half]['time'].SetDirectory(0)
			self.HISTS[ring+half]['lumi'].SetDirectory(0)
			self.HISTS[ring+half]['totl'].SetDirectory(0)
			self.HISTS[ring+half]['occ'].SetDirectory(0)
			self.HISTS[ring+half]['lct'].SetDirectory(0)
			self.HISTS[ring+half]['comp_t0'].SetDirectory(0)
			self.HISTS[ring+half]['comp_t1'].SetDirectory(0)
			self.HISTS[ring+half]['comp_t2'].SetDirectory(0)

# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	self.COUNTS = {}
	self.HISTS = {}
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	for ring in RINGLIST:
		for half in ['l','r','']:
			cham = CH.Chamber(CH.serialID(1, int(ring[0]), int(ring[1]), 1))
			bins = cham.nstrips*2+2
			self.HISTS[ring+half] = {
				'time' : R.TH1F('t'+ring+half,    '', 10, 0., 10.),
				'lumi' : R.TH1F('l'+ring+half,    '', 30, 0., 15.e33),
				'totl' : R.TH1F('a'+ring+half,    '', 30, 0., 15.e33),
				'occ'  : R.TH1F('o'+ring+half,    '', bins, 0., bins),
				'lct'  : R.TH1F('lct'+ring+half,  '', bins, 0, bins),
				'comp_t0' : R.TH1F('comp_t0'+ring+half, '', 2, 0, 2),
				'comp_t1' : R.TH1F('comp_t1'+ring+half, '', 2, 0, 2),
				'comp_t2' : R.TH1F('comp_t2'+ring+half, '', 2, 0, 2),
			}
			self.HISTS[ring+half]['time'].SetDirectory(0)
			self.HISTS[ring+half]['lumi'].SetDirectory(0)
			self.HISTS[ring+half]['totl'].SetDirectory(0)
			self.HISTS[ring+half]['occ'].SetDirectory(0)
			self.HISTS[ring+half]['lct'].SetDirectory(0)
			self.HISTS[ring+half]['comp_t0'].SetDirectory(0)
			self.HISTS[ring+half]['comp_t1'].SetDirectory(0)
			self.HISTS[ring+half]['comp_t2'].SetDirectory(0)

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
	canvas.save('pdfs/BGCompTime'+'_'+ring+'.pdf')
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

def makeLumiPlot(h1, h2, ring):
	binit = range(1, h1.GetNbinsX()+1)
	ncomps = [h1.GetBinContent(i) for i in binit]
	totals = [h2.GetBinContent(i) for i in binit]
	lumiA = np.array([(15.e33)/30 * (i+0.5) for i in range(30)])
	dataA = np.array([ncomp/float(total) if total != 0 else 0. for ncomp,total in zip(ncomps,totals)])
	lumi = np.array(lumiA[10:26])
	data = np.array(dataA[10:26])
	h = R.TGraph(len(lumi), lumi, data)

	plot = Plotter.Plot(h, option='PE')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.addMainPlot(plot)
	canvas.makeTransparent()
	canvas.scaleMargins(1.25, 'R')
	canvas.firstPlot.setTitles(X='Luminosity [cm^{-2}s^{-1}]', Y='#LT Number of Background Comparators #GT')
	canvas.firstPlot.GetXaxis().SetLimits(0., 15.e33)
	canvas.firstPlot.SetMinimum(0. )
	canvas.firstPlot.SetMaximum(0.6)
	canvas.firstPlot.scaleTitles(0.8)
	canvas.firstPlot.scaleLabels(0.8)
	canvas.firstPlot.scaleTitleOffsets(1.2)
	canvas.finishCanvas()
	canvas.save('pdfs/BGCompAvgN'+'_'+ring+'.pdf')
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

def makeLumiPlotLR(h1l, h2l, h1r, h2r, ring):
	binit = range(1, h1l.GetNbinsX()+1)
	ncompsl = [h1l.GetBinContent(i) for i in binit]
	totalsl = [h2l.GetBinContent(i) for i in binit]
	ncompsr = [h1r.GetBinContent(i) for i in binit]
	totalsr = [h2r.GetBinContent(i) for i in binit]
	lumiA = np.array([(15.e33)/30 * (i+0.5) for i in range(30)])
	dataAlist = []
	for ncompl,ncompr,totall,totalr in zip(ncompsl,ncompsr,totalsl,totalsr):
		sumC  = ncompr/float(totalr) if totalr != 0 else 0.
		sumC += ncompl/float(totall) if totall != 0 else 0.
		dataAlist.append(sumC)
	dataA = np.array(dataAlist)
	lumi = np.array(lumiA[10:26])
	data = np.array(dataA[10:26])
	h = R.TGraph(len(lumi), lumi, data)

	plot = Plotter.Plot(h, option='PE')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.addMainPlot(plot)
	canvas.makeTransparent()
	canvas.scaleMargins(1.25, 'R')
	canvas.firstPlot.setTitles(X='Luminosity [cm^{-2}s^{-1}]', Y='#LT Number of Background Comparators #GT')
	canvas.firstPlot.GetXaxis().SetLimits(0., 15.e33)
	canvas.firstPlot.SetMinimum(0. )
	canvas.firstPlot.SetMaximum(0.6)
	canvas.firstPlot.scaleTitles(0.8)
	canvas.firstPlot.scaleLabels(0.8)
	canvas.firstPlot.scaleTitleOffsets(1.2)
	canvas.finishCanvas()
	canvas.save('pdfs/BGCompAvgN'+'_'+ring+'_LR_norm.pdf')
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

def makeNumDum(h, ring, which):
	plot = Plotter.Plot(h, option='P')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.addMainPlot(plot)
	canvas.makeTransparent()
	canvas.scaleMargins(1.25, 'R')
	canvas.firstPlot.setTitles(X='Luminosity [cm^{-2}s^{-1}]', Y='Number of Background Comparators' if which == 'ncomp' else 'Counts')
	canvas.finishCanvas()
	canvas.save('pdfs/BGCompAvgN'+'_'+ring+'_'+which+'.pdf')
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

def makeOccPlot(h,ring):
	for logy in [True,False]:
		plot = Plotter.Plot(h,option='hist')
		canvas = Plotter.Canvas(lumi='ME'+ring+' Comparator Occupancy',logy=logy)
		canvas.addMainPlot(plot)
		canvas.makeTransparent()
		plot.setTitles(X='Comparator Half Strip',Y='Counts')
		canvas.finishCanvas()
		canvas.save('pdfs/BGCompOcc_'+ring, ['.pdf'])
		canvas.deleteCanvas()

def makeLCTPlot(h,ring):
	for logy in [True,False]:
		plot = Plotter.Plot(h,option='hist')
		canvas = Plotter.Canvas(lumi='ME'+ring+' LCT Occupancy',logy=logy)
		canvas.addMainPlot(plot)
		canvas.makeTransparent()
		plot.setTitles(X='Key Half Strip',Y='Counts')
		#canvas.finishCanvas('BOB')
		canvas.finishCanvas()
		canvas.save('pdfs/BGCompLCTOcc_'+ring,['.pdf'])
		canvas.deleteCanvas()

def makeCompPlot(h0,h1,h2,ring):
	for logy in [True,False]:
		plot0 = Plotter.Plot(h0,option='hist',legType='l',legName='Time Bin 0')
		plot1 = Plotter.Plot(h1,option='hist',legType='l',legName='Time Bin 1')
		plot2 = Plotter.Plot(h2,option='hist',legType='l',legName='Time Bin 2')
		canvas = Plotter.Canvas(lumi='ME'+ring+' L/R Comparator',logy=logy)
		canvas.addMainPlot(plot0)
		canvas.addMainPlot(plot1)
		canvas.addMainPlot(plot2)
		plot0.SetLineColor(R.kBlue)
		plot1.SetLineColor(R.kOrange+1)
		plot2.SetLineColor(R.kGreen)
		canvas.makeLegend(pos='tr')
		canvas.legend.moveLegend(X=-0.1)
		maximum = max(plot0.GetMaximum(),plot1.GetMaximum(),plot2.GetMaximum())
		canvas.firstPlot.SetMaximum(1.05*maximum)
		canvas.firstPlot.SetMinimum(0.)
		canvas.makeTransparent()
		canvas.firstPlot.setTitles(X='Comparator Half Strip Bit',Y='Counts')
		canvas.finishCanvas('BOB')
		canvas.save('pdfs/BGComp_LRbit_'+ring,['.pdf'])
		canvas.deleteCanvas()

for ring in RINGLIST:
	makeLumiPlotLR(data.HISTS[ring+'l']['lumi'], data.HISTS[ring+'l']['totl'],
				   data.HISTS[ring+'r']['lumi'], data.HISTS[ring+'r']['totl'],
				   ring)
	for half in ['l','r','']:
		makeLumiPlot(data.HISTS[ring+half]['lumi'], data.HISTS[ring+half]['totl'], ring+half)
		makeTimePlot(data.HISTS[ring+half]['time'], ring+half)
		makeNumDum(data.HISTS[ring+half]['lumi'], ring+half, 'ncomp')
		makeNumDum(data.HISTS[ring+half]['totl'], ring+half, 'lumi')
		makeOccPlot(data.HISTS[ring+half]['occ'], ring+half)
		makeLCTPlot(data.HISTS[ring+half]['lct'], ring+half)
		makeCompPlot(data.HISTS[ring+half]['comp_t0'], data.HISTS[ring+half]['comp_t1'], data.HISTS[ring+half]['comp_t2'], ring+half)

def makeAllTimePlot():
	h = data.HISTS[RINGLIST[0]]['time'].Clone()
	for ring in RINGLIST[1:]:
		h.Add(data.HISTS[ring]['time'])
	plot = Plotter.Plot(h, option='hist')
	plot.setTitles(X='Comparator Time [BX]',Y='Counts')
	canvas = Plotter.Canvas(lumi='All Stations', logy=False)
	canvas.addMainPlot(plot)
	canvas.makeTransparent()
	#canvas.firstPlot.plot.SetMaximum(1.05)
	canvas.firstPlot.plot.SetMinimum(0)
	#canvas.firstPlot.plot.SetMinimum(0.00001)
	canvas.finishCanvas()
	canvas.save('pdfs/BGCompTimeNewAll.pdf')
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

makeAllTimePlot()
