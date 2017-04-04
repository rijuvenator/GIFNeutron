import numpy as np
import subprocess as bash
import argparse
import ROOT as R
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.ChamberHandler as CH

#R.gROOT.SetBatch(True)
R.gStyle.SetPalette(55)

FILE = 'wireHitTestLog.txt'

##### FILL DATA STRUCTURE #####
class SimHit(object):
	def __init__(self, *data):
		self.Event    = data[0 ]
		self.TrackID  = data[1 ]
		self.DeltaS   = data[2 ]
		self.ELossG   = data[3 ]
		self.TOF      = data[4 ]
		self.ELossT   = data[5 ]
		self.NIC      = data[6 ]
		self.NIE      = data[7 ]
		self.PID      = data[8 ]
		self.AvgELoss = data[9 ]
		self.AvgStep  = data[10]
		self.Cham     = data[11]
	def addClusters(self, positions):
		self.clusters = positions
	def addCharges(self, charges):
		self.charges = charges

##### CREATE HISTOGRAMS FROM A LOG #####
# capitals become data members
f = open(FILE)
data = []
PIDList = []
fillPositions = False
for x, line in enumerate(f):
	if x%1000==0: print '{:2.0f}%'.format(x/float(12754277)*100), '\r',
	if fillPositions and ' / ' in line:
		cols = line.strip('\n').split()
		tup = [float(x) for x in cols[4].lstrip('(').rstrip(')').split(',')]
		positions.append(tup)
		charges.append(float(cols[6]))
		continue
	elif fillPositions and ' / ' not in line:
		fillPositions = False
		data[-1].addClusters(positions)
		data[-1].addCharges(charges)
	else: # fillPositions is False
		pass

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
		TOF      = float(cols[18])
		TrackID  = int(cols[23])
	elif 'SUMMARY: ionization' in line:
		cols = line.strip('\n').split()
		ELossT   = float(cols[33])
		DeltaS   = float(cols[8])
		NIC      = int(cols[16])
		NIE      = int(cols[23])
		AvgELoss = float(cols[26])
		AvgStep  = float(cols[12])
		data.append(SimHit(Event, TrackID, DeltaS, ELossG, TOF, ELossT, NIC, NIE, PID, AvgELoss, AvgStep, Cham))
		PIDList.append(PID)
	elif '[CSCWireHitSim]' in line:
		positions = []
		charges = []
		fillPositions = True
f.close()
PIDList = list(set(PIDList))
print '100% of file parsed'

TrackDict = {}
CHAMDICTRAW = bash.check_output('python SOLCriteria.py -t 2>/dev/null', shell=True).split('\n')
for line in CHAMDICTRAW:
	if line == '': continue
	cols = line.strip('\n').split()
	Event = int(cols[0])
	if Event not in TrackDict:
		TrackDict[Event] = []
	TrackDict[Event].append(int(cols[1]))
print len(TrackDict), '; TrackDict obtained'

DigiDict = {}
CHAMDICTRAW = bash.check_output('python SOLCriteria.py -d 2>/dev/null', shell=True).split('\n')
for line in CHAMDICTRAW:
	if line == '': continue
	cols = line.split()
	DigiDict[int(cols[0])] = [int(i) for i in cols[1:]]
print len(DigiDict), '; DigiDict obtained'

f = R.TFile('WD_AQ.root', 'RECREATE')

##### MAKE HISTOGRAMS #####
BINS = {
	'TOF': [1000, np.logspace(1.,4.,1000+1)],
	'WD' : [100, 0   , 0.25],
	'AQ' : [100, 0   , 200 ],
	'WDY': [200, -0.2, 0.2 ],
	'WDZ': [200, -0.5, 0.5 ],
}
h = {}
for SL in ['', '_S', '_L']:
	for HD in ['', '_YT', '_NT', '_YD', '_ND']:
		for AXISKEY in BINS:
			h['h'+AXISKEY+SL+HD] = R.TH1F('h'+AXISKEY+SL+HD, '', *BINS[AXISKEY])
		for AXISKEY in ['WD_AQ']:
			h['h'+AXISKEY+SL+HD] = R.TH2F('h'+AXISKEY+SL+HD, '', *(BINS['WD']+BINS['AQ']))

N = len(data)
for x, simhit in enumerate(data):
	#fstring = '{:3d} {:8.4f} {:8.4f} {:8.4f} {:4d}'.format(simhit.Event, d, simhit.ELossT, simhit.ELossG, simhit.NIE)

	short = simhit.DeltaS < 0.3 and abs(simhit.PID) == 11
	hasDigiT = simhit.Event in TrackDict and simhit.TrackID in TrackDict[simhit.Event]
	hasDigiD = simhit.Event in DigiDict and simhit.Cham.id in DigiDict[simhit.Event]

	for pos, AQ in zip(simhit.clusters, simhit.charges):
		TOF = simhit.TOF
		WD = sum([j**2. for j in pos[1:]])#**0.5
		SL = '_S' if short else '_L'
		HDT = '_YT' if hasDigiT else '_NT'
		HDD = '_YD' if hasDigiD else '_ND'

		HISTS = {'hTOF':(TOF,), 'hWD':(WD,), 'hAQ':(AQ,), 'hWD_AQ':(WD,AQ), 'hWDY':(pos[1],), 'hWDZ':(pos[2],)}

		for HIST in HISTS:
			for key in [HIST, HIST+HDT, HIST+HDD, HIST+SL, HIST+SL+HDT, HIST+SL+HDD]:
				h[key].Fill(*HISTS[HIST])


#h['hWD'     ].Write()
#h['hWD_S'   ].Write()
#h['hWD_S_YT'].Write()
#h['hWD_S_NT'].Write()
#h['hWD_S_YD'].Write()
#h['hWD_S_ND'].Write()
#
#print 'hWD      :', h['hWD'     ].GetEntries()
#print 'hWD_S    :', h['hWD_S'   ].GetEntries()
#print 'hWD_S_YT :', h['hWD_S_YT'].GetEntries()
#print 'hWD_S_NT :', h['hWD_S_NT'].GetEntries()
#print 'hWD_S_YD :', h['hWD_S_YD'].GetEntries()
#print 'hWD_S_ND :', h['hWD_S_ND'].GetEntries()

for SL in ['', '_S', '_L']:
	for HD in ['', '_YT', '_NT', '_YD', '_ND']:
		for AXISKEY in BINS:
			h['h'+AXISKEY+SL+HD].Write()
		for AXISKEY in ['WD_AQ']:
			h['h'+AXISKEY+SL+HD].Write()
