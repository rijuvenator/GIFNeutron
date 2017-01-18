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
#f_measgrid = 'measgrid_slim'
f_measgrid = '../datafiles/measgrid'
f_attenhut = '../datafiles/attenhut'

# Whether or not to only use Yuriy's 5 attenuations
castrated = False

# Whether or not to get the data from a file. None if not; filename if so.
fromFile = None
#fromFile = '../datafiles/compRes'

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
		if fromFile is None:
			for att in self.FFFMeas.keys():
				for ff,meas in enumerate(self.FFFMeas[att][0:1]):
					f = R.TFile.Open('/afs/cern.ch/work/a/adasgupt/public/GIF/16Dec/ana_'+str(meas)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')
					nStrips11=112.
					nStrips21=80.
					compResScat11 = R.TH2F('compResScat11','',500,0,nStrips11/2,int(nStrips11),0,nStrips11/2)
					compResScat21 = R.TH2F('compResScat21','',500,0,nStrips21/2,int(nStrips21),0,nStrips21/2)
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
								if not Aux.inPad(lct.keyHalfStrip,lct.keyWireGroup,cham): continue
								for s,seg in enumerate(segs):
									# Check on chamber, segment position, match the segment to the lct, and if we've already matched the segment
									if seg.cham!=cham: continue
									if not Aux.inPad(seg.halfStrip[3], seg.wireGroup[3], cham): continue
									if not Aux.matchSegLCT(seg,lct): continue
									if s in alreadyMatchedSeg: continue
									alreadyMatchedSeg.append(s)
									# Make list of rechits from the segment
									rhList = seg.rhID
									for rhID in rhList:
										# Check on chamber
										if rechits[rhID].cham!=cham: continue
										maxDiff = 999.
										compPos = float('inf')
										rechitPos = float('inf')
										matchIndex = 999
										FOUND = False
										for c,comp in enumerate(comps):
											# Check on chamber, layer, matching comp to rechit, and if we've already matched the comparator
											if comp.cham!=cham: continue
											if comp.layer!=rechits[rhID].layer: continue
											#if not self.matchRHComp(rechits[rhID],comp): continue
											if c in alreadyMatchedComp: continue
											# Add 1/2 to comparator half strip to align it with rec hit
											# Multiply by 1/2 to convert to strip units
											compPosTemp = 0.5*(comp.halfStrip+0.5)
											rechitPosTemp = 0.5*(rechits[rhID].halfStrip)
											if abs(compPosTemp - rechitPosTemp) < maxDiff:
												maxDiff = abs(compPosTemp - rechitPosTemp)
												compPos = compPosTemp
												rechitPos = rechitPosTemp
												matchIndex = c
												FOUND = True
										if FOUND:
											alreadyMatchedComp.append(matchIndex)
											if cham==1: 
												compResScat11.Fill(rechitPos,compPos)
											if cham==110:
												compResScat21.Fill(rechitPos,compPos)
									# Break out of segment loop since we've already found the matching segment to the lct
									break
					# Make histogram
					self.makeHist(compResScat11,meas,1,att,self.lumi(1,meas),ff)
					self.makeHist(compResScat21,meas,110,att,self.lumi(110,meas),ff)
					print meas
		else:
			# this file is the output of the printout above
			pass

	# a rechit/comparator match is if the comparator halfstrip is within 2 strips of the comparator halfstrip
	def matchRHComp(self, rh, comp):
		diff = abs(rh.halfStrip - comp.halfStrip+0.5)
		if diff<=4:
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
	def lumi(self, cham, meas):
		factor = 5. if cham == 110 else 3.3
		return factor * self.current(cham, meas)

	def res(self, cham, meas):
		return self.compRes[cham][meas]
	def mean(self, cham, meas):
		return self.compMean[cham][meas]

	# get a vector of efficiencies
	def resVector(self, cham, ff):
		return np.array([self.res(cham, self.FFFMeas[att][ff]) for att in self.attVector()])
	# get a vector of efficiencies
	def meanVector(self, cham, ff):
		return np.array([self.mean(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	def makeHist(self, hist, meas, cham, att, lumi, ff, pretty=pretty):
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
		CHAM = 2 if cham==110 else 1
		plot = Plotter.Plot(hist, '', option='colz')

		# Step 2
		ATT = str(int(att)) if str(att)!='inf' else 'NS'
		canvas = Plotter.Canvas('ME'+str(CHAM)+'/1, Ext. Trig., %2.1f'%(lumi)+'#times10^{33} Hz/cm^{2} ('+ATT+')', False, 0., '', 800, 600)

		# Step 3
		canvas.makeLegend()

		# Step 4
		canvas.addMainPlot(plot, True, False)

		# Step 5
		R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
		#R.gStyle.SetPalette(56) # kInvertedDarkBodyRadiator
		R.gStyle.SetPalette(55) #kRainBow
		plot.setTitles('RecHit position [strip]','Comparator position [strip]')
		plot.scaleTitles(0.8)
		plot.scaleLabels(0.8,axes='XYZ')
		canvas.mainPad.SetLeftMargin(canvas.mainPad.GetLeftMargin()*0.8)
		canvas.mainPad.SetRightMargin(canvas.mainPad.GetRightMargin()*1.2)
		
		canvas.makeTransparent()

		# Step 6

		# Step 7

		# Step 8
		canvas.finishCanvas()
		canvas.c.SaveAs('resPlots/compResScat_'+str(CHAM)+'1_'+str(meas)+'.pdf')
		R.SetOwnership(canvas.c, False)


# Do everything
data = MegaStruct(f_measgrid, f_attenhut, fromFile, castrated)


