import numpy as np
import Gif.TestBeamAnalysis.Plotter as Plotter
import ROOT as R
import sys

### PARAMETERS
# Which chambers to do; to compare to Yuriy only use ME1/1
# chamlist = [1]
chamlist = [1, 2]

# Which files contain the relevant list of measurements and currents
f_measgrid = '../datafiles/measgrid'
f_attenhut = '../datafiles/attenhut'

# Whether or not to only use Yuriy's 5 attenuations
castrated = False

# Whether or not to get the data from a file. None if not; filename if so.
#fromFile = None
fromFile = '../datafiles/old_efftable'

# Which efficiency to plot: 'all', 'pad', or 'seg'
efftype = 'seg'

# Additional filename
title2 = 'seg'

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
		if fromFile is None:
			print "\033[4mMeas  L1As  LCT1  Pad1  Seg1  LCT2  Pad2  Seg2\033[m"
			for att in self.FFFMeas.keys():
				for meas in self.FFFMeas[att]:
					f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/TestBeam5/ana_'+str(meas)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')
					nLCT_11 = 0
					nLCT_21 = 0
					nPaddle_11 = 0
					nPaddle_21 = 0
					nSegMatch_11 = 0
					nSegMatch_21 = 0
					for entry in t:
						# Count number of entries with at least one LCT
						# ID for ME1/1/GIF = 1
						if list(t.lct_id).count(1)>0: nLCT_11 = nLCT_11 + 1
						# ID for ME2/1/GIF = 110
						if list(t.lct_id).count(110)>0: nLCT_21 = nLCT_21 + 1

						# Count number of entries inside paddle and number of entries inside paddle with matching segment
						# Booleans
						Seg1 = False
						Seg2 = False
						Pad1 = False
						Pad2 = False
						# list of indices of lcts
						i1 = [i for i,x in enumerate(list(t.lct_id)) if x == 1]
						i2 = [i for i,x in enumerate(list(t.lct_id)) if x == 110]
						# list of rechit strips in STRIP units
						rhs1 = [ord(list(t.rh_strip_1)[rhsi]) for i,rhsi in enumerate(list(t.segment_recHitIdx_3)) if t.segment_id[i] == 1]
						rhs2 = [ord(list(t.rh_strip_1)[rhsi]) for i,rhsi in enumerate(list(t.segment_recHitIdx_3)) if t.segment_id[i] == 110]
						# check if the lct is in the paddle and if so, if there is a matching segment strip
						for i in i1:
							if not self.inPad(t.lct_keyHalfStrip[i], t.lct_keyWireGroup[i], 1): continue
							Pad1 = True
							if not self.matchedSeg(rhs1, t.lct_keyHalfStrip[i]): continue
							Seg1 = True
						for i in i2:
							if not self.inPad(t.lct_keyHalfStrip[i], t.lct_keyWireGroup[i], 2): continue
							Pad2 = True
							if not self.matchedSeg(rhs2, t.lct_keyHalfStrip[i]): continue
							Seg2 = True
						if Pad1: nPaddle_11 += 1
						if Pad2: nPaddle_21 += 1
						if Seg1: nSegMatch_11 += 1
						if Seg2: nSegMatch_21 += 1

					# printout
					nTot = t.GetEntries()
					print '%4i %5i %5i %5i %5i %5i %5i %5i' % (\
							meas,
							nTot,
							nLCT_11,
							nPaddle_11,
							nSegMatch_11,
							nLCT_21,
							nPaddle_21,
							nSegMatch_21
						)
					sys.stdout.flush()

					# fill dictionary
					self.Effs[1][meas] = [float(nLCT_11)/float(nTot), float(nPaddle_11)/float(nTot), float(nSegMatch_11)/float(nTot)]
					self.Effs[2][meas] = [float(nLCT_21)/float(nTot), float(nPaddle_21)/float(nTot), float(nSegMatch_21)/float(nTot)]
		else:
			# this file is the output of the printout above
			f = open(fromFile)
			for line in f:
				cols = line.strip('\n').split()

				meas         = int(cols[0])
				nTot         = int(cols[1])
				nLCT_11      = int(cols[2])
				nPaddle_11   = int(cols[3])
				nSegMatch_11 = int(cols[4])
				nLCT_21      = int(cols[5])
				nPaddle_21   = int(cols[6])
				nSegMatch_21 = int(cols[7])

				self.Effs[1][meas] = [float(nLCT_11)/float(nTot), float(nPaddle_11)/float(nTot), float(nSegMatch_11)/float(nTot)]
				self.Effs[2][meas] = [float(nLCT_21)/float(nTot), float(nPaddle_21)/float(nTot), float(nSegMatch_21)/float(nTot)]

	# defines a paddle region
	def inPad(self, hs, wg, cham):
		if cham == 1:
			if      ord(hs) >=  25\
				and ord(hs) <=  72\
				and ord(wg) >=  37\
				and ord(wg) <=  43:
				return True
			else:
				return False
		if cham == 2:
			if      ord(hs) >=   8\
				and ord(hs) <=  38\
				and ord(wg) >=  55\
				and ord(wg) <=  65:
				return True
			else:
				return False
	
	# a segment match is if the lct halfstrip/2 is within 1 of the rechit strip
	def matchedSeg(self, rhs, khs):
		diff = [abs(i-ord(khs)/2) for i in rhs]
		if 0 in diff or 1 in diff:
			return True
		else:
			return False

	# get a current measurement given a chamber and measurement number
	def current(self, cham, meas):
		if cham == 1:
			return sum(self.Currs[cham][meas])/6.0
		elif cham == 2:
			return sum(self.Currs[cham][meas][6:12])/6.0
	
	# get an efficiency value given a chamber, measurement number, and efftype
	def eff(self, cham, meas, name='all'):
		if name == 'all':
			idx = 0
		elif name == 'pad':
			idx = 1
		elif name == 'seg':
			idx = 2
		else:
			raise ValueError('Invalid efficiency type: options are \'all\', \'pad\', or \'seg\'.')
		return self.Effs[cham][meas][idx]

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

	# get a vector of efficiencies
	def effVector(self, cham, ff, name='all'):
		return np.array([self.eff(cham, self.FFFMeas[att][ff], name) for att in self.attVector()])

	# get a vector of efficiencies normalized to Original
	def normEffVector(self, cham, ff, name='all'):
		return np.array([self.eff(cham, self.FFFMeas[att][ff], name)/self.eff(cham, self.FFFMeas[att][0], name) for att in self.attVector()])

data = MegaStruct(f_measgrid, f_attenhut, fromFile, castrated)

### MAKEPLOT FUNCTION
def makePlot(x, y, cham, xtitle, ytitle, title, pretty=pretty):
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
		graphs.append(R.TGraph(len(x[i]), x[i], y[i]))

	# Step 1
	plots = []
	for i,p in enumerate(pretty.keys()):
		plots.append(Plotter.Plot(graphs[i], pretty[p]['name'], 'p', 'AP' if i==0 else 'P'))

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
		graphs[i].SetMarkerSize(2.2)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/LCT_'+str(cham)+'1_'+title+'_'+title2+'.pdf')
	R.SetOwnership(canvas.c, False)

### MAKE ALL PLOTS
for cham in chamlist:
	# Plots with current on x-axis
	makePlot(\
			[data.currentVector(cham, ff) for ff in pretty.keys()],
			[data.effVector(cham, ff, efftype) for ff in pretty.keys()],
			cham,
			'Mean Current [#muA]',
			'LCT Efficiency',
			'curr'
			)
	# Normalized to 'Original'
	makePlot(\
			[data.currentVector(cham, ff) for ff in pretty.keys()],
			[data.normEffVector(cham, ff, efftype) for ff in pretty.keys()],
			cham,
			'Mean Current [#muA]',
			'LCT Efficiency',
			'curr_norm'
			)
	# Plots with luminosity on x-axis
	makePlot(\
			[data.lumiVector(cham, ff) for ff in pretty.keys()],
			[data.effVector(cham, ff, efftype) for ff in pretty.keys()],
			cham,
			'Luminosity [Hz/cm^{2}]',
			'LCT Efficiency',
			'lumi'
			)
	# Normalized to 'Original'
	makePlot(\
			[data.lumiVector(cham, ff) for ff in pretty.keys()],
			[data.normEffVector(cham, ff, efftype) for ff in pretty.keys()],
			cham,
			'Luminosity [Hz/cm^{2}]',
			'LCT Efficiency',
			'lumi_norm'
			)
	# Plots with 1/A on x-axis
	makePlot(\
			[np.reciprocal(data.attVector()) for ff in pretty.keys()],
			[data.effVector(cham, ff, efftype) for ff in pretty.keys()],
			cham,
			'Source Intensity 1/A',
			'LCT Efficiency',
			'att'
			)
	# Normalized to 'Original'
	makePlot(\
			[np.reciprocal(data.attVector()) for ff in pretty.keys()],
			[data.normEffVector(cham, ff, efftype) for ff in pretty.keys()],
			cham,
			'Source Intensity 1/A',
			'LCT Efficiency',
			'att_norm'
			)
