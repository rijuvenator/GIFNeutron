import ROOT as R
import sys

FILE = sys.argv[1]

if sys.argv[2] == '-t':
	TRACK = True
elif sys.argv[2] == '-d':
	TRACK = False
else:
	exit()

#f = open('meh')
#haveList = []
#for line in f:
#	haveList.append(tuple([int(i) for i in line.strip('\n').split()]))

#f = R.TFile.Open('roots/output25000_HPT_Hack9TOF_1Layer.root')
f = R.TFile.Open(FILE)
t = f.Get('GIFTree/GIFDigiTree')

nChamND, nCham, nTracks = 0, 0, 0
for entry in t:
	#if len(t.sim_id) > 0:
	#	for i, c in enumerate(list(t.sim_id)):
	#		if (t.Event_EventNumber, t.sim_track_id[i]) not in haveList:
	#			print t.Event_EventNumber, t.sim_track_id[i]

	if len(t.sim_id) > 0:
		#nChamND += len(set([c for c in list(t.sim_id) if c not in list(t.wire_id)]))
		#nCham += len(set(list(t.sim_id)))

		if not TRACK:
			for c in list(t.sim_id):
				if c in list(t.wire_id):
					print t.Event_EventNumber, c

		else:
			for i, c in enumerate(list(t.sim_id)):
				if c in list(t.wire_id):
					#nTracks += 1
					print t.Event_EventNumber, t.sim_track_id[i]
