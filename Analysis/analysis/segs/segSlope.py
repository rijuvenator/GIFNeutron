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
							'dXdZ' : R.TH1F('hdXdZ_'+str(CHAM)+'_'+str(MEAS),'',100,-1,1),
							'dYdZ' : R.TH1F('hdYdZ_'+str(CHAM)+'_'+str(MEAS),'',100,-1,1),
							'dXdY' : R.TH2F('hdXdY_'+str(CHAM)+'_'+str(MEAS),'',100,-1,1,100,-1,1),
							'time' : R.TH1F('time_'+str(CHAM)+'_'+str(MEAS),'',100,-200,200)
						}
					for entry in t:
						E = Primitives.ETree(t,DecList=['SEGMENT','LCT','RECHIT'])
						lcts = [Primitives.LCT(E,i) for i in range(len(E.lct_cham))]
						segs = [Primitives.Segment(E,i) for i in range(len(E.seg_cham))]
						rhs  = [Primitives.RecHit(E,i) for i in range(len(E.rh_cham))]
						for CHAM in CHAMLIST:
							# Match by finding the closest segment to the LCT that has the highest number of rechits used
							for lct in lcts:
								if lct.cham != CHAM: continue
								if not Aux.inPad(lct.keyHalfStrip,lct.keyWireGroup,CHAM): continue
								mostHits = 0
								found = False
								for s,seg in enumerate(segs):
									if seg.cham != CHAM: continue
									if not Aux.matchSegLCT(seg, lct, thresh=(2,2)): continue
									found = True
									if seg.nHits > mostHits:
										mostHits = seg.nHits
										matchedSegs = [s]
									elif seg.nHits == mostHits:
										matchedSegs.append(s)
								closest = 999
								if found:
									for mseg in matchedSegs:
										#print mseg, segs[mseg].nHits, abs(lct.keyHalfStrip-segs[mseg].halfStrip[3]) 
										if abs(lct.keyHalfStrip-segs[mseg].halfStrip[3]) < closest:
											closest = abs(lct.keyHalfStrip-segs[mseg].halfStrip[3])
											thisSeg = mseg
									#print 'this',thisSeg, segs[thisSeg].nHits, abs(lct.keyHalfStrip-segs[thisSeg].halfStrip[3])
									# thisSeg is the closest segment with the highest number of hits
									self.hists[CHAM][MEAS]['dXdZ'].Fill(segs[thisSeg].slope['x'])
									self.hists[CHAM][MEAS]['dYdZ'].Fill(segs[thisSeg].slope['y'])
									self.hists[CHAM][MEAS]['dXdY'].Fill(segs[thisSeg].slope['x'],segs[thisSeg].slope['y'])
									time = np.array([rhs[rhid].stripTime for rhid in segs[thisSeg].rhID]).mean()
									#time = sum([rhs[rhid].stripTime for rhid in segs[thisSeg].rhID])/len(segs[thisSeg].rhID)
									self.hists[CHAM][MEAS]['time'].Fill(time)
					for CHAM in CHAMLIST:
						self.VALDATA[CHAM][MEAS] = {
							'dXdZ_mean' : self.hists[CHAM][MEAS]['dXdZ'].GetMean(),
							'dXdZ_stddev' : self.hists[CHAM][MEAS]['dXdZ'].GetStdDev(),
							'dYdZ_mean' : self.hists[CHAM][MEAS]['dYdZ'].GetMean(),
							'dYdZ_stddev' : self.hists[CHAM][MEAS]['dYdZ'].GetStdDev(),
							'time_mean' : self.hists[CHAM][MEAS]['time'].GetMean(),
							'time_stddev' : self.hists[CHAM][MEAS]['time'].GetStdDev()
						}
						self.savePlot(self.hists[CHAM][MEAS]['dXdZ'], 'dX/dZ', 'N(segments)', 'dXdZ', CHAM, ATT, MEAS)
						self.savePlot(self.hists[CHAM][MEAS]['dYdZ'], 'dY/dZ', 'N(segments)', 'dYdZ', CHAM, ATT, MEAS)
						self.savePlot(self.hists[CHAM][MEAS]['time'], 'time [ns]',     'N(segments)', 'time', CHAM, ATT, MEAS)
						self.savePlot(self.hists[CHAM][MEAS]['dXdY'], 'dX/dZ', 'dY/dZ', 'dXdY', CHAM, ATT, MEAS, is1d=False)
					print '%s %s %s %s %s %s %s %s %s %s %s %s %s'%(\
							MEAS,
							self.VALDATA[1][MEAS]['dXdZ_mean'],
							self.VALDATA[1][MEAS]['dXdZ_stddev'],
							self.VALDATA[1][MEAS]['dYdZ_mean'],
							self.VALDATA[1][MEAS]['dYdZ_stddev'],
							self.VALDATA[1][MEAS]['time_mean'],
							self.VALDATA[1][MEAS]['time_stddev'],
							self.VALDATA[110][MEAS]['dXdZ_mean'],
							self.VALDATA[110][MEAS]['dXdZ_stddev'],
							self.VALDATA[110][MEAS]['dYdZ_mean'],
							self.VALDATA[110][MEAS]['dYdZ_stddev'],
							self.VALDATA[110][MEAS]['time_mean'],
							self.VALDATA[110][MEAS]['time_stddev']
					)


		# for obtaining data dictionary from a file
		else:
			f = open(F_DATAFILE)
			for line in f:
				cols = line.strip('\n').split()
				MEAS = int(cols[0])
				self.VALDATA[1][MEAS] = {
					'dXdZ_mean' : float(cols[1]),
					'dXdZ_stddev' : float(cols[2]),
					'dYdZ_mean' : float(cols[3]),
					'dYdZ_stddev' : float(cols[4]),
					'time_mean' : float(cols[5]),
					'time_stddev' : float(cols[6])
				}
				self.VALDATA[110][MEAS] = {
					'dXdZ_mean' : float(cols[7]),
					'dXdZ_stddev' : float(cols[8]),
					'dYdZ_mean' : float(cols[9]),
					'dYdZ_stddev' : float(cols[10]),
					'time_mean' : float(cols[11]),
					'time_stddev' : float(cols[12])
				}

	# get a value given a chamber and measurement number
	def val(self, cham, meas, hist):
		return float(self.VALDATA[cham][meas][hist])

	# get a vector of values
	def valVector(self, cham, ff, hist):
		return np.array([self.val(cham, self.MEASDATA[att][ff], hist) for att in self.attVector()])

	# save per-measurement plots
	def savePlot(self, hist, xtitle, ytitle, title, CHAM, ATT, MEAS, is1d=True):
		cham = 1 if CHAM==1 else 2
		if is1d:
			plot = Plotter.Plot(hist,option='hist')
		else:
			plot = Plotter.Plot(hist,option='COLZ')
		canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 External Trigger', logy=False, extra='Internal', cWidth=800, cHeight=700)
		canvas.makeLegend()
		canvas.addMainPlot(plot,addToLegend=False)

		R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
		plot.setTitles(X=xtitle, Y=ytitle)
		#plot.plot.SetMinimum(0.0)
		#plot.plot.SetMaximum(3.5)
		plot.scaleTitles(0.8)
		plot.scaleLabels(0.8)
		plot.scaleTitleOffsets(1.2, 'Y')
		canvas.makeTransparent()

		if is1d:
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
		else:
			R.gStyle.SetPalette(55)
		
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
	if 'stddev' in title:
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
		[data.valVector (cham, ff,'dXdZ_mean') for ff in pretty.keys()],
		'Luminosity [Hz/cm^{2}]',
		'dX/dZ mean',
		'dXdZ_mean'
	)
	makePlot(\
			cham,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.valVector (cham, ff,'dXdZ_stddev') for ff in pretty.keys()],
		'Luminosity [Hz/cm^{2}]',
		'dX/dZ RMS',
		'dXdZ_stddev'
	)
	makePlot(\
			cham,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.valVector (cham, ff,'dYdZ_mean') for ff in pretty.keys()],
		'Luminosity [Hz/cm^{2}]',
		'dY/dZ mean',
		'dYdZ_mean'
	)
	makePlot(\
			cham,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.valVector (cham, ff,'dYdZ_stddev') for ff in pretty.keys()],
		'Luminosity [Hz/cm^{2}]',
		'dY/dZ RMS',
		'dYdZ_stddev'
	)
	makePlot(\
			cham,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.valVector (cham, ff,'time_mean') for ff in pretty.keys()],
		'Luminosity [Hz/cm^{2}]',
		'mean time [ns]',
		'time_mean'
	)
	makePlot(\
			cham,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.valVector (cham, ff,'time_stddev') for ff in pretty.keys()],
		'Luminosity [Hz/cm^{2}]',
		'RMS time [ns]',
		'time_stddev'
	)
