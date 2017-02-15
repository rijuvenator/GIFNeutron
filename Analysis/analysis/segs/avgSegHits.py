import numpy as np
import Gif.Analysis.OldPlotter as Plotter
import ROOT as R
import sys
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Auxiliary as Aux
from Gif.Analysis.MegaStruct import F_GIFDATA

##### PARAMETERS #####
# Which chambers to do
CHAMLIST = (1, 110)

##### SEMI-PARAMETERS #####
# Filenames
F_MEASGRID = '../datafiles/measgrid'
F_ATTENHUT = '../datafiles/attenhut'
#F_DATAFILE = None
F_DATAFILE = '../datafiles/data_seghits'

# Cosmetic data dictionary, comment out for fewer ones
pretty = {
	0 : { 'name' : 'Original',        'color' : R.kRed-3,   'marker' : R.kFullCircle      },
#	1 : { 'name' : 'TightPreCLCT',    'color' : R.kBlue-1,  'marker' : R.kFullSquare      },
#	2 : { 'name' : 'TightCLCT',       'color' : R.kOrange,  'marker' : R.kFullTriangleUp  },
#	3 : { 'name' : 'TightALCT',       'color' : R.kGreen+2, 'marker' : R.kFullCross       },
#	4 : { 'name' : 'TightPrePID',     'color' : R.kMagenta, 'marker' : R.kFullTriangleDown},
#	5 : { 'name' : 'TightPrePostPID', 'color' : R.kAzure+8, 'marker' : R.kFullDiamond     },
#	6 : { 'name' : 'TightPA',         'color' : R.kGray,    'marker' : R.kFullStar        },
#	7 : { 'name' : 'TightAll',        'color' : R.kBlack,   'marker' : R.kFullCircle      }
}

##### BEGIN CODE #####
R.gROOT.SetBatch(True)

##### MEGASTRUCT CLASS #####
class MegaStruct():
	#### BEGIN MEGASTRUCT COMMON: DO NOT EDIT BETWEEN THESE TAGS #####
	def __init__(self):
		self.fillMeas()
		self.fillCurr()
		self.fillData()
	
	# general fill measurement data function
	def fillMeas(self):
		f = open(F_MEASGRID)
		self.MEASDATA = {}
		for line in f:
			cols = line.strip('\n').split()
			self.MEASDATA[float(cols[0])] = [int(j) for j in cols[1:]]
		f.close()

	# general fill current data function
	def fillCurr(self):
		f = open(F_ATTENHUT)
		self.CURRDATA = { 1 : {}, 110: {} }
		currentCham = 1
		for line in f:
			if line == '\n':
				currentCham = 110
				continue
			cols = line.strip('\n').split()
			currentMeas = int(cols[1])
			self.CURRDATA[currentCham][currentMeas] = [float(i) for i in cols[2:]]
		f.close()

	# get a current measurement given a chamber and measurement number
	def current(self, cham, meas):
		if cham == 1:
			return sum(self.CURRDATA[cham][meas])/6.0
		elif cham == 110:
			return sum(self.CURRDATA[cham][meas][6:12])/6.0
	
	# get a vector of attenuations
	def attVector(self, castrated=False):
		if castrated: # for comparing to Yuriy
			return np.array([33., 46., 100., float('inf')])
		else:
			return np.array(sorted(self.MEASDATA.keys()))

	# get a vector of currents
	def currentVector(self, cham, ff, castrated=False):
		return np.array([self.current(cham, self.MEASDATA[att][ff]) for att in self.attVector(castrated)])

	# get a vector of equivalent luminosities
	def lumiVector(self, cham, ff, castrated=False):
		factor = 3.e33 if cham == 1 else 5.e33
		return factor * np.array([self.current(cham, self.MEASDATA[att][ff]) for att in self.attVector(castrated)])
	##### END MEGASTRUCT COMMON: DO NOT EDIT BETWEEN THESE TAGS #####

	# fill data: this function, and the access functions below it, are "user-defined" and script-dependent
	def fillData(self):
		self.VALDATA = { 1 : {}, 110: {} }
		if F_DATAFILE is None:
			for ATT in self.MEASDATA.keys():
				for MEAS in self.MEASDATA[ATT][0:1]: # only original
					f = R.TFile.Open(F_GIFDATA.replace('XXXX',str(MEAS)))
					t = f.Get('GIFTree/GIFDigiTree')
					nSeg       = {1:0, 110:0}
					nNHits     = {1:0, 110:0}
					nSegMuon   = {1:0, 110:0}
					nNHitsMuon = {1:0, 110:0}
					for entry in t:
						E = Primitives.ETree(t, DecList=['SEGMENT', 'LCT'])
						segs = [Primitives.Segment(E, i) for i in range(len(E.seg_cham))]
						lcts = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham))]
						for CHAM in CHAMLIST:
							nSeg  [CHAM] += E.seg_cham.count(CHAM)
							nNHits[CHAM] += sum([seg.nHits for seg in segs if seg.cham == CHAM])

							for lct in lcts:
								if lct.cham != CHAM: continue
								if not Aux.inPad(lct.keyHalfStrip,lct.keyWireGroup,CHAM): continue
								found, seg = Aux.bestSeg(lct, segs)
								if not found: continue
								nSegMuon  [CHAM] += 1
								nNHitsMuon[CHAM] += seg.nHits

					for CHAM in CHAMLIST:
						self.VALDATA[CHAM][MEAS] = {\
							'all' : float(nNHits    [CHAM])/nSeg    [CHAM] if nSeg    [CHAM] != 0 else 0.,
							'muon': float(nNHitsMuon[CHAM])/nSegMuon[CHAM] if nSegMuon[CHAM] != 0 else 0.
						}

					print '{:4d} {:7.3f} {:7.3f} {:7.3f} {:7.3f}'.format(\
						MEAS,
						self.VALDATA[1  ][MEAS]['all' ],
						self.VALDATA[110][MEAS]['all' ],
						self.VALDATA[1  ][MEAS]['muon'],
						self.VALDATA[110][MEAS]['muon']
					)
		else:
			# this file is the output of the printout above
			f = open(F_DATAFILE)
			for line in f:
				cols = line.strip('\n').split()
				MEAS = int(cols[0])
				self.VALDATA[1  ][MEAS] = {'all':0., 'muon':0.}
				self.VALDATA[110][MEAS] = {'all':0., 'muon':0.}

				self.VALDATA[1  ][MEAS]['all' ] = float(cols[1])
				self.VALDATA[110][MEAS]['all' ] = float(cols[2])
				self.VALDATA[1  ][MEAS]['muon'] = float(cols[3])
				self.VALDATA[110][MEAS]['muon'] = float(cols[4])

	# get a value given a chamber and measurement number
	def val(self, cham, meas, which):
		return float(self.VALDATA[cham][meas][which])

	# get a vector of values
	def valVector(self, cham, ff, which):
		return np.array([self.val(cham, self.MEASDATA[att][ff], which) for att in self.attVector()])

data = MegaStruct()

### MAKEPLOT FUNCTION
def makePlot(x, y, cham, xtitle, ytitle, title, pretty=pretty):
	# *** USAGE:
	#  1) construct Plotter.Plot(Object, legName, legType="felp", option)
	#  2) construct Plotter.Canvas(lumi, logy, ratioFactor, extra, cWidth=800, cHeight=600)
	#  3) call Plotter.Canvas.makeLegend(lWidth=0.125, lHeight=0.2, pos="tr", lOffset=0.02, fontsize=0.04)
	#  4) call Plotter.Canvas.addMainPlot(Plot, addToLegend)
	#  5) apply any cosmetic commands here
	# *6) call Plotter.Canvas.addLegendEntry(Plot)
	# *7) call Plotter.Canvas.makeRatioPlot(top, bottom, plusminus, option, ytit, xtit)
	#  8) call Plotter.Canvas.finishCanvas()
	#
	# * = optional; if addToLegend is always true, and/or if no ratio plot needed (ratioFactor = 0), neither of these steps are required
	#
	# Plotter.Canvas class members c, mainPad, ratPad, leg, rat, and gr are available
	#

	graphs = []
	ntypes = len(pretty.keys())
	for i in range(ntypes):
		graphs.append(R.TGraph(len(x[i]), x[i], y[i]))

	# Step 1
	plots = []
	for i,p in enumerate(pretty.keys()):
		plots.append(Plotter.Plot(graphs[i], pretty[p]['name'], 'p', 'P'))

	# Step 2
	canvas = Plotter.Canvas('ME'+str(cham)+'/1 External Trigger', False, 0., 'Internal', 800, 700)

	# Step 3
	canvas.makeLegend(.2,0.25,'bl',0.04, 0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i], addToLegend=True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	canvas.firstPlot.plot.GetYaxis().SetTitle(ytitle)
	canvas.firstPlot.plot.GetXaxis().SetTitle(xtitle)
	canvas.firstPlot.plot.SetMinimum(3.0)
	canvas.firstPlot.plot.SetMaximum(6.0)
	canvas.firstPlot.scaleTitles(0.8)
	canvas.firstPlot.scaleLabels(0.8)
	canvas.makeTransparent()

	for i,p in enumerate(pretty.keys()):
		graphs[i].SetMarkerColor(pretty[p]['color'])
		graphs[i].SetMarkerStyle(pretty[p]['marker'])
		graphs[i].SetMarkerSize(2.2)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/Seg_'+str(cham)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

### MAKE ALL PLOTS
for CHAM in CHAMLIST:
	# Plots with luminosity on x-axis
	makePlot(\
		[data.lumiVector(CHAM, ff) for ff in pretty.keys()],
		[data.valVector(CHAM, ff, 'all') for ff in pretty.keys()],
		CHAM/110+1,
		'Luminosity [cm^{-2}s^{-1}]',
		'#LT Segment nHits #GT',
		'lumi_all'
	)
	makePlot(\
		[data.lumiVector(CHAM, ff) for ff in pretty.keys()],
		[data.valVector(CHAM, ff, 'muon') for ff in pretty.keys()],
		CHAM/110+1,
		'Luminosity [cm^{-2}s^{-1}]',
		'#LT Muon Segment nHits #GT',
		'lumi_muon'
	)
