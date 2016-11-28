import numpy as np
import Gif.TestBeamAnalysis.Plotter as Plotter
import ROOT as R

R.gROOT.SetBatch(True)

### PARAMETERS
chamlist = [1, 2]
f_measgrid = 'measgrid'
f_attenhut = 'attenhut'

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
		if dump == 'all' or dump == 'sum':
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
			elif name == 'Window':
				x = [z[14] for z in self.Regs[cham][meas][:]]
			x = np.array(x)
			if dump == 'all':
				return x.mean()
			elif dump == 'sum':
				return x.sum()
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
			elif name == 'Window':
				return self.Regs[cham][meas][dump][14]
	
	def attVector(self):
		return np.array(sorted(self.FFFMeas.keys()))[1:]

	def currentVector(self, cham, ff):
		return np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	def lumiVector(self, cham, ff):
		factor = 5.e33 if cham == 2 else 3.e33
		return factor * np.array([self.current(cham, self.FFFMeas[att][ff]) for att in self.attVector()])

	def regVector(self, cham, ff, name):
		return np.array([self.register(cham, self.FFFMeas[att][ff], name) for att in self.attVector()])

data = MegaStruct(f_measgrid, f_attenhut)

### MAKEPLOT FUNCTION
def makePlot(x, y, ytit, fn, extra, logy, norm=None, normO=None, pretty=pretty):
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
	graphs = []

	if norm is None and normO is None:
		yrange = [ry.min(), ry.max()]
		for i in range(ntypes):
			graphs.append(R.TGraph(len(x[i]), x[i], y[i]))
	elif norm is not None and normO is None:
		yrange = [(ry/norm).min(), (ry/norm).max()]
		for i in range(ntypes):
			graphs.append(R.TGraph(len(x[i]), x[i], y[i]/norm[i]))
	elif norm is not None and normO is not None:
		yrange = [((ry/norm)/normO).min(), ((ry/norm)/normO).max()]
		for i in range(ntypes):
			graphs.append(R.TGraph(len(x[i]), x[i], (y[i]/norm[i])/normO[i]))

	# Step 1
	plots = []
	for i,p in enumerate(pretty.keys()):
		plots.append(Plotter.Plot(graphs[i], pretty[p]['name'], 'p', 'AP' if i==0 else 'P'))

	# Step 2
	canvas = Plotter.Canvas(extra, logy, 0., "Internal", 800, 700)

	# Step 3
	if normO is not None or ytit[0:3] == 'Win':
		lstring = 'bl'
	elif ytit[0:3] == 'L1A':
		lstring = 'tr'
	else:
		lstring = 'tl'
	canvas.makeLegend(.2,.25,lstring,0.04, 0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i], i==0, True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	graphs[0].GetYaxis().SetTitleOffset(graphs[0].GetYaxis().GetTitleOffset()*1.4)
	graphs[0].GetYaxis().SetTitle(ytit)
	graphs[0].GetXaxis().SetTitle('Mean Current [#muA]')
	graphs[0].SetMinimum(yrange[0]*0.8)
	graphs[0].SetMaximum(yrange[1]*1.2)
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
	canvas.c.SaveAs(fn)
	R.SetOwnership(canvas.c, False)

### TPRINT FUNCTION
def tprint(cols):
	x = np.transpose(np.array([data.attVector()] + cols))
	man = len(str(int(np.array(cols).max())))
	names = ['Orig', 'TPreC', 'TC', 'TA', 'TPID', 'TPPID', 'TPA', 'TAll']
	print '\033[1;4m Filter | ',
	for name in names:
		print '%*s | ' % (man + 6, name),
	print '\033[m'
	for i in x:
		print '%7.1f | ' % i[0],
		for j in i[1:]:
			print '%*.5f | ' % (man + 6, j),
		print ''

### MAKE ALL PLOTS
for cham in chamlist:
	for numer, denom, logy, normO in [\
			('ALCT*CLCT','L1A',False, False),
			('CFEB Sum' ,None ,True , False),
			('ALCT0'    ,'L1A',True , False),
			('CLCT0'    ,'L1A',True , False),
			('L1A'      ,None ,False, False),
			('ALCT*CLCT','L1A',False, True ),
			('Window'   ,'L1A',False, False)
			]:
		if numer == 'Window': tprint([data.regVector(cham, ff, numer)/(1 if denom is None else data.regVector(cham, ff, denom)) for ff in pretty.keys()])
		makePlot(\
				[data.currentVector(cham, ff) for ff in pretty.keys()],
				[data.regVector(cham, ff, numer) for ff in pretty.keys()],
				numer + ('' if denom is None else '/'+denom) + ('' if not normO else '/Original/L1A'),
				'pdfs/me'+str(cham)+'1-'+numer+('' if denom is not None else '-N')+('' if not normO else '-normO')+'_noHigh.pdf',
				'ME'+str(cham)+'/1',
				logy,
				#norm = None if denom is None else [data.regVector(cham, ff, denom)*data.regVector(cham, ff, 'Duration') for ff in pretty.keys()]
				#norm = [(1 if denom is None else data.regVector(cham, ff, denom))*data.regVector(cham, ff, 'Duration') for ff in pretty.keys()]
				norm = None if denom is None else [data.regVector(cham, ff, denom) for ff in pretty.keys()],
				normO = None if not normO else [data.regVector(cham, 0, numer)/data.regVector(cham, 0, 'L1A') for ff in pretty.keys()]
				)
