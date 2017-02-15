import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.OldPlotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.roottools as Tools

##### PARAMETERS #####
# Which chambers to do
CHAMLIST = (1, 110)

##### SEMI-PARAMETERS #####
# Filenames
F_MEASGRID = '../datafiles/measgrid'
F_ATTENHUT = '../datafiles/attenhut'
#F_DATAFILE = '../datafiles/data_segSlope'
#F_DATAFILE = 'data_segSlope'
F_DATAFILE = None

# Cosmetic data dictionary, comment out for fewer ones
pretty = {
	0 : { 'name' : 'Original',        'color' : R.kRed-3,   'marker' : R.kFullCircle      },
	#1 : { 'name' : 'TightPreCLCT',    'color' : R.kBlue-1,  'marker' : R.kFullSquare      },
	#2 : { 'name' : 'TightCLCT',       'color' : R.kOrange,  'marker' : R.kFullTriangleUp  },
	#3 : { 'name' : 'TightALCT',       'color' : R.kGreen+2, 'marker' : R.kFullCross       },
	#4 : { 'name' : 'TightPrePID',     'color' : R.kMagenta, 'marker' : R.kFullTriangleDown},
	#5 : { 'name' : 'TightPrePostPID', 'color' : R.kAzure+8, 'marker' : R.kFullDiamond     },
	#6 : { 'name' : 'TightPA',         'color' : R.kGray,    'marker' : R.kFullStar        },
	#7 : { 'name' : 'TightAll',        'color' : R.kBlack,   'marker' : R.kFullCircle      }
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
		self.VALDATA = { 1 : {}, 110: {} }
		self.hists = { 1 : {}, 110 : {} }
		if F_DATAFILE is None:
			for ATT in self.MEASDATA.keys():
				for MEAS in self.MEASDATA[ATT][0:1]:# Original only
					f = R.TFile.Open('/afs/cern.ch/work/a/adasgupt/public/GIF/16Dec/ana_'+str(MEAS)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')
					for CHAM in CHAMLIST:
						self.hists[CHAM][MEAS] = {\
							'mult' : R.TH1F('hMult_'+str(CHAM)+'_'+str(MEAS),'',15,0,15),
							'multScint' : R.TH1F('hMultScint_'+str(CHAM)+'_'+str(MEAS),'',15,0,15),
							'multMatch' : R.TH1F('hMultMatch_'+str(CHAM)+'_'+str(MEAS),'',2,0,2),
						}
					nLCTs11 = 0
					nLCTs21 = 0
					for entry in t:
						E = Primitives.ETree(t,DecList=['SEGMENT','LCT'])
						segs = [Primitives.Segment(E,i) for i in range(len(E.seg_cham))]
						lcts = [Primitives.LCT(E,i) for i in range(len(E.lct_cham))]
						nSegs11 = 0
						nSegs21 = 0
						nSegsScint11 = 0
						nSegsScint21 = 0
						nSegsMatch11 = 0
						nSegsMatch21 = 0
						# Count total segments/event and segments in scint/event
						for seg in segs:
							if seg.cham==1:   nSegs11 += 1
							if seg.cham==110: nSegs21 += 1
							if Aux.inPad(seg.halfStrip[3], seg.wireGroup[3], seg.cham):
								if seg.cham==1:   nSegsScint11 += 1
								if seg.cham==110: nSegsScint21 += 1
						# Count matched segments/event
						for lct in lcts:
							if not Aux.inPad(lct.keyHalfStrip,lct.keyWireGroup,lct.cham): continue
							if lct.cham==1:
								nLCTs11 += 1
							if lct.cham==110: 
								nLCTs21 += 1
							for seg in segs:
								if seg.cham != lct.cham: continue
								if not Aux.matchSegLCT(seg, lct, thresh=(2.,2.)): continue
								if seg.cham==1: nSegsMatch11 += 1
								if seg.cham==110: nSegsMatch21 += 1
								# Just need one segment to match to an LCT for multiplicity plot
								# doesn't matter if it is the "best" one
								break
						# Fill Histograms
						nSegsMatchTot11 = nSegsMatchTot11 + nSegsMatch11
						nSegsMatchTot21 = nSegsMatchTot21 + nSegsMatch21
						self.hists[1  ][MEAS]['mult'].Fill(nSegs11)
						self.hists[1  ][MEAS]['multScint'].Fill(nSegsScint11)
						self.hists[1  ][MEAS]['multMatch'].Fill(nSegsMatch11)
						self.hists[110][MEAS]['mult'].Fill(nSegs21)
						self.hists[110][MEAS]['multScint'].Fill(nSegsScint21)
						self.hists[110][MEAS]['multMatch'].Fill(nSegsMatch21)
					for CHAM in CHAMLIST:
						self.VALDATA[CHAM][MEAS] = {
							'mult_mean' : self.hists[CHAM][MEAS]['mult'].GetMean(),
							'mult_rms'  : self.hists[CHAM][MEAS]['mult'].GetStdDev(),
							'multScint_mean' : self.hists[CHAM][MEAS]['multScint'].GetMean(),
							'multScint_rms'  : self.hists[CHAM][MEAS]['multScint'].GetStdDev(),
							'multMatch_mean' : self.hists[CHAM][MEAS]['multMatch'].GetMean(),
							'multMatch_rms'  : self.hists[CHAM][MEAS]['multMatch'].GetStdDev(),
						}
						den = t.GetEntries()
						#den = 1.
						denMatch = 0.
						if CHAM==1:
							denMatch = nLCTs11
						else:
							denMatch = nLCTs21
						self.savePlot(self.hists[CHAM][MEAS]['mult'], 'N(segments)', 'Counts', 'mult', CHAM, ATT, MEAS, den)
						self.savePlot(self.hists[CHAM][MEAS]['multScint'], 'N(segments)', 'Counts', 'multScint', CHAM, ATT, MEAS, den)
						self.savePlot(self.hists[CHAM][MEAS]['multMatch'], 'N(segments)', 'Counts', 'multMatch', CHAM, ATT, MEAS, denMatch)
					'''
					print '%s %s %s %s %s %s %s %s %s %s %s %s %s'%(\
							MEAS,
							self.VALDATA[1][MEAS]['mult_mean'],
							self.VALDATA[1][MEAS]['mult_rms'],
							self.VALDATA[1][MEAS]['multScint_mean'],
							self.VALDATA[1][MEAS]['multScint_rms'],
							self.VALDATA[1][MEAS]['multMatch_mean'],
							self.VALDATA[1][MEAS]['multMatch_rms'],
							self.VALDATA[110][MEAS]['mult_mean'],
							self.VALDATA[110][MEAS]['mult_rms'],
							self.VALDATA[110][MEAS]['multScint_mean'],
							self.VALDATA[110][MEAS]['multScint_rms'],
							self.VALDATA[110][MEAS]['multMatch_mean'],
							self.VALDATA[110][MEAS]['multMatch_rms']
					)
					'''


		# for obtaining data dictionary from a file
		else:
			f = open(F_DATAFILE)
			for line in f:
				cols = line.strip('\n').split()
				MEAS = int(cols[0])
				self.VALDATA[1][MEAS] = {
					'mult_mean' : float(cols[1]),
					'mult_rms' : float(cols[2]),
					'multScint_mean' : float(cols[3]),
					'multScint_rms' : float(cols[4]),
					'multMatch_mean' : float(cols[5]),
					'multMatch_rms' : float(cols[6]),
				}
				self.VALDATA[110][MEAS] = {
					'mult_mean' : float(cols[7]),
					'mult_rms' : float(cols[8]),
					'multScint_mean' : float(cols[9]),
					'multScint_rms' : float(cols[10]),
					'multMatch_mean' : float(cols[11]),
					'multMatch_rms' : float(cols[12]),
				}

	# get a value given a chamber and measurement number
	def val(self, cham, meas, hist):
		return float(self.VALDATA[cham][meas][hist])

	# get a vector of values
	def valVector(self, cham, ff, hist):
		return np.array([self.val(cham, self.MEASDATA[att][ff], hist) for att in self.attVector()])

	# save per-measurement plots
	def savePlot(self, histTmp, xtitle, ytitle, title, CHAM, ATT, MEAS, den):
		cham = 1 if CHAM==1 else 2

		hist = Tools.DrawOverflow(histTmp)
		plot = Plotter.Plot(hist,option='hist')

		hist.Scale(1./den)

		canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 External Trigger', logy=False, extra='Internal', cWidth=800, cHeight=700)
		canvas.makeLegend()
		canvas.addMainPlot(plot,addToLegend=False)

		R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
		plot.setTitles(X=xtitle, Y=ytitle)
		plot.plot.SetMinimum(0.0)
		plot.plot.SetMaximum(1.05)
		plot.scaleTitles(0.8)
		plot.scaleLabels(0.8)
		plot.scaleTitleOffsets(1.2, 'Y')
		canvas.makeTransparent()

		hist.SetFillColor(R.kBlue+1)
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
		canvas.c.SaveAs('test/'+title+'_ME'+str(cham)+'1_m'+str(MEAS)+'.pdf')
		R.SetOwnership(canvas.c,False)

data = MegaStruct()

##### MAKEPLOT FUNCTION #####
def makePlot(cham, x, y, xtitle, ytitle, title):
	CHAM = 1 if cham == 1 else 2
	graphs = []
	ntypes = len(pretty.keys())
	for i in range(ntypes):
		graphs.append(R.TGraph(len(x[i]), x[i], y[i]))

	# Step 1
	plots = []
	for i, p in enumerate(pretty.keys()):
		plots.append(Plotter.Plot(graphs[i], legName=pretty[p]['name'], legType='p', option='P'))

	# Step 2
	canvas = Plotter.Canvas(lumi='ME'+str(CHAM)+'/1 External Trigger', logy=False, extra='Internal', cWidth=800, cHeight=700)

	# Step 3
	canvas.makeLegend(lWidth=0.2, lHeight=0.25, pos='bl', lOffset=0.04, fontsize=0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i], addToLegend=False)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	canvas.firstPlot.setTitles(X=xtitle, Y=ytitle)
	canvas.firstPlot.plot.SetMinimum(0.0)
	canvas.firstPlot.scaleTitles(0.8)
	canvas.firstPlot.scaleLabels(0.8)
	canvas.firstPlot.scaleTitleOffsets(1.2, 'Y')
	canvas.makeTransparent()

	for i,p in enumerate(pretty.keys()):
		graphs[i].SetMarkerColor(pretty[p]['color'])
		graphs[i].SetMarkerStyle(pretty[p]['marker'])
		graphs[i].SetMarkerSize(2.2)

	#att = [key for key in data.MEASDATA.keys() if int(title) in data.MEASDATA[key]][0]
	#ft = str(list(data.attVector()).index(att))


	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('test/ME'+str(CHAM)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

##### MAKE PLOTS #####
for CHAM in CHAMLIST:
	cham = int(CHAM)
	makePlot(\
			cham,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.valVector (cham, ff,'mult_mean') for ff in pretty.keys()],
		'Luminosity [cm^{-2}s^{-1}]',
		'N(segments) mean',
		'mult_mean'
	)
	makePlot(\
			cham,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.valVector (cham, ff,'mult_rms') for ff in pretty.keys()],
		'Luminosity [cm^{-2}s^{-1}]',
		'N(segments) RMS',
		'mult_rms'
	)
	makePlot(\
			cham,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.valVector (cham, ff,'multScint_mean') for ff in pretty.keys()],
		'Luminosity [cm^{-2}s^{-1}]',
		'N(segments) mean',
		'multScint_mean'
	)
	makePlot(\
			cham,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.valVector (cham, ff,'multScint_rms') for ff in pretty.keys()],
		'Luminosity [cm^{-2}s^{-1}]',
		'N(segments) RMS',
		'multScint_rms'
	)
	makePlot(\
			cham,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.valVector (cham, ff,'multMatch_mean') for ff in pretty.keys()],
		'Luminosity [cm^{-2}s^{-1}]',
		'N(segments) mean',
		'multMatch_mean'
	)
	makePlot(\
			cham,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.valVector (cham, ff,'multMatch_rms') for ff in pretty.keys()],
		'Luminosity [cm^{-2}s^{-1}]',
		'N(segments) RMS',
		'multMatch_rms'
	)
