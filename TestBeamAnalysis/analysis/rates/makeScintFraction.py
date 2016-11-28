import numpy as np
import Gif.TestBeamAnalysis.Plotter as Plotter
import ROOT as R
import sys

R.gROOT.SetBatch(True)

### PARAMETERS
chamlist = [1]
f_measgrid = 'measgrid'
f_attenhut = 'attenhut'

title2 = 'cast'
pretty = {
		0 : { 'name' : 'Original',        'color' : R.kRed-3    , 'marker' : R.kFullCircle      },
		1 : { 'name' : 'TightPreCLCT',    'color' : R.kBlue-1   , 'marker' : R.kFullCircle      },
		2 : { 'name' : 'TightCLCT',       'color' : R.kOrange   , 'marker' : R.kFullCircle      },
		3 : { 'name' : 'TightALCT',       'color' : R.kGreen+2  , 'marker' : R.kFullCircle      },
		4 : { 'name' : 'TightPrePID',     'color' : R.kMagenta  , 'marker' : R.kFullCircle      },
		5 : { 'name' : 'TightPrePostPID', 'color' : R.kAzure+8  , 'marker' : R.kFullCircle      },
		6 : { 'name' : 'TightPA',         'color' : R.kGray     , 'marker' : R.kFullCircle      },
		7 : { 'name' : 'TightAll',        'color' : R.kBlack    , 'marker' : R.kFullCircle      }
}

### DATA STRUCTURE CLASS
class MegaStruct():
	def __init__(self,measgrid,attenhut):
		f = open(measgrid)
		self.FFFMeas = {}
		for line in f:
			cols = line.strip('\n').split()
			self.FFFMeas[float(cols[0])] = [int(j) for j in cols[1:]]
		f.close()

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

		f = open('meh')
		self.Effs = { 1 : {}, 2 : {} }
		for line in f:
			cols = line.strip('\n').split()
			meas = int(cols[0])
			self.Effs[1][meas] = float(cols[-2])
			self.Effs[2][meas] = float(cols[-1])

	def current(self, cham, meas):
		if cham == 1:
			return sum(self.Currs[cham][meas])/6.0
		elif cham == 2:
			return sum(self.Currs[cham][meas][6:12])/6.0
	
	def eff(self, cham, meas):
		return self.Effs[cham][meas]

	def attVector(self):
		return np.array(sorted(self.FFFMeas.keys()))

	def currentVector(self, cham, ff):
		return np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	def lumiVector(self, cham, ff):
		factor = 5.e33 if cham == 2 else 3.e33
		return factor * np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	def effVector(self, cham, ff):
		return np.array([self.eff    (cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	def normEffVector(self, cham, ff):
		return np.array([self.eff    (cham, self.FFFMeas[att][ff])/self.eff(cham, self.FFFMeas[att][0]) for att in self.attVector()])

data = MegaStruct(f_measgrid, f_attenhut)

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
	canvas = Plotter.Canvas('ME'+str(cham)+'/1', False, 0., 'Internal', 800, 700)

	# Step 3
	canvas.makeLegend(.2,0.25,'bl',0.04, 0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i], i==0 , True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	graphs[0].GetYaxis().SetTitle(ytitle)
	graphs[0].GetYaxis().SetTitleOffset(graphs[0].GetYaxis().GetTitleOffset() * 1.4)
	graphs[0].GetXaxis().SetTitle(xtitle)
	graphs[0].SetMinimum(0.88)
	graphs[0].SetMaximum(0.97)
	plots[0].scaleTitles(0.7)
	plots[0].scaleLabels(0.7)

	for i,p in enumerate(pretty.keys()):
		graphs[i].SetMarkerColor(pretty[p]['color'])
		graphs[i].SetMarkerStyle(pretty[p]['marker'])
		graphs[i].SetMarkerSize(1.5)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

makePlot(\
		[data.lumiVector(1, ff) for ff in pretty.keys()],
		[data.effVector(1, ff) for ff in pretty.keys()],
		1,
		'Luminosity [Hz/cm^{2}]',
		'Fraction of Events in Scintillator',
		'paddle_1'
	)
makePlot(\
		[data.lumiVector(2, ff) for ff in pretty.keys()],
		[data.effVector(2, ff) for ff in pretty.keys()],
		2,
		'Luminosity [Hz/cm^{2}]',
		'Fraction of Events in Scintillator',
		'paddle_2'
	)
