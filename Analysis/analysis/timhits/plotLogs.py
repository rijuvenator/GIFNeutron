import numpy as np
import subprocess as bash
import argparse
import ROOT as R
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.ChamberHandler as CH

R.gROOT.SetBatch(True)

parser = argparse.ArgumentParser()
parser.add_argument('FILE'                 ,                      help='event log file/root file with hists')
parser.add_argument('-snd', '--SPLITNODIGI', action='store_true', help='split no digi' )
args = parser.parse_args()
FILE = args.FILE
SPLITNODIGI = args.SPLITNODIGI

EXT = FILE.split('.')[-1]
if EXT == 'log':
	FILETYPE = 'LOG'
elif EXT == 'root':
	FILETYPE = 'ROOT'

##### FILL DATA STRUCTURE #####
class SimHit(object):
	def __init__(self, *data):
		self.Event    = data[0 ]
		self.DeltaS   = data[1 ]
		self.ELossG   = data[2 ]
		self.TOF      = data[3 ]
		self.ELossT   = data[4 ]
		self.NIC      = data[5 ]
		self.NIE      = data[6 ]
		self.PID      = data[7 ]
		self.AvgELoss = data[8 ]
		self.AvgStep  = data[9 ]
		self.Cham     = data[10]

##### CREATE HISTOGRAMS FROM A LOG #####
if FILETYPE == 'LOG':
	# capitals become data members
	f = open(FILE)
	data = []
	PIDList = []
	for line in f:
		if 'starting event' in line:
			cols = line.strip('\n').split()
			Event    = int(cols[3])
		elif 'in layer' in line:
			cols = line.strip('\n').split()
			chamRaw  = cols[6:11]
			e,s,r,c  = 1 if chamRaw[0] == 'E:1' else -1, int(chamRaw[1][2:]), int(chamRaw[2][2:]), int(chamRaw[3][2:])
			Cham     = CH.Chamber(CH.serialID(e, s, r, c))
		elif 'particle type' in line:
			cols = line.strip('\n').split()
			PID      = int(cols[3])
			ELossG   = float(cols[13])
			try:
				TOF  = float(cols[18])
			except:
				TOF  = 0.
		elif 'SUMMARY: ionization' in line:
			cols = line.strip('\n').split()
			ELossT   = float(cols[33])
			DeltaS   = float(cols[8])
			NIC      = int(cols[16])
			NIE      = int(cols[23])
			AvgELoss = float(cols[26])
			AvgStep  = float(cols[12])
			data.append(SimHit(Event, DeltaS, ELossG, TOF, ELossT, NIC, NIE, PID, AvgELoss, AvgStep, Cham))
			PIDList.append(PID)
	f.close()
	PIDList = list(set(PIDList))

	##### DO ANALYSIS #####

	CONFS = {
		#'E' : {'bins' : 180, 'xmin' : 0, 'xmax' : 60},
		'E' : {'bins' : 45 , 'xmin' :   0, 'xmax' : 15   },           # Energy axes
		'X' : {'bins' : 100, 'xmin' :   0, 'xmax' : 5    },           # Delta S axes
		'N' : {'bins' : 100, 'xmin' :   0, 'xmax' : 400  },           # NIC axes
		'NE': {'bins' : 100, 'xmin' :   0, 'xmax' : 800  },           # NIE axes
		'AS': {'bins' : 100, 'xmin' :   0, 'xmax' : 0.027},           # AvgStep axes
		'AE': {'bins' : 100, 'xmin' :   0, 'xmax' : 300  },           # AvgELoss axes
		'DE': {'bins' :  50, 'xmin' : -10, 'xmax' : 10   },           # Energy Difference axes
		'T' : {'bins' :1000, 'binedges' : np.logspace(1.,4.,1000+1)}, # TOF axes
	}

	TAGS = {
		'DS'     : ('X' ,),     # hist : Delta S
		'EG'     : ('E' ,),     # hist : Energy GEANT
		'ET'     : ('E' ,),     # hist : Energy Tim
		'ET-M'   : ('E' ,),     # hist : Energy Tim Modified
		'ET-O'   : ('E' ,),     # hist : Energy Tim Original
		'NIC'    : ('N' ,),     # hist : NIC
		'NIE'    : ('NE',),     # hist : NIE
		'AS'     : ('AS',),     # hist : AvgStep
		'AE'     : ('AE',),     # hist : AvgELoss
		'TOF'    : ('T','',''), # hist : TOF

		'DS_EG'  : ('X', 'E'),  # hist : Delta S vs Energy GEANT
		'DS_ET'  : ('X', 'E'),  # hist : Delta S vs Energy Tim
		'NIC_EG' : ('N', 'E'),  # hist : NIC vs Energy GEANT
		'NIC_ET' : ('N', 'E'),  # hist : NIC vs Energy Tim
		'ET_EG'  : ('E', 'E'),  # hist : Energy Tim vs Energy GEANT
		'NIC_NIE': ('N', 'NE'), # hist : NIC vs NIE
	}

	if SPLITNODIGI:
		SNDTAGS = {
			'DS-HD' : ('X' ,),    # hist : Delta S Has Digi
			'DS-ND' : ('X' ,),    # hist : Delta S No Digi
			'EG-HD' : ('E' ,),    # hist : Energy GEANT Has Digi
			'EG-ND' : ('E' ,),    # hist : Energy GEANT No Digi
			'ET-HD' : ('E' ,),    # hist : Energy Tim Has Digi
			'ET-ND' : ('E' ,),    # hist : Energy Tim No Digi
			'NIC-HD': ('N' ,),    # hist : NIC Has Digi
			'NIC-ND': ('N' ,),    # hist : NIC No Digi
			'NIE-HD': ('N' ,),    # hist : NIE Has Digi
			'NIE-ND': ('N' ,),    # hist : NIE No Digi
		}
		TAGS.update(SNDTAGS)

	LTAG = FILE.lstrip('logs/log').rstrip('Layer.log')
	F = R.TFile('hists_'+LTAG+'.root', 'RECREATE')

	h = {}
	for TAG, CONFLIST in TAGS.iteritems():
		if len(CONFLIST) == 1:
			CONF = CONFS[CONFLIST[0]]
			h[TAG] = R.TH1F('h'+TAG, '', CONF['bins'], CONF['xmin'], CONF['xmax'])
		elif len(CONFLIST) == 2:
			CONF1 = CONFS[CONFLIST[0]]
			CONF2 = CONFS[CONFLIST[1]]
			h[TAG] = R.TH2F('h'+TAG, '', CONF1['bins'], CONF1['xmin'], CONF1['xmax'], CONF2['bins'], CONF2['xmin'], CONF2['xmax'])
		elif len(CONFLIST) == 3: # logscale
			CONF = CONFS[CONFLIST[0]]
			h[TAG] = R.TH1F('h'+TAG, '', CONF['bins'], CONF['binedges'])

	PIDHists = {'DE' : {}}
	for PID in PIDList:
		PIDHists['DE'][PID] = R.TH1F('PID'+'DE'+str(PID), '', CONFS['DE']['bins'], CONFS['DE']['xmin'], CONFS['DE']['xmax'])

	if SPLITNODIGI:
		DigiDict = {}
		LTAG = FILE.lstrip('logs/log')
		LTAG = LTAG.rstrip('Layer.log')
		CHAMDICTRAW = bash.check_output('python explorapedia.py -f {LTAG} -d -s'.format(LTAG=LTAG), shell=True).split('\n')
		for line in CHAMDICTRAW:
			if line == '': continue
			cols = line.split()
			DigiDict[int(cols[0])] = [int(i) for i in cols[1:]]

	PID = {}
	mod, orig = 0, 0
	for simhit in data:
		h['DS'     ].Fill(simhit.DeltaS  )
		h['EG'     ].Fill(simhit.ELossG  )
		h['ET'     ].Fill(simhit.ELossT  )
		h['NIC'    ].Fill(simhit.NIC     )
		h['NIE'    ].Fill(simhit.NIE     )
		h['AS'     ].Fill(simhit.AvgStep )
		h['AE'     ].Fill(simhit.AvgELoss)
		h['TOF'    ].Fill(simhit.TOF     )
		h['DS_EG'  ].Fill(simhit.DeltaS  , simhit.ELossG)
		h['DS_ET'  ].Fill(simhit.DeltaS  , simhit.ELossT)
		h['NIC_EG' ].Fill(simhit.NIC     , simhit.ELossG)
		h['NIC_ET' ].Fill(simhit.NIC     , simhit.ELossT)
		h['ET_EG'  ].Fill(simhit.ELossT  , simhit.ELossG)
		h['NIC_NIE'].Fill(simhit.NIC     , simhit.NIE   )

		#if simhit.DeltaS < 0.3:
		PIDHists['DE'][simhit.PID].Fill(simhit.ELossG - simhit.ELossT)

		if simhit.DeltaS < 0.3 and abs(simhit.PID) == 11:
			h['ET-M'].Fill(simhit.ELossT)
			mod += 1
		else:
			h['ET-O'].Fill(simhit.ELossT)
			orig += 1

		if SPLITNODIGI:
			if simhit.Event in DigiDict and simhit.Cham.id in DigiDict[simhit.Event]:
				print 1, simhit.Event, simhit.Cham.id
				h['DS-HD' ].Fill(simhit.DeltaS)
				h['EG-HD' ].Fill(simhit.ELossG)
				h['ET-HD' ].Fill(simhit.ELossT)
				h['NIC-HD'].Fill(simhit.NIC   )
				h['NIE-HD'].Fill(simhit.NIC   )
			else:
				print 0, simhit.Event, simhit.Cham.id
				h['DS-ND' ].Fill(simhit.DeltaS)
				h['EG-ND' ].Fill(simhit.ELossG)
				h['ET-ND' ].Fill(simhit.ELossT)
				h['NIC-ND'].Fill(simhit.NIC   )
				h['NIE-ND'].Fill(simhit.NIC   )

		if simhit.PID not in PID:
			PID[simhit.PID] = 0
		PID[simhit.PID] += 1
	print mod, orig

	#for pid, count in PID.iteritems():
	#	print pid, count

	for TAG in h:
		h[TAG].Write()
	for PID in PIDHists['DE']:
		PIDHists['DE'][PID].Write()

##### LOAD HISTOGRAMS FROM A FILE #####
elif FILETYPE == 'ROOT':
	f = R.TFile.Open(FILE)
	hNames = [str(x.GetName()) for x in list(f.GetListOfKeys())]
	h = {}
	PIDHists = { 'DE' : {} }
	for hName in hNames:
		if hName[0] == 'h':
			TAG = hName[1:]
			h[TAG] = f.Get('h'+TAG)
		elif hName[0:5] == 'PIDDE':
			PID = int(hName[5:])
			PIDHists['DE'][PID] = f.Get('PIDDE'+str(PID))

##### MAKE PLOTS #####
def StandardPlot(TAG, LUMI, XAXIS, FN):
	hist = h[TAG]
	plot = Plotter.Plot(hist)
	canvas = Plotter.Canvas(lumi=LUMI)
	canvas.addMainPlot(plot)
	plot.setTitles(X=XAXIS, Y='Counts')
	canvas.makeTransparent()
	canvas.mainPad.SetLogx(True)
	canvas.finishCanvas('BOB')
	canvas.save('pdfs/'+FN)
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

def PIDPlot(TAG):
	h = PIDHists[TAG][11].Clone()
	h.Add(PIDHists[TAG][-11].Clone())
	hplot = Plotter.Plot(h, legName = '', legType='f', option='hist')
	canvas = Plotter.Canvas(lumi='Energy Difference, Electron SimHits')
	canvas.addMainPlot(hplot)
	canvas.firstPlot.SetLineWidth(0)
	canvas.firstPlot.SetFillColor(R.kOrange)
	canvas.firstPlot.setTitles(X='E_{GEANT} #minus E_{CSCDigitizer} [keV]', Y='Counts')
	canvas.firstPlot.scaleTitleOffsets(1.1, 'X')
	canvas.makeTransparent()
	canvas.finishCanvas('BOB')
	canvas.save('pdfs/DE.pdf')
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

def EnergyPlot():
	plotG = Plotter.Plot(h['EG'], legName='GEANT'       , legType='l', option='hist')
	plotT = Plotter.Plot(h['ET'], legName='CSCDigitizer', legType='l', option='hist')
	canvas = Plotter.Canvas(lumi='Energy Loss')
	canvas.addMainPlot(plotT)
	canvas.addMainPlot(plotG)
	canvas.firstPlot.setTitles(X='Energy Loss [keV]', Y='Counts')
	canvas.firstPlot.SetMinimum(0)
	canvas.firstPlot.SetMaximum(3500)
	plotT.SetLineColor(R.kBlue)
	plotG.SetLineColor(R.kRed)
	canvas.makeLegend()
	canvas.legend.moveEdges(L=-0.1)
	canvas.legend.resizeHeight()
	X, Y = canvas.legend.GetX1(), canvas.legend.GetY2()
	canvas.drawText(pos=(X, Y     -0.01), align='tr', text='#color[{color}]{{#mu = {mean:.4f}}}'.format(color=R.kBlue, mean=plotT.GetMean()))
	canvas.drawText(pos=(X, Y-0.04-0.01), align='tr', text='#color[{color}]{{#mu = {mean:.4f}}}'.format(color=R.kRed , mean=plotG.GetMean()))
	canvas.makeTransparent()
	canvas.finishCanvas('BOB')
	canvas.save('pdfs/Energy.pdf')
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

def EnergyStackPlot():
	hs = R.THStack('hs', '')
	hs.Add(h['ET-M'])
	hs.Add(h['ET-O'])

	plotG  = Plotter.Plot(h['EG']  , legName='GEANT'                  , legType='l', option='hist')
	plotTM = Plotter.Plot(h['ET-M'], legName='CSCDigitizer (Modified)', legType='f', option='hist')
	plotTO = Plotter.Plot(h['ET-O'], legName='CSCDigitizer (Original)', legType='f', option='hist')
	plotHS = Plotter.Plot(hs       , option='hist')

	plotTM.SetFillColor(R.kAzure+1)
	plotTO.SetFillColor(R.kAzure-9)
	plotTM.SetLineWidth(0)
	plotTO.SetLineWidth(0)

	canvas = Plotter.Canvas(lumi='Energy Loss')
	canvas.addMainPlot(plotHS, addToPlotList=False)
	canvas.plotList.append(plotTM)
	canvas.plotList.append(plotTO)
	canvas.addMainPlot(plotG)

	plotG.SetLineColor(R.kRed)

	canvas.makeLegend()
	canvas.legend.moveEdges(L=-0.225)
	canvas.legend.resizeHeight()
	X, Y = canvas.legend.GetX1(), canvas.legend.GetY2()
	canvas.drawText(pos=(X, Y-0.02-0.01), align='tr', text='#color[{color}]{{#mu = {mean:.4f}}}'.format(color=R.kBlue, mean=plotHS.GetStack().Last().GetMean()))
	canvas.drawText(pos=(X, Y-0.08-0.01), align='tr', text='#color[{color}]{{#mu = {mean:.4f}}}'.format(color=R.kRed , mean=plotG.GetMean()))
	canvas.makeTransparent()
	canvas.firstPlot.setTitles(X='Energy Loss [keV]', Y='Counts')
	canvas.firstPlot.SetMinimum(0)
	canvas.firstPlot.SetMaximum(3500)
	canvas.finishCanvas('BOB')
	canvas.save('pdfs/Energy_Stack.pdf')
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

def ScatterPlot(TAG, LUMI, XAXIS, FN, YAXIS):
	hist = h[TAG]
	#if TAG[0] == 'N':
	#	gr = R.TGraph(2, np.array([0., CONFS['N']['xmax']]), np.array([0., CONFS['N']['xmax']*.034]))
	#	grplot = Plotter.Plot(gr, option='L')

	plot = Plotter.Plot(hist, option='colz')
	canvas = Plotter.Canvas(lumi=LUMI, cWidth=900)
	canvas.addMainPlot(plot)

	#if TAG[0] == 'N':
	#	canvas.addMainPlot(grplot)
	#	grplot.SetLineColor(R.kOrange)

	if plot.option == 'colz':
		canvas.scaleMargins(0.75, 'L')
		canvas.scaleMargins(2.25, 'R')
		plot.scaleTitleOffsets(0.7, 'Y')
		plot.setTitles(Z='Counts')

	plot.setTitles(X=XAXIS, Y=YAXIS)
	canvas.makeTransparent()
	canvas.finishCanvas('BOB')
	canvas.save('pdfs/'+FN)
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

StandardPlot('DS'     , '#Deltas'                          , '#Deltas [cm]'                  , 'DeltaS.pdf'              )
StandardPlot('NIC'    , 'Number of Ionizing Clusters'      , 'Number of Ionizing Clusters'   , 'NIC.pdf'                 )
StandardPlot('NIE'    , 'Number of Ionizing Electrons'     , 'Number of Ionizing Electrons'  , 'NIE.pdf'                 )
StandardPlot('AS'     , 'Average Step'                     , '#LTStep#GT [cm]'               , 'AvgStep.pdf'             )
StandardPlot('AE'     , 'Average Energy Loss per Step'     , '#LTEnergy Loss#GT [eV]'        , 'AvgELoss.pdf'            )
StandardPlot('TOF'    , 'Time of Flight'                   , 'Time of Flight [ns]'           , 'TOF.pdf'                 )

ScatterPlot ('DS_ET'  , 'Energy vs. #Deltas (CSCDigitizer)', '#Deltas [cm]'                  , 'Scatter_DeltaS_Tim.pdf'  , 'Energy Loss [keV]')
ScatterPlot ('DS_EG'  , 'Energy vs. #Deltas (GEANT)'       , '#Deltas [cm]'                  , 'Scatter_DeltaS_GEANT.pdf', 'Energy Loss [keV]')
ScatterPlot ('NIC_ET' , 'Energy vs. N.I.C. (CSCDigitizer)' , 'Number of Ionizing Clusters'   , 'Scatter_NIC_Tim.pdf'     , 'Energy Loss [keV]')
ScatterPlot ('NIC_EG' , 'Energy vs. N.I.C. (GEANT)'        , 'Number of Ionizing Clusters'   , 'Scatter_NIC_GEANT.pdf'   , 'Energy Loss [keV]')
ScatterPlot ('ET_EG'  , 'GEANT vs. CSCDigitizer'           , 'Energy Loss [keV]'             , 'Scatter_Tim_GEANT.pdf'   , 'Energy Loss [keV]')
ScatterPlot ('NIC_NIE', 'N.I.E. vs. N.I.C.'                , 'Number of Ionizing Clusters'   , 'Scatter_NIC_NIE.pdf'     , 'Number of Ionized Electrons')

PIDPlot('DE')
EnergyPlot()
EnergyStackPlot()

if SPLITNODIGI:
	StandardPlot('DS-HD' , '#Deltas, Has Digis'                      , '#Deltas [cm]'                  , 'DeltaS_HasDigi.pdf'      )
	StandardPlot('DS-ND' , '#Deltas, No Digis'                       , '#Deltas [cm]'                  , 'DeltaS_NoDigi.pdf'       )
	StandardPlot('NIC-HD', 'Number of Ionizing Clusters, Has Digis'  , 'Number of Ionizing Clusters'   , 'NIC_HasDigi.pdf'         )
	StandardPlot('NIC-ND', 'Number of Ionizing Clusters, No Digis'   , 'Number of Ionizing Clusters'   , 'NIC_NoDigi.pdf'          )
	StandardPlot('NIE-HD', 'Number of Ionizing Electrons, Has Digis' , 'Number of Ionizing Electrons'  , 'NIE_HasDigi.pdf'         )
	StandardPlot('NIE-ND', 'Number of Ionizing Electrons, No Digis'  , 'Number of Ionizing Electrons'  , 'NIE_NoDigi.pdf'          )
	StandardPlot('EG-HD' , 'Energy Loss, Has Digis (GEANT)'          , 'Energy Loss [keV]'             , 'Energy_HasDigi_GEANT.pdf')
	StandardPlot('EG-ND' , 'Energy Loss, No Digis (GEANT)'           , 'Energy Loss [keV]'             , 'Energy_NoDigi_GEANT.pdf' )
	StandardPlot('ET-HD' , 'Energy Loss, Has Digis (CSCDigitizer)'   , 'Energy Loss [keV]'             , 'Energy_HasDigi_Tim.pdf'  )
	StandardPlot('ET-ND' , 'Energy Loss, No Digis (CSCDigitizer)'    , 'Energy Loss [keV]'             , 'Energy_NoDigi_Tim.pdf'   )
