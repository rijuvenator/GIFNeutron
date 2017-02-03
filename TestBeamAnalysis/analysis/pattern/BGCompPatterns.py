import os, math
import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.Plotter as Plotter
import Gif.TestBeamAnalysis.Auxiliary as Aux
import Gif.TestBeamAnalysis.ChamberHandler as CH
import Gif.TestBeamAnalysis.MegaStruct as MS

PFN = 'bgpatterns.root'

FP = None
#FP = PFN

def PatternID(comp, comps):
	id_ = 0

	# definition of bits
	bits = (\
		(-1, +1), # 0
		( 0, +1), # 1
		(+1, +1), # 2
		(+1,  0), # 3
		(+1, -1), # 4
		( 0, -1), # 5
		(-1, -1), # 6
		(-1,  0)  # 7
	)
	# compute ID
	for c in comps:
		if c.cham != comp.cham: continue
		for bit,(SHS,LAY) in enumerate(bits):
			if  c.staggeredHalfStrip == comp.staggeredHalfStrip + SHS\
			and c.layer              == comp.layer              + LAY:
				id_ = id_ | (1<<bit)
	
	# list of edges for each bit, ordered clockwise
	edges = (\
		((-2,  0), (-2, +1), (-2, +2), (-1, +2), ( 0, +2)), # 0
		((-1, +2), ( 0, +2), (+1, +2)                    ), # 1
		(( 0, +2), (+1, +2), (+2, +2), (+2, +1), (+2,  0)), # 2
		((+2, +1), (+2,  0), (+2, -1)                    ), # 3
		((+2,  0), (+2, -1), (+2, -2), (+1, -2), ( 0, -2)), # 4
		((+1, -2), ( 0, -2), (-1, -2)                    ), # 5
		(( 0, -2), (-1, -2), (-2, -2), (-2, -1), (-2,  0)), # 6
		((-2, -1), (-2,  0), (-2, +1)                    )  # 7
	)

	# figure out list of edges To Be Considered
	tbc = []
	for bit, edgelist in enumerate(edges):
		if id_ & (1<<bit):
			tbc.extend(list(edgelist))
	tbc = list(set(tbc))

	# veto if edge comparators exist
	for c in comps:
		if c.cham != comp.cham: continue
		for SHS, LAY in tbc:
			if  c.staggeredHalfStrip == comp.staggeredHalfStrip + SHS\
			and c.layer              == comp.layer              + LAY:
				#print '{:2d} {:2d} {:2d}'.format(SHS, LAY, id_)
				return -1

	return id_


# make sure you're not accidentally overwriting anything
if os.path.isfile(PFN) and FP is None:
	answer = raw_input('OK to overwrite existing files? [y/n] ')
	if answer == 'y':
		print 'Overwriting files...'
	else:
		print 'Using existing files...'
		FP = PFN

# make sure the file exists
if not os.path.isfile(PFN) and FP is not None:
	print 'Input files do not exist; exiting now...'
	exit()

# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	FN = PARAMS
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	self.HIST = R.TH1F('h', '', 256, 0, 256)
	self.HIST.SetDirectory(0)

# once per file
def analyze(self, t, PARAMS):
	for idx, entry in enumerate(t):
		#print 'Events:', idx, '\r',

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

		twolcts = list(set([i for i in E.lct_cham if E.lct_cham.count(i)>1]))
		for lct in lcts:
			if lct.cham in twolcts: continue
			cham = CH.Chamber(lct.cham)
			nHS = cham.nstrips*2
			nWG = cham.nwires
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
			for key in LCTAreas.keys():
				if  lct.keyWireGroup >= LCTAreas[key]['wg0'] and lct.keyWireGroup <= LCTAreas[key]['wg1']\
				and lct.keyHalfStrip >= LCTAreas[key]['hs0'] and lct.keyHalfStrip <= LCTAreas[key]['hs1']:
					for comp in comps:
						if comp.cham != lct.cham: continue
						if comp.staggeredHalfStrip >= OppAreas[key]['hs0'] and comp.staggeredHalfStrip <= OppAreas[key]['hs1']:
							if comp.timeBin >= 1 and comp.timeBin <= 5:
								pid = PatternID(comp, comps)
								if pid >= 0:
									self.HIST.Fill(pid)
									if pid == 34:
										print idx, comp.cham


	self.F_OUT.cd()
	self.HIST.Write()

def cleanup(self, PARAMS):
	print ''

# if file is already made
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HIST = f.Get('h')
	self.HIST.SetDirectory(0)

# override class methods
R.gROOT.SetBatch(True)
MS. P5Analyzer.analyze = analyze
MS. P5Analyzer.load = load
MS. P5Analyzer.setup = setup
MS. P5Analyzer.cleanup = cleanup

# run analysis!
pdata = MS.P5Analyzer (PARAMS=PFN, F_DATAFILE=FP, RUNLIST=[282663])

##### MAKEPLOT FUNCTIONS #####
def makePlot(h):
	print 'The histogram was filled', int(h.GetEntries()), 'times'
	pdict = {}
	for i in range(256):
		if h.GetBinContent(i+1)>0:
			#print '{:3d} {:6d}'.format(i, int(plot.GetBinContent(i+1)))
			pdict[i] = int(h.GetBinContent(i+1))

	labels = [\
		0,                   # 1 isolated
		1, 16, 4, 64,        # 2 diag: neg neg pos pos
			2, 32,           # 2 vert
			8, 128,          # 2 horiz
		3, 24, 160,          # 3 Corner
			6, 40, 192,      # 3 Gamma
			9, 72, 132, 144, # 3 knight: TL BL TR BR
			10, 48, 129,     # 3 L
			12, 96, 130,     # 3 J
			17, 68,          # 3 diag: neg pos
			18, 33, 36, 66,  # 3 periscope: BR TL TR BR
			5, 20, 80, 65,   # 3 C: U R B L
			34,              # 3 vert
			136,             # 3 horiz
		161                  # 4 S
	]
	for label in labels:
		if label not in pdict.keys():
			pdict[label] = 0

	print 'List of new IDs are:', [i for i in pdict.keys() if i not in labels]

	binslices = {\
		1 : range(1 , 2 ),
		2 : range(2 , 10),
		3 : range(10, 38),
		4 : range(38, 39)
	}

	hists = {}
	for ncomps in binslices.keys():
		hists[ncomps] = R.TH1F('hists'+str(ncomps), '', len(labels), 0, len(labels))
		for bin_ in binslices[ncomps]:
			hists[ncomps].SetBinContent(bin_, pdict[labels[bin_-1]])
	for bin_, label in enumerate(labels):
		hists[1].GetXaxis().SetBinLabel(bin_+1, str(label))
	
	plots = {}
	for ncomps in binslices.keys():
		plots[ncomps] = Plotter.Plot(hists[ncomps], option='hist', legName=str(ncomps)+' hits', legType='f')

	canvas = Plotter.Canvas(lumi='Background Comparators Pattern ID', cWidth=1500, logy=True)
	R.gStyle.SetLineWidth(1)

	for ncomps in binslices.keys():
		canvas.addMainPlot(plots[ncomps])

	canvas.makeTransparent()
	canvas.scaleMargins(0.5, 'L')
	canvas.firstPlot.setTitles(X='Pattern ID', Y='Counts')
	canvas.firstPlot.scaleLabels(1.25, 'X')
	canvas.firstPlot.scaleTitleOffsets(0.6, 'Y')
	canvas.firstPlot.SetMaximum(10**math.ceil(math.log(canvas.firstPlot.GetMaximum(),10)) - 1)
	canvas.firstPlot.SetMinimum(10**-1 + 0.0001)

	canvas.scaleMargins(2., 'R')
	canvas.makeLegend()
	canvas.legend.moveLegend(X=.16)

	colors = {1 : R.kGreen, 2 : R.kBlue, 3 : R.kOrange, 4 : R.kRed}
	for ncomps in binslices.keys():
		plots[ncomps].SetLineWidth(0)
		plots[ncomps].SetFillColor(colors[ncomps])

	# two neighboring comparators; should be suppressed
	shades = R.TH1F('shades','',len(labels), 0, len(labels))
	bins = [3, 24, 160, 6, 40, 192, 8, 128, 9, 72, 132, 144, 10, 48, 129, 12, 96, 130, 136, 161]
	for bin_ in bins:
		shades.SetBinContent(labels.index(bin_)+1, canvas.firstPlot.GetMaximum())
	shades.SetLineWidth(0)
	shades.SetFillStyle(3004)
	shades.SetFillColorAlpha(R.kBlack, 0.5)
	shades.Draw('same')
	for ncomps in binslices.keys():
		plots[ncomps].Draw('same')

	ymin = canvas.firstPlot.GetMinimum()
	ymax = canvas.firstPlot.GetMaximum()
	lines = []
	bins = [0, 64, 32, 128, 160, 192, 144, 129, 130, 68, 66, 65, 34, 136, 161]
	for bin_ in bins:
		lines.append(R.TLine(labels.index(bin_)+1, ymin, labels.index(bin_)+1, ymax))
		lines[-1].Draw()

	canvas.finishCanvas()
	canvas.save('pdfs/BGPatterns.pdf')
	R.SetOwnership(canvas, False)

makePlot(pdata.HIST)
