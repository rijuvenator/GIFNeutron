import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.OldPlotter as Plotter
import Gif.Analysis.Auxiliary as Aux
from Gif.Analysis.MegaStruct import F_GIFDATA

##### PARAMETERS #####
# Which chambers to do
CHAMLIST = (1, 110)

##### SEMI-PARAMETERS #####
# Filenames
F_MEASGRID = '../datafiles/measgrid'
F_ATTENHUT = '../datafiles/attenhut'
#F_DATAFILE = None
F_DATAFILE = '../datafiles/data_segrh.root'
#F_OUT = R.TFile('../datafiles/data_segrh.root', 'RECREATE')

# Cosmetic data dictionary, comment out for fewer ones
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
		self.VALDATA = { 1 : {}, 110 : {} }
		self.HISTS   = { 1 : {}, 110 : {} }
		CBINS = 4000
		CMIN = 0.
		CMAX = 10.
		if F_DATAFILE is None:
			#for ATT in [22.]:
			for ATT in self.MEASDATA.keys():
				for MEAS in self.MEASDATA[ATT][0:1]: # only interested in Original for now
					for CHAM in CHAMLIST:
						self.HISTS[CHAM][MEAS] = {\
							'ML'  : R.TH1F('hML'+str(CHAM)+str(MEAS), '', CBINS, CMIN, CMAX),                   # "missing layer"
							'IS'  : R.TH1F('hIS'+str(CHAM)+str(MEAS), '', CBINS, CMIN, CMAX),                   # "in segment"
							'2M'  : R.TH2F('h2M'+str(CHAM)+str(MEAS), '', CBINS, CMIN, CMAX, 400, -200., 200.), # "2D Missing"
							'2S'  : R.TH2F('h2S'+str(CHAM)+str(MEAS), '', CBINS, CMIN, CMAX, 400, -200., 200.), # "2D Segment"
							'SM'  : R.TH2F('hSM'+str(CHAM)+str(MEAS), '', 4000, -10., 10., 4000, -10., 10.),    # "Scatter Missing"
							'SS'  : R.TH2F('hSS'+str(CHAM)+str(MEAS), '', 4000, -10., 10., 4000, -10., 10.),    # "Scatter Segment"
							'TM'  : R.TH1F('hTM'+str(CHAM)+str(MEAS), '', 400, -200., 200.),                    # "Time Missing"
							'TS'  : R.TH1F('hTS'+str(CHAM)+str(MEAS), '', 400, -200., 200.),                    # "Time Segment"
						}
					f = R.TFile.Open(F_GIFDATA.replace('XXXX',str(MEAS)))
					t = f.Get('GIFTree/GIFDigiTree')
					for IDX, entry in enumerate(t):
						E = Primitives.ETree(t, DecList=['SEGMENT', 'LCT', 'RECHIT'])
						segs    = [Primitives.Segment(E, i) for i in xrange(len(E.seg_cham))]
						lcts    = [Primitives.LCT    (E, i) for i in xrange(len(E.lct_cham))]
						rechits = [Primitives.RecHit (E, i) for i in xrange(len(E.rh_cham ))]

						def inTime(time, CHAM):
							if CHAM == 1:
								if      time <=  25. \
									and time >= -55.:
									return True
								else:
									return False
							if CHAM == 110:
								if      time <= -30. \
									and time >= -125.:
									return True
								else:
									return False

						for CHAM in CHAMLIST:
							for lct in lcts:
								if lct.cham != CHAM: continue
								if not Aux.inPad(lct.keyHalfStrip,lct.keyWireGroup,CHAM): continue
								found, seg = Aux.bestSeg(lct, segs)
								if not found: continue
								for i in seg.rhID:
									DX = (rechits[i].pos['x'] - seg.pos[rechits[i].layer]['x'])
									DY = (rechits[i].pos['y'] - seg.pos[rechits[i].layer]['y'])
									D  = (DX**2. + DY**2.)**0.5
									self.HISTS[CHAM][MEAS]['IS'].Fill(D)
									self.HISTS[CHAM][MEAS]['SS'].Fill(DX, DY)
									self.HISTS[CHAM][MEAS]['2S'].Fill(D, rechits[i].stripTime)
									self.HISTS[CHAM][MEAS]['TS'].Fill(rechits[i].stripTime)
								layers = [rechits[i].layer for i in seg.rhID]
								for layer in [1, 2, 3, 4, 5, 6]:
									if layer in layers: continue
									closestRHPosDiff = float('inf')
									fillValD         = float('inf')
									fillValDX        = float('inf')
									fillValDY        = float('inf')
									fillTime         = float('inf')
									for rh in rechits:
										if rh.layer == layer:
											DX = (rh.pos['x']-seg.pos[layer]['x'])
											DY = (rh.pos['y']-seg.pos[layer]['y'])
											D  = (DX**2. + DY**2.)**0.5
											if D < closestRHPosDiff:
												closestRHPosDiff = D
												fillValD         = D
												fillValDX        = DX
												fillValDY        = DY
												fillTime         = rh.stripTime
									#if inTime(time, CHAM):
									if True:
										self.HISTS[CHAM][MEAS]['ML'].Fill(fillValD)
										self.HISTS[CHAM][MEAS]['SM'].Fill(fillValDX, fillValDY)
										self.HISTS[CHAM][MEAS]['TM'].Fill(fillTime)
									self.HISTS[CHAM][MEAS]['2M'].Fill(fillValD, fillTime)
					f.Close()
					for CHAM in CHAMLIST:
						self.VALDATA[CHAM][MEAS] = {\
							'ML_SD': self.HISTS[CHAM][MEAS]['ML'].GetStdDev(),
							'IS_SD': self.HISTS[CHAM][MEAS]['IS'].GetStdDev(),
							'ML_MU': self.HISTS[CHAM][MEAS]['ML'].GetMean(),
							'IS_MU': self.HISTS[CHAM][MEAS]['IS'].GetMean()
						}
						F_OUT.cd()
						self.HISTS[CHAM][MEAS]['ML'].Write()
						self.HISTS[CHAM][MEAS]['IS'].Write()
						self.HISTS[CHAM][MEAS]['2M'].Write()
						self.HISTS[CHAM][MEAS]['2S'].Write()
						self.HISTS[CHAM][MEAS]['SM'].Write()
						self.HISTS[CHAM][MEAS]['SS'].Write()
						self.HISTS[CHAM][MEAS]['TM'].Write()
						self.HISTS[CHAM][MEAS]['TS'].Write()
					print MEAS, 'Done'

		# for obtaining data dictionary from a file
		else:
			MIN = 0.
			MAX = 5.
			#BINS = int((MAX-MIN)/((CMAX-CMIN)/CBINS))/32
			BINS = 50
			f = R.TFile.Open(F_DATAFILE)
			#for ATT in [22.]:
			for ATT in self.MEASDATA.keys():
				for MEAS in self.MEASDATA[ATT][0:1]: # only interested in Original for now
					for CHAM in CHAMLIST:
						hML = f.Get('hML'+str(CHAM)+str(MEAS))
						hIS = f.Get('hIS'+str(CHAM)+str(MEAS))
						h2M = f.Get('h2M'+str(CHAM)+str(MEAS))
						h2S = f.Get('h2S'+str(CHAM)+str(MEAS))
						hSM = f.Get('hSM'+str(CHAM)+str(MEAS))
						hSS = f.Get('hSS'+str(CHAM)+str(MEAS))
						hTM = f.Get('hTM'+str(CHAM)+str(MEAS))
						hTS = f.Get('hTS'+str(CHAM)+str(MEAS))
						self.HISTS[CHAM][MEAS] = {\
							'ML' : hML.Rebin(BINS, 'hNML'+str(CHAM)+str(MEAS), np.array([MIN + i*(MAX-MIN)/float(BINS) for i in range(BINS+1)])),
							'IS' : hIS.Rebin(BINS, 'hNIS'+str(CHAM)+str(MEAS), np.array([MIN + i*(MAX-MIN)/float(BINS) for i in range(BINS+1)])),
							'2M' : h2M.Rebin2D(BINS, 5, 'hN2M'+str(CHAM)+str(MEAS)),
							'2S' : h2S.Rebin2D(BINS, 5, 'hN2S'+str(CHAM)+str(MEAS)),
							'SM' : hSM.Rebin2D(50, 50, 'hNSM'+str(CHAM)+str(MEAS)),
							'SS' : hSS.Rebin2D(50, 50, 'hNSS'+str(CHAM)+str(MEAS)),
							'TM' : hTM.Rebin(50, 'hNTM'+str(CHAM)+str(MEAS), np.array([-200 + i*400/float(50) for i in range(50+1)])),
							'TS' : hTS.Rebin(50, 'hNTS'+str(CHAM)+str(MEAS), np.array([-200 + i*400/float(50) for i in range(50+1)])),
						}
						self.HISTS[CHAM][MEAS]['ML'].SetDirectory(0)
						self.HISTS[CHAM][MEAS]['IS'].SetDirectory(0)
						self.HISTS[CHAM][MEAS]['2M'].SetDirectory(0)
						self.HISTS[CHAM][MEAS]['2S'].SetDirectory(0)
						self.HISTS[CHAM][MEAS]['SM'].SetDirectory(0)
						self.HISTS[CHAM][MEAS]['SS'].SetDirectory(0)
						self.HISTS[CHAM][MEAS]['TM'].SetDirectory(0)
						self.HISTS[CHAM][MEAS]['TS'].SetDirectory(0)
						self.VALDATA[CHAM][MEAS] = {\
							'ML_SD' : hML.GetStdDev(),
							'IS_SD' : hIS.GetStdDev(),
							'ML_MU' : hML.GetMean(),
							'IS_MU' : hIS.GetMean()
						}

	# get a value given a chamber and measurement number
	def val(self, cham, meas, which):
		return float(self.VALDATA[cham][meas][which])

	# get a vector of values
	def valVector(self, cham, ff, which):
		return np.array([self.val(cham, self.MEASDATA[att][ff], which) for att in self.attVector()])

data = MegaStruct()

##### MAKEPLOT FUNCTIONS #####
def makeDistPlot(cham, hists, xtitle, ytitle, title):

	#hists['ML'].Scale(1./hists['ML'].GetEntries())
	#hists['IS'].Scale(1./hists['IS'].GetEntries())

	hML = hists['ML']
	hIS = hists['IS']

	# Step 1
	plots = {}
	plots['ML'] = Plotter.Plot(hML, legName='Missing Layer', legType='l', option='hist')
	plots['IS'] = Plotter.Plot(hIS, legName='In Segment'   , legType='l', option='hist')

	# Step 2
	canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 External Trigger', logy=False, extra='Internal', cWidth=800, cHeight=700)

	# Step 3
	canvas.makeLegend(lWidth=0.2, lHeight=0.125, pos='tl', lOffset=0.04, fontsize=0.03)

	# Step 4
	canvas.addMainPlot(plots['IS'])
	canvas.addMainPlot(plots['ML'])

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	canvas.firstPlot.setTitles(X=xtitle, Y=ytitle)
	#canvas.firstPlot.plot.SetMinimum(0.0)
	#canvas.firstPlot.plot.SetMaximum(1.1)
	canvas.firstPlot.scaleTitles(0.8)
	canvas.firstPlot.scaleLabels(0.8)
	R.TGaxis.SetMaxDigits(3)
	canvas.firstPlot.scaleTitleOffsets(1.2, 'Y')
	canvas.makeTransparent()

	plots['ML'].plot.SetLineColor(R.kRed)
	plots['IS'].plot.SetLineColor(R.kBlue)

	att = [key for key in data.MEASDATA.keys() if int(title) in data.MEASDATA[key]][0]
	canvas.drawText(text='A = {:.1f}'.format(att) if att < float('inf') else 'A = off'            , pos=(.70, .80))
	canvas.drawText(text='#color[2]{#mu:'    + '{:.4f}'.format(plots['ML'].plot.GetMean())   + '}', pos=(.70, .75))
	canvas.drawText(text='#color[2]{#sigma:' + '{:.4f}'.format(plots['ML'].plot.GetStdDev()) + '}', pos=(.70, .70))
	canvas.drawText(text='#color[4]{#mu:'    + '{:.4f}'.format(plots['IS'].plot.GetMean())   + '}', pos=(.70, .65))
	canvas.drawText(text='#color[4]{#sigma:' + '{:.4f}'.format(plots['IS'].plot.GetStdDev()) + '}', pos=(.70, .60))

	ft = str(list(data.attVector()).index(att))

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/CRHX_ME'+str(cham)+'1_'+ft+'.pdf')
	R.SetOwnership(canvas.c, False)

def makeTimePlot(cham, hists, xtitle, ytitle, title):

	hTM = hists['TM']
	hTS = hists['TS']

	# Step 1
	plots = {}
	plots['TM'] = Plotter.Plot(hTM, legName='Missing Layer', legType='l', option='hist')
	plots['TS'] = Plotter.Plot(hTS, legName='In Segment'   , legType='l', option='hist')

	# Step 2
	canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 External Trigger', logy=False, extra='Internal', cWidth=800, cHeight=700)

	# Step 3
	canvas.makeLegend(lWidth=0.2, lHeight=0.125, pos='tl', lOffset=0.04, fontsize=0.03)

	# Step 4
	canvas.addMainPlot(plots['TS'])
	canvas.addMainPlot(plots['TM'])

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	canvas.firstPlot.setTitles(X=xtitle, Y=ytitle)
	#canvas.firstPlot.plot.SetMinimum(0.0)
	#canvas.firstPlot.plot.SetMaximum(1.1)
	canvas.firstPlot.scaleTitles(0.8)
	canvas.firstPlot.scaleLabels(0.8)
	R.TGaxis.SetMaxDigits(3)
	canvas.firstPlot.scaleTitleOffsets(1.2, 'Y')
	canvas.makeTransparent()

	plots['TM'].plot.SetLineColor(R.kRed)
	plots['TS'].plot.SetLineColor(R.kBlue)

	att = [key for key in data.MEASDATA.keys() if int(title) in data.MEASDATA[key]][0]
	canvas.drawText(text='A = {:.1f}'.format(att) if att < float('inf') else 'A = off'            , pos=(.70, .80))
	canvas.drawText(text='#color[2]{#mu:'    + '{:.4f}'.format(plots['TM'].plot.GetMean())   + '}', pos=(.70, .75))
	canvas.drawText(text='#color[2]{#sigma:' + '{:.4f}'.format(plots['TM'].plot.GetStdDev()) + '}', pos=(.70, .70))
	canvas.drawText(text='#color[4]{#mu:'    + '{:.4f}'.format(plots['TS'].plot.GetMean())   + '}', pos=(.70, .65))
	canvas.drawText(text='#color[4]{#sigma:' + '{:.4f}'.format(plots['TS'].plot.GetStdDev()) + '}', pos=(.70, .60))

	ft = str(list(data.attVector()).index(att))

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/CRHTime_ME'+str(cham)+'1_'+ft+'.pdf')
	R.SetOwnership(canvas.c, False)

def makeLumiPlot(cham, x, y, xtitle, ytitle, title):

	gML = R.TGraph(len(x[0]), x[0], y[0])
	gIS = R.TGraph(len(x[1]), x[1], y[1])

	# Step 1
	plots = {}
	plots['ML'] = Plotter.Plot(gML, legName='Missing Layer', legType='p', option='P')
	plots['IS'] = Plotter.Plot(gIS, legName='In Segment'   , legType='p', option='P')

	# Step 2
	canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 External Trigger', logy=False, extra='Internal', cWidth=800, cHeight=700)

	# Step 3
	canvas.makeLegend(lWidth=0.2, lHeight=0.125, pos='tl', lOffset=0.04, fontsize=0.03)

	# Step 4
	canvas.addMainPlot(plots['ML'], addToLegend=True)
	canvas.addMainPlot(plots['IS'], addToLegend=True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	canvas.firstPlot.setTitles(X=xtitle, Y=ytitle)
	canvas.firstPlot.plot.SetMinimum(0.0)
	canvas.firstPlot.plot.SetMaximum(3.5)
	canvas.firstPlot.scaleTitles(0.8)
	canvas.firstPlot.scaleLabels(0.8)
	canvas.firstPlot.scaleTitleOffsets(1.2, 'Y')
	canvas.makeTransparent()

	plots['ML'].plot.SetMarkerColor(R.kRed)
	plots['IS'].plot.SetMarkerColor(R.kBlue)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/CRHX_ME'+str(cham)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

def make2DPlot(cham, hists, xtitle, ytitle, meas, suffix):

	h2M = hists[0] # hists['2M']
	h2S = hists[1] # hists['2S']

	# Step 1
	plots = {}
	plots['2M'] = Plotter.Plot(h2M, legName='Missing Layer', legType='l', option='hist')
	plots['2S'] = Plotter.Plot(h2S, legName='In Segment'   , legType='l', option='hist')

	# Step 2
	canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 External Trigger', logy=False, extra='Internal', cWidth=1600, cHeight=1400)

	# Step 3
	canvas.makeLegend(lWidth=0.2, lHeight=0.125, pos='br', lOffset=0.04, fontsize=0.03)

	# Step 4
	canvas.addMainPlot(plots['2S'], addToLegend=False)
	canvas.addMainPlot(plots['2M'], addToLegend=False)

	# Step 5
	R.gStyle.SetPalette(55)

	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	canvas.firstPlot.setTitles(X=xtitle, Y=ytitle)
	#canvas.firstPlot.plot.SetMinimum(0.0)
	#canvas.firstPlot.plot.SetMaximum(1.1)
	canvas.firstPlot.scaleTitles(0.8, axes='XYZ')
	canvas.firstPlot.scaleLabels(0.8, axes='XYZ')
	canvas.firstPlot.scaleTitleOffsets(1.2, 'Y')
	canvas.firstPlot.plot.SetMarkerSize(1)
	canvas.makeTransparent()

	plots['2M'].plot.SetMarkerColor(R.kRed)
	plots['2S'].plot.SetMarkerColor(R.kBlue)
	plots['2M'].plot.SetLineColor(R.kRed)
	plots['2S'].plot.SetLineColor(R.kBlue)

	att = [key for key in data.MEASDATA.keys() if int(meas) in data.MEASDATA[key]][0]
	canvas.drawText(text='A = {:.1f}'.format(att) if att < float('inf') else 'A = off', pos=(.70, .80))

	ft = str(list(data.attVector()).index(att))

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/CRHX2D_ME'+str(cham)+'1_'+ft+suffix+'.png')
	R.SetOwnership(canvas.c, False)

##### MAKE PLOTS #####
for cham in CHAMLIST:
	for meas in data.HISTS[cham].keys():
		makeDistPlot(\
			cham if cham == 1 else 2,
			data.HISTS[cham][meas],
			'Distance [cm]',
			'Counts',
			str(meas),
		)
		makeTimePlot(\
			cham if cham == 1 else 2,
			data.HISTS[cham][meas],
			'Time [ns]',
			'Counts',
			str(meas),
		)
		make2DPlot(\
			cham if cham == 1 else 2,
			[data.HISTS[cham][meas]['2M'], data.HISTS[cham][meas]['2S']],
			'Distance [cm]',
			'Time Peak [ns]',
			str(meas),
			''
		)
		make2DPlot(\
			cham if cham == 1 else 2,
			[data.HISTS[cham][meas]['SM'], data.HISTS[cham][meas]['SS']],
			'x Distance [cm]',
			'y Distance [cm]',
			str(meas),
			'_SCAT'
		)

	makeLumiPlot(\
		cham if cham == 1 else 2,
		[data.lumiVector(cham, 0) for which in ['ML_SD', 'IS_SD']],
		[data.valVector(cham, 0, which) for which in ['ML_SD', 'IS_SD']],
		'Luminosity [Hz/cm^{2}]',
		'Standard Deviation [cm]',
		'stddev'
	)

	makeLumiPlot(\
		cham if cham == 1 else 2,
		[data.lumiVector(cham, 0) for which in ['ML_MU', 'IS_MU']],
		[data.valVector(cham, 0, which) for which in ['ML_MU', 'IS_MU']],
		'Luminosity [Hz/cm^{2}]',
		'Mean [cm]',
		'mean'
	)
