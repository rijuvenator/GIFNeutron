import sys, os, argparse
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS

RINGLIST = ['11', '12', '13', '21', '22', '31', '32', '41', '42']

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'P5'  : 'BGComp_P5.root'
	#'P5'  : 'BGComp_P5_noGap.root',
	#'P5'  : 'BGComp_P5_Gap8.root',
	#'P5'  : 'BGComp_P5_Gap11.root',
	#'P5'  : 'BGComp_P5_Gap35.root',
	#'P5'  : 'BGComp_P5_Gap35_NoZJetCut.root',
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA, REMAINDER = MS.ParseArguments(CONFIG, extraArgs=True)

parser = argparse.ArgumentParser()
parser.add_argument('-ng', '--nogap'     , action='store_false', dest='NOGAP')
parser.add_argument('-nz', '--nozjetcuts', action='store_false', dest='NOZJETS')
parser.add_argument('-f' , '--file'      , default=''          , dest='FILE')
parser.add_argument('-g' , '--gapsize'   , default='35'        , dest='GAP')
args = parser.parse_args(REMAINDER)

DOGAP   = args.NOGAP
DOZJETS = args.NOZJETS
GAP     = int(args.GAP)
OFN = 'BGComp_P5' + ('' if args.FILE == '' else '_') + args.FILE + '.root'
if FDATA is not None: FDATA = OFN

##### IMPLEMENT ANALYZERS #####
def analyze(self, t, PARAMS):
	DOGAP = PARAMS[2]
	DOZJETS = PARAMS[3]
	GAP = PARAMS[4]
	Primitives.SelectBranches(t, DecList=['LCT', 'COMP'])
	for idx, entry in enumerate(t):
		if idx == 10000: break
		#print 'Events    :', idx+1, '\r',

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

		# Background comparators
		if list(t.lct_id) == [] or list(t.comp_id) == []: continue
		E = Primitives.ETree(t, DecList=['LCT','COMP'])
		lcts  = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham ))]
		comps = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham))]

		twolcts = list(set([i for i in E.lct_cham if E.lct_cham.count(i)>1]))
		for lct in lcts:
			if lct.cham in twolcts: continue
			nComp = 0
			cham = CH.Chamber(lct.cham)
			nHS = cham.nstrips*2
			nWG = cham.nwires
			if cham.station==1 and cham.ring==1:
				# ME1/1a and ME1/1b are separated by a cut in the strips.
				# Since wires are tilted use the a/b divider as a crude radial cut
				# on LCT position instead of wires.
				# ME1/1b : strips  1 to  64 (top)    | hs   0 to 127 (top)
				# ME1/1a : strips 65 to 112 (bottom) | hs 128 to 224 (bottom)
				# (remember strips are numbered from 1 while hs are numbered from 0!)
				#
				# For ME1/1 the +/- endcaps are 'flipped' wrt each other
				# (+,0) is (-,3) and vice versa
				# (+,1) is (-,2) and vice versa
				# Does not actually matter for what we are doing but important to keep in mind!
				#
				# -> LCTAreas are defined for ME+1/1
				# ME+1/1b - 1 : (  0, 31) , 2 : ( 95,127) (hs are numbered R to L - top)
				# ME+1/1a - 0 : (200,224) , 3 : (128,152) (hs are numbered L to R - bottom)
				#
				# For opposite area, the set of opposite half halfstrips are disjoint for LCT 
				# areas 2 and 3
				#
				# -> OppAreas are defined for ME+1/1
				#           (top) +   (bottom)
				# 0,1 : (64, 127) + (128, 171)
				# 2,3 : ( 0,  63) + (172, 223)
				LCTAreas = \
				{
					0 : {'wg0' : 0. , 'wg1' : nWG , 'hs0' : 200. , 'hs1' : 223},
					1 : {'wg0' : 0. , 'wg1' : nWG , 'hs0' : 0.   , 'hs1' : 31 },
					2 : {'wg0' : 0. , 'wg1' : nWG , 'hs0' : 96   , 'hs1' : 127},
					3 : {'wg0' : 0. , 'wg1' : nWG , 'hs0' : 128  , 'hs1' : 151},
				}
				OppAreas = \
				{
					0 : {'hs0' : 64 , 'hs1' : 127 , 'hs2' : 128 , 'hs3' : 171},
					1 : {'hs0' : 64 , 'hs1' : 127 , 'hs2' : 128 , 'hs3' : 171},
					2 : {'hs0' :  0 , 'hs1' :  63 , 'hs2' : 172 , 'hs3' : 223},
					3 : {'hs0' :  0 , 'hs1' :  63 , 'hs2' : 172 , 'hs3' : 223},
				}
			else:
				LCTAreas = \
				{
					0 : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : 0.          , 'hs1' : nHS*0.25},
					1 : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : 0.          , 'hs1' : nHS*0.25},
					2 : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
					3 : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
				}
				OppAreas = \
				{
					0 : {'hs0' : (1-0.50)*nHS, 'hs1' : nHS     },
					1 : {'hs0' : (1-0.50)*nHS, 'hs1' : nHS     },
					2 : {'hs0' : 0.          , 'hs1' : nHS*0.50},
					3 : {'hs0' : 0.          , 'hs1' : nHS*0.50},
				}
			# Loop on all areas (we've already forced there to be only one LCT in this chamber)
			for key in LCTAreas.keys():
				# If LCT in a corner
				if  lct.keyWireGroup >= LCTAreas[key]['wg0'] and lct.keyWireGroup <= LCTAreas[key]['wg1']\
				and lct.keyHalfStrip >= LCTAreas[key]['hs0'] and lct.keyHalfStrip <= LCTAreas[key]['hs1']:
					for comp in comps:
						if comp.cham != lct.cham: continue
						# For comparators in opposite half of LCT
						OPPAREA = False
						if cham.station==1 and cham.ring==1:
							if ((comp.staggeredHalfStrip >= OppAreas[key]['hs0'] and comp.staggeredHalfStrip <= OppAreas[key]['hs1'])\
									or \
								(comp.staggeredHalfStrip >= OppAreas[key]['hs2'] and comp.staggeredHalfStrip <= OppAreas[key]['hs3'])):
								OPPAREA = True
						else:
							if comp.staggeredHalfStrip >= OppAreas[key]['hs0'] and comp.staggeredHalfStrip <= OppAreas[key]['hs1']:
								OPPAREA = True
						if OPPAREA:
							self.HISTS[cham.display('{S}{R}')]['time'].Fill(comp.timeBin)
							if comp.timeBin >= 1 and comp.timeBin <= 5:
								#print idx, cham.id, size, comp.timeBin
								nComp += 1
					self.HISTS[cham.display('{S}{R}')]['lumi'].Fill(self.lumi(t.Event_RunNumber, t.Event_LumiSection), float(nComp))
					self.HISTS[cham.display('{S}{R}')]['totl'].Fill(self.lumi(t.Event_RunNumber, t.Event_LumiSection), float(1.   ))

	self.F_OUT.cd()
	for ring in RINGLIST:
		self.HISTS[ring]['time'].Write()
		self.HISTS[ring]['lumi'].Write()
		self.HISTS[ring]['totl'].Write()

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
		self.HISTS[ring] = {\
			'time' : f.Get('t'+ring),
			'lumi' : f.Get('l'+ring),
			'totl' : f.Get('a'+ring),
		}
		self.HISTS[ring]['time'].SetDirectory(0)
		self.HISTS[ring]['lumi'].SetDirectory(0)
		self.HISTS[ring]['totl'].SetDirectory(0)

# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	self.COUNTS = {}
	self.HISTS = {}
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	for ring in RINGLIST:
		self.HISTS[ring] = {\
			'time': R.TH1F('t'+ring, '', 10, 0., 10.),
			'lumi': R.TH1F('l'+ring, '', 30, 0., 15.e33),
			'totl': R.TH1F('a'+ring, '', 30, 0., 15.e33),
		}
		self.HISTS[ring]['time'].SetDirectory(0)
		self.HISTS[ring]['lumi'].SetDirectory(0)
		self.HISTS[ring]['totl'].SetDirectory(0)

def cleanup(self, PARAMS):
	print ''
	pass

##### DECLARE ANALYZERS AND RUN ANALYSIS #####
R.gROOT.SetBatch(True)
METHODS = ['analyze', 'load', 'setup', 'cleanup']
ARGS = {\
	'PARAMS'     : [OFN, TYPE, DOGAP, DOZJETS, GAP],
	'F_DATAFILE' : FDATA
}
if TYPE == 'GIF':
	ARGS['ATTLIST'] = [float('inf')]
Analyzer = getattr(MS, TYPE+'Analyzer')
for METHOD in METHODS:
	setattr(Analyzer, METHOD, locals()[METHOD])
data = Analyzer(**ARGS)

##### MAKE PLOTS #####
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

for ring in RINGLIST:
	makeTimePlot(data.HISTS[ring]['time'], ring)
	makeLumiPlot(data.HISTS[ring]['lumi'], data.HISTS[ring]['totl'], ring)
	makeNumDum(data.HISTS[ring]['lumi'], ring, 'ncomp')
	makeNumDum(data.HISTS[ring]['totl'], ring, 'lumi')

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
makeAllTimePlot()
