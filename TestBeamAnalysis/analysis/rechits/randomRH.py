import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.OldPlotter as Plotter
import Gif.TestBeamAnalysis.Auxiliary as Aux

##### PARAMETERS #####
# Which chambers to do
CHAMLIST = (1, 110)

##### SEMI-PARAMETERS #####
# Filenames
F_MEASGRID = '../datafiles/measgrid'
F_ATTENHUT = '../datafiles/attenhut'
F_DATAFILE = '../datafiles/data_randrh.root'
#F_DATAFILE = None
#F_OUT = R.TFile('../datafiles/data_randrh.root', 'RECREATE')

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
		self.VALDATA = { 1 : {}, 110 : {} }
		self.HISTS   = { 1 : {}, 110 : {} }
		CBINS = 4000
		CMIN = 0.
		CMAX = 224.
		if F_DATAFILE is None:
			for ATT in self.MEASDATA.keys():
				for MEAS in self.MEASDATA[ATT][0:1]:
					for CHAM in CHAMLIST:
						self.HISTS[CHAM][MEAS] = R.TH1F('h'+str(CHAM)+str(MEAS), '', CBINS, CMIN, CMAX)
					f = R.TFile.Open('../../trees/ana_'+str(MEAS)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')
					for entry in t:
						E = Primitives.ETree(t, DecList=['RECHIT', 'SEGMENT'])
						rechits = [Primitives.RecHit (E, i) for i in range(len(E.rh_cham))]
						segs    = [Primitives.Segment(E, i) for i in range(len(E.seg_cham))]

						for CHAM in CHAMLIST:
							rhlist = []
							for seg in segs:
								if seg.nHits == 3: continue
								rhlist.extend(seg.rhID)
							for i, rh in enumerate(rechits):
								if rh.cham != CHAM: continue
								if i in rhlist: continue
								if not Aux.inPad(rh.halfStrip, rh.wireGroup, CHAM):
									self.HISTS[CHAM][MEAS].Fill(rh.halfStrip)
							#RAND = 40. if CHAM == 1 else 22.
							#aclosest = float('inf')
							#for rh in rechits:
							#	if rh.cham != CHAM: continue
							#	if abs(rh.halfStrip/2 - RAND) < aclosest:
							#		aclosest = abs(rh.halfStrip/2 - RAND)
							#		self.HISTS[CHAM][MEAS].Fill(rh.halfStrip/2 - RAND)
					f.Close()
					for CHAM in CHAMLIST:
						self.VALDATA[CHAM][MEAS] = self.HISTS[CHAM][MEAS].GetStdDev()
						F_OUT.cd()
						self.HISTS[CHAM][MEAS].Write()
					print MEAS

		# for obtaining data dictionary from a file
		else:
			MIN = 0.
			MAX = 224.
			#BINS = int((MAX-MIN)/((CMAX-CMIN)/CBINS))/16
			BINS = CBINS
			f = R.TFile.Open(F_DATAFILE)
			for ATT in self.MEASDATA.keys():
				for MEAS in self.MEASDATA[ATT][0:1]:
					for CHAM in CHAMLIST:
						h = f.Get('h'+str(CHAM)+str(MEAS))
						self.HISTS[CHAM][MEAS] = h.Rebin(BINS, 'hN'+str(CHAM)+str(MEAS), np.array([MIN + i*(MAX-MIN)/float(BINS) for i in range(BINS+1)]))
						self.HISTS[CHAM][MEAS].SetDirectory(0)
						self.VALDATA[CHAM][MEAS] = h.GetStdDev()

	# get a value given a chamber and measurement number
	def val(self, cham, meas):
		return float(self.VALDATA[cham][meas])

	# get a vector of values
	def valVector(self, cham, ff):
		return np.array([self.val(cham, self.MEASDATA[att][ff]) for att in self.attVector()])

data = MegaStruct()

##### MAKEPLOT FUNCTIONS #####
def makeDistPlot(cham, hist, xtitle, ytitle, title):

	hist.Scale(1./hist.GetEntries())

	h = hist

	# Step 1
	plot = Plotter.Plot(h, legName='', legType='l', option='hist')

	# Step 2
	canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 External Trigger', logy=True, extra='Internal', cWidth=800, cHeight=700)

	# Step 3
	canvas.makeLegend(lWidth=0.2, lHeight=0.125, pos='tl', lOffset=0.04, fontsize=0.03)

	# Step 4
	canvas.addMainPlot(plot, addToLegend=False)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	canvas.firstPlot.setTitles(X=xtitle, Y=ytitle)
	#canvas.firstPlot.plot.SetMinimum(0.0)
	#canvas.firstPlot.plot.SetMaximum(1.1)
	canvas.firstPlot.scaleTitles(0.8)
	canvas.firstPlot.scaleLabels(0.8)
	canvas.firstPlot.scaleTitleOffsets(1.2, 'Y')
	canvas.makeTransparent()

	plot.plot.SetLineColor(R.kRed)

	att = [key for key in data.MEASDATA.keys() if int(title) in data.MEASDATA[key]][0]
	canvas.drawText(text='{:.1f}'.format(att)                                              , pos=(.75, .80))
	canvas.drawText(text='#color[2]{#mu:'    + '{:.4f}'.format(plot.plot.GetMean())   + '}', pos=(.75, .75))
	canvas.drawText(text='#color[2]{#sigma:' + '{:.4f}'.format(plot.plot.GetStdDev()) + '}', pos=(.75, .70))

	lines = []
	for i in range(5):
		lines.append(R.TLine(32.*i, 0., 32.*i, 1.))
		lines[-1].SetLineColor(R.kBlue)
		lines[-1].Draw()
	CHAM = (cham==2)*110 + (cham==1)*1
	scints = []
	for i in range(2):
		scints.append(R.TLine(Aux.SCINT[CHAM]['HS'][i], 0., Aux.SCINT[CHAM]['HS'][i], 1.))
		scints[-1].SetLineColor(R.kMagenta)
		scints[-1].Draw()

	ft = str(list(data.attVector()).index(att))

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/RRH_ME'+str(cham)+'1_'+ft+'.pdf')
	R.SetOwnership(canvas.c, False)

def makeSDPlot(cham, x, y, xtitle, ytitle, title):

	g = R.TGraph(len(x), x, y)

	# Step 1
	plot = Plotter.Plot(g, legName='', legType='p', option='P')

	# Step 2
	canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 External Trigger', logy=False, extra='Internal', cWidth=800, cHeight=700)

	# Step 3
	canvas.makeLegend(lWidth=0.2, lHeight=0.125, pos='tl', lOffset=0.04, fontsize=0.03)

	# Step 4
	canvas.addMainPlot(plot, addToLegend=False)

	# Step 5

	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	canvas.firstPlot.setTitles(X=xtitle, Y=ytitle)
	canvas.firstPlot.plot.SetMinimum(0.0)
	canvas.firstPlot.plot.SetMaximum(10.0)
	canvas.firstPlot.scaleTitles(0.8)
	canvas.firstPlot.scaleLabels(0.8)
	canvas.firstPlot.scaleTitleOffsets(1.2, 'Y')
	canvas.makeTransparent()

	plot.plot.SetMarkerColor(R.kRed)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/RRH_ME'+str(cham)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

##### MAKE PLOTS #####
for cham in CHAMLIST:
	for meas in data.HISTS[cham].keys():
		makeDistPlot(\
			cham if cham == 1 else 2,
			data.HISTS[cham][meas],
			'Half Strip',
			'Counts',
			str(meas)
		)

#	makeSDPlot(\
#		cham if cham == 1 else 2,
#		data.lumiVector(cham, 0),
#		data.valVector(cham, 0),
#		'Luminosity [Hz/cm^{2}]',
#		'Standard Deviation [cm]',
#		'stddev'
#	)
