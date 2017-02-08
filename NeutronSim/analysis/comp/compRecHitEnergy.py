import numpy as np
import ROOT as R
import Gif.NeutronSim.OldPlotter as Plotter
import Gif.NeutronSim.Primitives as Primitives
import Gif.NeutronSim.roottools as tools
import Gif.NeutronSim.Auxiliary as Aux
import sys

### PARAMETERS
# Which chambers to do; to compare to Yuriy only use ME1/1
CHAMLIST = (1, 110)

# Which files contain the relevant list of measurements and currents
#f_measgrid = 'measgrid_noSource'
f_measgrid = '../datafiles/measgrid'
f_attenhut = '../datafiles/attenhut'

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
		self.hists = { 1 : {} , 110 : {} }
		for att in self.FFFMeas.keys():
			for ff,MEAS in enumerate(self.FFFMeas[att]):
				f = R.TFile.Open('../../trees/ana_'+str(MEAS)+'.root')
				t = f.Get('GIFTree/GIFDigiTree')
				for CHAM in CHAMLIST:
					self.hists[CHAM][MEAS] = {\
						'rhEnergy' : R.TH1F('rh_e_'+str(CHAM)+'_'+str(MEAS),'',100,0,1500),
						'rhEnergyMatch' : R.TH1F('rh_e_match_'+str(CHAM)+'_'+str(MEAS),'', 100,0,1500),
						'rhEnergyNoMatch' : R.TH1F('rh_e_nomatch_'+str(CHAM)+'_'+str(MEAS),'',100,0,1500)
					}
				for entry in t:
					DecList = ['SEGMENT','LCT','COMP','RECHIT']#,'STRIP','WIRE']
					E = Primitives.ETree(t, DecList)
					lcts    = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham  ))]
					rechits = [Primitives.RecHit (E, i) for i in range(len(E.rh_cham ))]
					comps   = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham ))]
					segs    = [Primitives.Segment(E, i) for i in range(len(E.seg_cham  ))]
					#strips  = [Primitives.Strip  (E, i) for i in range(len(E.strip_cham))]
					#wires   = [Primitives.Wire   (E, i) for i in range(len(E.wire_cham  ))]

					for CHAM in CHAMLIST:
						for lct in lcts:
							if lct.cham!=CHAM: continue
							if not Aux.inPad(lct.keyHalfStrip,lct.keyWireGroup,CHAM): continue
							found, seg = Aux.bestSeg(lct,segs)
							if not found: continue
							rhList = seg.rhID
							alreadyMatched = []
							for rhID in rhList:
								if rechits[rhID].cham!=lct.cham: continue
								matched = False
								for c,comp in enumerate(comps):
									if comp.cham!=rechits[rhID].cham: continue
									if comp.layer!=rechits[rhID].layer: continue
									if not self.matchRHComp(rechits[rhID],comp): continue
									if c in alreadyMatched: continue
									if not Aux.inLCTPattern(lct,comp): continue
									alreadyMatched.append(c)
									matched = True
									break
								if CHAM==1:
									self.hists[1][MEAS]['rhEnergy'].Fill(rechits[rhID].energy)
								if CHAM==110:
									self.hists[110][MEAS]['rhEnergy'].Fill(rechits[rhID].energy)
								if matched:
									if CHAM==1:
										self.hists[1][MEAS]['rhEnergyMatch'].Fill(rechits[rhID].energy)
									if CHAM==110:
										self.hists[110][MEAS]['rhEnergyMatch'].Fill(rechits[rhID].energy)
								else:
									if CHAM==1:
										self.hists[1][MEAS]['rhEnergyNoMatch'].Fill(rechits[rhID].energy)
									if CHAM==110:
										self.hists[110][MEAS]['rhEnergyNoMatch'].Fill(rechits[rhID].energy)

				for CHAM in CHAMLIST:
					self.makePlot(self.hists[CHAM][MEAS]['rhEnergy'], MEAS, CHAM, att, self.lumi(CHAM,MEAS), ff,'all')
					self.makePlot(self.hists[CHAM][MEAS]['rhEnergyMatch'], MEAS,CHAM,  att, self.lumi(CHAM,MEAS), ff,'match')
					self.makePlot(self.hists[CHAM][MEAS]['rhEnergyNoMatch'], MEAS, CHAM, att, self.lumi(CHAM,MEAS), ff,'nomatch')
					self.makeStack(self.hists[CHAM][MEAS]['rhEnergyMatch'],self.hists[CHAM][MEAS]['rhEnergyNoMatch'], 
						MEAS,CHAM,  att, self.lumi(CHAM,MEAS), ff)

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
	def makePlot(self, histTmp, meas, cham, att, lumi, ff, title, pretty=pretty):
		# *** USAGE:
		#  1) construct Plotter.Plot(Object, legName, legType="felp", option)
		#  2) construct Plotter.Canvas(lumi, logy, ratioFactor, extra, cWidth=800, cHeight=600)
		#  3) call Plotter.Canvas.makeLegend(lWidth=0.125, lHeight=0.2, pos="tr", lOffset=0.02, fontsize=0.04)
		#  4) call Plotter.Canvas.addMainPlot(Plot, addToLegend)
		#  5) apply any cosmetic commands here
		# *6) call Plotter.Canvas.addLegendEntry(Plot)
		# *7) call Plotter.Canvas.makeRatioPlot(top, bottom, plusminus, option, ytit, xtit)
		#  8) call Plotter.Canvas.finishCanvas()
		#
		# * = optional; if addToLegend is always true, and/or if no ratio plot needed (ratioFactor = 0), neither of these steps are required
		#
		# Plotter.Canvas class members c, mainPad, ratPad, leg, rat, and gr are available
		#

		# Step 1
		CHAM = 1 if cham==1 else 2
		hist = tools.DrawOverflow(histTmp)
		plot = Plotter.Plot(hist,'', option='hist')

		# Step 2
		ATT = str(int(att)) if str(att)!='inf' else 'NS'
		canvas = Plotter.Canvas('ME'+str(CHAM)+'/1, Ext. Trig., %2.1f'%(lumi)+'#times10^{33} Hz/cm^{2} ('+ATT+')', False, 0., '', 800, 600)

		# Step 3
		canvas.makeLegend()

		# Step 4
		canvas.addMainPlot(plot, False)

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
		canvas.c.SaveAs('rhEnPlots/recHitEnergy_'+str(CHAM)+'1_'+str(meas)+'_'+title+'.pdf')
		R.SetOwnership(canvas.c, False)
	
	### MAKESTACK FUNCTION
	def makeStack(self, histTmp1,histTmp2, meas, cham, att, lumi, ff, pretty=pretty):
		# *** USAGE:
		#  1) construct Plotter.Plot(Object, legName, legType="felp", option)
		#  2) construct Plotter.Canvas(lumi, logy, ratioFactor, extra, cWidth=800, cHeight=600)
		#  3) call Plotter.Canvas.makeLegend(lWidth=0.125, lHeight=0.2, pos="tr", lOffset=0.02, fontsize=0.04)
		#  4) call Plotter.Canvas.addMainPlot(Plot, addToLegend)
		#  5) apply any cosmetic commands here
		# *6) call Plotter.Canvas.addLegendEntry(Plot)
		# *7) call Plotter.Canvas.makeRatioPlot(top, bottom, plusminus, option, ytit, xtit)
		#  8) call Plotter.Canvas.finishCanvas()
		#
		# * = optional; if addToLegend is always true, and/or if no ratio plot needed (ratioFactor = 0), neither of these steps are required
		#
		# Plotter.Canvas class members c, mainPad, ratPad, leg, rat, and gr are available
		#

		# Step 1
		# Make histogram objects
		hist1 = tools.DrawOverflow(histTmp1)
		hist1.SetFillColor(R.kBlue)
		hist2 = tools.DrawOverflow(histTmp2)
		hist2.SetFillColor(R.kRed)
		#plot1 = Plotter.Plot(hist1, 'Matched RecHit to Comp', 'f', 'hist')
		#plot2 = Plotter.Plot(hist2, 'Not Matched RecHit to Comp', 'f', 'hist')
		plot1 = Plotter.Plot(hist1, '', option='hist')
		plot2 = Plotter.Plot(hist2, '', option='hist')

		# Make stack object
		stack = R.THStack('stack','')
		# Draw match on top of no match
		stack.Add(hist2)
		stack.Add(hist1)
		stackPlot = Plotter.Plot(stack,'',option='hist')

		# Step 2
		CHAM = 1 if cham==1 else 2
		ATT = str(int(att)) if str(att)!='inf' else 'NS'
		canvas = Plotter.Canvas('ME'+str(CHAM)+'/1, Ext. Trig., %2.1f'%(lumi)+'#times10^{33} Hz/cm^{2} ('+ATT+')', False, 0., '', 800, 600)

		# Step 3
		#canvas.makeLegend(pos='tr',lWidth=0.35,fontsize=0.03)
		canvas.makeLegend()

		# Step 4
		canvas.addMainPlot(stackPlot, False)

		# Step 5
		R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
		stack.GetYaxis().SetTitle('Counts')
		stack.GetXaxis().SetTitle('RecHit Energy [ADC]')
		stack.SetMinimum(0.0)
		stackPlot.scaleTitles(0.8)
		stackPlot.scaleLabels(0.8)
		canvas.makeTransparent()

		# Step 6
		#canvas.addLegendEntry(plot1)
		#canvas.addLegendEntry(plot2)

		# Step 7

		# Step 8
		canvas.finishCanvas()
		canvas.c.SaveAs('rhEnPlots/recHitEnergyStack_'+str(CHAM)+'1_'+str(meas)+'.pdf')
		R.SetOwnership(canvas.c, False)

data = MegaStruct(f_measgrid, f_attenhut, fromFile, castrated)
