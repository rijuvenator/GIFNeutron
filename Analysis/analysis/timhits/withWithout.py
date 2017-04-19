import ROOT as R
import sys

f = R.TFile.Open(sys.argv[1])
t = f.Get('GIFTree/GIFDigiTree')

N = t.GetEntries()
N_hasSH, N_hasWG = 0, 0
hasSH, noHasDigi = [], []
for entry in t:
	if len(t.sim_id) > 0:
		if len(t.wire_id) > 0: N_hasWG += 1
		N_hasSH += 1
		hasSH.extend(list(set(list(t.sim_id))))
		noHasDigi.extend([c for c in list(set(list(t.sim_id))) if c not in list(t.wire_id)])

print N, 'events, of which', N_hasSH, 'have Simhits, of which', N_hasWG, 'have wire group hits (so', N_hasSH-N_hasWG, 'did not)'
print len(hasSH), 'chambers had SimHits, of which', len(noHasDigi), 'did not have wire group hits (so', len(hasSH)-len(noHasDigi), 'did)'

import itertools
import Gif.Analysis.ChamberHandler as CH

print '\nBreakdown by Ring:'
hasSH.sort()
noHasDigi.sort()
hasSH_ESR = [CH.Chamber(x).display('{E}{S}{R}') for x in hasSH]
noHasDigi_ESR = [CH.Chamber(x).display('{E}{S}{R}') for x in noHasDigi]
stuff = {}
for key, group in itertools.groupby(noHasDigi_ESR):
	stuff[key] = [len(list(group))]
for key, group in itertools.groupby(hasSH_ESR):
	stuff[key].append(len(list(group)))
for key, thing in sorted(stuff.items()):
	print '{:3s} {:4d} {:4d} {:4.1f}%'.format(key, thing[0], thing[1], float(thing[0])/thing[1]*100)
