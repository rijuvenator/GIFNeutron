import ROOT as R
import Gif.NeutronSim.ChamberHandler as CH

f = R.TFile.Open('../test.root')
t = f.Get('GIFTree/GIFDigiTree')

CHAMS = {}
for idx, entry in enumerate(t):
	chams = [list(i) for i in list(t.muon_chamlist)]
	if len(chams) < 2: continue
	lcts = list(t.lct_id)
	if len(lcts) == 0: continue
	if len(chams) == 2:
		if chams[0] == [] or chams[1] == []: continue
		#print '{:4d} | {}'.format(idx, " ".join([str(i) for i in lcts]))
		for c in chams[0]:
			if c not in CHAMS.keys():
				CHAMS[c] = [idx]
			else:
				CHAMS[c].append(idx)
		for c in chams[1]:
			if c not in CHAMS.keys():
				CHAMS[c] = [idx]
			else:
				CHAMS[c].append(idx)

for c in CHAMS.keys():
	l = list(set(CHAMS[c]))
	l.sort()
	CHAMS[c] = l
	ch = CH.Chamber(c)
	print '{:<9s} | {:3d} | {}'.format(ch.display('ME{E}{S}/{R}/{C}'), c, " ".join([str(x) for x in CHAMS[c]]))
