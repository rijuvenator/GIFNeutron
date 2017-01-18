import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.Plotter as Plotter

CHAMLIST = [1, 110]

F_MEASGRID = '../datafiles/measgrid'
F_ATTENHUT = '../datafiles/attenhut'
F_DATAFILE = '../datafiles/data_segprim'
#F_DATAFILE = None

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
					f = R.TFile.Open('../../trees/ana_'+str(MEAS)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')

					# keep track for entire measurement
					nL1A   = {1:t.GetEntries(), 110:t.GetEntries()}
					nWire  = {1:0, 110:0}
					nStrip = {1:0, 110:0}
					for j,entry in enumerate(t):
						# Get the event, make the ETree, and make lists of primitives objects
						E = Primitives.ETree(t, DecList=['STRIP', 'WIRE'])
						#strips = [Primitives.Strip  (E, i) for i in range(len(E.strip_cham))]
						#wires  = [Primitives.Wire   (E, i) for i in range(len(E.wire_cham ))]

						for CHAM in CHAMLIST:
							if CHAM in E.strip_cham: nStrip[CHAM] += 1
							if CHAM in E.wire_cham : nWire [CHAM] += 1

					self.VALDATA[1  ][MEAS] = {'strip' : float(nStrip[1  ])/nL1A[1  ] , 'wire' : float(nWire[1  ])/nL1A[1  ]}
					self.VALDATA[110][MEAS] = {'strip' : float(nStrip[110])/nL1A[110] , 'wire' : float(nWire[110])/nL1A[110]}

					print '{:4d} {:5d} {:5d} {:5d} {:.4f} {:.4f} {:5d} {:5d} {:5d} {:.4f} {:.4f}'.format(\
						MEAS,
						nL1A  [1  ],
						nStrip[1  ],
						nWire [1  ],
						float(nStrip[1  ])/nL1A[1  ],
						float(nWire [1  ])/nL1A[1  ],
						nL1A  [110],
						nStrip[110],
						nWire [110],
						float(nStrip[110])/nL1A[110],
						float(nWire [110])/nL1A[110]
					)
		else:
			# this file is the output of the printout above
			f = open(F_DATAFILE)
			for line in f:
				cols = line.strip('\n').split()
				MEAS = int(cols[0])
				nL1A   = { 1 : int(cols[1]), 110 : int(cols[6])}
				nStrip = { 1 : int(cols[2]), 110 : int(cols[7])}
				nWire  = { 1 : int(cols[3]), 110 : int(cols[8])}
				self.VALDATA[1  ][MEAS] = {'strip' : float(nStrip[1  ])/nL1A[1  ] , 'wire' : float(nWire[1  ])/nL1A[1  ]}
				self.VALDATA[110][MEAS] = {'strip' : float(nStrip[110])/nL1A[110] , 'wire' : float(nWire[110])/nL1A[110]}

	# get a value given a chamber and measurement number
	def val(self, cham, meas, which):
		return self.VALDATA[cham][meas][which]

	# get a vector of values
	def valVector(self, cham, ff, which):
		return np.array([self.val(cham, self.MEASDATA[att][ff], which) for att in self.attVector()])

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
	canvas.firstPlot.plot.SetMinimum(0.0)
	canvas.firstPlot.plot.SetMaximum(1.05)
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
	canvas.c.SaveAs('pdfs/PrimEff_'+str(cham)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

for cham in CHAMLIST:
	makePlot(\
		cham if cham == 1 else 2,
		[data.lumiVector(cham, ff         ) for ff in pretty.keys()],
		[data.valVector (cham, ff, 'strip') for ff in pretty.keys()],
		'Luminosity [Hz/cm^{2}]',
		'Strip Read-Out Efficiency',
		'strip'
	)
	makePlot(\
		cham if cham == 1 else 2,
		[data.lumiVector(cham, ff        ) for ff in pretty.keys()],
		[data.valVector (cham, ff, 'wire') for ff in pretty.keys()],
		'Luminosity [Hz/cm^{2}]',
		'Wire Read-Out Efficiency',
		'wire'
	)
