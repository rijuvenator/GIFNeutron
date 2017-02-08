''' Purpose of this script is to measure the Comp resolution.
Resolution = RMS(comparator pos - segment pos)
Bias       = Mean(comparator pos - segment pos)
Plus plots for each measurement of the distribution
'''

import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.OldPlotter as Plotter
import Gif.Analysis.Auxiliary as Aux

##### PARAMETERS #####
# Which chambers to do
CHAMLIST = (1, 110)

##### SEMI-PARAMETERS #####
# Filenames
F_MEASGRID = '../datafiles/measgrid'
F_ATTENHUT = '../datafiles/attenhut'
F_DATAFILE = '../datafiles/data_compSegRes'
#F_DATAFILE = None

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
		self.resolution = { 1 : {}, 110: {} }
		self.mean = { 1 : {}, 110 : {} }
		self.hists = { 1 : {}, 110 : {} }
		if F_DATAFILE is None:
			for ATT in self.MEASDATA.keys():
				for MEAS in self.MEASDATA[ATT]:
					f = R.TFile.Open('/afs/cern.ch/work/a/adasgupt/public/GIF/16Dec/ana_'+str(MEAS)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')
					for cham in CHAMLIST:
						self.mean[cham][MEAS] = 0
						self.resolution[cham][MEAS] = 0
						self.hists[cham][MEAS] = {
							'res' : R.TH1F('hRes_'+str(cham)+'_'+str(MEAS),'', 200, -5, 5)
						}
					DecList = ['STRIP','WIRE','COMP','LCT','CLCT','SEGMENT']
					for entry in t:
						E = Primitives.ETree(t,DecList)
						strips = [Primitives.Strip(E,i)   for i in range(len(E.strip_cham))]
						wires  = [Primitives.Wire(E,i)    for i in range(len(E.wire_cham))]
						comps  = [Primitives.Comp(E,i)    for i in range(len(E.comp_cham))]
						lcts   = [Primitives.LCT(E,i)     for i in range(len(E.lct_cham))]
						segs   = [Primitives.Segment(E,i) for i in range(len(E.seg_cham))]
						for cham in CHAMLIST:
							# Require the presence of Wire Groups, Strips, Segments, and LCTs
							if cham not in [lct.cham for lct in lcts]: continue
							if cham not in [wire.cham for wire in wires]: continue
							if cham not in [strip.cham for strip in strips]: continue
							if cham not in [seg.cham for seg in segs]: continue
							# Find matched LCT and segment inside scintillator acceptance
							for lct in lcts:
								if lct.cham is not cham: continue
								if not Aux.inPad(lct.keyHalfStrip,lct.keyWireGroup,lct.cham): continue
								found, seg = Aux.bestSeg(lct, segs)
								if not found: continue
								# Loop on comparators and find the nearest comparator to the segment position in each layer
								minCompSegDist = {1:999., 2:999., 3:999., 4:999., 5:999., 6:999.}
								for lay in range(1,7):
									minDist = 999.
									for comp in comps:
										if comp.cham is not cham: continue
										if comp.layer is not lay: continue
										# -2 offset because comparator hs starts counting from 1
										# Divide by 2 to convert to strip units
										CompSegDist = (comp.staggeredHalfStrip-seg.staggeredHalfStrip[lay]-2)/2.
										if abs(CompSegDist) < minDist:
											minDist = abs(CompSegDist)
											minCompSegDist[lay] = CompSegDist
									#print lay, minCompSegDist[lay]
									# Fill histograms per segment
									if minCompSegDist[lay]<999.:
										if cham==1:
											self.hists[1][MEAS]['res'].Fill(float(minCompSegDist[lay]))
										else:
											self.hists[110][MEAS]['res'].Fill(float(minCompSegDist[lay]))
					# Save per chamber, measurement plots
					# Fill per measurement dictionaries
					for CHAM in CHAMLIST:
						self.mean[CHAM][MEAS]       = self.hists[CHAM][MEAS]['res'].GetMean()
						self.resolution[CHAM][MEAS] = self.hists[CHAM][MEAS]['res'].GetStdDev()
						self.savePlot(self.hists[CHAM][MEAS]['res'],CHAM,MEAS,ATT)

					print MEAS,
					print self.mean[1][MEAS], self.resolution[1][MEAS],
					print self.mean[110][MEAS], self.resolution[110][MEAS]

		# for obtaining data dictionary from a file
		else:
			f = open(F_DATAFILE)
			for line in f:
				cols = line.strip('\n').split()
				MEAS = int(cols[0])
				self.mean[1][MEAS] = cols[1]
				self.resolution[1][MEAS] = cols[2]
				self.mean[110][MEAS] = cols[3]
				self.resolution[110][MEAS] = cols[4]

	# get a value given a chamber and measurement number
	def meanValue(self, cham, meas):
		return float(self.mean[cham][meas])

	# get a vector of values
	def meanValueVector(self, cham, ff):
		return np.array([self.meanValue(cham, self.MEASDATA[att][ff]) for att in self.attVector()])
	
	# get a value given a chamber and measurement number
	def res(self, cham, meas):
		return float(self.resolution[cham][meas])

	# get a vector of values
	def resVector(self, cham, ff):
		return np.array([self.res(cham, self.MEASDATA[att][ff]) for att in self.attVector()])

	# Plot Saver function
	def savePlot(self,hist,cham,MEAS,ATT):
		CHAM = 1 if cham==1 else 2
		plot = Plotter.Plot(hist,option='hist')

		canvas = Plotter.Canvas(lumi='ME'+str(CHAM)+'/1 External Trigger', logy=False, extra='Internal', cWidth=800, cHeight=700)
		canvas.makeLegend()
		canvas.addMainPlot(plot,addToLegend=False)

		plot.setTitles('Comparator position - Segment position [strip]','Counts')
		plot.scaleTitles(0.8)
		plot.scaleLabels(0.8)
		plot.scaleTitleOffsets(1.2, 'Y')

		canvas.makeTransparent()
		hist.SetFillColor(R.kBlue+1)
		hist.SetLineColor(R.kBlue+1)

		text = R.TLatex()
		text.SetTextAlign(11)
		text.SetTextFont(42)
		text.SetTextSize(0.04)
		if ATT!=float('inf'):
			text.DrawLatexNDC(.75, .80, '{:.1f}'.format(ATT))
		else:
			text.DrawLatexNDC(.75, .80, 'No Source')
		text.DrawLatexNDC(.75, .75, '#color[1]{#mu:'    + '{:.4f}'.format(hist.GetMean())   + '}')
		text.DrawLatexNDC(.75, .70, '#color[1]{#sigma:' + '{:.4f}'.format(hist.GetStdDev()) + '}')

		canvas.finishCanvas()
		canvas.save('segRes/compSegRes_ME'+str(CHAM)+'1_m'+str(MEAS)+'.pdf')
		R.SetOwnership(canvas.c, False)

data = MegaStruct()

##### MAKEPLOT FUNCTION #####
def makePlot(cham, x, y, xtitle, ytitle, title, name):
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
	if name=='Res':
		canvas.makeLegend(lWidth=0.2, lHeight=0.25, pos='br', lOffset=0.04, fontsize=0.03)
	else:
		canvas.makeLegend(lWidth=0.2, lHeight=0.25, pos='bl', lOffset=0.04, fontsize=0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i], addToLegend=True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	plots[0].setTitles(X=xtitle, Y=ytitle)
	if name=='Res':
		graphs[0].SetMinimum(0.0)
		graphs[0].SetMaximum(2.0)
	else:
		graphs[0].SetMinimum(-1.0)
		graphs[0].SetMaximum(1.0)
	plots[0].scaleTitles(0.8)
	plots[0].scaleLabels(0.8)
	plots[0].scaleTitleOffsets(1.2, 'Y')
	canvas.makeTransparent()

	for i,p in enumerate(pretty.keys()):
		graphs[i].SetMarkerColor(pretty[p]['color'])
		graphs[i].SetMarkerStyle(pretty[p]['marker'])
		graphs[i].SetMarkerSize(2.2)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('segRes/compSeg'+name+'_ME'+str(cham)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

##### MAKE PLOTS #####
for cham in CHAMLIST:
	makePlot(\
		cham if cham == 1 else 2,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.resVector (cham, ff) for ff in pretty.keys()],
		'Luminosity [Hz/cm^{2}]',
		'Comparator-Segment Resolution',
		'lumi',
		'Res'
	)
	makePlot(\
		cham if cham == 1 else 2,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.meanValueVector (cham, ff) for ff in pretty.keys()],
		'Luminosity [Hz/cm^{2}]',
		'Comparator-Segment Mean',
		'lumi',
		'Mean'
	)
