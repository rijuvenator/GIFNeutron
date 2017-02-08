import numpy as np
import Gif.TestBeamAnalysis.Plotter as Plotter
import ROOT as R

### PARAMETERS
# Which chambers to do
chamlist = [1]

# Which files contain the relevant list of measurements and currents
f_measgrid = '../datafiles/measgrid_Y'
f_attenhut = '../datafiles/attenhut_Y'

# Dictionary containing cosmetic data, comment out for fewer ones
pretty = {
	0 : { 'name' : 'Original',  'color' : R.kRed-3,   'marker' : R.kFullCircle      },
	1 : { 'name' : 'Algo0'   ,  'color' : R.kBlue-1,  'marker' : R.kFullSquare      },
	2 : { 'name' : 'Algo1'   ,  'color' : R.kOrange,  'marker' : R.kFullTriangleUp  },
	3 : { 'name' : 'Algo2'   ,  'color' : R.kGreen+2, 'marker' : R.kFullCross       },
	4 : { 'name' : 'Algo3'   ,  'color' : R.kMagenta, 'marker' : R.kFullTriangleDown},
	5 : { 'name' : 'Algo4'   ,  'color' : R.kAzure+8, 'marker' : R.kFullDiamond     },
}

R.gROOT.SetBatch(True)

###############################################################################################
### BEGIN CODE
### DATA STRUCTURE CLASS
class MegaStruct():
	def __init__(self,measgrid,attenhut):

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

		# Fill dictionary connecting chamber and measurement number to efficiency value
		self.Effs = { 1 : {}, 2 : {} }
		for att in self.FFFMeas.keys():
			for meas in self.FFFMeas[att]:
				f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/TestBeam5/ana_'+str(meas)+'.root')
				t = f.Get('GIFTree/GIFDigiTree')
				nLCT_11 = 0
				nLCT_21 = 0
				# Count number of entries with at least one LCT
				for entry in t:
					# ID for ME1/1/GIF = 1
					if list(t.lct_id).count(1)>0: nLCT_11 = nLCT_11 + 1
					# ID for ME2/1/GIF = 110
					if list(t.lct_id).count(110)>0: nLCT_21 = nLCT_21 + 1

				nTot = t.GetEntries()
				print '%4i %5i %5i %5i' % (meas, nLCT_11, nLCT_21, nTot)

				self.Effs[1][meas] = float(nLCT_11)/float(nTot)
				self.Effs[2][meas] = float(nLCT_21)/float(nTot)

	# get a current measurement given a chamber and measurement number
	def current(self, cham, meas):
		if cham == 1:
			return sum(self.Currs[cham][meas])/6.0
		elif cham == 2:
			return sum(self.Currs[cham][meas][6:12])/6.0
	
	# get an efficiency value given a chamber, measurement number, and efftype
	def eff(self, cham, meas):
		return self.Effs[cham][meas]

	# get a vector of attenuations
	def attVector(self):
		return np.array(sorted(self.FFFMeas.keys()))

	# get a vector of currents
	def currentVector(self, cham, ff):
		return np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	# get a vector of equivalent luminosities
	def lumiVector(self, cham, ff):
		factor = 5.e33 if cham == 2 else 3.e33
		return factor * np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	# get a vector of efficiencies
	def effVector(self, cham, ff):
		return np.array([self.eff(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	# get a vector of efficiencies normalized to Original
	def normEffVector(self, cham, ff):
		return np.array([self.eff(cham, self.FFFMeas[att][ff])/self.eff(cham, self.FFFMeas[att][0]) for att in self.attVector()])

data = MegaStruct(f_measgrid, f_attenhut)

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

	for i,p in enumerate(pretty.keys()):
		graphs[i].SetMarkerColor(pretty[p]['color'])
		graphs[i].SetMarkerStyle(pretty[p]['marker'])
		graphs[i].SetMarkerSize(2.2)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/LCT_'+str(cham)+'1_'+title+'_Y.pdf')
	R.SetOwnership(canvas.c, False)

### MAKE ALL PLOTS
for cham in chamlist:
	# Plots with current on x-axis
	makePlot(\
		[data.currentVector(cham, ff) for ff in pretty.keys()],
		[data.effVector(cham, ff) for ff in pretty.keys()],
		cham,
		'Mean Current [#muA]',
		'LCT Efficiency',
		'curr'
	)
	# Normalized to 'Original'
	makePlot(\
		[data.currentVector(cham, ff) for ff in pretty.keys()],
		[data.normEffVector(cham, ff) for ff in pretty.keys()],
		cham,
		'Mean Current [#muA]',
		'LCT Efficiency',
		'curr_norm'
		)
	# Plots with luminosity on x-axis
	makePlot(\
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.effVector(cham, ff) for ff in pretty.keys()],
		cham,
		'Luminosity [Hz/cm^{2}]',
		'LCT Efficiency',
		'lumi'
	)
	# Normalized to 'Original'
	makePlot(\
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.normEffVector(cham, ff) for ff in pretty.keys()],
		cham,
		'Luminosity [Hz/cm^{2}]',
		'LCT Efficiency',
		'lumi_norm'
	)
	# Plots with 1/A on x-axis
	makePlot(\
		[np.reciprocal(data.attVector()) for ff in pretty.keys()],
		[data.effVector(cham, ff) for ff in pretty.keys()],
		cham,
		'Source Intensity 1/A',
		'LCT Efficiency',
		'att'
	)
	# Normalized to 'Original'
	makePlot(\
		[np.reciprocal(data.attVector()) for ff in pretty.keys()],
		[data.normEffVector(cham, ff) for ff in pretty.keys()],
		cham,
		'Source Intensity 1/A',
		'LCT Efficiency',
		'att_norm'
	)
