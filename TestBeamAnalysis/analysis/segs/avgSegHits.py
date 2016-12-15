import numpy as np
import Gif.TestBeamAnalysis.Plotter as Plotter
import ROOT as R
import sys
import Gif.TestBeamAnalysis.Primitives as Primitives

### PARAMETERS
# Which chambers to do; to compare to Yuriy only use ME1/1
# chamlist = [1]
chamlist = [1, 2]

# Which files contain the relevant list of measurements and currents
f_measgrid = '../datafiles/measgrid'
f_attenhut = '../datafiles/attenhut'

# Whether or not to only use Yuriy's 5 attenuations
castrated = False

# Whether or not to get the data from a file. None if not; filename if so.
#fromFile = None
fromFile = '../datafiles/data_seghits'

# Dictionary containing cosmetic data, comment out for fewer ones
pretty = {
	0 : { 'name' : 'Original',        'color' : R.kRed-3,   'marker' : R.kFullCircle      },
	1 : { 'name' : 'TightPreCLCT',    'color' : R.kBlue-1,  'marker' : R.kFullSquare      },
	2 : { 'name' : 'TightCLCT',       'color' : R.kOrange,  'marker' : R.kFullTriangleUp  },
	3 : { 'name' : 'TightALCT',       'color' : R.kGreen+2, 'marker' : R.kFullCross       },
	4 : { 'name' : 'TightPrePID',     'color' : R.kMagenta, 'marker' : R.kFullTriangleDown},
	5 : { 'name' : 'TightPrePostPID', 'color' : R.kAzure+8, 'marker' : R.kFullDiamond     },
	6 : { 'name' : 'TightPA',         'color' : R.kGray,    'marker' : R.kFullStar        },
	7 : { 'name' : 'TightAll',        'color' : R.kBlack,   'marker' : R.kFullCircle      }
}

R.gROOT.SetBatch(True)

###############################################################################################
### BEGIN CODE
### DATA STRUCTURE CLASS
class MegaStruct():
	def __init__(self,measgrid,attenhut,fromFile,castrated):
		self.castrated = castrated

		# Fill dictionary connecting attenuation to list of measurement numbers, ordered by FF
		f = open(measgrid)
		self.FFFMeas = {}
		for line in f:
			cols = line.strip('\n').split()
			self.FFFMeas[float(cols[0])] = [int(j) for j in cols[1:]]
		f.close()

		# Fill dictionary connecting chamber and measurement number to list of currents
		f = open(attenhut)
		self.Currs = { 1 : {}, 2 : {} }
		currentCham = 1
		for line in f:
			if line == '\n':
				currentCham = 2
				continue
			cols = line.strip('\n').split()
			currentMeas = int(cols[1])
			self.Currs[currentCham][currentMeas] = [float(i) for i in cols[2:]]
		f.close()

		# Fill dictionary connecting chamber and measurement number to average segment nHits
		self.Vals = { 1 : {}, 2 : {} }
		if fromFile is None:
			for att in self.FFFMeas.keys():
				for meas in self.FFFMeas[att]:
					f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/15Dec/ana_'+str(meas)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')
					nSeg       = {1:0, 110:0}
					nNHits     = {1:0, 110:0}
					nSegMuon   = {1:0, 110:0}
					nNHitsMuon = {1:0, 110:0}
					for entry in t:
						E = Primitives.ETree(t, DecList=['SEGMENT', 'LCT'])
						segs = [Primitives.Segment(E, i) for i in range(len(E.seg_cham))]
						lcts = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham))]
						for cham in (1, 110):
							nSeg  [cham] += E.seg_cham.count(cham)
							nNHits[cham] += sum([seg.nHits for seg in segs if seg.cham == cham])

							for seg in segs:
								if seg.cham != cham: continue
								for lct in lcts:
									if lct.cham != cham: continue
									if self.inPad(seg.halfStrip[3], seg.wireGroup[3], cham if cham == 1 else 2) and self.matchSegLCT(seg, lct):
										nSegMuon  [cham] += 1
										nNHitsMuon[cham] += seg.nHits
										break

					self.Vals[1][meas] = {'all':0., 'muon':0.}
					self.Vals[2][meas] = {'all':0., 'muon':0.}

					self.Vals[1][meas]['all' ] = float(nNHits    [1  ])/nSeg    [1  ] if nSeg    [1  ] != 0 else 0
					self.Vals[2][meas]['all' ] = float(nNHits    [110])/nSeg    [110] if nSeg    [110] != 0 else 0
					self.Vals[1][meas]['muon'] = float(nNHitsMuon[1  ])/nSegMuon[1  ] if nSegMuon[1  ] != 0 else 0
					self.Vals[2][meas]['muon'] = float(nNHitsMuon[110])/nSegMuon[110] if nSegMuon[110] != 0 else 0

					print '{:4d} {:7.3f} {:7.3f} {:7.3f} {:7.3f}'.format(\
						meas,
						self.Vals[1][meas]['all' ],
						self.Vals[2][meas]['all' ],
						self.Vals[1][meas]['muon'],
						self.Vals[2][meas]['muon']
					)
		else:
			# this file is the output of the printout above
			f = open(fromFile)
			for line in f:
				cols = line.strip('\n').split()
				meas = int(cols[0])
				self.Vals[1][meas] = {'all':0., 'muon':0.}
				self.Vals[2][meas] = {'all':0., 'muon':0.}

				self.Vals[1][meas]['all' ] = float(cols[1])
				self.Vals[2][meas]['all' ] = float(cols[2])
				self.Vals[1][meas]['muon'] = float(cols[3])
				self.Vals[2][meas]['muon'] = float(cols[4])

	# defines a paddle region
	def inPad(self, hs, wg, cham):
		if cham == 1:
			if      hs >=  25\
				and hs <=  72\
				and wg >=  37\
				and wg <=  43:
				return True
			else:
				return False
		if cham == 2:
			if      hs >=   8\
				and hs <=  38\
				and wg >=  55\
				and wg <=  65:
				return True
			else:
				return False
	
	# determines if a segment and an lct match each other
	def matchSegLCT(self, seg, lct):
		if abs(seg.halfStrip[3] - lct.keyHalfStrip) <= 2 and abs(seg.wireGroup[3] - lct.keyWireGroup) <= 2:
			return True
		else:
			return False
	
	# get a current measurement given a chamber and measurement number
	def current(self, cham, meas):
		if cham == 1:
			return sum(self.Currs[cham][meas])/6.0
		elif cham == 2:
			return sum(self.Currs[cham][meas][6:12])/6.0
	
	# get a value given a chamber and measurement number
	def val(self, cham, meas, type_):
		return self.Vals[cham][meas][type_]

	# get a vector of attenuations
	def attVector(self):
		if self.castrated:
			return np.array([33., 46., 100., float('inf')])
		else:
			return np.array(sorted(self.FFFMeas.keys()))

	# get a vector of currents
	def currentVector(self, cham, ff):
		return np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	# get a vector of equivalent luminosities
	def lumiVector(self, cham, ff):
		factor = 3.e33 if cham == 1 else 5.e33
		return factor * np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	# get a vector of values
	def valVector(self, cham, ff, type_):
		return np.array([self.val(cham, self.FFFMeas[att][ff], type_) for att in self.attVector()])

data = MegaStruct(f_measgrid, f_attenhut, fromFile, castrated)

### MAKEPLOT FUNCTION
def makePlot(x, y, cham, xtitle, ytitle, title, pretty=pretty):
	# *** USAGE:
	#  1) construct Plotter.Plot(Object, legName, legType="felp", option)
	#  2) construct Plotter.Canvas(lumi, logy, ratioFactor, extra, cWidth=800, cHeight=600)
	#  3) call Plotter.Canvas.makeLegend(lWidth=0.125, lHeight=0.2, pos="tr", lOffset=0.02, fontsize=0.04)
	#  4) call Plotter.Canvas.addMainPlot(Plot, isFirst, addToLegend)
	#  5) apply any cosmetic commands here
	# *6) call Plotter.Canvas.addLegendEntry(Plot)
	# *7) call Plotter.Canvas.makeRatioPlot(top, bottom, plusminus, option, ytit, xtit)
	#  8) call Plotter.Canvas.finishCanvas()
	#
	# * = optional; if addToLegend is always true, and/or if no ratio plot needed (ratioFactor = 0), neither of these steps are required
	#
	# Plotter.Canvas class members c, mainPad, ratPad, leg, rat, and gr are available
	#
	# Note: If TYPE is a TGraph and option="P", a draw option of "AP" is required for the FIRST plot (first addMainPlot)
	# So change plot.option, either to "P" after (if option="AP"), or change plot.option to "AP" before and "P" after (if option="P")
	#

	graphs = []
	ntypes = len(pretty.keys())
	for i in range(ntypes):
		graphs.append(R.TGraph(len(x[i]), x[i], y[i]))

	# Step 1
	plots = []
	for i,p in enumerate(pretty.keys()):
		plots.append(Plotter.Plot(graphs[i], pretty[p]['name'], 'p', 'AP' if i==0 else 'P'))

	# Step 2
	canvas = Plotter.Canvas('ME'+str(cham)+'/1 External Trigger', False, 0., 'Internal', 800, 700)

	# Step 3
	canvas.makeLegend(.2,0.25,'bl',0.04, 0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i], i==0, True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	graphs[0].GetYaxis().SetTitle(ytitle)
	graphs[0].GetXaxis().SetTitle(xtitle)
	graphs[0].SetMinimum(3.0)
	graphs[0].SetMaximum(6.0)
	plots[0].scaleTitles(0.8)
	plots[0].scaleLabels(0.8)
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
for cham in chamlist:
	# Plots with luminosity on x-axis
	makePlot(\
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.valVector(cham, ff, 'all') for ff in pretty.keys()],
		cham,
		'Luminosity [Hz/cm^{2}]',
		'#LT Segment nHits, all #GT',
		'lumi_all'
	)
	makePlot(\
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.valVector(cham, ff, 'muon') for ff in pretty.keys()],
		cham,
		'Luminosity [Hz/cm^{2}]',
		'#LT Segment nHits, muon #GT',
		'lumi_muon'
	)
