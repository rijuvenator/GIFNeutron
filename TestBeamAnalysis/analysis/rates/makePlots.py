import sys
import numpy as np
import Gif.TestBeamAnalysis.Plotter as Plotter
import ROOT as R

R.gROOT.SetBatch(True)

# PARAMETERS
chamlist = [1, 2]
f_measgrid = 'measgrid'
f_attenhut = 'attenhut'
#cham = int(sys.argv[1])
#numer = sys.argv[2]
#denom = None if sys.argv[3] == 'None' else sys.argv[3]
#logy = True if sys.argv[4] == '1' else False

#quants = ['CFEB Sum', 'CLCT0', 'CLCT1', 'ALCT0', 'ALCT1', 'ALCT*CLCT', 'L1A']
pretty = {
    0:['Original',        R.kRed-3,   R.kFullCircle],
    1:['TightPreCLCT',    R.kBlue-1,  R.kFullSquare],
    2:['TightCLCT',       R.kOrange,  R.kFullTriangleUp],
    3:['TightALCT',       R.kGreen+2, R.kFullCross],
    4:['TightPrePID',     R.kMagenta, R.kFullTriangleDown],
    5:['TightPrePostPID', R.kAzure+8, R.kFullDiamond],
    6:['TightPA',         R.kGray,    R.kFullStar],
    7:['TightAll',        R.kBlack,   R.kFullCircle]
}

class MegaStruct():
	def __init__(self,measgrid,attenhut):
		f = open(measgrid)
		self.FFFMeas = {}
		for line in f:
			cols = line.strip('\n').split()
			self.FFFMeas[float(cols[0])] = [int(j) for j in cols[1:]]
		f.close()

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

		f = open('trigdata')
		self.Regs = { 1 : {}, 2 : {} }
		currentMeas = 0
		for line in f:
			if line == '\n':
				continue
			elif '---' in line:
				continue
			else:
				cols = line.strip('\n').split()
				currentCham = int(cols[1])
				if int(cols[0]) != currentMeas:
					currentMeas = int(cols[0])
					self.Regs[1][currentMeas] = []
					self.Regs[2][currentMeas] = []
				self.Regs[currentCham][currentMeas].append([float(i) for i in cols[2:]])
		f.close()
	
	def current(self, cham, meas):
		if cham == 1:
			return sum(self.Currs[cham][meas])/6.0
		elif cham == 2:
			return sum(self.Currs[cham][meas][6:12])/6.0
	
	def register(self, cham, meas, name, dump=0):
		if dump == 'all':
			if name == 'CFEB Sum':
				x = [sum(z[2:9]) for z in self.Regs[cham][meas][:]]
			elif name == 'ALCT0':
				x = [z[0] for z in self.Regs[cham][meas][:]]
			elif name == 'ALCT1':
				x = [z[1] for z in self.Regs[cham][meas][:]]
			elif name == 'CLCT0':
				x = [z[9] for z in self.Regs[cham][meas][:]]
			elif name == 'CLCT1':
				x = [z[10] for z in self.Regs[cham][meas][:]]
			elif name == 'ALCT*CLCT':
				x = [z[11] for z in self.Regs[cham][meas][:]]
			elif name == 'L1A':
				x = [z[12] for z in self.Regs[cham][meas][:]]
			elif name == 'Duration':
				x = [z[13] for z in self.Regs[cham][meas][:]]
			x = np.array(x)
			return x.mean()
		else:
			if name == 'CFEB Sum':
				return sum(self.Regs[cham][meas][dump][2:9])
			elif name == 'ALCT0':
				return self.Regs[cham][meas][dump][0]
			elif name == 'ALCT1':
				return self.Regs[cham][meas][dump][1]
			elif name == 'CLCT0':
				return self.Regs[cham][meas][dump][9]
			elif name == 'CLCT1':
				return self.Regs[cham][meas][dump][10]
			elif name == 'ALCT*CLCT':
				return self.Regs[cham][meas][dump][11]
			elif name == 'L1A':
				return self.Regs[cham][meas][dump][12]
			elif name == 'Duration':
				return self.Regs[cham][meas][dump][13]
	
	def attVector(self):
		return np.array(sorted(self.FFFMeas.keys()))
	
	def currentVector(self, cham, ff):
		return np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	def lumiVector(self, cham, ff):
		factor = 5.e33 if cham == 2 else 3.e33
		return factor * np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	def regVector(self, cham, ff, name):
		return np.array([self.register(cham, self.FFFMeas[att][ff], name) for att in self.attVector()])

data = MegaStruct(f_measgrid, f_attenhut)

def makePlot(x, y, ytit, fn, extra, logy, norm=None, pretty=pretty):
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

	ntypes = len(pretty.keys())

	ry = np.array(y)
	yrange = [(ry/norm).min(), (ry/norm).max()] if norm is not None else [ry.min(), ry.max()]
	#yrange[1] = 0.6 / (1 if '2' in extra else 2)

	graphs = []
	if norm is None:
		for i in range(ntypes):
			graphs.append(R.TGraph(len(x[i][0:]), x[i][0:], y[i][0:]))
	else:
		for i in range(ntypes):
			graphs.append(R.TGraph(len(x[i][0:]), x[i][0:], y[i][0:]/norm[i][0:]))

	# Step 1
	plots = []
	for i in range(ntypes):
		plots.append(Plotter.Plot(graphs[i], pretty[i][0], 'p', 'AP' if i==0 else 'P'))

	# Step 2
	canvas = Plotter.Canvas(extra, logy, 0., "Internal", 800, 700)

	# Step 3
	canvas.makeLegend(.2,.25,'tl',0.04, 0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i], i==0, True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
#	canvas.mainPad.SetLogx(True)

	graphs[0].GetYaxis().SetTitleOffset(graphs[0].GetYaxis().GetTitleOffset()*1.4)
	graphs[0].GetYaxis().SetTitle(ytit)
	graphs[0].GetXaxis().SetTitle('Mean Current [#muA]')
	graphs[0].SetMinimum(yrange[0]*0.8)
	graphs[0].SetMaximum(yrange[1]*1.2)
	plots[0].scaleTitles(0.8)
	plots[0].scaleLabels(0.8)

    for i,p in enumerate(pretty.keys()):
        graphs[i].SetMarkerColor(pretty[i][1])
        graphs[i].SetMarkerStyle(pretty[i][2])
        graphs[i].SetMarkerSize(2.2)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs(fn)
	R.SetOwnership(canvas.c, False)

for cham in chamlist:
	for numer, denom, logy in [\
			('ALCT*CLCT','L1A',False),
			('CFEB Sum',None,True),
			('ALCT0','L1A',True),
			('CLCT0','L1A',False),
			('L1A',None,False)
			]:
		makePlot(\
				[data.currentVector(cham, ff) for ff in pretty.keys()],
				[data.regVector(cham, ff, numer) for ff in pretty.keys()],
				numer + ('' if denom is None else '/'+denom),
				'pdfs/me'+str(cham)+'1-'+numer+('' if denom is not None else '-N')+'.pdf',
				'ME'+str(cham)+'/1',
				logy,
				#norm = None if denom is None else [data.regVector(cham, ff, denom)*data.regVector(cham, ff, 'Duration') for ff in pretty.keys()]
				#norm = [(1 if denom is None else data.regVector(cham, ff, denom))*data.regVector(cham, ff, 'Duration') for ff in pretty.keys()]
				norm = None if denom is None else [data.regVector(cham, ff, denom) for ff in pretty.keys()]
				)
