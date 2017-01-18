import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.Plotter as Plotter

##### PARAMETERS #####
# Which chambers to do
CHAMLIST = (1, 110)

##### SEMI-PARAMETERS #####
# Filenames
F_MEASGRID = '../datafiles/measgrid'
F_ATTENHUT = '../datafiles/attenhut'
F_EFF      = '../datafiles/compEff'
F_RES      = '../datafiles/compRes'

# Cosmetic data dictionary, comment out for fewer ones
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
		# fill a data dictionary as desired
		self.EFFDATA = { 1 : {}, 110: {} }
		self.RESDATA = { 1 : {}, 110: {} }

		f = open(F_EFF)
		for line in f:
			cols = line.strip('\n').split()
			MEAS = int(cols[0])
			self.EFFDATA[1  ][MEAS] = float(cols[1])
			self.EFFDATA[110][MEAS] = float(cols[4])
		f.close()
		f = open(F_RES)
		for line in f:
			cols = line.strip('\n').split()
			MEAS = int(cols[0])
			self.RESDATA[1  ][MEAS] = float(cols[2])
			self.RESDATA[110][MEAS] = float(cols[4])

	# get a value given a chamber and measurement number
	def eff(self, cham, meas):
		return float(self.EFFDATA[cham][meas])

	# get a vector of values
	def effVector(self, cham, ff):
		return np.array([self.eff(cham, self.MEASDATA[att][ff]) for att in self.attVector()])

	# get a value given a chamber and measurement number
	def res(self, cham, meas):
		return float(self.RESDATA[cham][meas])

	# get a vector of values
	def resVector(self, cham, ff):
		return np.array([self.res(cham, self.MEASDATA[att][ff]) for att in self.attVector()])

data = MegaStruct()

##### MAKEPLOT FUNCTION #####
def makePlot(cham, x, y, xtitle, ytitle, title):
	graphs = []
	ntypes = len(pretty.keys())
	for i in range(ntypes):
		graphs.append(R.TGraph(len(x[i]), x[i], y[i]))

	# Step 1
	plots = []
	for i, p in enumerate(pretty.keys()):
		plots.append(Plotter.Plot(graphs[i], legName=pretty[p]['name'], legType='p', option='P'))

	# Step 2
	canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 External Trigger', logy=False, extra='Internal', cWidth=800, cHeight=700)

	# Step 3
	canvas.makeLegend(lWidth=0.2, lHeight=0.25, pos='bl', lOffset=0.04, fontsize=0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i], addToLegend=True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	canvas.firstPlot.setTitles(X=xtitle, Y=ytitle)
	canvas.firstPlot.plot.SetMinimum(0.0)
	canvas.firstPlot.plot.SetMaximum(1.1)
	canvas.firstPlot.scaleTitles(0.8)
	canvas.firstPlot.scaleLabels(0.8)
	canvas.firstPlot.scaleTitleOffsets(1.2, 'Y')
	canvas.makeTransparent()

	for i,p in enumerate(pretty.keys()):
		graphs[i].SetMarkerColor(pretty[p]['color'])
		graphs[i].SetMarkerStyle(pretty[p]['marker'])
		graphs[i].SetMarkerSize(2.2)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/EffRes_ME'+str(cham)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

##### MAKE PLOTS #####
for cham in CHAMLIST:
	makePlot(\
		cham if cham == 1 else 2,
		[data.resVector(cham, ff) for ff in pretty.keys()],
		[data.effVector(cham, ff) for ff in pretty.keys()],
		'Comparator Resolution',
		'Comparator Efficiency',
		'all'
	)
