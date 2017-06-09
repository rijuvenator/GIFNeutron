import ROOT as R
import sys
import itertools

FILE = sys.argv[1]
f = R.TFile.Open(FILE)
t = f.Get('GIFTree/GIFDigiTree')

for entry in t:
	if len(t.wire_id) == 0: continue
	print t.Event_EventNumber,
	chams = list(t.wire_id)
	chams.sort()
	for cham, g in itertools.groupby(chams):
		print '{},{}'.format(cham, len(list(g))),
	print ''
