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
CHAMLIST = [1, 110]

# Which files contain the relevant list of measurements and currents
#f_measgrid = 'measgrid_slim'
f_measgrid = '../datafiles/measgrid'
f_attenhut = '../datafiles/attenhut'
fromFile = '../datafiles/data_compRecHitRes'

# Whether or not to only use Yuriy's 5 attenuations
castrated = False

# Whether or not to get the data from a file. None if not; filename if so.
#fromFile = None

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
		self.compRes  = { 1 : {}, 110 : {} }
		self.compMean = { 1 : {}, 110 : {} }
		self.hists = { 1 : {}, 110 : {} }
		if fromFile is None:
			pass
			for att in self.FFFMeas.keys():
				for ff,MEAS in enumerate(self.FFFMeas[att]):
					f = R.TFile.Open('../../trees/ana_'+str(MEAS)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')
					for CHAM in CHAMLIST:
						self.hists[CHAM][MEAS] = {
							'compRes' : R.TH1F('compRes_'+str(CHAM)+'_'+str(MEAS),'',100,-1,1)
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
							alreadyMatchedComp = []
							alreadyMatchedSeg = []
							for lct in lcts:
								# Check on chamber and LCT position
								if lct.cham!=CHAM: continue
								if not Aux.inPad(lct.keyHalfStrip,lct.keyWireGroup,lct.cham): continue
								found, seg = Aux.bestSeg(lct,segs)
								if not found: continue
								rhList = seg.rhID
								for rhID in rhList:
									# Check on chamber
									if rechits[rhID].cham!=lct.cham: continue
									for c,comp in enumerate(comps):
										# Check on chamber, layer, matching comp to rechit, and if we've already matched the comparator
										if comp.cham!=rechits[rhID].cham: continue
										if comp.layer!=rechits[rhID].layer: continue
										if not self.matchRHComp(rechits[rhID],comp): continue
										if c in alreadyMatchedComp: continue
										alreadyMatchedComp.append(c)
										# Add 1/2 to comparator half strip to align it with rec hit
										# Divide by 2 to get it in strip units
										DIFF = float((rechits[rhID].halfStrip - comp.halfStrip+0.5)*0.5)
										# multiply by -1 because all of Cam's plots are comp-RH
										if CHAM==1: 
											self.hists[1][MEAS]['compRes'].Fill(-1.*DIFF)
										if CHAM==110:
											self.hists[110][MEAS]['compRes'].Fill(-1.*DIFF)
										# Break out of the comparator loop since we've already found the matching comparator to the rechit
										break

					for CHAM in CHAMLIST:
						# Make histogram
						self.makeHist(self.hists[CHAM][MEAS]['compRes'],MEAS,CHAM,att,self.lumi(CHAM,MEAS),ff)
						# fill dictionary
						self.compMean[CHAM][MEAS] = self.hists[CHAM][MEAS]['compRes'].GetMean()
						self.compRes[CHAM][MEAS] = self.hists[CHAM][MEAS]['compRes'].GetStdDev()

					print MEAS,
					print self.compMean[1][MEAS], self.compRes[1][MEAS],
					print self.compMean[110][MEAS], self.compRes[110][MEAS]
		else:
			# this file is the output of the printout above
			f = open(fromFile)
			for line in f:
				cols = line.strip('\n').split()
				MEAS = int(cols[0])
				self.compMean[1][MEAS] = float(cols[1])
				self.compRes[1][MEAS] = float(cols[2])
				self.compMean[110][MEAS] = float(cols[3])
				self.compRes[110][MEAS] = float(cols[4])

	# a rechit/comparator match is if the comparator halfstrip is within 2 strips of the comparator halfstrip
	def matchRHComp(self, rh, comp):
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
		plot = Plotter.Plot(hist, '', option='hist')

		# Step 2
		ATT = str(int(att)) if str(att)!='inf' else 'NS'
		canvas = Plotter.Canvas('ME'+str(CHAM)+'/1, Ext. Trig., %2.1f'%(lumi)+'#times10^{33} Hz/cm^{2} ('+ATT+')', False, 0., '', 800, 600)

		# Step 3
		canvas.makeLegend()

		# Step 4
		canvas.addMainPlot(plot, True, False)

		# Step 5
		R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
		hist.GetYaxis().SetTitle('Counts')
		hist.GetXaxis().SetTitle('Comparator Resolution [strips]')
		hist.SetMinimum(0.0)
		hist.SetFillColor(R.kBlue)
		plot.scaleTitles(0.8)
		plot.scaleLabels(0.8)

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

		canvas.makeTransparent()

		# Step 6

		# Step 7

		# Step 8
		canvas.finishCanvas()
		canvas.c.SaveAs('resPlots/compRes_'+str(CHAM)+'1_'+str(meas)+'.pdf')
		R.SetOwnership(canvas.c, False)



data = MegaStruct(f_measgrid, f_attenhut, fromFile, castrated)

### MAKEPLOT FUNCTION
def makePlot(x, y,cham, xtitle, ytitle, title, RES=False,pretty=pretty):
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

	CHAM = 2 if cham==110 else 1
	graphs = []
	ntypes = len(pretty.keys())
	for i in range(ntypes):
		graphs.append(R.TGraph(len(x[i]), x[i], y[i]))

	# Step 1
	plots = []
	for i,p in enumerate(pretty.keys()):
		plots.append(Plotter.Plot(graphs[i], pretty[p]['name'], 'pe', 'APE' if i==0 else 'PE'))

	# Step 2
	canvas = Plotter.Canvas('ME'+str(CHAM)+'/1 External Trigger', False, 0., 'Internal', 800, 700)

	# Step 3
	canvas.makeLegend(.2,0.25,'br',0.04, 0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i], i==0, True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	graphs[0].GetYaxis().SetTitle(ytitle)
	graphs[0].GetXaxis().SetTitle(xtitle)
	if RES:
		graphs[0].SetMinimum(0.0)
		graphs[0].SetMaximum(0.3)
	else:
		graphs[0].SetMinimum(-0.1)
		graphs[0].SetMaximum(0.1)
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
	canvas.c.SaveAs('resPlots/comp_'+str(CHAM)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

### MAKE ALL PLOTS
for cham in chamlist:
	# Plots with current on x-axis
	makePlot(\
			[data.currentVector(cham, ff) for ff in pretty.keys()],
			[data.resVector(cham, ff) for ff in pretty.keys()],
			cham,
			'Mean Current [#muA]',
			'Comparator Resolution [strip]',
			'res_curr',
			RES=True
			)
	# Plots with luminosity on x-axis
	makePlot(\
			[data.lumiVector(cham, ff) for ff in pretty.keys()],
			[data.resVector(cham, ff) for ff in pretty.keys()],
			cham,
			'Luminosity [Hz/cm^{2}]',
			'Comparator Resolution [strip]',
			'res_lumi',
			RES=True
			)
	# Plots with 1/A on x-axis
	makePlot(\
			[np.reciprocal(data.attVector()) for ff in pretty.keys()],
			[data.resVector(cham, ff) for ff in pretty.keys()],
			cham,
			'Source Intensity 1/A',
			'Comparator Resolution [strip]',
			'res_att',
			RES=True
			)
	# Plots with current on x-axis
	makePlot(\
			[data.currentVector(cham, ff) for ff in pretty.keys()],
			[data.meanVector(cham, ff) for ff in pretty.keys()],
			cham,
			'Mean Current [#muA]',
			'Comparator Bias [strip]',
			'mean_curr'
			)
	# Plots with luminosity on x-axis
	makePlot(\
			[data.lumiVector(cham, ff) for ff in pretty.keys()],
			[data.meanVector(cham, ff) for ff in pretty.keys()],
			cham,
			'Luminosity [Hz/cm^{2}]',
			'Comparator Bias [strip]',
			'mean_lumi'
			)
	# Plots with 1/A on x-axis
	makePlot(\
			[np.reciprocal(data.attVector()) for ff in pretty.keys()],
			[data.meanVector(cham, ff) for ff in pretty.keys()],
			cham,
			'Source Intensity 1/A',
			'Comparator Bias [strip]',
			'mean_att'
			)
