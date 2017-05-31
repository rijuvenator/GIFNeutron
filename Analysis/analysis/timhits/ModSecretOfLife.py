import numpy as np
import subprocess as bash
import argparse
import ROOT as R
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.ChamberHandler as CH

#R.gROOT.SetBatch(True)
R.gStyle.SetPalette(55)

#NLINES, FILE = 26766897, 'logs/skysong_92.log'
#NLINES, FILE = 21459460, 'logs/skysong_no50el.log'
#NLINES, FILE = 26792232, 'logs/skysong_noTOF.log'
#NLINES, FILE = 8097366 , 'logs/skysong_noLay.log'
NLINES, FILE = 26609958, 'logs/skysong_noBad.log'

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

TrackDict = {}
#CHAMDICTRAW = bash.check_output('python SOLCriteria.py -t 2>/dev/null', shell=True).split('\n')
CHAMDICTRAW = bash.check_output('python selectSimHits.py {FILE} -t 2>/dev/null'.format(FILE=ROOTFILE), shell=True).split('\n')
for line in CHAMDICTRAW:
	if line == '': continue
	cols = line.strip('\n').split()
	Event = int(cols[0])
	if Event not in TrackDict:
		TrackDict[Event] = []
	TrackDict[Event].append(int(cols[1]))
print len(TrackDict), '; TrackDict obtained'

DigiDict = {}
#CHAMDICTRAW = bash.check_output('python SOLCriteria.py -d 2>/dev/null', shell=True).split('\n')
CHAMDICTRAW = bash.check_output('python selectSimHits.py {FILE} -d 2>/dev/null'.format(FILE=ROOTFILE), shell=True).split('\n')
for line in CHAMDICTRAW:
	if line == '': continue
	cols = line.strip('\n').split()
	#DigiDict[int(cols[0])] = [int(i) for i in cols[1:]] # This is for use with SOLCriteria
	Event = int(cols[0])
	if Event not in DigiDict:
		DigiDict[Event] = []
	DigiDict[Event].append(int(cols[1]))
print len(DigiDict), '; DigiDict obtained'

f = R.TFile('WD_AQ.root', 'RECREATE')

##### MAKE HISTOGRAMS #####
#BINS = {
#	'TOF': [1000, np.logspace(1.,4.,1000+1)],
#	'WD' : [100, 0   , 0.25],
##	'AQ' : [100, 0   , 200 ],
#	'WDY': [200, -0.2, 0.2 ],
#	'WDZ': [200, -0.5, 0.5 ],
#	'DS' : [200,  0.0, 5.0 ],
#}
#h = {}
#for SL in ['', '_S', '_L']:
#	for HD in ['', '_YT', '_NT', '_YD', '_ND']:
#		for AXISKEY in BINS:
#			h['h'+AXISKEY+SL+HD] = R.TH1F('h'+AXISKEY+SL+HD, '', *BINS[AXISKEY])
##		for AXISKEY in ['WD_AQ']:
##			h['h'+AXISKEY+SL+HD] = R.TH2F('h'+AXISKEY+SL+HD, '', *(BINS['WD']+BINS['AQ']))
#		for AXISKEY in ['WDZ_DS']:
#			h['h'+AXISKEY+SL+HD] = R.TH2F('h'+AXISKEY+SL+HD, '', *(BINS['WDZ']+BINS['DS']))

N = len(data)
hdc = 0
inc = 0
for x, simhit in enumerate(data):
	if x%1000==0: print '{:2.0f}%'.format(x/float(N)*100), '\r',
	#fstring = '{:3d} {:8.4f} {:8.4f} {:8.4f} {:4d}'.format(simhit.Event, d, simhit.ELossT, simhit.ELossG, simhit.NIE)

	short = simhit.DeltaS < 0.3# and abs(simhit.PID) == 11
	hasDigiT = simhit.Event in TrackDict and simhit.TrackID in TrackDict[simhit.Event]
	hasDigiD = simhit.Event in DigiDict and simhit.Cham.id in DigiDict[simhit.Event]
	SL  = '_S'  if short    else '_L'
	HDT = '_YT' if hasDigiT else '_NT'
	HDD = '_YD' if hasDigiD else '_ND'
	
	if not hasDigiD:
		hdc += 1
		#print '{:4d} {:4d} {:10.7f} {:10.1f} {:8.3f} {:8.3f} {}'.format(hdc, simhit.NIC, simhit.DeltaS, simhit.TOF, simhit.ELossG, simhit.ELossT, simhit.SKIP+('' if not short else ' SHORT'))
		#print '{HDC:4d} {EVT:5d} {CID:3d} {TID:7d} {NZR:5d} {NRI:5d} {ZFR:.4f} {NIC:4d} {NIE:4d} {DLS:9.4f} {ISR}'.format(
		print '{HDC:4d} {EVT:5d} {CHM:s} {TID:7d} {NZR:5d} {NRI:5d} {ZFR:.4f} {NIC:4d} {NIE:4d} {DLS:9.4f} {ISR}'.format(
			HDC=hdc,
			EVT=simhit.Event,
			#CID=simhit.Cham.id,
			CHM=CH.Chamber(simhit.Cham.id).display(),
			TID=simhit.TrackID,
			NZR=simhit.ZF[0],
			NRI=simhit.ZF[1],
			ZFR=1 if simhit.ZF[1]==0 else simhit.ZF[0]/float(simhit.ZF[1]),
			NIC=simhit.NIC,
			NIE=simhit.NIE,
			DLS=simhit.DeltaS,
			ISR='SHORT' if simhit.DeltaS<0.3 else ''
		)
		#print '{:4d} {:s}'.format(hdc, 'YES' if simhit.ZF[1]==0 or simhit.ZF[0]/simhit.ZF[1] else '')

	if len(simhit.clusters) == 0:
		#print simhit.TrackID
		inc += 1
#		l.append(simhit.TrackID)
#		if not (simhit.ZF[1]==0 or simhit.ZF[0]/simhit.ZF[1]==1):
#			ll.append(simhit.TrackID)
		continue


	# this part does once per simhit instead of once per cluster. don't forget to comment out AQs
#	TOF = simhit.TOF
#	WD  = float('inf') if len(simhit.clusters)==0 else min([p[1]**2. + p[2]**2. for p in simhit.clusters])
#	WDY = float('inf') if len(simhit.clusters)==0 else min([p[1] for p in simhit.clusters], key=abs)
#	WDZ = float('inf') if len(simhit.clusters)==0 else min([p[2] for p in simhit.clusters], key=abs)
#
#	HISTS = {
#		'hTOF'    : (TOF,),
#		'hDS'     : (simhit.DeltaS,),
#		'hWD'     : (WD,),
#		'hWDY'    : (WDY,),
#		'hWDZ'    : (WDZ,),
#		'hWDZ_DS' : (WDZ,simhit.DeltaS),
#	}
#	for HIST in HISTS:
#		for key in [HIST, HIST+HDT, HIST+HDD, HIST+SL, HIST+SL+HDT, HIST+SL+HDD]:
#			h[key].Fill(*HISTS[HIST])

	#TOF = simhit.TOF
	#HISTS = {'hTOF':(TOF,), 'hDS':(simhit.DeltaS,)}
	#for HIST in HISTS:
	#	for key in [HIST, HIST+HDT, HIST+HDD, HIST+SL, HIST+SL+HDT, HIST+SL+HDD]:
	#		h[key].Fill(*HISTS[HIST])

	#for pos, AQ in zip(simhit.clusters, simhit.charges):
	#	WD = sum([j**2. for j in pos[1:]])#**0.5

	#	HISTS = {'hWD':(WD,), 'hAQ':(AQ,), 'hWD_AQ':(WD,AQ), 'hWDY':(pos[1],), 'hWDZ':(pos[2],), 'hWDZ_DS':(pos[2],simhit.DeltaS)}

	#	for HIST in HISTS:
	#		for key in [HIST, HIST+HDT, HIST+HDD, HIST+SL, HIST+SL+HDT, HIST+SL+HDD]:
	#			h[key].Fill(*HISTS[HIST])

print '100% of SimHits traversed'
print 'I skipped', inc, 'of the', N, 'SimHits'
#print ' '.join([str(x) for x in ll])


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

#for SL in ['', '_S', '_L']:
#	for HD in ['', '_YT', '_NT', '_YD', '_ND']:
#		for AXISKEY in BINS:
#			h['h'+AXISKEY+SL+HD].Write()
#		#for AXISKEY in ['WD_AQ', 'WDZ_DS']:
#		for AXISKEY in ['WDZ_DS']:
#			h['h'+AXISKEY+SL+HD].Write()
