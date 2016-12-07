import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives

MEASGRID = '../rates/measgrid'
FF = 1
SCINT = {1:{'HS':(25,72),'WG':(37,43)},110:{'HS':(8,38),'WG':(55,65)}}

f = open(MEASGRID)
MeasDict = {}
for line in f:
	cols = line.strip('\n').split()
	MeasDict[float(cols[0])] = (cols[0], cols[FF])
f.close()

print '\033[4m{att:>5s} {meas:>4s} {cham:>4s} {tot:>7s} {LCT:>7s} {pHS:>7s} {pWG:>7s} {p:>7s} {sHS:>7s} {sWG:>7s} {s:>7s} {bHS:>7s} {bWG:>7s} {b:>7s}\033[m'.format(\
		att  = 'Atten',
		meas = 'Meas',
		cham = 'Cham',
		tot  = 'Total',
		LCT  = 'LCT',
		pHS  = 'PadHS',
		pWG  = 'PadWG',
		p    = 'PadBoth',
		sHS  = 'SegHS',
		sWG  = 'SegWG',
		s    = 'SegBoth',
		bHS  = 'BothHS',
		bWG  = 'BothWG',
		b    = 'Both'
	)
for ATT in sorted(MeasDict.keys()):
	MEAS = MeasDict[ATT][1]
	ATT = MeasDict[ATT][0]
	f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/5Dec/ana_'+MEAS+'.root')
	t = f.Get('GIFTree/GIFDigiTree')

	nTot = t.GetEntries()

	nLCT        = {1:0, 110:0}
	nScintHS    = {1:0, 110:0}
	nScintWG    = {1:0, 110:0}
	nScint      = {1:0, 110:0}
	nSegHS      = {1:0, 110:0}
	nSegWG      = {1:0, 110:0}
	nSeg        = {1:0, 110:0}
	nSegScintHS = {1:0, 110:0}
	nSegScintWG = {1:0, 110:0}
	nSegScint   = {1:0, 110:0}

	for entry in t:
		E = Primitives.ETree(t, DecList=('LCT', 'SEGMENT'))
		lcts = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham))]
		segs = [Primitives.Segment(E, i) for i in range(len(E.seg_cham))]

		for CHAM in (1, 110):
			if CHAM in E.lct_cham:
				nLCT[CHAM] += 1

			scintBools = {'HS':False, 'WG':False}
			segBools   = {'HS':False, 'WG':False}
			for lct in lcts:
				if lct.cham != CHAM: continue
				if lct.keyHalfStrip >= SCINT[CHAM]['HS'][0] and lct.keyHalfStrip <= SCINT[CHAM]['HS'][1]:
					scintBools['HS'] = True
					for seg in segs:
						if seg.cham != CHAM: continue
						if abs(2 * seg.strip - lct.keyHalfStrip) <= 2:
							segBools['HS'] = True
				if lct.keyWireGroup >= SCINT[CHAM]['WG'][0] and lct.keyWireGroup <= SCINT[CHAM]['WG'][1]:
					scintBools['WG'] = True
					for seg in segs:
						if seg.cham != CHAM: continue
						if abs(seg.wireGroup - lct.keyWireGroup) <= 2:
							segBools['WG'] = True

			nScintHS   [CHAM] += scintBools['HS']
			nScintWG   [CHAM] += scintBools['WG']
			nScint     [CHAM] += scintBools['HS'] and scintBools['WG']
			nSegHS     [CHAM] += segBools  ['HS']
			nSegWG     [CHAM] += segBools  ['WG']
			nSeg       [CHAM] += segBools  ['HS'] and segBools  ['WG']
			nSegScintHS[CHAM] += scintBools['HS'] and segBools  ['HS']
			nSegScintWG[CHAM] += scintBools['WG'] and segBools  ['WG']
			nSegScint  [CHAM] += scintBools['HS'] and segBools  ['HS'] and scintBools['WG'] and segBools  ['WG']

	for CHAM in (1, 110):
		print '{att:>5s} {meas:4s} {cham:4s} {tot:7d} {LCT:7.5f} {pHS:7.5f} {pWG:7.5f} {p:7.5f} {sHS:7.5f} {sWG:7.5f} {s:7.5f} {bHS:7.5f} {bWG:7.5f} {b:7.5f}'.format(\
				att  = ATT,
				meas = MEAS,
				cham = 'ME11' if CHAM==1 else 'ME21',
				tot  = nTot,
				LCT  = nLCT       [CHAM]/float(nTot),
				pHS  = nScintHS   [CHAM]/float(nTot),
				pWG  = nScintWG   [CHAM]/float(nTot),
				p    = nScint     [CHAM]/float(nTot),
				sHS  = nSegHS     [CHAM]/float(nTot),
				sWG  = nSegWG     [CHAM]/float(nTot),
				s    = nSeg       [CHAM]/float(nTot),
				bHS  = nSegScintHS[CHAM]/float(nTot),
				bWG  = nSegScintWG[CHAM]/float(nTot),
				b    = nSegScint  [CHAM]/float(nTot)
			)
