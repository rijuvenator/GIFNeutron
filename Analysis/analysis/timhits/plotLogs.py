import numpy as np
import subprocess as bash
import argparse
import ROOT as R
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.ChamberHandler as CH

R.gROOT.SetBatch(True)

parser = argparse.ArgumentParser()
parser.add_argument('FILE'                 ,                      help='event log file')
parser.add_argument('-snd', '--SPLITNODIGI', action='store_true', help='split no digi' )
args = parser.parse_args()
FILE = args.FILE
SPLITNODIGI = args.SPLITNODIGI

##### FILL DATA STRUCTURE #####
class SimHit(object):
	def __init__(self, *data):
		self.Event    = data[0]
		self.DeltaS   = data[1]
		self.ELossG   = data[2]
		self.ELossT   = data[3]
		self.NIE      = data[4]
		self.PID      = data[5]
		self.AvgELoss = data[6]
		self.AvgStep  = data[7]
		self.Cham     = data[8]

# capitals become data members
f = open(FILE)
data = []
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
		ELossG   = float(cols[-2])
	elif 'SUMMARY: ionization' in line:
		cols = line.strip('\n').split()
		ELossT   = float(cols[-2])
		DeltaS   = float(cols[8])
		NIE      = int(cols[16])
		AvgELoss = float(cols[26])
		AvgStep  = float(cols[12])
		data.append(SimHit(Event, DeltaS, ELossG, ELossT, NIE, PID, AvgELoss, AvgStep, Cham))
f.close()

##### DO ANALYSIS #####

CONFS = {
	#'E' : {'bins' : 180, 'xmin' : 0, 'xmax' : 60},
	'E' : {'bins' : 45 , 'xmin' : 0, 'xmax' : 15   }, # Energy axes
	'X' : {'bins' : 100, 'xmin' : 0, 'xmax' : 5    }, # Delta S axes
	'N' : {'bins' : 100, 'xmin' : 0, 'xmax' : 400  }, # NIE axes
	'AS': {'bins' : 100, 'xmin' : 0, 'xmax' : 0.027}, # AvgStep axes
	'AE': {'bins' : 100, 'xmin' : 0, 'xmax' : 300  }, # AvgELoss axes
}

TAGS = {
	'DS'    : ('X' ,),    # hist : Delta S 
	'EG'    : ('E' ,),    # hist : Energy GEANT
	'ET'    : ('E' ,),    # hist : Energy Tim
	'NIE'   : ('N' ,),    # hist : NIE
	'AS'    : ('AS',),    # hist : AvgStep
	'AE'    : ('AE',),    # hist : AvgELoss
	'DS_EG' : ('X', 'E'), # hist : Delta S vs Energy GEANT
	'DS_ET' : ('X', 'E'), # hist : Delta S vs Energy Tim
	'NIE_EG': ('N', 'E'), # hist : NIE vs Energy GEANT
	'NIE_ET': ('N', 'E'), # hist : NIE vs Energy Tim
	'ET_EG' : ('E', 'E'), # hist : Energy Tim vs Energy GEANT
}

if SPLITNODIGI:
	SNDTAGS = {
		'DS-HD' : ('X' ,),    # hist : Delta S Has Digi
		'DS-ND' : ('X' ,),    # hist : Delta S No Digi
		'EG-HD' : ('E' ,),    # hist : Energy GEANT Has Digi
		'EG-ND' : ('E' ,),    # hist : Energy GEANT No Digi
		'ET-HD' : ('E' ,),    # hist : Energy Tim Has Digi
		'ET-ND' : ('E' ,),    # hist : Energy Tim No Digi
		'NIE-HD': ('N' ,),    # hist : NIE Has Digi
		'NIE-ND': ('N' ,),    # hist : NIE No Digi
	}
	TAGS.update(SNDTAGS)

h = {}
for TAG, CONFLIST in TAGS.iteritems():
	if len(CONFLIST) == 1:
		CONF = CONFS[CONFLIST[0]]
		h[TAG] = R.TH1F('h'+TAG, '', CONF['bins'], CONF['xmin'], CONF['xmax'])
	elif len(CONFLIST) == 2:
		CONF1 = CONFS[CONFLIST[0]]
		CONF2 = CONFS[CONFLIST[1]]
		h[TAG] = R.TH2F('h'+TAG, '', CONF1['bins'], CONF1['xmin'], CONF1['xmax'], CONF2['bins'], CONF2['xmin'], CONF2['xmax'])

if SPLITNODIGI:
	DigiDict = {}
	LTAG = FILE.lstrip('logs/log')
	LTAG = LTAG.strip('Layer')
	CHAMDICTRAW = bash.check_output('python explorapedia.py -f {LTAG} -d -s'.format(LTAG=LTAG), shell=True).split('\n')
	for line in CHAMDICTRAW:
		if line == '': continue
		cols = line.split()
		DigiDict[int(cols[0])] = [int(i) for i in cols[1:]]

PID = {}
for simhit in data:
	h['DS'    ].Fill(simhit.DeltaS  )
	h['EG'    ].Fill(simhit.ELossG  )
	h['ET'    ].Fill(simhit.ELossT  )
	h['NIE'   ].Fill(simhit.NIE     )
	h['AS'    ].Fill(simhit.AvgStep )
	h['AE'    ].Fill(simhit.AvgELoss)
	h['DS_EG' ].Fill(simhit.DeltaS  , simhit.ELossG)
	h['DS_ET' ].Fill(simhit.DeltaS  , simhit.ELossT)
	h['NIE_EG'].Fill(simhit.NIE     , simhit.ELossG)
	h['NIE_ET'].Fill(simhit.NIE     , simhit.ELossT)
	h['ET_EG' ].Fill(simhit.ELossT  , simhit.ELossG)

	if SPLITNODIGI:
		if simhit.Event in DigiDict and simhit.Cham.id in DigiDict[simhit.Event]:
			print 1, simhit.Event, simhit.Cham.id
			h['DS-HD' ].Fill(simhit.DeltaS)
			h['EG-HD' ].Fill(simhit.ELossG)
			h['ET-HD' ].Fill(simhit.ELossT)
			h['NIE-HD'].Fill(simhit.NIE   )
		else:
			print 0, simhit.Event, simhit.Cham.id
			h['DS-ND' ].Fill(simhit.DeltaS)
			h['EG-ND' ].Fill(simhit.ELossG)
			h['ET-ND' ].Fill(simhit.ELossT)
			h['NIE-ND'].Fill(simhit.NIE   )

	if simhit.PID not in PID:
		PID[simhit.PID] = 0
	PID[simhit.PID] += 1

#for pid, count in PID.iteritems():
#	print pid, count

##### MAKE PLOTS #####
def StandardPlot(TAG, LUMI, XAXIS, FN):
	hist = h[TAG]
	plot = Plotter.Plot(hist)
	canvas = Plotter.Canvas(lumi=LUMI)
	canvas.addMainPlot(plot)
	plot.setTitles(X=XAXIS, Y='Counts')
	#canvas.makeTransparent()
	canvas.finishCanvas()
	canvas.save('pdfs/'+FN)
	R.SetOwnership(canvas, False)

def EnergyPlot():
	plotG = Plotter.Plot(h['EG'], legName='GEANT'       , legType='l', option='hist')
	plotT = Plotter.Plot(h['ET'], legName='CSCDigitizer', legType='l', option='hist')
	canvas = Plotter.Canvas(lumi='Energy Loss')
	canvas.addMainPlot(plotT)
	canvas.addMainPlot(plotG)
	canvas.firstPlot.setTitles(X='Energy Loss [keV]', Y='Counts')
	plotT.SetLineColor(R.kBlue)
	plotG.SetLineColor(R.kRed)
	canvas.makeLegend()
	canvas.legend.moveEdges(L=-0.1)
	canvas.legend.resizeHeight()
	X, Y = canvas.legend.GetX1NDC(), canvas.legend.GetY2NDC()
	canvas.drawText(pos=(X, Y     -0.01), align='tr', text='#color[{color}]{{#mu = {mean:.4f}}}'.format(color=R.kBlue, mean=plotT.GetMean()))
	canvas.drawText(pos=(X, Y-0.04-0.01), align='tr', text='#color[{color}]{{#mu = {mean:.4f}}}'.format(color=R.kRed , mean=plotG.GetMean()))
	#canvas.makeTransparent()
	canvas.finishCanvas()
	canvas.save('pdfs/Energy.pdf')
	R.SetOwnership(canvas, False)

def ScatterPlot(TAG, LUMI, XAXIS, FN):
	hist = h[TAG]
	#if TAG[0] == 'N':
	#	gr = R.TGraph(2, np.array([0., CONFS['N']['xmax']]), np.array([0., CONFS['N']['xmax']*.034]))
	#	grplot = Plotter.Plot(gr, option='L')

	plot = Plotter.Plot(hist, option='')
	canvas = Plotter.Canvas(lumi=LUMI)
	canvas.addMainPlot(plot)

	#if TAG[0] == 'N':
	#	canvas.addMainPlot(grplot)
	#	grplot.SetLineColor(R.kOrange)

	plot.setTitles(X=XAXIS, Y='Energy Loss [keV]')
	#canvas.makeTransparent()
	canvas.finishCanvas()
	canvas.save('pdfs/'+FN)
	R.SetOwnership(canvas, False)

StandardPlot('DS'    , '#Deltas'                                , '#Deltas [cm]'                 , 'DeltaS.pdf'              )
StandardPlot('NIE'   , 'Number of Ionizing Electrons'           , 'Number of Ionizing Electrons' , 'NIE.pdf'                 )
StandardPlot('AS'    , 'Average Step'                           , '#LTStep#GT [cm]'              , 'AvgStep.pdf'             )
StandardPlot('AE'    , 'Average Energy Loss per Step'           , '#LTEnergy Loss#GT [eV]'       , 'AvgELoss.pdf'            )
ScatterPlot ('DS_ET' , 'Energy vs. #Deltas (CSCDigitizer)'      , '#Deltas [cm]'                 , 'Scatter_DeltaS_Tim.pdf'  )
ScatterPlot ('DS_EG' , 'Energy vs. #Deltas (GEANT)'             , '#Deltas [cm]'                 , 'Scatter_DeltaS_GEANT.pdf')
ScatterPlot ('NIE_ET', 'Energy vs. N.I.E. (CSCDigitizer)'       , '#Number of Ionizing Electrons', 'Scatter_NIE_Tim.pdf'     )
ScatterPlot ('NIE_EG', 'Energy vs. N.I.E. (GEANT)'              , '#Number of Ionizing Electrons', 'Scatter_NIE_GEANT.pdf'   )
ScatterPlot ('ET_EG' , 'GEANT vs. CSCDigitizer'                 , 'Energy Loss [keV]'            , 'Scatter_Tim_GEANT.pdf'   )
EnergyPlot()

if SPLITNODIGI:
	StandardPlot('DS-HD' , '#Deltas, Has Digis'                     , '#Deltas [cm]'                 , 'DeltaS_HasDigi.pdf'      )
	StandardPlot('DS-ND' , '#Deltas, No Digis'                      , '#Deltas [cm]'                 , 'DeltaS_NoDigi.pdf'       )
	StandardPlot('NIE-HD', 'Number of Ionizing Electrons, Has Digis', 'Number of Ionizing Electrons' , 'NIE_HasDigi.pdf'         )
	StandardPlot('NIE-ND', 'Number of Ionizing Electrons, No Digis' , 'Number of Ionizing Electrons' , 'NIE_NoDigi.pdf'          )
	StandardPlot('EG-HD' , 'Energy Loss, Has Digis (GEANT)'         , 'Energy Loss [keV]'            , 'Energy_HasDigi_GEANT.pdf')
	StandardPlot('EG-ND' , 'Energy Loss, No Digis (GEANT)'          , 'Energy Loss [keV]'            , 'Energy_NoDigi_GEANT.pdf' )
	StandardPlot('ET-HD' , 'Energy Loss, Has Digis (CSCDigitizer)'  , 'Energy Loss [keV]'            , 'Energy_HasDigi_Tim.pdf'  )
	StandardPlot('ET-ND' , 'Energy Loss, No Digis (CSCDigitizer)'   , 'Energy Loss [keV]'            , 'Energy_NoDigi_Tim.pdf'   )
