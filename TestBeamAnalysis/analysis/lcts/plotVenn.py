import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.Plotter as Plotter

##### PARAMETERS #####
# Which chambers to do
CHAMLIST = (1, 110)
# Configuration dictionary
EFFLIST = (\
	{'num' : 'LCT'        , 'denom' : 'L1A'        , 'ytitle':'LCT Efficiency'             , 'castrated' : False, 'norm' : False},
	{'num' : 'LCTScint'   , 'denom' : 'L1A'        , 'ytitle':'LCT-Scint Efficiency'       , 'castrated' : False, 'norm' : False},
	{'num' : 'LCTSegMatch', 'denom' : 'L1A'        , 'ytitle':'LCT-Seg Match Efficiency'   , 'castrated' : False, 'norm' : False},
	{'num' : 'Seg'        , 'denom' : 'L1A'        , 'ytitle':'Segment Efficiency'         , 'castrated' : False, 'norm' : False},
	{'num' : 'SegScint'   , 'denom' : 'L1A'        , 'ytitle':'Seg-Scint Efficiency'       , 'castrated' : False, 'norm' : False},
	{'num' : 'AllMatch'   , 'denom' : 'L1A'        , 'ytitle':'Muon Efficiency'            , 'castrated' : False, 'norm' : False},
	{'num' : 'AllMatch'   , 'denom' : 'LCTScint'   , 'ytitle':'Muon Match Efficiency'      , 'castrated' : False, 'norm' : False},
	{'num' : 'AllMatch'   , 'denom' : 'LCTSegMatch', 'ytitle':'Muon Match-Scint Efficiency', 'castrated' : False, 'norm' : False},
	{'num' : 'AllMatch'   , 'denom' : 'SegScint'   , 'ytitle':'Muon Seg Match Efficiency'  , 'castrated' : False, 'norm' : False},
	{'num' : 'SegScint'   , 'denom' : 'Seg'        , 'ytitle':'Seg-Scint/Seg Efficiency'   , 'castrated' : False, 'norm' : False},
	{'num' : 'LCTScint'   , 'denom' : 'LCT'        , 'ytitle':'LCT-Scint/LCT Efficiency'   , 'castrated' : False, 'norm' : False}
)

##### SEMI-PARAMETERS #####
# Filenames
F_MEASGRID = '../datafiles/measgrid'
F_ATTENHUT = '../datafiles/attenhut'
F_DATAFILE = '../datafiles/data_efftable'

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
	
	##### THESE THREE ARE MODIFIED FROM THE "DEFAULT" #####
	# get a vector of attenuations
	def attVector(self, CASTRATED=False):
		if CASTRATED:
			return np.array([33., 46., 100., float('inf')])
		else:
			return np.array(sorted(self.MEASDATA.keys()))

	# get a vector of currents
	def currentVector(self, cham, ff, CASTRATED=False):
		return np.array([self.current(cham, self.MEASDATA[att][ff]) for att in self.attVector(CASTRATED)])

	# get a vector of equivalent luminosities
	def lumiVector(self, cham, ff, CASTRATED=False):
		factor = 3.e33 if cham == 1 else 5.e33
		return factor * np.array([self.current(cham, self.MEASDATA[att][ff]) for att in self.attVector(CASTRATED)])
	##### END MEGASTRUCT COMMON: DO NOT EDIT BETWEEN THESE TAGS #####

	# fill data: this function, and the access functions below it, are "user-defined" and script-dependent
	def fillData(self):
		self.VALDATA = { 1 : {}, 110: {} }
		f = open(F_DATAFILE)
		for line in f:
			if 'Att' in line or line == '\n': continue
			cols = line.strip('\n').split()
			CHAM = 1 if cols[2] == 'ME11' else 110
			MEAS = int(cols[1])
			self.VALDATA[CHAM][MEAS] = {\
				'L1A'         : int(cols[3]),
				'LCT'         : int(cols[4]),
				'LCTScint'    : int(cols[5]),
				'LCTSegMatch' : int(cols[6]),
				'AllMatch'    : int(cols[7]),
				'Seg'         : int(cols[8]),
				'SegScint'    : int(cols[9])
			}

	# get a value given a chamber and measurement number
	def val(self, cham, meas, crit):
		return float(self.VALDATA[cham][meas][crit])

	# get a vector of values
	def valVector(self, cham, ff, crit):
		return np.array([self.val(cham, self.MEASDATA[att][ff], crit) for att in self.attVector()])

	# get a vector of efficiencies
	def effVector(self, cham, ff, num, denom, norm=False):
		if denom is None:
			if norm:
				return self.effVector(cham, ff, num)/self.effVector(cham, 0, num)
			else:
				return self.valVector(cham, ff, num)
		else:
			if norm:
				return self.effVector(cham, ff, num, denom)/self.effVector(cham, 0, num, denom)
			else:
				return np.array(self.valVector(cham, ff, num) / self.valVector(cham, ff, denom))

data = MegaStruct()

##### MAKEPLOT FUNCTION #####
def makePlot(cham, x, y, xtitle, ytitle, title):
	graphs = []
	ntypes = len(pretty.keys())
	for i in range(ntypes):
		graphs.append(R.TGraph(len(x[i]), x[i], y[i]))

	plots = []
	for i, p in enumerate(pretty.keys()):
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
	graphs[0].SetMinimum(0.0)
	graphs[0].SetMaximum(1.1)
	plots[0].scaleTitles(0.8)
	plots[0].scaleLabels(0.8)
	graphs[0].GetYaxis().SetTitleOffset(graphs[0].GetYaxis().GetTitleOffset() * 1.2)
	canvas.makeTransparent()

	for i,p in enumerate(pretty.keys()):
		graphs[i].SetMarkerColor(pretty[p]['color'])
		graphs[i].SetMarkerStyle(pretty[p]['marker'])
		graphs[i].SetMarkerSize(2.2)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/Eff_'+str(cham)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

##### MAKE PLOTS #####
for cham in CHAMLIST:
	for quant in EFFLIST:
		makePlot(\
			cham if cham == 1 else 2,
			[data.lumiVector(cham, ff, quant['castrated']                         ) for ff in pretty.keys()],
			[data.effVector (cham, ff, quant['num'], quant['denom'], quant['norm']) for ff in pretty.keys()],
			'Luminosity [Hz/cm^{2}]',
			quant['ytitle'],
			quant['num'] \
				+ ('' if quant['denom'] is None else '_'+quant['denom']) \
				+ ('' if not quant['norm']      else '_norm'           ) \
				+ ('' if not quant['castrated'] else '_cast'           )
		)
