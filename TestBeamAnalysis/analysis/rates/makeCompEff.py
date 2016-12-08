import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Plotter as Plotter
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.roottools as tools
import sys

### PARAMETERS
# Which chambers to do; to compare to Yuriy only use ME1/1
# chamlist = [1]
chamlist = [1, 2]

# Which files contain the relevant list of measurements and currents
f_measgrid = 'measgrid'
f_attenhut = 'attenhut'

# Whether or not to only use Yuriy's 5 attenuations
castrated = False

# Whether or not to get the data from a file. None if not; filename if so.
fromFile = None
#fromFile = 'compEff'

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
		self.Currs = { 1 : {}, 2 : {} }
		currentCham = 1
		for line in f:
			if line == '\n':
				currentCham = 2
				continue
			cols = line.strip('\n').split()
			currentMeas = int(cols[1])
			self.Currs[currentCham][currentMeas] = [float(i) for i in cols[2:]]
		f.close()

		# Fill dictionary connecting chamber, measurement number, and efftype to efficiency value
		self.Effs = { 1 : {}, 2 : {} }
		self.ErrsUp = { 1 : {}, 2 : {} }
		self.ErrsDown = { 1 : {}, 2 : {} }
		if fromFile is None:
			pass
			for att in self.FFFMeas.keys():
				for meas in self.FFFMeas[att]:
					f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/5Dec/ana_'+str(meas)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')
					#numerator1 = 0
					#denominator1 = 0
					#numerator2 = 0
					#denominator2 = 0
					denominator = 0
					numerator = 0
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
							alreadyMatchedComp = []
							alreadyMatchedSeg = []
							for lct in lcts:
								# Check on chamber and LCT position
								if lct.cham!=cham: continue
								if not self.inPad(lct.keyHalfStrip,lct.keyWireGroup,cham): continue
								for s,seg in enumerate(segs):
									# Check on chamber, segment position, match the segment to the lct, and if we've already matched the segment
									if seg.cham!=cham: continue
									if not self.inPad(seg.halfStrip, seg.wireGroup, cham): continue
									if not self.matchSegLCT(seg,lct): continue
									if s in alreadyMatchedSeg: continue
									alreadyMatchedSeg.append(s)
									# Make list of rechits from the segment
									rhList = []
									if seg.nHits >=1: rhList.append(seg.rhID1)
									if seg.nHits >=2: rhList.append(seg.rhID2)
									if seg.nHits >=3: rhList.append(seg.rhID3)
									if seg.nHits >=4: rhList.append(seg.rhID4)
									if seg.nHits >=5: rhList.append(seg.rhID5)
									if seg.nHits ==6: rhList.append(seg.rhID6)
									denominator += seg.nHits
									#denominator += len(rhList)
									#if cham==1: denominator1 += len(rhList)
									#if cham==110: denominator2 += len(rhList)
									matchedRHComp = 0
									for rhID in rhList:
										# Check on chamber
										if rechits[rhID].cham!=cham: continue
										for c,comp in enumerate(comps):
											# Check on chamber, layer, matching comp to rechit, and if we've already matched the comparator
											if comp.cham!=cham: continue
											if comp.layer!=rechits[rhID].layer: continue
											if not self.matchRHComp(rechits[rhID],comp): continue
											if c in alreadyMatchedComp: continue
											alreadyMatchedComp.append(c)
											matchedRHComp +=1
											# Break out of the comparator loop since we've already found the matching comparator to the rechit
											break
									numerator += matchedRHComp
									#if cham==1: numerator1 += matchedRHComp
									#if cham==110: numerator2 += matchedRHComp
								# Break out of segment loop since we've already found the matching segment to the lct
								break

							eff,errUp,errDown = tools.clopper_pearson(numerator,denominator)
							ch = 1 if cham==1 else 2
							self.Effs[ch][meas] = eff
							self.ErrsUp[ch][meas] = errUp
							self.ErrsDown[ch][meas] = errDown
					print meas, 
					print self.Effs[1][meas], self.ErrsUp[1][meas], self.ErrsDown[1][meas],
					print self.Effs[2][meas], self.ErrsUp[2][meas], self.ErrsDown[2][meas]
					'''
					eff1,errUp1,errDown1 = tools.clopper_pearson(numerator1,denominator1)
					eff2,errUp2,errDown2 = tools.clopper_pearson(numerator2,denominator2)
					print meas, eff1, errUp1, errDown1, eff2, errUp2, errDown2
					# fill dictionary
					self.Effs[1][meas] = eff1
					self.ErrsUp[1][meas] = errUp1
					self.ErrsDown[1][meas] = errDown1
					self.Effs[2][meas] = eff2
					self.ErrsUp[2][meas] = errUp2
					self.ErrsDown[2][meas] = errDown2
					'''
		else:
			# this file is the output of the printout above
			f = open(fromFile)
			for line in f:
				cols = line.strip('\n').split()
				meas = int(cols[0])
				self.Effs[1][meas] = float(cols[1])
				self.ErrsUp[1][meas] = float(cols[2])
				self.ErrsDown[1][meas] = float(cols[3])
				self.Effs[2][meas] = float(cols[4])
				self.ErrsUp[2][meas] = float(cols[5])
				self.ErrsDown[2][meas] = float(cols[6])

	# defines a paddle region
	def inPad(self, hs, wg, cham):
		if cham == 1:
			if      hs >=  25\
				and hs <=  72\
				and wg >=  37\
				and wg <=  43:
				return True
			else:
				return False
		if cham == 110:
			if      hs >=   8\
				and hs <=  38\
				and wg >=  55\
				and wg <=  65:
				return True
			else:
				return False
	
	# a segment match is if the lct halfstrip is within 2 halfstrips of the segment halfstrip and 1 wire group 
	def matchSegLCT(self, seg, lct):
		diffHS = abs(seg.halfStrip - lct.keyHalfStrip)
		diffWG = abs(seg.wireGroup- lct.keyWireGroup)
		if diffHS<=2 and diffWG<=1:
			return True
		else:
			return False

	# a rechit/comparator match is if the comparator halfstrip is within 2 strips of the comparator halfstrip
	def matchRHComp(self, rh, comp):
		diff = abs(rh.halfStrip - comp.halfStrip)
		if diff<=2:
			return True
		else:
			return False

	# get a current measurement given a chamber and measurement number
	def current(self, cham, meas):
		if cham == 1:
			return sum(self.Currs[cham][meas])/6.0
		elif cham == 2:
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
		factor = 5.e33 if cham == 2 else 3.e33
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
	# Note: If TYPE is a TGraph and option="P", a draw option of "AP" is required for the FIRST plot (first addMainPlot)
	# So change plot.option, either to "P" after (if option="AP"), or change plot.option to "AP" before and "P" after (if option="P")
	#

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
		plots.append(Plotter.Plot(graphs[i], pretty[p]['name'], 'pe', 'APE' if i==0 else 'PE'))

	# Step 2
	canvas = Plotter.Canvas('ME'+str(cham)+'/1 External Trigger', False, 0., 'Internal', 800, 700)

	# Step 3
	canvas.makeLegend(.2,0.25,'bl',0.04, 0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i], i==0, True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	graphs[0].GetYaxis().SetTitle(ytitle)
	graphs[0].GetXaxis().SetTitle(xtitle)
	graphs[0].SetMinimum(0.0)
	graphs[0].SetMaximum(1.1)
	plots[0].scaleTitles(0.8)
	plots[0].scaleLabels(0.8)
	canvas.makeTransparent()

	for i,p in enumerate(pretty.keys()):
		graphs[i].SetMarkerColor(pretty[p]['color'])
		graphs[i].SetMarkerStyle(pretty[p]['marker'])
		graphs[i].SetMarkerSize(1.5)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('test/compEff_'+str(cham)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

### MAKE ALL PLOTS
'''
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
'''
