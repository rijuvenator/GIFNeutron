import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.OldPlotter as Plotter
from Gif.Analysis.MegaStruct import F_GIFDATA

CHAMLIST = [1, 110]

F_MEASGRID = '../datafiles/measgrid'
F_ATTENHUT = '../datafiles/attenhut'
#F_DATAFILE = '../datafiles/data_cfebeff'
F_DATAFILE = None

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
	def attVector(self):
		return np.array(sorted(self.MEASDATA.keys()))

	# get a vector of currents
	def currentVector(self, cham, ff):
		return np.array([self.current(cham, self.MEASDATA[att][ff]) for att in self.attVector()])

	# get a vector of equivalent luminosities
	def lumiVector(self, cham, ff):
		factor = 3.e33 if cham == 1 else 5.e33
		return factor * np.array([self.current(cham, self.MEASDATA[att][ff]) for att in self.attVector()])
	##### END MEGASTRUCT COMMON: DO NOT EDIT BETWEEN THESE TAGS #####

	# fill data: this function, and the access functions below it, are "user-defined" and script-dependent
	def fillData(self):
		self.VALDATA = { 1 : {}, 110: {} }
		if F_DATAFILE is None:
			for ATT in self.MEASDATA.keys():
				for MEAS in self.MEASDATA[ATT]:
					# Get file and tree
					f = R.TFile.Open(F_GIFDATA.replace('XXXX',str(MEAS)))
					t = f.Get('GIFTree/GIFDigiTree')

					# keep track for entire measurement
					nLCT  = {1:0, 110:0}
					nRead = {1:0, 110:0}
					for j,entry in enumerate(t):
						# Get the event, make the ETree, and make lists of primitives objects
						E = Primitives.ETree(t, DecList=['STRIP', 'LCT'])
						strips = [Primitives.Strip  (E, i) for i in range(len(E.strip_cham))]
						lcts =   [Primitives.LCT    (E, i) for i in range(len(E.lct_cham  ))]

						for CHAM in CHAMLIST:
							# Make Active CFEB list
							ActiveCFEBs = [False] * (7 if CHAM == 1 else 5)
							for strip in strips:
								if strip.cham != CHAM: continue
								ActiveCFEBs[int(strip.number - 1) / 16] = True

							# Determine if LCT's CFEB was read out
							for lct in lcts:
								if lct.cham != CHAM: continue
								nLCT[CHAM] += 1
								if ActiveCFEBs[lct.keyHalfStrip / 32]:
									nRead[CHAM] += 1
								else:
									pass
									#print MEAS, CHAM if CHAM == 1 else 2, j

					self.VALDATA[1  ][MEAS] = float(nRead[1  ])/nLCT[1  ]
					self.VALDATA[110][MEAS] = float(nRead[110])/nLCT[110]

					print '{:4d} {:5d} {:5d} {:.4f} {:5d} {:5d} {:.4f}'.format(\
						MEAS,
						nLCT[1],
						nRead[1],
						float(nRead[1])/nLCT[1],
						nLCT[110],
						nRead[110],
						float(nRead[110])/nLCT[110]
					)
		else:
			# this file is the output of the printout above
			f = open(F_DATAFILE)
			for line in f:
				cols = line.strip('\n').split()
				MEAS = int(cols[0])
				nLCT  = {1:int(cols[1]), 110:int(cols[4])}
				nRead = {1:int(cols[2]), 110:int(cols[5])}
				self.VALDATA[1  ][MEAS] = float(nRead[1  ])/nLCT[1  ]
				self.VALDATA[110][MEAS] = float(nRead[110])/nLCT[110]

	# get a value given a chamber and measurement number
	def val(self, cham, meas):
		return self.VALDATA[cham][meas]

	# get a vector of values
	def valVector(self, cham, ff):
		return np.array([self.val(cham, self.MEASDATA[att][ff]) for att in self.attVector()])

data = MegaStruct()

def makePlot(cham, x, y, xtitle, ytitle, title):
	graphs = []
	ntypes = len(pretty.keys())
	for i in range(ntypes):
		graphs.append(R.TGraph(len(x[i]), x[i], y[i]))

	plots = []
	for i, p in enumerate(pretty.keys()):
		plots.append(Plotter.Plot(graphs[i], pretty[p]['name'], 'p', 'P'))

	# Step 2
	canvas = Plotter.Canvas('ME'+str(cham)+'/1 External Trigger', False, 0., 'Internal', 800, 700)

	# Step 3
	canvas.makeLegend(.2,0.25,'bl',0.04, 0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i], True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	canvas.firstPlot.plot.GetYaxis().SetTitle(ytitle)
	canvas.firstPlot.plot.GetXaxis().SetTitle(xtitle)
	canvas.firstPlot.plot.SetMinimum(0.9)
	canvas.firstPlot.plot.SetMaximum(1.)
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
	canvas.c.SaveAs('pdfs/CFEBEff_'+str(cham)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

for cham in CHAMLIST:
	makePlot(\
		cham if cham == 1 else 2,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.valVector (cham, ff) for ff in pretty.keys()],
		'Luminosity [cm^{-2}s^{-1}]',
		'CFEB Read-Out Efficiency',
		'all'
	)
