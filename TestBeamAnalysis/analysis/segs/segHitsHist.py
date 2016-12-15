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
F_DATAFILE = '../datafiles/data_seghitssplit'
#F_DATAFILE = None

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
		self.VALDATA  = {}
		if F_DATAFILE is None:
			for ATT in self.MEASDATA.keys():
				for MEAS in self.MEASDATA[ATT][0:1]: # I only cared about Original for this plot
					f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/5Dec/ana_'+str(MEAS)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')
					# indexed by meas, cham, and nHits; 0 for total (just for fewer lines of code; it's less readable fasho)
					self.VALDATA[MEAS] = {1:{0:0, 3:0, 4:0, 5:0, 6:0}, 110:{0:0, 3:0, 4:0, 5:0, 6:0}}
					for entry in t:
						E = Primitives.ETree(t, DecList=['SEGMENT', 'LCT'])
						segs = [Primitives.Segment(E, i) for i in range(len(E.seg_cham))]
						lcts = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham))]
						for CHAM in CHAMLIST:
							for seg in segs:
								if seg.cham != CHAM: continue
								for lct in lcts:
									if lct.cham != CHAM: continue
									if self.inPad(seg.halfStrip[3], seg.wireGroup[3], CHAM) and self.matchSegLCT(seg, lct):
										self.VALDATA[MEAS][CHAM][0        ] += 1
										self.VALDATA[MEAS][CHAM][seg.nHits] += 1
					print '{:4d} {:5d} {:5d} {:5d} {:5d} {:5d} {:5d} {:5d} {:5d} {:5d} {:5d}'.format(\
						MEAS,
						self.VALDATA[MEAS][1  ][0],
						self.VALDATA[MEAS][1  ][3],
						self.VALDATA[MEAS][1  ][4],
						self.VALDATA[MEAS][1  ][5],
						self.VALDATA[MEAS][1  ][6],
						self.VALDATA[MEAS][110][0],
						self.VALDATA[MEAS][110][3],
						self.VALDATA[MEAS][110][4],
						self.VALDATA[MEAS][110][5],
						self.VALDATA[MEAS][110][6]
					)
		# for obtaining data dictionary from a file
		else:
			f = open(F_DATAFILE)
			for line in f:
				cols = [int(x) for x in line.strip('\n').split()]
				MEAS = cols[0]
				self.VALDATA[MEAS] = {\
					1:{\
						0:cols[1 ],
						3:cols[2 ],
						4:cols[3 ],
						5:cols[4 ],
						6:cols[5 ]
					},
					110:{\
						0:cols[6 ],
						3:cols[7 ],
						4:cols[8 ],
						5:cols[9 ],
						6:cols[10]
					}
				}

	# defines a paddle region
	def inPad(self, hs, wg, CHAM):
		if      hs >= SCINT[CHAM]['HS'][0]\
			and hs <= SCINT[CHAM]['HS'][1]\
			and wg >= SCINT[CHAM]['WG'][0]\
			and wg <= SCINT[CHAM]['WG'][1]:
			return True
		else:
			return False

	# determines if a segment and an lct match each other
	def matchSegLCT(self, seg, lct):
		if abs(seg.halfStrip[3] - lct.keyHalfStrip) <= 2 and abs(seg.wireGroup[3] - lct.keyWireGroup) <= 2:
			return True
		else:
			return False

	# get a value given a chamber and measurement number
	def val(self, cham, meas, nhits):
		return float(self.VALDATA[meas][cham][nhits])

	# get a vector of values
	def valVector(self, cham, nhits):
		return np.array([self.val(cham, self.MEASDATA[att][0], nhits) for att in self.attVector()])

	# get a vector of fractions
	def fracVector(self, cham, nhits):
		return np.array(self.valVector(cham, nhits)/self.valVector(cham, 0)) # remember 0 is "total"

data = MegaStruct()

##### MAKEPLOT FUNCTION #####
def makePlot(cham, x, y, xtitle, ytitle, title):
	graphs = []
	n = 4
	for i in range(n):
		# I'm hacking together my own version of hstack so that I don't have to change a lot of code.
		# To get the fill to mimic the hstack, I need to add (0, 0) and (LUMIMAX, 0) to each graph
		# Don't forget that x is backwards -- right to left -- because it's sorted by attenuation
		X = np.array([x[i][0]] + list(x[i]                          ) + [0.])
		Y = np.array([0.]      + list(np.array(y[0:i+1]).sum(axis=0)) + [0.])
		graphs.append(R.TGraph(len(X), X, Y))

	# Step 1
	plots = []
	for i in range(n):
		plots.append(Plotter.Plot(graphs[i], legName=str(i+3)+' hits', legType='p', option='F'))

	# Step 2
	canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 External Trigger', logy=False, extra='Internal', cWidth=800, cHeight=700)

	# Step 3
	canvas.makeLegend(lWidth=0.2, lHeight=0.25, pos='tl', lOffset=0.04, fontsize=0.03)

	# Step 4
	for i in reversed(range(n)): # add in reverse order so that the fills will look nice
		if i == 3:
			plots[i].option = 'AF'
			canvas.addMainPlot(plots[i], isFirst=True, addToLegend=False)
		else:
			canvas.addMainPlot(plots[i], isFirst=False, addToLegend=False)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	plots[3].setTitles(X=xtitle, Y=ytitle)
	graphs[3].SetMinimum(0.0)
	graphs[3].SetMaximum(1.0)
	graphs[3].GetXaxis().SetRangeUser(0., x[i][0])
	plots[3].scaleTitles(0.8)
	plots[3].scaleLabels(0.8)
	plots[3].scaleTitleOffsets(1.2, 'Y')
	canvas.makeTransparent()

	# set colors
	#colors = [R.kCyan-7, R.kAzure+6, R.kAzure+7, R.kAzure-3]
	#colors = [17, 16, 15, 14]
	colors = list(reversed([R.kRed+2, R.kRed+1, R.kRed-4, R.kRed-7]))
	for i in range(n):
		graphs[i].SetMarkerColor(colors[i])
		graphs[i].SetLineColor  (colors[i])
		graphs[i].SetFillColor  (colors[i])
	
	# write on the plot
	text = R.TLatex()
	text.SetTextAlign(11)
	text.DrawLatexNDC(.7, .2, '#color[0]{3 hits}')
	text.DrawLatexNDC(.7, .4, '#color[0]{4 hits}')
	text.DrawLatexNDC(.7, .6, '#color[0]{5 hits}')
	text.DrawLatexNDC(.7, .8, '#color[0]{6 hits}')

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/SegNHitsFrac_ME'+str(cham)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

##### MAKE PLOTS #####
for cham in CHAMLIST:
	makePlot(\
		cham if cham == 1 else 2,
		[data.lumiVector(cham, 0)     for nhits in [3, 4, 5, 6]],
		[data.fracVector(cham, nhits) for nhits in [3, 4, 5, 6]],
		'Luminosity [Hz/cm^{2}]',
		'Fraction of Muon Segments',
		'all'
	)