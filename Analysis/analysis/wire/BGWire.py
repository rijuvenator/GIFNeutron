import os
import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS

#### SETUP SCRIPT #####
# Output file names
CONFIG = {
	'P5'  : 'BGWire_P5.root',
}
# Set module globals: TYPE=[GIF/P5/MC], OFN=Output File Name, FDATA=[OFN/None]
TYPE, OFN, FDATA = MS.ParseArguments(CONFIG)

# runs before file loop; open a file, declare a hist dictionary
def setup(self, PARAMS):
	self.HISTS = {}
	FN = PARAMS[0]
	self.F_OUT = R.TFile(FN,'RECREATE')
	self.F_OUT.cd()
	for ring in ringlist:
		self.HISTS[ring] = {\
			'time': R.TH1F('t'+ring, '', 10, 0., 16.),
			'lumi': R.TH1F('l'+ring, '', 30, 0., 15.e33),
			'totl': R.TH1F('a'+ring, '', 30, 0., 15.e33),
		}
		self.HISTS[ring]['time'].SetDirectory(0)
		self.HISTS[ring]['lumi'].SetDirectory(0)
		self.HISTS[ring]['totl'].SetDirectory(0)

shortringlist = ['11','12','13','21','22','31','32','41','42']
ringlist = [i+'u' for i in shortringlist] + [i+'l' for i in shortringlist]

# once per file
def analyze(self, t, PARAMS):
	for idx, entry in enumerate(t):
		#if idx == 10000: break

		if      t.Z_mass <= 98. and t.Z_mass >= 84.\
			and t.nJets20 == 0\
			and t.Z_pT <= 20.:
			pass
		else:
			continue

		if list(t.lct_id) == [] or list(t.comp_id) == []: continue
		E = Primitives.ETree(t, DecList=['LCT','WIRE'])
		lcts  = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham ))]
		wires = [Primitives.Wire   (E, i) for i in range(len(E.wire_cham))]

		twolcts = list(set([i for i in E.lct_cham if E.lct_cham.count(i)>1]))
		for lct in lcts:
			if lct.cham in twolcts: continue
			nWire = 0
			cham = CH.Chamber(lct.cham)
			nHS = cham.nstrips*2
			nWG = cham.nwires
			if cham.station==1 and cham.ring==1:
				# ME1/1 has wires tilted at 29 degrees wrt local +x axis
				# Instead of requiring that the LCT is in a "corner", for 
				# ME1/1 we use "bottom" and "top" parts to look for an LCT
				# "Bottom" is defined as  1 <= kwg <= 12 (0,3)
				# "Top"    is defined as 37 <= kwg <= 48 (1,2)
				# (Only defined differently because in ME1/1 we don't 
				#  make any requirement on the HS of the LCT)
				LCTAreas = \
				{
					'0' : {'wg0' :  1. , 'wg1' : 12. , 'hs0' : 0. , 'hs1' : nHS},
					'1' : {'wg0' : 37. , 'wg1' : 48. , 'hs0' : 0. , 'hs1' : nHS},
					'2' : {'wg0' : 37. , 'wg1' : 48. , 'hs0' : 0. , 'hs1' : nHS},
					'3' : {'wg0' :  1. , 'wg1' : 12. , 'hs0' : 0. , 'hs1' : nHS},
				}
				# ME1/1 opposite areas are the other "half"
				# keys correspond to LCT location
				# "Bottom" LCTs -> Look for wgs in 25 <= wg <= 48 (0,3)
				#    "Top" LCTs -> Look for wgs in  1 <= wg <= 24 (1,2)
				# (Same for all other chambers but defined explicitly for ME1/1)
				OppAreas = \
				{
					0 : {'wg0' :  25 , 'wg1' : 48 },
					1 : {'wg0' :   1 , 'wg1' : 24 },
					2 : {'wg0' :   1 , 'wg1' : 24 },
					3 : {'wg0' :  25 , 'wg1' : 48 },
				}
			else:
				LCTAreas = \
				{
					0 : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : 0.          , 'hs1' : nHS*0.25},
					1 : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : 0.          , 'hs1' : nHS*0.25},
					2 : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
					3 : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
				}
				OppAreas = \
				{
					0 : {'wg0' : (1-0.50)*nWG, 'wg1' : nWG     },
					1 : {'wg0' : 0.          , 'wg1' : nWG*0.50},
					2 : {'wg0' : 0.          , 'wg1' : nWG*0.50},
					3 : {'wg0' : (1-0.50)*nWG, 'wg1' : nWG     },
				}
			for key in LCTAreas.keys():
				if  lct.keyWireGroup >= LCTAreas[key]['wg0'] and lct.keyWireGroup <= LCTAreas[key]['wg1']\
				and lct.keyHalfStrip >= LCTAreas[key]['hs0'] and lct.keyHalfStrip <= LCTAreas[key]['hs1']:
					for wire in wires:
						if wire.cham != lct.cham: continue
						if wire.number >= OppAreas[key]['wg0'] and wire.number <= OppAreas[key]['wg1']:
							if key==0 or key==3: # Fill upper bg wire group hist
								self.HISTS[cham.display('{S}{R}u')]['time'].Fill(wire.timeBin)
							if key==1 or key==2: # Fill lower bg wire group hist
								self.HISTS[cham.display('{S}{R}l')]['time'].Fill(wire.timeBin)
							if wire.timeBin >= 1 and wire.timeBin <= 5:
								nWire += 1
					if key==0 or key==3: # upper bg wires
						self.HISTS[cham.display('{S}{R}u')]['lumi'].Fill(self.lumi(t.Event_RunNumber, t.Event_LumiSection), float(nWire))
						self.HISTS[cham.display('{S}{R}u')]['totl'].Fill(self.lumi(t.Event_RunNumber, t.Event_LumiSection), float(1.   ))
					elif key==1 or key==2: # lower bg wires
						self.HISTS[cham.display('{S}{R}l')]['lumi'].Fill(self.lumi(t.Event_RunNumber, t.Event_LumiSection), float(nWire))
						self.HISTS[cham.display('{S}{R}l')]['totl'].Fill(self.lumi(t.Event_RunNumber, t.Event_LumiSection), float(1.   ))

	self.F_OUT.cd()
	for ring in ringlist:
		self.HISTS[ring]['time'].Write()
		self.HISTS[ring]['lumi'].Write()
		self.HISTS[ring]['totl'].Write()

# if file is already made
def load(self, PARAMS):
	f = R.TFile.Open(self.F_DATAFILE)
	self.HISTS = {}
	for ring in ringlist:
		self.HISTS[ring] = {\
			'time' : f.Get('t'+ring),
			'lumi' : f.Get('l'+ring),
			'totl' : f.Get('a'+ring),
		}
		self.HISTS[ring]['time'].SetDirectory(0)
		self.HISTS[ring]['lumi'].SetDirectory(0)
		self.HISTS[ring]['totl'].SetDirectory(0)

##### DECLARE ANALYZERS AND RUN ANALYSIS #####
R.gROOT.SetBatch(True)
METHODS = ['analyze', 'load', 'setup']
ARGS = {\
	'PARAMS'     : [OFN, TYPE],
	'F_DATAFILE' : FDATA
}
Analyzer = getattr(MS, TYPE+'Analyzer')
for METHOD in METHODS:
	setattr(Analyzer, METHOD, locals()[METHOD])
data = Analyzer(**ARGS)

##### MAKEPLOT FUNCTIONS #####
def makeTimePlot(h, ring):
	if h.Integral() == 0: return
	plot = Plotter.Plot(h, option='hist')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.addMainPlot(plot)
	canvas.makeTransparent()
	#canvas.firstPlot.plot.SetMaximum(1.05)
	canvas.firstPlot.plot.SetMinimum(0)
	#canvas.firstPlot.plot.SetMinimum(0.00001)
	canvas.finishCanvas()
	canvas.SaveAs('pdfs/BGWireTime'+'_'+ring+'.pdf')
	R.SetOwnership(canvas, False)

def makeLumiPlotFull(h1u, h1l, h2u, h2l, ring):
	binit = range(1, h1u.GetNbinsX()+1)
	nwiresu = [h1u.GetBinContent(i) for i in binit]
	nwiresl = [h1l.GetBinContent(i) for i in binit]
	totalsu = [h2u.GetBinContent(i) for i in binit]
	totalsl = [h2l.GetBinContent(i) for i in binit]
	#lumi = np.array([])
	#lumi = h1.GetXaxis().GetCenter(lumi)
	#lumi = np.array(lumi)
	lumiA = np.array([(15.e33)/30 * (i+0.5) for i in range(30)])
	dataAu = np.array([nwire/float(total) if total != 0 else 0. for nwire,total in zip(nwiresu,totalsu)])
	dataAl = np.array([nwire/float(total) if total != 0 else 0. for nwire,total in zip(nwiresl,totalsl)])
	lumi = np.array(lumiA[10:26])
	datau = np.array(dataAu[10:26])
	datal = np.array(dataAl[10:26])
	hu = R.TGraph(len(lumi), lumi, datau)
	hl = R.TGraph(len(lumi), lumi, datal)
	#print lumi, data
	plotu = Plotter.Plot(hu, legName = ring+' upper', option='PE', legType = 'P')
	plotl = Plotter.Plot(hl, legName = ring+' lower', option='PE', legType = 'P')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.addMainPlot(plotu)
	canvas.addMainPlot(plotl)
	canvas.makeTransparent()
	canvas.scaleMargins(1.25, 'R')
	canvas.firstPlot.setTitles(X='Luminosity [cm^{-2}s^{-1}]', Y='#LT Number of Background Wire Groups#GT')
	canvas.firstPlot.GetXaxis().SetLimits(0., 15.e33)
	canvas.firstPlot.SetMinimum(0. )
	canvas.firstPlot.SetMaximum(1.0)
	canvas.firstPlot.scaleTitleOffsets(1.2)
	plotu.SetMarkerColor(R.kRed)
	plotl.SetMarkerColor(R.kBlue)
	canvas.makeLegend(pos='tl')
	canvas.finishCanvas()
	canvas.SaveAs('pdfs/BGWireAvgN'+'_'+ring+'.pdf')
	R.SetOwnership(canvas, False)

def makeLumiPlot(h1, h2, ring):
	binit = range(1, h1.GetNbinsX()+1)
	nwires = [h1.GetBinContent(i) for i in binit]
	totals = [h2.GetBinContent(i) for i in binit]
	#lumi = np.array([])
	#lumi = h1.GetXaxis().GetCenter(lumi)
	#lumi = np.array(lumi)
	lumiA = np.array([(15.e33)/30 * (i+0.5) for i in range(30)])
	dataA = np.array([nwire/float(total) if total != 0 else 0. for nwire,total in zip(nwires,totals)])
	lumi = np.array(lumiA[10:26])
	data = np.array(dataA[10:26])
	h = R.TGraph(len(lumi), lumi, data)
	#print lumi, data
	plot = Plotter.Plot(h, option='PE')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.addMainPlot(plot)
	canvas.makeTransparent()
	canvas.scaleMargins(1.25, 'R')
	canvas.firstPlot.setTitles(X='Luminosity [cm^{-2}s^{-1}]', Y='#LT Number of Background Wire Groups#GT')
	canvas.firstPlot.GetXaxis().SetLimits(0., 15.e33)
	canvas.firstPlot.SetMinimum(0. )
	canvas.firstPlot.SetMaximum(1.0)
	canvas.firstPlot.scaleTitleOffsets(1.2)
	canvas.finishCanvas()
	canvas.SaveAs('pdfs/BGWireAvgN'+'_'+ring+'.pdf')
	R.SetOwnership(canvas, False)

def makeNumDum(h, ring, which):
	plot = Plotter.Plot(h, option='P')
	canvas = Plotter.Canvas(lumi='ME'+ring, logy=False)
	canvas.addMainPlot(plot)
	canvas.makeTransparent()
	canvas.scaleMargins(1.25, 'R')
	canvas.firstPlot.setTitles(X='Luminosity [cm^{-2}s^{-1}]', Y='Number of Background Wire Groups' if which == 'nwire' else 'Counts')
	canvas.finishCanvas()
	canvas.SaveAs('pdfs/BGWireAvgN'+'_'+ring+'_'+which+'.pdf')
	R.SetOwnership(canvas, False)

for ring in ringlist:
	makeTimePlot(data.HISTS[ring]['time'], ring)
	makeLumiPlot(data.HISTS[ring]['lumi'], data.HISTS[ring]['totl'], ring)
	makeNumDum(data.HISTS[ring]['lumi'], ring, 'nwire')
	makeNumDum(data.HISTS[ring]['totl'], ring, 'lumi')
for ring in shortringlist:
	makeLumiPlotFull(data.HISTS[ring+'u']['lumi'],data.HISTS[ring+'l']['lumi'], data.HISTS[ring+'u']['totl'], data.HISTS[ring+'l']['totl'],ring)
