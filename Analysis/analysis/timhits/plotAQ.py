import numpy as np
import subprocess as bash
import argparse
import ROOT as R
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.ChamberHandler as CH

#R.gROOT.SetBatch(True)
R.gStyle.SetPalette(55)

#NLINES, FILE = 26766897, 'logs/skysong_92.log'
NLINES, FILE = 21501703, 'logs/skysong_good.log'
ROOTFILE = FILE.replace('logs/','roots/').replace('.log','.root')

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
		self.SKIP     = data[12]
		self.ZF       = data[13]
	def addClusters(self, positions):
		self.clusters = positions[:]
	def addCharges(self, charges):
		self.charges = charges[:]

##### CREATE HISTOGRAMS FROM A LOG #####
# capitals become data members
f = open(FILE)
data = []
PIDList = []
fillPositions = False
state = ''
setState = False
isFirst = True
resetZeros = True
justFilled = True
nRiju, nZeros = 0, 0
for x, line in enumerate(f):
	if x%1000==0: print '{:2.0f}%'.format(x/float(NLINES)*100), '\r',

	# start of new event/chamber with simhits
	if 'starting event' in line:
		if not justFilled:
			data.append(SimHit(Event, TrackID, DeltaS, ELossG, TOF, ELossT, NIC, NIE, PID, AvgELoss, AvgStep, Cham, state, (nZeros, nRiju)))
			PIDList.append(PID)
			data[-1].addClusters(positions)
			data[-1].addCharges(charges)
			nZeros, nRiju = 0, 0
			justFilled = True

		cols = line.strip('\n').split()
		Event    = int(cols[3])
		continue
	elif 'in layer' in line:
		if not justFilled:
			data.append(SimHit(Event, TrackID, DeltaS, ELossG, TOF, ELossT, NIC, NIE, PID, AvgELoss, AvgStep, Cham, state, (nZeros, nRiju)))
			PIDList.append(PID)
			data[-1].addClusters(positions)
			data[-1].addCharges(charges)
			nZeros, nRiju = 0, 0
			justFilled = True

		cols = line.strip('\n').split()
		chamRaw  = cols[6:11]
		e,s,r,c  = 1 if chamRaw[0] == 'E:1' else -1, int(chamRaw[1][2:]), int(chamRaw[2][2:]), int(chamRaw[3][2:])
		Cham     = CH.Chamber(CH.serialID(e, s, r, c))
		continue
	
	# start of new simhit
	if 'START OF NEW SIMHIT' in line:
		setState = True
		if isFirst:
			isFirst = False
			continue

		if not justFilled:
			# fill data here
			data.append(SimHit(Event, TrackID, DeltaS, ELossG, TOF, ELossT, NIC, NIE, PID, AvgELoss, AvgStep, Cham, state, (nZeros, nRiju)))
			PIDList.append(PID)
			data[-1].addClusters(positions)
			data[-1].addCharges(charges)
			nZeros, nRiju = 0, 0
			TrackID, DeltaS, ELossG, TOF, ELossT, NIC, NIE, PID, AvgELoss, AvgStep, state = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

		justFilled = False
		continue

	# note what type it is -- I know this unambiguously now
	if setState:
		setState = False
		if 'n_try' in line:
			state = 'NTRY'
		elif 'is too large' in line:
			state = 'ELOSS'
		elif '----------' in line:
			state = 'NORMAL'
		continue

	# gather properties
	if 'particle type' in line:
		realState = str(state)
		cols = line.strip('\n').split()
		PID      = int(cols[3])
		ELossG   = float(cols[13])
		TOF      = float(cols[18])
		TrackID  = int(cols[23])
		continue

	if 'SUMMARY: ionization' in line:
		cols = line.strip('\n').split()
		ELossT   = float(cols[33])
		DeltaS   = float(cols[8])
		NIC      = int(cols[16])
		NIE      = int(cols[23])
		AvgELoss = float(cols[26])
		AvgStep  = float(cols[12])
		continue

	# keep track of how many are outside of the layer geometry
	if '[RIJU] ' in line:
		if resetZeros:
			nRiju, nZeros = 0, 0
			resetZeros = False
		nRiju += 1
		if '[RIJU] 0' in line:
			nZeros += 1
		continue

	# if i've gotten to here, the [RIJU] block is done, so
	resetZeros = True

	# prepare to fill positions and charges
	if '[CSCWireHitSim]' in line:
		positions = []
		charges = []
		fillPositions = True
		continue

	# fill positions
	if fillPositions and ' / ' in line and 'SIGNALPRINT' not in line:
		cols = line.strip('\n').split()
		tup = [float(x) for x in cols[4].lstrip('(').rstrip(')').split(',')]
		positions.append(tup)
		charges.append(float(cols[6]))
		continue

	# done; terminate filling positions
	if fillPositions and (' / ' not in line or 'SIGNALPRINT' in line):
		fillPositions = False

# one last time for the last simhit
data.append(SimHit(Event, TrackID, DeltaS, ELossG, TOF, ELossT, NIC, NIE, PID, AvgELoss, AvgStep, Cham, state, (nZeros, nRiju)))
PIDList.append(PID)
data[-1].addClusters(positions)
data[-1].addCharges(charges)

f.close()
PIDList = list(set(PIDList))
print '100% of file parsed'

WireDict = {}
WireDictRaw = bash.check_output('python countWireHits.py {FILE}'.format(FILE=ROOTFILE), shell=True).split('\n')
for line in WireDictRaw:
	if line == '': continue
	cols = line.strip('\n').split()
	Event = int(cols[0])
	WireDict[Event] = []
	for pair in cols[1:]:
		WireDict[Event].append(tuple(int(i) for i in pair.split(',')))

f = R.TFile('WD_AQ.root', 'RECREATE')

##h = R.TH1F('h', '', 100, 0, 200)
#h = R.TH1F('h', '', 100, 0, 5000)
#
#for simhit in data:
#	#if abs(simhit.PID) == 13: continue
#	#for q in simhit.charges:
#	#	h.Fill(q)
#	if len(simhit.charges) == 0: continue
#	h.Fill(sum(simhit.charges))
#h.Write()
#
##import itertools
##hCPH = R.TH1F('h', '', 100, 0, 5000)
### this line should not be necessary; they should already be sorted by event
###sortedSimHits = sorted(data, key=lambda s: s.Event)
##for event, simHitsGen in itertools.groupby(data, key=lambda s: s.Event):
##	simHits = list(simHitsGen)
##	simHits.sort(key=lambda s: s.Cham.id)
##	for cham, simHitsCham in itertools.groupby(simHits, key=lambda s: s.Cham.id):
##		nWG = 0
##		if event in WireDict:
##			for c, n in WireDict[event]:
##				if c == cham:
##					nWG += n
##		if nWG == 0: continue
##
##		AQ = sum([sum(simhit.charges) for simhit in simHitsCham])
##		hCPH.Fill(float(AQ)/float(nWG))
##hCPH.Write()

hCSH1 = R.TH1F('hCSH1', '', 100, 0, 5000)
hCSH2 = R.TH1F('hCSH2', '', 100, 0, 5000)

for simhit in data:
	#if abs(simhit.PID) == 13: continue
	#for q in simhit.charges:
	#	h.Fill(q)
	if len(simhit.charges) == 0: continue
	if simhit.Cham.station == 1 and simhit.Cham.ring == 1:
		hCSH1.Fill(sum(simhit.charges))
	else:
		hCSH2.Fill(sum(simhit.charges))
hCSH1.Write()
hCSH2.Write()

import itertools
hCPH1 = R.TH1F('hCPH1', '', 100, 0, 5000)
hCPH2 = R.TH1F('hCPH2', '', 100, 0, 5000)
# this line should not be necessary; they should already be sorted by event
#sortedSimHits = sorted(data, key=lambda s: s.Event)
for event, simHitsGen in itertools.groupby(data, key=lambda s: s.Event):
	simHits = list(simHitsGen)
	simHits.sort(key=lambda s: s.Cham.id)
	for cham, simHitsCham in itertools.groupby(simHits, key=lambda s: s.Cham.id):
		nWG = 0
		if event in WireDict:
			for c, n in WireDict[event]:
				if c == cham:
					nWG += n
		if nWG == 0: continue

		ch = CH.Chamber(cham)
		AQ = sum([sum(simhit.charges) for simhit in simHitsCham])
		if ch.station == 1 and ch.ring == 1:
			hCPH1.Fill(float(AQ)/float(nWG))
		else:
			hCPH2.Fill(float(AQ)/float(nWG))
hCPH1.Write()
hCPH2.Write()
