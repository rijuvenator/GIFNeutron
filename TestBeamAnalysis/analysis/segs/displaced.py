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
# Scintillator definition
SCINT = {1:{'HS':(25,72),'WG':(37,43)},110:{'HS':(8,38),'WG':(55,65)}}

##### BEGIN CODE #####
R.gROOT.SetBatch(True)

##### HELPER FUNCTIONS #####
# defines a paddle region
def inPad(hs, wg, CHAM):
	if      hs >= SCINT[CHAM]['HS'][0]\
		and hs <= SCINT[CHAM]['HS'][1]\
		and wg >= SCINT[CHAM]['WG'][0]\
		and wg <= SCINT[CHAM]['WG'][1]:
		return True
	else:
		return False

# determines if a segment and an lct match each other
def matchSegLCT(seg, lct):
	if abs(seg.halfStrip[3] - lct.keyHalfStrip) <= 2 and abs(seg.wireGroup[3] - lct.keyWireGroup) <= 2:
		return True
	else:
		return False

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
		CMIN = -10.
		CMAX = 10.
		if F_DATAFILE is None:
			for ATT in self.MEASDATA.keys():
				for MEAS in self.MEASDATA[ATT][0:1]: # only interested in Original for now
					for CHAM in CHAMLIST:
						self.HISTS[CHAM][MEAS] = R.TH1F('h'+str(CHAM)+str(MEAS), '', CBINS, CMIN, CMAX)
						#self.HISTS[CHAM][MEAS].SetDirectory(0)
					f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/5Dec/ana_'+str(MEAS)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')
					for entry in t:
						E = Primitives.ETree(t, DecList=['SEGMENT', 'LCT', 'RECHIT'])
						segs    = [Primitives.Segment(E, i) for i in xrange(len(E.seg_cham))]
						lcts    = [Primitives.LCT    (E, i) for i in xrange(len(E.lct_cham))]
						rechits = [Primitives.RecHit (E, i) for i in xrange(len(E.rh_cham ))]

						for CHAM in CHAMLIST:
							for seg in segs:
								if seg.cham != CHAM: continue
								for lct in lcts:
									if lct.cham != CHAM: continue
									if inPad(seg.halfStrip[3], seg.wireGroup[3], CHAM) and matchSegLCT(seg, lct):
										layers = [rechits[i].layer for i in seg.rhID]
										for layer in [1, 2, 3, 4, 5, 6]:
											if layer in layers: continue
											closestRHPosXDiff = float('inf')
											fillVal = float('inf')
											for rh in rechits:
												if rh.layer == layer and inPad(30, rh.wireGroup, CHAM):
													D = rh.pos['x']-seg.pos[layer]['x']
													if abs(D) < closestRHPosXDiff:
														closestRHPosXDiff = abs(D)
														fillVal = D
											self.HISTS[CHAM][MEAS].Fill(fillVal)
					f.Close()
					for CHAM in CHAMLIST:
						F_OUT.cd()
						self.HISTS[CHAM][MEAS].Write()
					print MEAS, 'Done'

		# for obtaining data dictionary from a file
		else:
			MIN = -6.
			MAX = 6.
			BINS = int((MAX-MIN)/((CMAX-CMIN)/CBINS))/16
			f = R.TFile.Open(F_DATAFILE)
			for ATT in self.MEASDATA.keys():
				for MEAS in self.MEASDATA[ATT][0:1]: # only interested in Original for now
					for CHAM in CHAMLIST:
						H = f.Get('h'+str(CHAM)+str(MEAS))
						H.Scale(1./H.Integral())
						self.HISTS[CHAM][MEAS] = H.Rebin(BINS, 'hN'+str(CHAM)+str(MEAS), np.array([MIN + i*(MAX-MIN)/float(BINS) for i in range(BINS+1)]))
						self.HISTS[CHAM][MEAS].SetDirectory(0)

	# get a value given a chamber and measurement number
	def val(self, cham, meas):
		return float(self.VALDATA[cham][meas])

	# get a vector of values
	def valVector(self, cham, ff):
		return np.array([self.val(cham, self.MEASDATA[att][ff]) for att in self.attVector()])

data = MegaStruct()

##### MAKEPLOT FUNCTION #####
def makePlot(cham, hist, xtitle, ytitle, title):

	# Step 1
	plot = Plotter.Plot(hist, legName=title, legType='p', option='hist')

	# Step 2
	canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 External Trigger', logy=False, extra='Internal', cWidth=800, cHeight=700)

	# Step 3
	canvas.makeLegend(lWidth=0.2, lHeight=0.25, pos='bl', lOffset=0.04, fontsize=0.03)

	# Step 4
	canvas.addMainPlot(plot, isFirst=True, addToLegend=False)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	plot.setTitles(X=xtitle, Y=ytitle)
	#hist.SetMinimum(0.0)
	#hist.SetMaximum(1.1)
	plot.scaleTitles(0.8)
	plot.scaleLabels(0.8)
	plot.scaleTitleOffsets(1.2, 'Y')
	canvas.makeTransparent()

	att = [key for key in data.MEASDATA.keys() if int(title) in data.MEASDATA[key]][0]
	text = R.TLatex()
	text.SetTextAlign(11)
	text.SetTextFont(42)
	text.SetTextSize(0.04)
	text.DrawLatexNDC(.75, .80, '{:.1f}'.format(att))
	text.DrawLatexNDC(.75, .75, '#mu:'    + '{:.4f}'.format(hist.GetMean()))
	text.DrawLatexNDC(.75, .70, '#sigma:' + '{:.4f}'.format(hist.GetStdDev()))

	ft = str(list(data.attVector()).index(att))

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/CRHX_ME'+str(cham)+'1_'+ft+'.pdf')
	R.SetOwnership(canvas.c, False)

##### MAKE PLOTS #####
for cham in CHAMLIST:
	for meas in data.HISTS[cham].keys():
		makePlot(\
			cham if cham == 1 else 2,
			data.HISTS[cham][meas],
			'min |RH(x) - Seg(x)| for Missing Layers',
			'Counts',
			str(meas)
		)
