import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.Plotter as Plotter
import Gif.TestBeamAnalysis.Auxiliary as Aux

##### PARAMETERS #####
# Which chambers to do
CHAMLIST = (1, 110)
chamlist = [1,110]

##### SEMI-PARAMETERS #####
# Filenames
F_MEASGRID = '../datafiles/measgrid'
F_ATTENHUT = '../datafiles/attenhut'
F_DATAFILE = '../datafiles/data_segEff'
#F_DATAFILE = None

# Cosmetic data dictionary, comment out for fewer ones
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
# Scintillator definition
SCINT = {1:{'HS':(25,72),'WG':(37,43)},110:{'HS':(8,38),'WG':(55,65)}}

##### BEGIN CODE #####
R.gROOT.SetBatch(True)

##### HELPER FUNCTIONS #####
# defines a paddle region
def inPad(hs, wg, CHAM):
	if      hs >= SCINT[CHAM]['HS'][0]\
		and hs <= SCINT[CHAM]['HS'][1]\
		and wg >= SCINT[CHAM]['WG'][0]\
		and wg <= SCINT[CHAM]['WG'][1]:
		return True
	else:
		return False

# determines if a segment and an lct match each other
def matchSegLCT(seg, lct):
	if abs(seg.halfStrip - lct.keyHalfStrip) <= 2 and abs(seg.wireGroup - lct.keyWireGroup) <= 2:
		return True
	else:
		return False

##### MEGASTRUCT CLASS #####
class MegaStruct():
	#### BEGIN MEGASTRUCT COMMON: DO NOT EDIT BETWEEN THESE TAGS #####
	def __init__(self):
		self.fillMeas()
		self.fillCurr()
		self.fillData()
	
	# general fill measurement data function
	def fillMeas(self):
		f = open(F_MEASGRID)
		self.MEASDATA = {}
		for line in f:
			cols = line.strip('\n').split()
			self.MEASDATA[float(cols[0])] = [int(j) for j in cols[1:]]
		f.close()

	# general fill current data function
	def fillCurr(self):
		f = open(F_ATTENHUT)
		self.CURRDATA = { 1 : {}, 110: {} }
		currentCham = 1
		for line in f:
			if line == '\n':
				currentCham = 110
				continue
			cols = line.strip('\n').split()
			currentMeas = int(cols[1])
			self.CURRDATA[currentCham][currentMeas] = [float(i) for i in cols[2:]]
		f.close()

	# get a current measurement given a chamber and measurement number
	def current(self, cham, meas):
		if cham == 1:
			return sum(self.CURRDATA[cham][meas])/6.0
		elif cham == 110:
			return sum(self.CURRDATA[cham][meas][6:12])/6.0
	
	# get a vector of attenuations
	def attVector(self, castrated=False):
		if castrated: # for comparing to Yuriy
			return np.array([33., 46., 100., float('inf')])
		else:
			return np.array(sorted(self.MEASDATA.keys()))

	# get a vector of currents
	def currentVector(self, cham, ff, castrated=False):
		return np.array([self.current(cham, self.MEASDATA[att][ff]) for att in self.attVector(castrated)])

	# get a vector of equivalent luminosities
	def lumiVector(self, cham, ff, castrated=False):
		factor = 3.e33 if cham == 1 else 5.e33
		return factor * np.array([self.current(cham, self.MEASDATA[att][ff]) for att in self.attVector(castrated)])
	##### END MEGASTRUCT COMMON: DO NOT EDIT BETWEEN THESE TAGS #####

	# fill data: this function, and the access functions below it, are "user-defined" and script-dependent
	def fillData(self):
		# fill a data dictionary as desired
		self.noSegs= { 1 : {}, 110: {} }
		self.yesSegs= { 1 : {}, 110: {} }
		self.yesSegYesInPad = { 1 : {}, 110 : {} }
		self.yesSegYesInPadYesMatchLCT = { 1 : {}, 110 : {} }
		self.yesSegYesInPadNoMatchLCT = { 1 : {}, 110 : {} }
		self.yesSegNoInPad = { 1 : {}, 110 : {} }
		self.yesSegYesMatchLCT = { 1 : {}, 110 : {} }
		self.yesSegNoMatchLCT = { 1 : {}, 110 : {} }
		self.noSegsNoStrips = { 1 : {}, 110 : {} }
		self.noSegsNoWires = { 1 : {}, 110 : {} }
		self.noSegsNoStripsNoWires = { 1 : {}, 110 : {} }
		self.noSegsNoStripsNoWiresNoComp = { 1 : {}, 110 : {} }
		self.noSegsNoStripsNoWiresYesComp = { 1 : {}, 110 : {} }
		self.noSegsYesStripsWires = { 1 : {}, 110 : {} }
		self.noSegYesStripsWiresNoCFEB = { 1 : {}, 110 : {} }
		self.noSegYesStripsWiresYesCFEB = { 1 : {}, 110 : {} }
		self.noSegYesStripsWiresYes1of2CFEB = { 1 : {}, 110 : {} }
		self.noSegYesStripWiresNoComp = { 1 : {}, 110 : {} }
		self.denominator = { 1 : {}, 110 : {} }
		self.numerator   = { 1 : {}, 110 : {} }
		if F_DATAFILE is None:
			for ATT in self.MEASDATA.keys():
				for MEAS in self.MEASDATA[ATT][0:1]: # only original
					for cham in chamlist:
						self.noSegs[cham][MEAS] = 0
						self.yesSegs[cham][MEAS] = 0
						self.yesSegYesInPad[cham][MEAS] = 0
						self.yesSegYesInPadYesMatchLCT[cham][MEAS] = 0
						self.yesSegYesInPadNoMatchLCT[cham][MEAS] = 0
						self.yesSegNoInPad[cham][MEAS] = 0
						self.yesSegYesMatchLCT[cham][MEAS] = 0
						self.yesSegNoMatchLCT[cham][MEAS] = 0
						self.noSegsNoStrips[cham][MEAS] = 0
						self.noSegsNoWires[cham][MEAS] = 0
						self.noSegsNoStripsNoWires[cham][MEAS] = 0
						self.noSegsNoStripsNoWiresNoComp[cham][MEAS] = 0
						self.noSegsNoStripsNoWiresYesComp[cham][MEAS] = 0
						self.noSegsYesStripsWires[cham][MEAS] = 0
						self.noSegYesStripsWiresNoCFEB[cham][MEAS] = 0
						self.noSegYesStripsWiresYesCFEB[cham][MEAS] = 0
						self.noSegYesStripsWiresYes1of2CFEB[cham][MEAS] = 0
						self.noSegYesStripWiresNoComp[cham][MEAS] = 0
					f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/15Dec/ana_'+str(MEAS)+'.root')
					t = f.Get('GIFTree/GIFDigiTree')
					nL1A = t.GetEntries()
					for evt,entry in enumerate(t):
						E = Primitives.ETree(t,DecList=['SEGMENT','LCT','RECHIT','WIRE','COMP','STRIP'])
						segs    = [Primitives.Segment(E,i) for i in range(len(E.seg_cham))]
						lcts    = [Primitives.LCT(E,i)     for i in range(len(E.lct_cham))]
						rechits = [Primitives.RecHit(E,i)  for i in range(len(E.rh_cham))]
						wires   = [Primitives.Wire(E,i)    for i in range(len(E.wire_cham))]
						comps   = [Primitives.Comp(E,i)    for i in range(len(E.comp_cham))]
						strips  = [Primitives.Strip(E,i)   for i in range(len(E.strip_cham))]
						for cham in [1,110]:
							#if cham!=110: continue
							# No Segment condition
							if cham not in [seg.cham for seg in segs]:

								# No segment counter
								self.noSegs[cham][MEAS] += 1

								# No strip yes wire and no segment counter
								if cham not in [strip.cham for strip in strips] and \
								   cham in [wire.cham for wire in wires]:
									self.noSegsNoStrips[cham][MEAS] += 1

								# No wire yes strip and no segment counter
								if cham in [strip.cham for strip in strips] and \
								   cham not in [wire.cham for wire in wires]:
									self.noSegsNoWires[cham][MEAS] += 1

								# No strip and no wire and no segment counter
								if cham not in [strip.cham for strip in strips] and \
								   cham not in [wire.cham for wire in wires]:
									self.noSegsNoStripsNoWires[cham][MEAS] += 1
									# No comparator
									if cham not in [comp.cham for comp in comps]:
										self.noSegsNoStripsNoWiresNoComp[cham][MEAS] += 1
									# Yes comparator
									else:
										self.noSegsNoStripsNoWiresYesComp[cham][MEAS] += 1

								# Yes strip yes wire and no segment counter
								if cham in [strip.cham for strip in strips] and \
								   cham in [wire.cham for wire in wires]:
									self.noSegsYesStripsWires[cham][MEAS] += 1

									# Make Active CFEB list
									ActiveCFEBs = [False] * (7 if cham == 1 else 5)
									for strip in strips:
										if strip.cham != cham: continue
										ActiveCFEBs[int(strip.number - 1) / 16] = True

									# Determine if LCT's CFEB was read out
									# Yes comparator
									if cham in [comp.cham for comp in comps]:
										correct = 0
										total = 0
										for lct in lcts:
											if lct.cham != cham: continue
											total += 1
											if ActiveCFEBs[lct.keyHalfStrip / 32]:
												correct += 1
										if correct==2 or (correct==1 and total==1):
											# One or both of the correct CFEBs are read out; check RecHits
											self.noSegYesStripsWiresYesCFEB[cham][MEAS] += 1
											#print evt
										elif correct==1 and total==2:
											# 1/2 correct CFEBs were read out
											self.noSegYesStripsWiresYes1of2CFEB[cham][MEAS] += 1
										else:
											# Wrong CFEB is read out
											self.noSegYesStripsWiresNoCFEB[cham][MEAS] += 1
									else:
										# No comparator
										self.noSegYesStripWiresNoComp[cham][MEAS] += 1

											
							# Yes segment counter
							if cham in [seg.cham for seg in segs]:
								self.yesSegs[cham][MEAS] += 1
								segInPad = False
								matchSegLCTinPad = False
								matchSegLCT = False
								for seg in segs:
									if seg.cham!=cham: continue
									# Find segments in Paddle
									if Aux.inPad(seg.halfStrip[3], seg.wireGroup[3], cham):
										segInPad = True
										# If there's a segment in the paddle, check if it matches to an LCT
										for lct in lcts:
											if lct.cham!=cham: continue
											if Aux.matchSegLCT(seg,lct):
												matchSegLCTinPad = True
									# Check if any segment matches an LCT
									for lct in lcts:
										if lct.cham!=cham: continue
										if Aux.matchSegLCT(seg,lct):
											matchSegLCT = True
								# Increment counters
								if segInPad:
									self.yesSegYesInPad[cham][MEAS] += 1
								else:
									self.yesSegNoInPad[cham][MEAS] += 1
								if matchSegLCT:
									self.yesSegYesMatchLCT[cham][MEAS] += 1
								else:
									self.yesSegNoMatchLCT[cham][MEAS] += 1
								if matchSegLCTinPad:
									self.yesSegYesInPadYesMatchLCT[cham][MEAS] += 1
								elif segInPad:
									self.yesSegYesInPadNoMatchLCT[cham][MEAS] += 1

					# Print per measurement
					printString = \
'''{:4d}
{:5d}
Yes Segments {:5d} {:5d}
\t Yes in scint {:5d} {:5d} (any seg)
\t\t   Match to LCT {:5d} {:5d}
\t\tNo match to LCT {:5d} {:5d}
\tNone in scint {:5d} {:5d}
\t   Match to LCT {:5d} {:5d} (any match)
\tNo match to LCT {:5d} {:5d}

No  Segments {:4d} {:4d}
\tNo  Strips, No  Wires {:3d} {:3d}
\t\t No Comparators {:3d} {:3d} (Chamber didn't read out)
\t\tYes Comparators {:3d} {:3d}
\tYes Strips, No  Wires {:3d} {:3d}
\tNo  Strips, Yes Wires {:3d} {:3d}
\tYes Strips, Yes Wires {:3d} {:3d}
\t\t      No Comparators {:3d} {:3d} 
\t\tAll correct CFEB/LCT {:3d} {:3d} (Probably missing RecHits)
\t\t1/2 correct CFEB/LCT {:3d} {:3d} (Probably missing RecHits)
\t\t No correct CFEB/LCT {:3d} {:3d} 
'''
					'''
					print printString.format(\
							MEAS,
							nL1A,

							self.yesSegs[1][MEAS]                       ,self.yesSegs[110][MEAS],
							self.yesSegYesInPad[1][MEAS]                ,self.yesSegYesInPad[110][MEAS],
							self.yesSegYesInPadYesMatchLCT[1][MEAS]     ,self.yesSegYesInPadYesMatchLCT[110][MEAS],
							self.yesSegYesInPadNoMatchLCT[1][MEAS]      ,self.yesSegYesInPadNoMatchLCT[110][MEAS],
							self.yesSegNoInPad[1][MEAS]                 ,self.yesSegNoInPad[110][MEAS],
							self.yesSegYesMatchLCT[1][MEAS]             ,self.yesSegYesMatchLCT[110][MEAS],
							self.yesSegNoMatchLCT[1][MEAS]              ,self.yesSegNoMatchLCT[110][MEAS],

							self.noSegs[1][MEAS]                        ,self.noSegs[110][MEAS],

							self.noSegsNoStripsNoWires[1][MEAS]         ,self.noSegsNoStripsNoWires[110][MEAS],
							self.noSegsNoStripsNoWiresNoComp[1][MEAS]   ,self.noSegsNoStripsNoWiresNoComp[110][MEAS],
							self.noSegsNoStripsNoWiresYesComp[1][MEAS]  ,self.noSegsNoStripsNoWiresYesComp[110][MEAS],

							self.noSegsNoWires[1][MEAS]                 ,self.noSegsNoWires[110][MEAS],
							self.noSegsNoStrips[1][MEAS]                ,self.noSegsNoStrips[110][MEAS],
							self.noSegsYesStripsWires[1][MEAS]          ,self.noSegsYesStripsWires[110][MEAS],

							self.noSegYesStripWiresNoComp[1][MEAS]      ,self.noSegYesStripWiresNoComp[110][MEAS],
							self.noSegYesStripsWiresYesCFEB[1][MEAS]    ,self.noSegYesStripsWiresYesCFEB[110][MEAS],
							self.noSegYesStripsWiresYes1of2CFEB[1][MEAS],self.noSegYesStripsWiresYes1of2CFEB[110][MEAS],
							self.noSegYesStripsWiresNoCFEB[1][MEAS]     ,self.noSegYesStripsWiresNoCFEB[110][MEAS],


						)
					'''
					self.numerator[1][MEAS] = self.yesSegYesInPad[1][MEAS]
					self.numerator[110][MEAS] = self.yesSegYesInPad[110][MEAS]
					self.denominator[1][MEAS] = nL1A
					self.denominator[110][MEAS] = nL1A
					#print MEAS, self.numerator[1][MEAS], self.denominator[1][MEAS], self.numerator[110][MEAS], self.denominator[110][MEAS]
					segIneffString = '{:4d} {:4d} {:4d} {:4d} {:4d} {:4d} {:4d} {:4d} {:4d} {:4d} {:4d} {:4d} {:4d}'
					print segIneffString.format(\
						MEAS, 
						nL1A-self.yesSegYesInPad[1][MEAS], self.yesSegNoInPad[1][MEAS], self.noSegsNoStripsNoWires[1][MEAS],
						self.noSegsNoWires[1][MEAS], self.noSegsNoStrips[1][MEAS], self.noSegsYesStripsWires[1][MEAS],
						nL1A-self.yesSegYesInPad[110][MEAS], self.yesSegNoInPad[110][MEAS], self.noSegsNoStripsNoWires[110][MEAS], 
						self.noSegsNoWires[110][MEAS], self.noSegsNoStrips[110][MEAS], self.noSegsYesStripsWires[110][MEAS]
					)
										
		# for obtaining data dictionary from a file
		else:
			f = open(F_DATAFILE)
			for line in f:
				cols = line.strip('\n').split()
				MEAS = int(cols[0])
				self.numerator[1][MEAS] = float(cols[1])
				self.denominator[1][MEAS] = float(cols[2])
				self.numerator[110][MEAS] = float(cols[3])
				self.denominator[110][MEAS] = float(cols[4])

	# get a value given a chamber and measurement number
	def eff(self, cham, meas):
		return float(self.numerator[cham][meas]/self.denominator[cham][meas])

	# get a vector of values
	def effVector(self, cham, ff):
		return np.array([self.eff(cham, self.MEASDATA[att][ff]) for att in self.attVector()])

data = MegaStruct()

##### MAKEPLOT FUNCTION #####
def makePlot(cham, x, y, xtitle, ytitle, title):
	graphs = []
	ntypes = len(pretty.keys())
	for i in range(ntypes):
		graphs.append(R.TGraph(len(x[i]), x[i], y[i]))

	# Step 1
	plots = []
	for i, p in enumerate(pretty.keys()):
		plots.append(Plotter.Plot(graphs[i], legName=pretty[p]['name'], legType='p', option='P'))

	# Step 2
	canvas = Plotter.Canvas(lumi='ME'+str(cham)+'/1 External Trigger', logy=False, extra='Internal', cWidth=800, cHeight=700)

	# Step 3
	canvas.makeLegend(lWidth=0.2, lHeight=0.25, pos='bl', lOffset=0.04, fontsize=0.03)

	# Step 4
	for i in range(ntypes):
		canvas.addMainPlot(plots[i], addToLegend=True)

	# Step 5
	R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
	canvas.firstPlot.setTitles(X=xtitle, Y=ytitle)
	canvas.firstPlot.plot.SetMinimum(0.0)
	canvas.firstPlot.plot.SetMaximum(1.1)
	canvas.firstPlot.scaleTitles(0.8)
	canvas.firstPlot.scaleLabels(0.8)
	canvas.firstPlot.scaleTitleOffsets(1.2, 'Y')
	canvas.makeTransparent()

	for i,p in enumerate(pretty.keys()):
		graphs[i].SetMarkerColor(pretty[p]['color'])
		graphs[i].SetMarkerStyle(pretty[p]['marker'])
		graphs[i].SetMarkerSize(2.2)

	# Step 6

	# Step 7

	# Step 8
	canvas.finishCanvas()
	canvas.c.SaveAs('pdfs/segEff_ME'+str(cham)+'1_'+title+'.pdf')
	R.SetOwnership(canvas.c, False)

'''
##### MAKE PLOTS #####
for cham in CHAMLIST:
	makePlot(\
		cham if cham == 1 else 2,
		[data.lumiVector(cham, ff) for ff in pretty.keys()],
		[data.effVector (cham, ff) for ff in pretty.keys()],
		'Luminosity [Hz/cm^{2}]',
		'Segment Efficiency',
		'lumi'
	)
'''
