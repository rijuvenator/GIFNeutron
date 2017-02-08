import numpy as np
import ROOT as R
import Gif.NeutronSim.Primitives as Primitives
import Gif.NeutronSim.OldPlotter as Plotter
import Gif.NeutronSim.Auxiliary as Aux

##### PARAMETERS #####
# Which chambers to do
CHAMLIST = (1, 110)

##### SEMI-PARAMETERS #####
# Filenames
F_MEASGRID = '../datafiles/measgrid'
F_ATTENHUT = '../datafiles/attenhut'
F_DATAFILE = '../datafiles/data_segchisq'
#F_DATAFILE = None

## Cosmetic data dictionary, comment out for fewer ones
#pretty = {
#	0 : { 'name' : 'Original',        'color' : R.kRed-3,   'marker' : R.kFullCircle      },
#	1 : { 'name' : 'TightPreCLCT',    'color' : R.kBlue-1,  'marker' : R.kFullSquare      },
#	2 : { 'name' : 'TightCLCT',       'color' : R.kOrange,  'marker' : R.kFullTriangleUp  },
#	3 : { 'name' : 'TightALCT',       'color' : R.kGreen+2, 'marker' : R.kFullCross       },
#	4 : { 'name' : 'TightPrePID',     'color' : R.kMagenta, 'marker' : R.kFullTriangleDown},
#	5 : { 'name' : 'TightPrePostPID', 'color' : R.kAzure+8, 'marker' : R.kFullDiamond     },
#	6 : { 'name' : 'TightPA',         'color' : R.kGray,    'marker' : R.kFullStar        },
#	7 : { 'name' : 'TightAll',        'color' : R.kBlack,   'marker' : R.kFullCircle      }
#}
# Scintillator definition
SCINT = {1:{'HS':(25,72),'WG':(37,43)},110:{'HS':(8,38),'WG':(55,65)}}

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
		self.VALDATA = { 1 : {}, 110: {} }
		if F_DATAFILE is None:
			for ATT in self.MEASDATA.keys():
				for MEAS in self.MEASDATA[ATT][0:1]: # only interested in Original
					f = R.TFile.Open('../../trees/ana_'+str(MEAS)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')

					BINS = 1000
					CHIMIN = 0
					CHIMAX = 10
					h = {1: {}, 110: {}}
					for CHAM in CHAMLIST:
						for DOF in [0, 2, 4, 6, 8]:
							h[CHAM][DOF] = R.TH1F('h'+str(CHAM)+str(DOF), '', BINS, CHIMIN, CHIMAX)
					for entry in t:
						E = Primitives.ETree(t, DecList=['SEGMENT', 'LCT'])
						segs = [Primitives.Segment(E, i) for i in range(len(E.seg_cham))]
						lcts = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham))]
						for CHAM in CHAMLIST:
							for seg in segs:
								if seg.cham != CHAM: continue
								for lct in lcts:
									if lct.cham != CHAM: continue
									if Aux.inPad(seg.halfStrip[3], seg.wireGroup[3], CHAM) and Aux.matchSegLCT(seg, lct):
										h[CHAM][seg.dof].Fill(seg.chisq/seg.dof)
										h[CHAM][   0   ].Fill(seg.chisq/seg.dof)
					for CHAM in CHAMLIST:
						self.VALDATA[CHAM][MEAS] = {}
						for DOF in [0, 2, 4, 6, 8]:
							self.VALDATA[CHAM][MEAS][DOF] = {\
								'MEAN' : h[CHAM][DOF].GetMean(),
								'STDD' : h[CHAM][DOF].GetStdDev()
							}
						print '{:4d} {:1d} {:7.4f} {:7.4f} {:7.4f} {:7.4f} {:7.4f} {:7.4f} {:7.4f} {:7.4f} {:7.4f} {:7.4f}'.format(\
							MEAS,
							CHAM if CHAM == 1 else 2,
							self.VALDATA[CHAM][MEAS][0]['MEAN'],
							self.VALDATA[CHAM][MEAS][0]['STDD'],
							self.VALDATA[CHAM][MEAS][2]['MEAN'],
							self.VALDATA[CHAM][MEAS][2]['STDD'],
							self.VALDATA[CHAM][MEAS][4]['MEAN'],
							self.VALDATA[CHAM][MEAS][4]['STDD'],
							self.VALDATA[CHAM][MEAS][6]['MEAN'],
							self.VALDATA[CHAM][MEAS][6]['STDD'],
							self.VALDATA[CHAM][MEAS][8]['MEAN'],
							self.VALDATA[CHAM][MEAS][8]['STDD']
						)
					del h

		# for obtaining data dictionary from a file
		else:
			f = open(F_DATAFILE)
			for line in f:
				cols = line.strip('\n').split()
				MEAS = int(cols[0])
				CHAM = 1 if cols[1] == '1' else 110
				self.VALDATA[CHAM][MEAS] = {}
				for DOF in [0, 2, 4, 6, 8]:
					self.VALDATA[CHAM][MEAS][DOF] = {\
						'MEAN' : float(cols[DOF+2]),
						'STDD' : float(cols[DOF+3])
					}

	# get a value given a chamber and measurement number
	def val(self, cham, meas, dof, stat):
		return float(self.VALDATA[cham][meas][dof][stat])

	# get a vector of values
	def valVector(self, cham, ff, dof, stat):
		return np.array([self.val(cham, self.MEASDATA[att][ff], dof, stat) for att in self.attVector()])

data = MegaStruct()

##### MAKEPLOT FUNCTION #####
def makePlot(cham, x, y, xtitle, ytitle, title):
	graphs = []
	ngraphs = 5
	for i in range(ngraphs):
		graphs.append(R.TGraph(len(x[i]), x[i], y[i]))

	# Step 1
	plots = []
	for i in range(ngraphs):
		if i == 0:
			DOF = 'All DOF'
		else:
			DOF = str(2 * i) + ' DOF'
		plots.append(Plotter.Plot(graphs[i], legName=DOF, legType='p', option='P'))

	# Step 2
	canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 External Trigger', logy=False, extra='Internal', cWidth=800, cHeight=700)

	# Step 3
	canvas.makeLegend(lWidth=0.2, lHeight=0.25, pos='br', lOffset=0.04, fontsize=0.03)

	# Step 4
	for i in range(ngraphs):
		#if i == 1: continue
		canvas.addMainPlot(plots[i], addToLegend=True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	canvas.firstPlot.setTitles(X=xtitle, Y=ytitle)
	canvas.firstPlot.plot.SetMinimum(0.0)
	canvas.firstPlot.plot.SetMaximum(4.0)
	canvas.firstPlot.scaleTitles(0.8)
	canvas.firstPlot.scaleLabels(0.8)
	canvas.firstPlot.scaleTitleOffsets(1.2, 'Y')
	canvas.makeTransparent()

	colors = [R.kBlack, R.kRed+1, R.kOrange+1, R.kGreen+2, R.kBlue-3]
	for i in range(ngraphs):
		graphs[i].SetMarkerColor(colors[i])

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/SeqChiSqLumi_ME'+str(cham)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

##### MAKE PLOTS #####
for cham in CHAMLIST:
	makePlot(\
		cham if cham == 1 else 2,
		[data.lumiVector(cham, 0             ) for dof in [0, 2, 4, 6, 8]],
		[data.valVector (cham, 0, dof, 'MEAN') for dof in [0, 2, 4, 6, 8]],
		'Luminosity [Hz/cm^{2}]',
		'Mean of #chi^{2} Distribution',
		'mean'
	)
	makePlot(\
		cham if cham == 1 else 2,
		[data.lumiVector(cham, 0             ) for dof in [0, 2, 4, 6, 8]],
		[data.valVector (cham, 0, dof, 'STDD') for dof in [0, 2, 4, 6, 8]],
		'Luminosity [Hz/cm^{2}]',
		'Standard Deviation of #chi^{2} Distribution',
		'stddev'
	)
