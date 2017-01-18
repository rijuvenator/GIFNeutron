import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Plotter as Plotter
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.roottools as tools
import Gif.TestBeamAnalysis.Auxiliary as Aux
import sys

### PARAMETERS
# Which chambers to do; to compare to Yuriy only use ME1/1
# chamlist = [1]
chamlist = [1, 110]

# Which files contain the relevant list of measurements and currents
f_measgrid = '../datafiles/measgrid'
#f_measgrid = 'measgrid_15'
f_attenhut = '../datafiles/attenhut'

# Whether or not to only use Yuriy's 5 attenuations
castrated = False

# Whether or not to get the data from a file. None if not; filename if so.
#fromFile = None
#fromFile = '../datafiles/compEff'
fromFile = 'compEff'

# Dictionary containing cosmetic data, comment out for fewer ones
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

###############################################################################################
### BEGIN CODE
### DATA STRUCTURE CLASS
class MegaStruct():
	def __init__(self,measgrid,attenhut,fromFile,castrated):
		self.castrated = castrated

		# Fill dictionary connecting attenuation to list of measurement numbers, ordered by FF
		f = open(measgrid)
		self.FFFMeas = {}
		for line in f:
			cols = line.strip('\n').split()
			self.FFFMeas[float(cols[0])] = [int(j) for j in cols[1:]]
		f.close()

		# Fill dictionary connecting chamber and measurement number to list of currents
		f = open(attenhut)
		self.Currs = { 1 : {}, 110 : {} }
		currentCham = 1
		for line in f:
			if line == '\n':
				currentCham = 110
				continue
			cols = line.strip('\n').split()
			currentMeas = int(cols[1])
			self.Currs[currentCham][currentMeas] = [float(i) for i in cols[2:]]
		f.close()

		# Fill dictionary connecting chamber, measurement number, and efftype to efficiency value
		self.Effs = { 1 : {}, 110 : {} }
		self.ErrsUp = { 1 : {}, 110 : {} }
		self.ErrsDown = { 1 : {}, 110 : {} }
		if fromFile is None:
			pass
			for att in self.FFFMeas.keys():
				for meas in self.FFFMeas[att]:
					f = R.TFile.Open('../../trees/ana_'+str(meas)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')
					numerator1 = 0
					denominator1 = 0
					numerator2 = 0
					denominator2 = 0
					nMatchedSegs1 = 0
					nMatchedSegs2 = 0
					A1 = 0
					A2 = 0
					B1 = 0
					B2 = 0
					for entry in t:
						DecList = ['SEGMENT','LCT','COMP','RECHIT']#,'STRIP','WIRE']
						E = Primitives.ETree(t, DecList)
						lcts    = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham  ))]
						rechits = [Primitives.RecHit (E, i) for i in range(len(E.rh_cham ))]
						comps   = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham ))]
						segs    = [Primitives.Segment(E, i) for i in range(len(E.seg_cham  ))]
						#strips  = [Primitives.Strip  (E, i) for i in range(len(E.strip_cham))]
						#wires   = [Primitives.Wire   (E, i) for i in range(len(E.wire_cham  ))]

						for cham in [1,110]:
							alreadyMatchedSeg = []
							for lct in lcts:
								# Check on chamber and LCT position
								if lct.cham!=cham: continue
								if not Aux.inPad(lct.keyHalfStrip,lct.keyWireGroup,cham): continue
								mostHits = -999.
								found = False
								bestSeg = -999
								closeSeg = False
								for s,seg in enumerate(segs):
									# Check on chamber, segment position, match the segment to the lct, and if we've already matched the segment
									if seg.cham!=lct.cham: continue
									if not Aux.matchSegLCT(seg,lct): continue
									if not Aux.inPad(seg.halfStrip, seg.wireGroup, cham): continue
									#print abs(seg.halfStrip - lct.keyHalfStrip), seg.nHits, s
									if seg.nHits > mostHits:
										if seg in alreadyMatchedSeg: continue
										mostHits = seg.nHits
										bestSeg = s
										found = True
								if found==True:
									if cham==1: nMatchedSegs1 +=1
									if cham==110: nMatchedSegs2 +=1
									alreadyMatchedSeg.append(bestSeg)
									#print abs(segs[bestSeg].halfStrip - lct.keyHalfStrip),segs[bestSeg].nHits,  bestSeg, segs[bestSeg].cham, lct.cham
									seg = segs[bestSeg]
									# Make list of rechits from the segment
									rhList = seg.rhID

									matchedRHComp = 0
									for rhID in rhList:
										# Check on chamber
										if rechits[rhID].cham!=lct.cham: continue
										closestRHDist = 999
										CloseRH = False
										closestComp = -999
										# Find closest comparator in same layer
										for c,comp in enumerate(comps):
											# Check on chamber and layer 
											if comp.cham!=lct.cham: continue
											if comp.layer!=rechits[rhID].layer: continue
											# Find closest comparator in the layer
											RHdist = abs(rechits[rhID].halfStrip-comp.halfStrip+0.5)
											if RHdist < closestRHDist: 
												closestRHDist = RHdist
												closestComp = c
												CloseRH = True
										# Make sure that the closest comp is w/in 2 half strips, wasn't already matched
										# and is inside the LCT pattern
										if CloseRH:
											comp = comps[closestComp]
											if not Aux.inLCTPattern(lct,comp) and self.matchRHComp(rechits[rhID],comp):
												continue
											'''
											if not self.matchRHComp(rechits[rhID],comp): 
												if cham==1: B1 += 1
												if cham==110: B2 += 1
												continue
											'''
											if self.matchRHComp(rechits[rhID],comp) and Aux.inLCTPattern(lct,comp):
												if cham==1: A1 += 1
												if cham==110: A2 += 1
											if not self.matchRHComp(rechits[rhID],comp) and not Aux.inLCTPattern(lct,comp):
												if cham==1: B1 += 1
												if cham==110: B2 += 1
										# Add to B if no comparator in same layer as rechit
										else:
											if cham==1: B1 += 1
											if cham==110: B2 += 1

					eff1,errUp1,errDown1 = tools.clopper_pearson(A1,A1+B1)
					eff2,errUp2,errDown2 = tools.clopper_pearson(A2,A2+B2)
					print meas, eff1, errUp1, errDown1, eff2, errUp2, errDown2
					# fill dictionary
					self.Effs[1][meas] = eff1
					self.ErrsUp[1][meas] = errUp1
					self.ErrsDown[1][meas] = errDown1
					self.Effs[110][meas] = eff2
					self.ErrsUp[110][meas] = errUp2
					self.ErrsDown[110][meas] = errDown2
		else:
			# this file is the output of the printout above
			f = open(fromFile)
			for line in f:
				cols = line.strip('\n').split()
				meas = int(cols[0])
				self.Effs[1][meas] = float(cols[1])
				self.ErrsUp[1][meas] = float(cols[2])
				self.ErrsDown[1][meas] = float(cols[3])
				self.Effs[110][meas] = float(cols[4])
				self.ErrsUp[110][meas] = float(cols[5])
				self.ErrsDown[110][meas] = float(cols[6])

	# a rechit/comparator match is if the comparator halfstrip is within 2 halfstrips of the comparator halfstrip
	def matchRHComp(self, rh, comp):
		# Shift comparator halfstrip by 1/2 so that it has the same origin as the rechit halfstrips
		diff = abs(rh.halfStrip - comp.halfStrip+0.5)
		if diff<=2:
			return True
		else:
			return False
	
	# get a current measurement given a chamber and measurement number
	def current(self, cham, meas):
		if cham == 1:
			return sum(self.Currs[cham][meas])/6.0
		elif cham == 110:
			return sum(self.Currs[cham][meas][6:12])/6.0
	
	# get a vector of attenuations
	def attVector(self):
		if self.castrated:
			return np.array([33., 46., 100., float('inf')])
		else:
			return np.array(sorted(self.FFFMeas.keys()))

	# get a vector of currents
	def currentVector(self, cham, ff):
		return np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	# get a vector of equivalent luminosities
	def lumiVector(self, cham, ff):
		factor = 5.e33 if cham == 110 else 3.e33
		return factor * np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	def eff(self, cham, meas):
		return self.Effs[cham][meas]
	def errUp(self, cham, meas):
		return self.ErrsUp[cham][meas]
	def errDown(self, cham, meas):
		return self.ErrsDown[cham][meas]

	# get a vector of efficiencies
	def effVector(self, cham, ff):
		return np.array([self.eff(cham, self.FFFMeas[att][ff]) for att in self.attVector()])
	# get a vector of efficiencies
	def errUpVector(self, cham, ff):
		return np.array([self.errDown(cham, self.FFFMeas[att][ff]) for att in self.attVector()])
	# get a vector of erriciencies
	def errDownVector(self, cham, rr):
		return np.array([self.errDown(cham, self.FFFMeas[att][ff]) for att in self.attVector()])


data = MegaStruct(f_measgrid, f_attenhut, fromFile, castrated)

### MAKEPLOT FUNCTION
def makePlot(x, y,eyh,eyl, cham, xtitle, ytitle, title, pretty=pretty):
	# *** USAGE:
	#  1) construct Plotter.Plot(Object, legName, legType="felp", option)
	#  2) construct Plotter.Canvas(lumi, logy, ratioFactor, extra, cWidth=800, cHeight=600)
	#  3) call Plotter.Canvas.makeLegend(lWidth=0.125, lHeight=0.2, pos="tr", lOffset=0.02, fontsize=0.04)
	#  4) call Plotter.Canvas.addMainPlot(Plot, isFirst, addToLegend)
	#  5) apply any cosmetic commands here
	# *6) call Plotter.Canvas.addLegendEntry(Plot)
	# *7) call Plotter.Canvas.makeRatioPlot(top, bottom, plusminus, option, ytit, xtit)
	#  8) call Plotter.Canvas.finishCanvas()
	#
	# * = optional; if addToLegend is always true, and/or if no ratio plot needed (ratioFactor = 0), neither of these steps are required
	#
	# Plotter.Canvas class members c, mainPad, ratPad, leg, rat, and gr are available
	#

	CHAM = 2 if cham==110 else 1
	graphs = []
	ntypes = len(pretty.keys())
	for i in range(ntypes):
		ex = np.zeros(len(x[i]))
		low = y[i]-eyl[i]
		high = eyh[i]-y[i]
		graphs.append(R.TGraphAsymmErrors(len(x[i]), x[i], y[i],ex,ex,low,high))

	# Step 1
	plots = []
	for i,p in enumerate(pretty.keys()):
		plots.append(Plotter.Plot(graphs[i], pretty[p]['name'], 'p', 'PE'))

	# Step 2
	canvas = Plotter.Canvas('ME'+str(CHAM)+'/1 External Trigger', False, 0., 'Internal', 800, 700)

	# Step 3
	canvas.makeLegend(.2,0.25,'bl',0.04, 0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i],False)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	canvas.firstPlot.plot.GetYaxis().SetTitle(ytitle)
	canvas.firstPlot.plot.GetXaxis().SetTitle(xtitle)
	canvas.firstPlot.plot.SetMinimum(0.0)
	canvas.firstPlot.plot.SetMaximum(1.1)
	canvas.firstPlot.scaleTitles(0.8)
	canvas.firstPlot.scaleLabels(0.8)
	canvas.makeTransparent()

	for i,p in enumerate(pretty.keys()):
		graphs[i].SetMarkerColor(pretty[p]['color'])
		graphs[i].SetMarkerStyle(pretty[p]['marker'])
		graphs[i].SetMarkerSize(2)

	# Step 6
	for i in range(ntypes):
		canvas.addLegendEntry(plots[i])

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('best/compEff_'+str(CHAM)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

### MAKE ALL PLOTS
for cham in chamlist:
	# Plots with current on x-axis
	makePlot(\
			[data.currentVector(cham, ff) for ff in pretty.keys()],
			[data.effVector(cham, ff) for ff in pretty.keys()],
			[data.errUpVector(cham, ff) for ff in pretty.keys()],
			[data.errDownVector(cham, ff) for ff in pretty.keys()],
			cham,
			'Mean Current [#muA]',
			'Comparator Efficiency',
			'curr'
			)
	# Plots with luminosity on x-axis
	makePlot(\
			[data.lumiVector(cham, ff) for ff in pretty.keys()],
			[data.effVector(cham, ff) for ff in pretty.keys()],
			[data.errUpVector(cham, ff) for ff in pretty.keys()],
			[data.errDownVector(cham, ff) for ff in pretty.keys()],
			cham,
			'Luminosity [Hz/cm^{2}]',
			'Comparator Efficiency',
			'lumi')
	# Plots with 1/A on x-axis
	makePlot(\
			[np.reciprocal(data.attVector()) for ff in pretty.keys()],
			[data.effVector(cham, ff) for ff in pretty.keys()],
			[data.errUpVector(cham, ff) for ff in pretty.keys()],
			[data.errDownVector(cham, ff) for ff in pretty.keys()],
			cham,
			'Source Intensity 1/A',
			'Comparator Efficiency',
			'att')
