import numpy as np
import Gif.TestBeamAnalysis.Plotter as Plotter
import ROOT as R

R.gROOT.SetBatch(True)

### PARAMETERS
chamlist = [1]#, 2]
f_measgrid = 'measgrid_Y'
f_attenhut = 'attenhut_Y'

doEff = True
doCount = True
ymax = 30.0
Lloc = 'tl'
# Directory to store plots
where = 'yuiry'
# track = 'LCT' or 'CLCT' or 'ALCT' or 'comp' or 'wg' or 'segment' or 'strip'
track = 'wg'
# Description of which set of measurements to be plotted
title2 = 'Y'
pretty = {
		0 : { 'name' : 'Original',  'color' : R.kRed-3,   'marker' : R.kFullCircle      },
		1 : { 'name' : 'Algo0'   ,  'color' : R.kBlue-1,  'marker' : R.kFullSquare      },
		2 : { 'name' : 'Algo1'   ,  'color' : R.kOrange,  'marker' : R.kFullTriangleUp  },
		3 : { 'name' : 'Algo2'   ,  'color' : R.kGreen+2, 'marker' : R.kFullCross       },
		4 : { 'name' : 'Algo3'   ,  'color' : R.kMagenta, 'marker' : R.kFullTriangleDown},
		5 : { 'name' : 'Algo4'   ,  'color' : R.kAzure+8, 'marker' : R.kFullDiamond     },
}

### DATA STRUCTURE CLASS
class MegaStruct():
	def __init__(self,measgrid,attenhut):
		f = open(measgrid)
		self.FFFMeas = {}
		for line in f:
			cols = line.strip('\n').split()
			self.FFFMeas[float(cols[0])] = [int(j) for j in cols[1:]]
		f.close()

		f = open(attenhut)
		self.Currs = { 1 : {}}
		currentCham = 1
		for line in f:
			cols = line.strip('\n').split()
			currentMeas = int(cols[1])
			self.Currs[currentCham][currentMeas] = [float(i) for i in cols[2:]]
		f.close()

		self.Effs = { 1 : {}}
		self.nCount = { 1 : {}}
		for att in self.FFFMeas.keys():
			for meas in self.FFFMeas[att]:
				f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/TestBeam5/ana_'+str(meas)+'.root')
				t = f.Get('GIFTree/GIFDigiTree')
				nTrack_11 = 0
				nCount_11 = 0
				# Count number of entries with at least one LCT
				# ID for ME1/1/GIF = 1
				for entry in t:
					if track == 'LCT':
						if list(t.lct_id).count(1)>0: nTrack_11 = nTrack_11 + 1
					elif track == 'CLCT':
						if list(t.clct_id).count(1)>0: nTrack_11 = nTrack_11 + 1
					elif track == 'ALCT':
						if list(t.alct_id).count(1)>0: nTrack_11 = nTrack_11 + 1
					elif track == 'comp':
						if list(t.comp_id).count(1)>0: nTrack_11 = nTrack_11 + 1
						if doCount:
							nCount_11 = nCount_11 + list(t.comp_id).count(1)
					elif track == 'wg':
						if list(t.wire_id).count(1)>0: nTrack_11 = nTrack_11 + 1
						if doCount:
							nCount_11 = nCount_11 + list(t.wire_id).count(1)
					elif track == 'segment':
						if list(t.segment_id).count(1)>0: nTrack_11 = nTrack_11 + 1
						if doCount:
							nCount_11 = nCount_11 + list(t.segment_id).count(1)
					elif track == 'strip':
						if list(t.strip_id).count(1)>0: nTrack_11 = nTrack_11 + 1
						if doCount:
							nCount_11 = nCount_11 + list(t.strip_id).count(1)


				nTot = t.GetEntries()

				print meas
				self.Effs[1][meas] = float(nTrack_11)/float(nTot)
				print '     %s %6i %5i' % ('Eff  ', nTrack_11, nTot)
				if doCount:
					self.nCount[1][meas] = float(nCount_11)/float(nTrack_11)
					print '     %s %6i %5i' % ('Count', nCount_11, nTot)



	def current(self, cham, meas):
		if cham == 1:
			return sum(self.Currs[cham][meas])/6.0
	
	def eff(self, cham, meas):
		return self.Effs[cham][meas]
	def effVector(self, cham, ff):
		return np.array([self.eff    (cham, self.FFFMeas[att][ff]) for att in self.attVector()])
	def normEffVector(self, cham, ff):
		return np.array([self.eff    (cham, self.FFFMeas[att][ff])/self.eff(cham, self.FFFMeas[att][0]) for att in self.attVector()])

	if doCount:
		def nTrig(self, cham, meas):
			return self.nCount[cham][meas]
		def TrigVector(self, cham, ff):
			return np.array([self.nTrig(cham, self.FFFMeas[att][ff]) for att in self.attVector()])
		def normTrigVector(self, cham, ff):
			return np.array([self.nTrig(cham, self.FFFMeas[att][ff])/self.nTrig(cham, self.FFFMeas[att][0]) for att in self.attVector()])

	def attVector(self):
		return np.array(sorted(self.FFFMeas.keys()))
	def currentVector(self, cham, ff):
		return np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])
	def lumiVector(self, cham, ff):
		factor = 5.e33 if cham == 2 else 3.e33
		return factor * np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

data = MegaStruct(f_measgrid, f_attenhut)

### MAKEPLOT FUNCTION
def makePlot(x, y, cham, xtitle, ytitle, title0, title1, pretty=pretty, ylims=[0.0,1.1], loc='bl'):
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
	canvas.makeLegend(.2,0.25,loc,0.04, 0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i], i==0, True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	graphs[0].GetYaxis().SetTitle(ytitle)
	graphs[0].GetXaxis().SetTitle(xtitle)
	graphs[0].SetMinimum(ylims[0])
	graphs[0].SetMaximum(ylims[1])
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
	canvas.c.SaveAs(where+'/'+title0+'_'+str(cham)+'1_'+title1+'_'+title2+'.pdf')
	R.SetOwnership(canvas.c, False)

### MAKE ALL PLOTS
for cham in chamlist:
	if doEff==True:
		# Plots with current on x-axis
		makePlot(\
				[data.currentVector(cham, ff) for ff in pretty.keys()],
				[data.effVector(cham, ff) for ff in pretty.keys()],
				cham,
				'Mean Current [#muA]',
				track+' Efficiency',
				'Eff'+track,
				'curr'
				)
		# Normalized to 'Original'
		makePlot(\
				[data.currentVector(cham, ff) for ff in pretty.keys()],
				[data.normEffVector(cham, ff) for ff in pretty.keys()],
				cham,
				'Mean Current [#muA]',
				track+' Efficiency',
				'Eff'+track,
				'curr_norm'
				)
		# Plots with luminosity on x-axis
		makePlot(\
				[data.lumiVector(cham, ff) for ff in pretty.keys()],
				[data.effVector(cham, ff) for ff in pretty.keys()],
				cham,
				'Luminosity [Hz/cm^{2}]',
				track+' Efficiency',
				'Eff'+track,
				'lumi'
				)
		# Normalized to 'Original'
		makePlot(\
				[data.lumiVector(cham, ff) for ff in pretty.keys()],
				[data.normEffVector(cham, ff) for ff in pretty.keys()],
				cham,
				'Luminosity [Hz/cm^{2}]',
				track+' Efficiency',
				'Eff'+track,
				'lumi_norm'
				)
		# Plots with 1/A on x-axis
		makePlot(\
				[np.reciprocal(data.attVector()) for ff in pretty.keys()],
				[data.effVector(cham, ff) for ff in pretty.keys()],
				cham,
				'Source Intensity 1/A',
				track+' Efficiency',
				'Eff'+track,
				'att'
				)
		# Normalized to 'Original'
		makePlot(\
				[np.reciprocal(data.attVector()) for ff in pretty.keys()],
				[data.normEffVector(cham, ff) for ff in pretty.keys()],
				cham,
				'Source Intensity 1/A',
				track+' Efficiency',
				'Eff'+track,
				'att_norm'
				)
	if doCount:
		# Plots with current on x-axis
		makePlot(\
				[data.currentVector(cham, ff) for ff in pretty.keys()],
				[data.TrigVector(cham, ff) for ff in pretty.keys()],
				cham,
				'Mean Current [#muA]',
				'<N('+track+'s)>',
				'N'+track,
				'curr',
				ylims=[0.0,ymax],
				loc = Lloc
				)
		# Normalized to 'Original'
		makePlot(\
				[data.currentVector(cham, ff) for ff in pretty.keys()],
				[data.normTrigVector(cham, ff) for ff in pretty.keys()],
				cham,
				'Mean Current [#muA]',
				'<N('+track+'s)>',
				'N'+track,
				'curr_norm',
				)
		# Plots with luminosity on x-axis
		makePlot(\
				[data.lumiVector(cham, ff) for ff in pretty.keys()],
				[data.TrigVector(cham, ff) for ff in pretty.keys()],
				cham,
				'Luminosity [Hz/cm^{2}]',
				'<N('+track+'s)>',
				'N'+track,
				'lumi',
				ylims=[0.0,ymax],
				loc = Lloc
				)
		# Normalized to 'Original'
		makePlot(\
				[data.lumiVector(cham, ff) for ff in pretty.keys()],
				[data.normTrigVector(cham, ff) for ff in pretty.keys()],
				cham,
				'Luminosity [Hz/cm^{2}]',
				'<N('+track+'s)>',
				'N'+track,
				'lumi_norm',
				)
		# Plots with 1/A on x-axis
		makePlot(\
				[np.reciprocal(data.attVector()) for ff in pretty.keys()],
				[data.TrigVector(cham, ff) for ff in pretty.keys()],
				cham,
				'Source Intensity 1/A',
				'<N('+track+'s)>',
				'N'+track,
				'att',
				ylims=[0.0,ymax],
				loc = Lloc
				)
		# Normalized to 'Original'
		makePlot(\
				[np.reciprocal(data.attVector()) for ff in pretty.keys()],
				[data.normTrigVector(cham, ff) for ff in pretty.keys()],
				cham,
				'Source Intensity 1/A',
				'<N('+track+'s)>',
				'N'+track,
				'att_norm'
				)
