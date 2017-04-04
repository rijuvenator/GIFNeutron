import ROOT as R
import sys

f = R.TFile.Open(sys.argv[1])
t = f.Get('GIFTree/GIFDigiTree')

N = t.GetEntries()
hasE, nohasE = 0, 0
hasC, nohasC = 0, 0
for entry in t:
	if len(t.sim_id) > 0:
		if len(t.wire_id) > 0:
			hasE += 1
		else:
			nohasE += 1
		chamlist = list(set(list(t.sim_id)))
		for c in chamlist:
			if c in list(t.wire_id):
				hasC += 1
			else:
				nohasC += 1

print N, 'entries'
print hasC, 'chambers with, in', hasE, 'events'
print nohasC, 'chambers without, in', nohasE, 'events'
