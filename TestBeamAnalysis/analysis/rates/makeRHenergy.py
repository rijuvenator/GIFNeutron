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
f_measgrid = 'measgrid_noSource'
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
		for ff,att in enumerate(self.FFFMeas.keys()):
			for meas in self.FFFMeas[att]:
				f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/5Dec/ana_'+str(meas)+'.root')
				t = f.Get('GIFTree/GIFDigiTree')
				rh_e1 = R.TH1F('rh_e1','',100,0,1500)
				rh_e2 = R.TH1F('rh_e2','',100,0,1500)
				rh_e_match1 = R.TH1F('rh_e_match1','',100,0,1500)
				rh_e_match2 = R.TH1F('rh_e_match2','',100,0,1500)
				rh_e_nomatch1 = R.TH1F('rh_e_nomatch1','',100,0,1500)
				rh_e_nomatch2 = R.TH1F('rh_e_nomatch2','',100,0,1500)
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
						for lct in lcts:
							if lct.cham!=cham: continue
							if not self.inPad(lct.keyHalfStrip,lct.keyWireGroup,cham if cham==1 else 2): continue
							for seg in segs:
								if seg.cham!=cham: continue
								if not self.inPad(seg.halfStrip, seg.wireGroup, cham if cham==1 else 2): continue
								if not self.matchSegLCT(seg,lct): continue
								rhList = []
								if seg.nHits >=1: rhList.append(seg.rhID1)
								if seg.nHits >=2: rhList.append(seg.rhID2)
								if seg.nHits >=3: rhList.append(seg.rhID3)
								if seg.nHits >=4: rhList.append(seg.rhID4)
								if seg.nHits >=5: rhList.append(seg.rhID5)
								if seg.nHits ==6: rhList.append(seg.rhID6)
								alreadyMatched = []
								for rhID in rhList:
									if rechits[rhID].cham!=cham: continue
									matched = False
									for c,comp in enumerate(comps):
										if comp.cham!=cham: continue
										if comp.layer!=rechits[rhID].layer: continue
										if not self.matchRHComp(rechits[rhID],comp): continue
										if c in alreadyMatched: continue
										alreadyMatched.append(c)
										matched = True
										break
									if cham==1:
										rh_e1.Fill(rechits[rhID].energy)
									if cham==110:
										rh_e2.Fill(rechits[rhID].energy)
									if matched:
										if cham==1:
											rh_e_match1.Fill(rechits[rhID].energy)
										if cham==110:
											rh_e_match2.Fill(rechits[rhID].energy)
									else:
										if cham==1:
											rh_e_nomatch1.Fill(rechits[rhID].energy)
										if cham==110:
											rh_e_nomatch2.Fill(rechits[rhID].energy)

				self.makePlot(rh_e1, meas, cham, att, self.lumi(cham,meas), ff)
				self.makePlot(rh_e2, meas, cham, att, self.lumi(cham,meas), ff)
				self.makePlot(rh_e_match1, meas,cham,  att, self.lumi(cham,meas), ff)
				self.makePlot(rh_e_match2, meas, cham, att, self.lumi(cham,meas), ff)
				self.makePlot(rh_e_nomatch1, meas, cham, att, self.lumi(cham,meas), ff)
				self.makePlot(rh_e_nomatch2, meas, cham, att, self.lumi(cham,meas), ff)
				self.makeStack(rh_e_match1,rh_e_nomatch1, meas,cham,  att, self.lumi(cham,meas), ff)
				self.makeStack(rh_e_match2,rh_e_nomatch2, meas, cham, att, self.lumi(cham,meas), ff)

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
	
	# a segment match is if the lct halfstrip is within 2 halfstrips of the segment halfstrip
	def matchSegLCT(self, seg, lct):
		diffHS = abs(seg.halfStrip - lct.keyHalfStrip)
		diffWG = abs(seg.wireGroup- lct.keyWireGroup)
		if diffHS<=2 and diffWG<=2:
			return True
		else:
			return False

	# a rechit/comparator match is if the comparator halfstrip is within 2 strips of the comparator halfstrip
	def matchRHComp(self, rh, comp):
		# all in halfstrip units
		diff = abs(rh.halfStrip - comp.halfStrip)
		# 2 strips = 4 halfstrips
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

	# get a vector of equivalent luminosities
	def lumi(self, cham, meas):
		factor = 5. if cham == 110 else 3.
		return factor * float(self.current(cham, meas))

	### MAKEPLOT FUNCTION
	def makePlot(self, histTmp, meas, cham, att, lumi, ff, pretty=pretty):
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

		# Step 1
		CHAM = 1 if cham==1 else 2
		hist = tools.DrawOverflow(histTmp)
		plot = Plotter.Plot(hist, pretty[ff]['name'], 'f', 'hist')

		# Step 2
		CHAM = 1 if cham==1 else 2
		ATT = str(int(att)) if att!='inf' else 'NS'
		canvas = Plotter.Canvas('ME'+str(CHAM)+'/1, Ext. Trig., %2.1f'%(lumi)+'#times10^{33} Hz/cm^{2} ('+ATT+')', False, 0., '', 800, 600)

		# Step 3
		canvas.makeLegend(pos='tr')

		# Step 4
		canvas.addMainPlot(plot, True, True)

		# Step 5
		R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
		hist.GetYaxis().SetTitle('Counts')
		hist.GetXaxis().SetTitle('RecHit Energy [ADC]')
		hist.SetMinimum(0.0)
		hist.SetFillColor(R.kBlue)
		plot.scaleTitles(0.8)
		plot.scaleLabels(0.8)
		canvas.makeTransparent()

		# Step 6

		# Step 7

		# Step 8
		canvas.finishCanvas()
		canvas.c.SaveAs('test/recHitEnergy_'+str(CHAM)+'1_'+str(meas)+'.pdf')
		R.SetOwnership(canvas.c, False)
	
	### MAKESTACK FUNCTION
	def makeStack(self, histTmp1,histTmp2, meas, cham, att, lumi, ff, pretty=pretty):
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

		# Step 1
		# Make histogram objects
		hist1 = tools.DrawOverflow(histTmp1)
		hist1.SetFillColor(R.kBlue)
		hist2 = tools.DrawOverflow(histTmp2)
		hist2.SetFillColor(R.kRed)
		plot1 = Plotter.Plot(hist1, pretty[ff]['name'], 'f', 'hist')
		plot2 = Plotter.Plot(hist2, pretty[ff]['name'], 'f', 'hist')

		# Make stack object
		stack = R.THStack('stack','')
		# Draw match on top of no match
		stack.Add(hist2)
		stack.Add(hist1)
		stackPlot = Plotter.Plot(stack,option='hist')

		# Step 2
		CHAM = 1 if cham==1 else 2
		ATT = str(int(att)) if str(att)!='inf' else 'NS'
		canvas = Plotter.Canvas('ME'+str(CHAM)+'/1, Ext. Trig., %2.1f'%(lumi)+'#times10^{33} Hz/cm^{2} ('+ATT+')', False, 0., '', 800, 600)

		# Step 3
		canvas.makeLegend(pos='tr')

		# Step 4
		canvas.addMainPlot(stackPlot, True, True)

		# Step 5
		R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
		stack.GetYaxis().SetTitle('Counts')
		stack.GetXaxis().SetTitle('RecHit Energy [ADC]')
		stack.SetMinimum(0.0)
		stackPlot.scaleTitles(0.8)
		stackPlot.scaleLabels(0.8)
		canvas.makeTransparent()

		# Step 6
		canvas.addLegendEntry(plot1)
		canvas.addLegendEntry(plot2)

		# Step 7

		# Step 8
		canvas.finishCanvas()
		canvas.c.SaveAs('test/recHitEnergyStack_'+str(CHAM)+'1_'+str(meas)+'.pdf')
		R.SetOwnership(canvas.c, False)

data = MegaStruct(f_measgrid, f_attenhut, fromFile, castrated)