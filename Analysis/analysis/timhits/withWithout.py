import ROOT as R
import sys
import Gif.Analysis.ChamberHandler as CH

f = R.TFile.Open(sys.argv[1])
t = f.Get('GIFTree/GIFDigiTree')

N = t.GetEntries()
N_hasSH, N_hasWG = 0, 0
N_SH, N_SHWOD, N_short = 0, 0, 0
hasSH, noHasDigi = [], []
for entry in t:
	if len(t.sim_id) > 0:
		if len(t.wire_id) > 0: N_hasWG += 1
		N_hasSH += 1
		N_SH += len(t.sim_id)
		hasSH.extend(list(set(list(t.sim_id))))
		noChams = [c for c in list(set(list(t.sim_id))) if c not in list(t.wire_id)]
		noHasDigi.extend(noChams)
		N_SHWOD += len([c for c in list(t.sim_id) if c not in list(t.wire_id)])

		#if noChams != []: print '** {}'.format(t.Event_EventNumber), [CH.Chamber(i).display() for i in noChams], [t.sim_track_id[i] for i, x in enumerate(list(t.sim_id)) if x in noChams]

		X, Y, Z = (list(t.sim_entry_x),list(t.sim_exit_x)), (list(t.sim_entry_y),list(t.sim_exit_y)), (list(t.sim_entry_z),list(t.sim_exit_z))
#		for i, c in enumerate(list(t.sim_id)):
#			if c not in list(t.wire_id):
#				print ((X[1][i]-X[0][i])**2 + (Y[1][i]-Y[0][i])**2 + (Z[1][i]-Z[0][i])**2)**0.5

		N_short += len([1 for d in [((X[1][i]-X[0][i])**2 + (Y[1][i]-Y[0][i])**2 + (Z[1][i]-Z[0][i])**2)**0.5 for i in range(len(X[0])) if abs(list(t.sim_particle_id)[i])!=13] if d<0.3])

print N, 'events, of which', N_hasSH, 'have SimHits, of which', N_hasWG, 'have wire group hits (so', N_hasSH-N_hasWG, 'did not)'
print len(hasSH), 'chambers had SimHits, of which', len(noHasDigi), 'did not have wire group hits (so', len(hasSH)-len(noHasDigi), 'did)'
print N_SH, 'SimHits, of which', N_SHWOD, 'were in chambers without digis'
#print N_short, 'were shorter than 0.3 cm'

#import itertools
#import Gif.Analysis.ChamberHandler as CH
#
#print '\nBreakdown by Ring:'
#hasSH.sort()
#noHasDigi.sort()
#hasSH_ESR = [CH.Chamber(x).display('{E}{S}{R}') for x in hasSH]
#noHasDigi_ESR = [CH.Chamber(x).display('{E}{S}{R}') for x in noHasDigi]
#stuff = {}
#for key, group in itertools.groupby(noHasDigi_ESR):
#	stuff[key] = [len(list(group))]
#for key, group in itertools.groupby(hasSH_ESR):
#	stuff[key].append(len(list(group)))
#for key, thing in sorted(stuff.items()):
#	print '{:3s} {:4d} {:4d} {:4.1f}%'.format(key, thing[0], thing[1], float(thing[0])/thing[1]*100)
