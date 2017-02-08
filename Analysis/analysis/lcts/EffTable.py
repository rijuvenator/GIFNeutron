import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import sys

MEASGRID = '../datafiles/measgrid'
FF = 1 if len(sys.argv) < 2 else int(sys.argv[1])
SCINT = {1:{'HS':(25,72),'WG':(37,43)},110:{'HS':(8,38),'WG':(55,65)}}

f = open(MEASGRID)
MeasDict = {}
for line in f:
	cols = line.strip('\n').split()
	MeasDict[float(cols[0])] = (cols[0], cols[FF])
f.close()

print '\033[4m{att:>5s} {meas:>4s} {cham:>4s} {L1A:>7s} {LCT:>7s} {LSc:>7s} {LSM:>7s} {AM:>7s} {S:>7s} {SSc:>7s}\033[m'.format(\
		att  = 'Att',
		meas = 'Meas',
		cham = 'Cham',
		L1A  = 'L1A',
		LCT  = 'LCT',
		LSc  = 'LSc',
		LSM  = 'LSM',
		AM   = 'AM',
		S    = 'Seg',
		SSc  = 'SSc'
	)
for ATT in sorted(MeasDict.keys()):
	MEAS = MeasDict[ATT][1]
	ATT = MeasDict[ATT][0]
	f = R.TFile.Open('../../trees/ana_'+MEAS+'.root')
	t = f.Get('GIFTree/GIFDigiTree')

	nL1A         = t.GetEntries() # nL1A
	nLCT         = {1:0, 110:0}
	nLCTScint    = {1:0, 110:0}
	nLCTSegMatch = {1:0, 110:0}
	nAllMatch    = {1:0, 110:0} # AllMatch <==> LCTScintSegMatch
	nSeg         = {1:0, 110:0}
	nSegScint    = {1:0, 110:0}

	for entry in t:
		E = Primitives.ETree(t, DecList=('LCT', 'SEGMENT'))
		lcts = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham))]
		segs = [Primitives.Segment(E, i) for i in range(len(E.seg_cham))]

		for CHAM in (1, 110):
			# nLCT
			if CHAM in E.lct_cham:
				nLCT[CHAM] += 1
			# nSeg
			if CHAM in E.seg_cham:
				nSeg[CHAM] += 1

			flag_LCTScint    = False
			flag_LCTSegMatch = False
			flag_AllMatch    = False
			flag_SegScint    = False

			for lct in lcts:
				if lct.cham != CHAM: continue
				# nLCTScint
				if Aux.inPad(lct.keyHalfStrip, lct.keyWireGroup, CHAM):
					flag_LCTScint = True
					for seg in segs:
						if seg.cham != CHAM: continue
						# nAllMatch
						if Aux.matchSegLCT(seg, lct):
							flag_AllMatch = True
							break
				if flag_AllMatch:
					flag_LCTSegMatch = True
				else:
					for seg in segs:
						if seg.cham != CHAM: continue
						# nLCTSegMatch
						if Aux.matchSegLCT(seg, lct):
							flag_LCTSegMatch = True
							break

			if flag_AllMatch:
				flag_SegScint = True
			else:
				for seg in segs:
					# nSegScint
					if Aux.inPad(seg.halfStrip[3], seg.wireGroup[3], CHAM):
						flag_SegScint = True
						break

			nLCTScint   [CHAM] += flag_LCTScint
			nLCTSegMatch[CHAM] += flag_LCTSegMatch
			nAllMatch   [CHAM] += flag_AllMatch
			nSegScint   [CHAM] += flag_SegScint

	for CHAM in (1, 110):
		print '{att:>5s} {meas:4s} {cham:4s} {L1A:7d} {LCT:7d} {LSc:7d} {LSM:7d} {AM:7d} {S:7d} {SSc:7d}'.format(\
				att  = ATT,
				meas = MEAS,
				cham = 'ME11' if CHAM==1 else 'ME21',
				L1A  = nL1A,
				LCT  = nLCT        [CHAM],
				LSc  = nLCTScint   [CHAM],
				LSM  = nLCTSegMatch[CHAM],
				AM   = nAllMatch   [CHAM],
				S    = nSeg        [CHAM],
				SSc  = nSegScint   [CHAM]
			)
