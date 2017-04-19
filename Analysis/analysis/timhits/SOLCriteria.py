import ROOT as R
import argparse
import subprocess as bash

# This is a version of explorapedia that does nothing except print out lines
# that are intended for use in secretOfLife.py to determine whether or not a SimHit
# was digitized. There are two sets of criteria: track and digi.
# track means SH by SH print out the event and trackID if the SH is near a wire.
# digi means print out the event and chamList of chambers that have wires.

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--TRACK', action='store_true')
parser.add_argument('-d', '--DIGI' , action='store_true')
args = parser.parse_args()

if args.TRACK:
	import Gif.Analysis.Primitives as Primitives

FILE = '25000_HPT_Hack3_1'

# make gaslist and timlist
eventHitList = bash.check_output('python printLogStats.py logs/log'+FILE+'Layer.log -e -s', shell=True)
lines = eventHitList.split('\n')
gaslist, timlist = [], []
for line in lines:
	if line == '': continue
	cols = line.split()
	gaslist.append(int(cols[0]))
	timlist.append(int(cols[1]))
gas = dict(zip(gaslist, timlist))

# run over the tree
f = R.TFile.Open('roots/output'+FILE+'Layer.root')
t = f.Get('GIFTree/GIFDigiTree')

if args.DIGI:
	t.SetBranchStatus('*', 0)
	BranchList = ['sim_id', 'comp_id', 'wire_id', 'strip_id', 'lct_id', 'alct_id', 'clct_id']
	for br in BranchList:
		t.SetBranchStatus(br, 1)

for idx, entry in enumerate(t):
	if len(t.sim_id) > 0:
		if idx+1 in gaslist:

			if args.DIGI:
				digichamlist = list(set([str(cham) for cham in list(t.sim_id) if cham in list(t.wire_id)]))
				if digichamlist != []:
					print idx+1, ' '.join(digichamlist)

			if args.TRACK:
				E = Primitives.ETree(t, DecList=['WIRE','SIMHIT'])
				simhits = [Primitives.SimHit(E, i) for i in range(len(t.sim_id))]
				wires   = [Primitives.Wire(E, i) for i in range(len(t.wire_id))]
				def isNearWH(sh):
					return sum([sh.layer==wire.layer and abs(sh.wirePos-wire.number)<1 for wire in wires])>0
				for sh in simhits:
					if isNearWH(sh):
						print idx+1, sh.trackID
