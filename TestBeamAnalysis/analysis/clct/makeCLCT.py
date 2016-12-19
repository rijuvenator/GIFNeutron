import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Plotter as Plotter
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.roottools as tools
import Gif.TestBeamAnalysis.Auxiliary as Aux
import sys

### PARAMETERS
# Which chambers to do; to compare to Yuriy only use ME1/1
# chamlist = [1]
chamlist = [1, 110]

# Which files contain the relevant list of measurements and currents
f_measgrid = '../datafiles/measgrid'
f_attenhut = '../datafiles/attenhut'

# Whether or not to only use Yuriy's 5 attenuations
castrated = False

# Whether or not to get the data from a file. None if not; filename if so.
#fromFile = None
fromFile = '../datafiles/clctLay'

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
		self.Currs = { 1 : {}, 110 : {} }
		currentCham = 1
		for line in f:
			if line == '\n':
				currentCham = 110
				continue
			cols = line.strip('\n').split()
			currentMeas = int(cols[1])
			self.Currs[currentCham][currentMeas] = [float(i) for i in cols[2:]]
		f.close()

		# Fill dictionary connecting chamber, measurement number, and efftype to efficiency value
		self.clctLay = { 1 : {}, 110 : {} }
		if fromFile is None:
			pass
			for att in self.FFFMeas.keys():
				for meas in self.FFFMeas[att]:
					f = R.TFile.Open('/afs/cern.ch/work/a/adasgupt/public/GIF/16Dec/ana_'+str(meas)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')
					clctLay11 = []
					clctLay21 = []
					nCLCT11 = 0
					nCLCT21 = 0
					for entry in t:
						DecList = ['SEGMENT','CLCT']
						E = Primitives.ETree(t, DecList)
						clcts   = [Primitives.CLCT   (E, i) for i in range(len(E.clct_cham  ))]
						segs    = [Primitives.Segment(E, i) for i in range(len(E.seg_cham  ))]

						for cham in [1,110]:
							alreadyMatchedSeg = []
							for clct in clcts:
								# Check on chamber and LCT position
								if clct.cham!=cham: continue
								if not Aux.inPad(clct.keyHalfStrip, 40 if cham == 1 else 60, cham): continue
								for s,seg in enumerate(segs):
									# Check on chamber, segment position, match the segment to the lct, and if we've already matched the segment
									if seg.cham!=cham: continue
									if not Aux.inPad(seg.halfStrip[3], seg.wireGroup[3], cham): continue
									if not self.matchSegCLCT(seg,clct): continue
									if s in alreadyMatchedSeg: continue
									alreadyMatchedSeg.append(s)
									if cham==1:
										clctLay11.append(clct.quality)
										nCLCT11 += 1
									if cham==110:
										clctLay21.append(clct.quality)
										nCLCT21 += 1
									break

					# fill dictionary
					self.clctLay[1][meas] = np.array(clctLay11).mean()
					self.clctLay[110][meas] = np.array(clctLay21).mean()
					print meas, self.clctLay[1][meas], self.clctLay[110][meas]
		else:
			f = open(fromFile)
			for line in f:
				cols = line.strip('\n').split()
				meas = int(cols[0])
				self.clctLay[1][meas] = float(cols[1])
				self.clctLay[110][meas] = float(cols[2])

	# a segment match is if the lct halfstrip is within 2 halfstrips of the segment halfstrip and 1 wire group 
	def matchSegCLCT(self, seg, clct):
		diffHS = abs(seg.halfStrip[3] - clct.keyHalfStrip)
		if diffHS<=2:
			return True
		else:
			return False

	# get a current measurement given a chamber and measurement number
	def current(self, cham, meas):
		if cham == 1:
			return sum(self.Currs[cham][meas])/6.0
		elif cham == 110:
			return sum(self.Currs[cham][meas][6:12])/6.0
	
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
		factor = 5.e33 if cham == 110 else 3.e33
		return factor * np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	def clct(self, cham, meas):
		return self.clctLay[cham][meas]

	def clctVector(self, cham, ff):
		return np.array([self.clct(cham, self.FFFMeas[att][ff]) for att in self.attVector()])


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

	CHAM = 1 if cham==1 else 2
	graphs = []
	ntypes = len(pretty.keys())
	for i in range(ntypes):
		graphs.append(R.TGraph(len(x[i]), x[i], y[i]))

	# Step 1
	plots = []
	for i,p in enumerate(pretty.keys()):
		plots.append(Plotter.Plot(graphs[i], pretty[p]['name'], 'pe', 'APE' if i==0 else 'PE'))

	# Step 2
	canvas = Plotter.Canvas('ME'+str(CHAM)+'/1 External Trigger', False, 0., 'Internal', 800, 700)

	# Step 3
	canvas.makeLegend(.2,0.25,'bl',0.04, 0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i], i==0, True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	graphs[0].GetYaxis().SetTitle(ytitle)
	graphs[0].GetXaxis().SetTitle(xtitle)
	graphs[0].SetMinimum(0.0)
	graphs[0].SetMaximum(6.1)
	plots[0].scaleTitles(0.8)
	plots[0].scaleLabels(0.8)
	canvas.makeTransparent()

	for i,p in enumerate(pretty.keys()):
		graphs[i].SetMarkerColor(pretty[p]['color'])
		graphs[i].SetMarkerStyle(pretty[p]['marker'])
		graphs[i].SetMarkerSize(2)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('layPlots/clctLay_'+str(CHAM)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

### MAKE ALL PLOTS
for cham in chamlist:
	# Plots with current on x-axis
	makePlot(\
			[data.currentVector(cham, ff) for ff in pretty.keys()],
			[data.clctVector(cham, ff) for ff in pretty.keys()],
			cham,
			'Mean Current [#muA]',
			'CLCT Layers',
			'curr'
			)
	# Plots with luminosity on x-axis
	makePlot(\
			[data.lumiVector(cham, ff) for ff in pretty.keys()],
			[data.clctVector(cham, ff) for ff in pretty.keys()],
			cham,
			'Luminosity [Hz/cm^{2}]',
			'CLCT Layers',
			'lumi')
	# Plots with 1/A on x-axis
	makePlot(\
			[np.reciprocal(data.attVector()) for ff in pretty.keys()],
			[data.clctVector(cham, ff) for ff in pretty.keys()],
			cham,
			'Source Intensity 1/A',
			'CLCT Layers',
			'att')
