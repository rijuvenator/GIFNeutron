import sys, os
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
import Gif.Analysis.BGDigi as BGDigi
R.gStyle.SetOptFit(0)

###################################################
# A skeleton analyzer template to be used with MS #
# Setup involves specifying a CONFIG of filenames #
# Defines analyze, load, setup, cleanup for a     #
# MS class; declares the analyzer which runs it   #
# Plotting functions at the bottom                #
###################################################

#########################
## IMPLEMENT ANALYZERS ##
#########################

# analysis function; runs once per tree
def analyze(self, t, PARAMS):
	#Primitives.SelectBranches(t, DecList=[], branches=['*'])
	for idx, entry in enumerate(t):
		print 'Events:', idx+1, '\r',
		loopFunction(self, t, PARAMS)
	print '\n', self.ATT, 'Done'

# loop function; runs once per event
def loopFunction(self, t, PARAMS):
	E = Primitives.ETree(t, DecList=['WIRE'])
	wires = [Primitives.Wire(E, i) for i in range(len(E.wire_cham))]

	N = t.GetEntries()
	for wire in wires:
		if wire.timeBin < 1 or wire.timeBin > 5: continue
		if wire.cham==1:
			seg = 1
		else:
			# HVs1
			if (1 <= wire.number and wire.number <= 44):
				seg = 1
			# HVs2
			elif (45 <= wire.number and wire.number <= 81):
				seg = 2
			# HVs3
			elif (82 <= wire.number and wire.number <= 112):
				seg = 3
			# Spacer bars
			else:
				continue

		self.VALDATA[wire.cham][seg][(self.ATT, wire.layer)] += 1./N * 1./5. * 1./25. * 1.e9

# load function; loads the file specified in config instead of running analysis
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)

# pre-analysis function; declare histograms, etc.
def setup(self, PARAMS):
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	segs = {
			1:[1],
			110:[1,2,3],
			}
	self.VALDATA = {1:{1:{}},110:{1:{},2:{},3:{}}}
	for cham in (1, 110):
		for layer in range(1, 7):
			for att in self.attVector():
				for seg in segs[cham]:
					self.VALDATA[cham][seg][(att, layer)] = 0

# post-analysis function; print extra lines, etc.
def cleanup(self, PARAMS):
	print ''
	self.F_OUT.cd()
	self.GRAPHS = { 1 : {1:{},'ALL':{}}, 110 : { 1:{},2:{},3:{},'ALL':{} } }
	fitRanges = {
			1:{
				1:{
					1:(0,30000000,30000000),
					2:(0,30000000,30000000),
					3:(0,30000000,30000000),
					4:(0,30000000,30000000),
					5:(0,30000000,30000000),
					6:(0,30000000,30000000),
					},
				'ALL':(0,130000000,130000000),
				},
			110:{
				1:{
					1:(0,4000000,20000000),
					2:(0,4000000,20000000),
					3:(0,4000000,20000000),
					4:(0,4000000,20000000),
					5:(0,4000000,20000000),
					6:(0,4000000,20000000),
					'ALL':(0,20000000,80000000),
					},
				2:{
					1:(0,4000000,20000000),
					2:(0,4000000,20000000),
					3:(0,4000000,20000000),
					4:(0,4000000,20000000),
					5:(0,4000000,20000000),
					6:(0,4000000,20000000),
					'ALL':(0,20000000,80000000)
					},
				3:{
					1:(0,3000000,20000000),
					2:(0,3000000,20000000),
					3:(0,3000000,20000000),
					4:(0,3000000,20000000),
					5:(0,3000000,20000000),
					6:(0,3000000,20000000),
					'ALL':(0,20000000,80000000)
					},
				'ALL':(0,50000000,210000000),
				},
			}
	fitfunc = '[0]*x'
	#fitfunc = '[0]+[1]*x'
	fitFuncs = {
			1:{
				1:{
					lay:R.TF1('ff_1_'+str(lay),'[0]*x',fitRanges[1][1][lay][0],fitRanges[1][1][lay][1]) for lay in range(1,7)
					},
				'ALL':R.TF1('ff_1_ALL','[0]*x',fitRanges[1]['ALL'][0],fitRanges[1]['ALL'][0])
				}, 
			110:{
				1:{
					lay:R.TF1('ff_110_s1_l'+str(lay),'[0]*x',fitRanges[110][1][lay][0],fitRanges[110][1][lay][1]) for lay in [1,2,3,4,5,6,'ALL']
					},
				2:{
					lay:R.TF1('ff_110_s2_l'+str(lay),'[0]*x',fitRanges[110][2][lay][0],fitRanges[110][2][lay][1]) for lay in [1,2,3,4,5,6,'ALL']
					},
				3:{
					lay:R.TF1('ff_110_s3_l'+str(lay),'[0]*x',fitRanges[110][3][lay][0],fitRanges[110][3][lay][1]) for lay in [1,2,3,4,5,6,'ALL']
					},
				'ALL':R.TF1('ff_110_ALL','[0]*x',fitRanges[110]['ALL'][0],fitRanges[110]['ALL'][1]),
				},
			}

	segs = {
			1:[1],
			110:[1,2,3],
			}
	for cham in (1, 110):
		for layer in range(1, 7):
			for seg in segs[cham]:
				# individual channels
				currs = sum([self.atomicCurrentVector(cham, layer, seg)])
				#currs = self.atomicCurrentVector(cham, layer, 1)
				counts = np.array([float(self.VALDATA[cham][seg][(att, layer)]) for att in self.attVector()])
				self.GRAPHS[cham][seg][layer] = R.TGraph(len(currs), counts, currs)
				name = 'g_S'+str(seg)+'_L'+str(layer)+'_C'+str(cham)
				self.GRAPHS[cham][seg][layer].SetNameTitle(name, 'Segment '+str(seg)+' Layer '+str(layer)+' Chamber '+str(cham)+';Hits/s;Current [#muA]')
				print name
				self.GRAPHS[cham][seg][layer].Fit(fitFuncs[cham][seg][layer],'R')#,'','',fitRanges[cham][0],fitRanges[cham][1])
				fitFuncs[cham][seg][layer].Draw()
				self.GRAPHS[cham][seg][layer].GetXaxis().SetLimits(fitRanges[cham][seg][layer][0],fitRanges[cham][seg][layer][2])
				self.GRAPHS[cham][seg][layer].Write(name)
				plot = Plotter.Plot(self.GRAPHS[cham][seg][layer],option='p')
				title = 'GIF++ ME'+('1' if cham==1 else '2')+'/1 '+('HVs#'+str(seg) if cham==110 else '')+' Layer '+str(layer)
				canv = Plotter.Canvas(lumi=title)
				canv.addMainPlot(plot)
				canv.makeTransparent()
				canv.firstPlot.setTitles(X='Hits/s',Y='Current [#muA]')
				canv.finishCanvas('BOB')
				canv.save('plots/'+name+'.pdf')
				print

		# Each segment together
		if cham==110:
			for seg in segs[cham]:
				currs = sum([self.atomicCurrentVector(cham, layer, seg) for layer in range(1, 7)])
				counts = sum([np.array([float(self.VALDATA[cham][seg][(att, layer)]) for att in self.attVector()]) for layer in range(1, 7)])
				self.GRAPHS[cham][seg]['ALL'] = R.TGraph(len(counts), counts, currs)
				name = 'g_S'+str(seg)+'_C'+str(cham)
				self.GRAPHS[cham][seg]['ALL'].SetNameTitle(name, 'Chamber '+str(cham)+';Hits/s;Current [#muA]')
				print name
				self.GRAPHS[cham][seg]['ALL'].Fit(fitFuncs[cham][seg]['ALL'],'R')#,'','',fitRanges[cham][0],fitRanges[cham][1])
				fitFuncs[cham][seg]['ALL'].Draw()
				self.GRAPHS[cham][seg]['ALL'].GetXaxis().SetLimits(fitRanges[cham][seg]['ALL'][0],fitRanges[cham][seg]['ALL'][2])
				self.GRAPHS[cham][seg]['ALL'].Write(name)
				plot = Plotter.Plot(self.GRAPHS[cham][seg]['ALL'],option='p')
				title = 'GIF++ ME'+('1' if cham==1 else '2')+'/1 '+('HVs#'+str(seg) if cham==110 else '')
				canv = Plotter.Canvas(lumi=title)
				canv.addMainPlot(plot)
				canv.makeTransparent()
				canv.firstPlot.setTitles(X='Hits/s',Y='Current [#muA]')
				canv.finishCanvas('BOB')
				canv.save('plots/'+name+'.pdf')
				print

		# total chamber
		currs = sum([self.atomicCurrentVector(cham, layer, seg) for layer in range(1, 7) for seg in segs[cham]])
		counts = sum( [ np.array([float(self.VALDATA[cham][seg][(att, layer)]) for att in self.attVector()]) for layer in range(1, 7) for seg in segs[cham]])
		self.GRAPHS[cham]['ALL']['ALL'] = R.TGraph(len(counts), counts, currs)
		name = 'g_ALL_C'+str(cham)
		self.GRAPHS[cham]['ALL']['ALL'].SetNameTitle(name, 'Chamber '+str(cham)+';Hits/s;Current [#muA]')
		print name
		self.GRAPHS[cham]['ALL']['ALL'].Fit(fitFuncs[cham]['ALL'],'R')#,'','',fitRanges[cham][0],fitRanges[cham][1])
		fitFuncs[cham]['ALL'].Draw()
		self.GRAPHS[cham]['ALL']['ALL'].GetXaxis().SetLimits(fitRanges[cham]['ALL'][0],fitRanges[cham]['ALL'][2])
		self.GRAPHS[cham]['ALL']['ALL'].Write(name)
		plot = Plotter.Plot(self.GRAPHS[cham]['ALL']['ALL'],option='p')
		title = 'GIF++ ME'+('1' if cham==1 else '2')+'/1'
		canv = Plotter.Canvas(lumi=title)
		canv.addMainPlot(plot)
		canv.makeTransparent()
		canv.firstPlot.setTitles(X='Hits/s',Y='Current [#muA]')
		canv.finishCanvas('BOB')
		canv.save('plots/'+name+'.pdf')
		print


########################
## PLOTTING FUNCTIONS ##
########################

def makePlot():
	gr   = data.GRAPHS[1]['ALL']
	#fit  = R.TF1('fit', '[0]*x', 0., 1.e9)
	#fit.SetParameter(0, 3.8e-6)
	#fit.SetLineColor(R.kRed)
	#fit.SetLineWidth(2)
	#gr.Fit('fit')

	plot = Plotter.Plot(gr, legName='Data', legType='p', option='p')

	canvas = Plotter.Canvas(lumi='')
	canvas.addMainPlot(plot)
	#canvas.setFitBoxStyle(gr)

	canvas.firstPlot.GetXaxis().SetLimits(0, 135.e6)

	canvas.finishCanvas()
	canvas.save('plot.pdf')
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

########################
##  MAIN MODULE CODE  ##
########################

if __name__ == '__main__':
	#### SETUP SCRIPT #####
	# Output file names
	CONFIG = {
		'GIF' : 'rates.root',
	}
	# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
	TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

	##### DECLARE ANALYZERS AND RUN ANALYSIS #####
	R.gROOT.SetBatch(True)
	METHODS = ['analyze', 'load', 'setup', 'cleanup']
	ARGS = {
		'PARAMS'     : [OFN, TYPE],
		'F_DATAFILE' : FDATA
	}
	if TYPE == 'GIF':
		ARGS['ATTLIST'] = None
	Analyzer = getattr(MS, TYPE+'Analyzer')
	for METHOD in METHODS:
		setattr(Analyzer, METHOD, locals()[METHOD])
	data = Analyzer(**ARGS)
	makePlot()
