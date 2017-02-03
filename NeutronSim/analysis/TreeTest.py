def statusMsg(string):
	print '\033[32m' + string + '\033[31m'
statusMsg('Running TreeTest...')

import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.OldPlotter as Plotter
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.Auxiliary as Aux
statusMsg('All modules imported.')

f = R.TFile.Open('../trees/ana_3284.root')
t = f.Get('GIFTree/GIFDigiTree')
statusMsg('File and tree obtained.')

t.GetEntry(0)
E = Primitives.ETree(t)
statusMsg('All ETree members declared.')
comps  = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham)) ]
wires  = [Primitives.Wire   (E, i) for i in range(len(E.wire_cham)) ]
strips = [Primitives.Strip  (E, i) for i in range(len(E.strip_cham))]
rhs    = [Primitives.RecHit (E, i) for i in range(len(E.rh_cham))   ]
segs   = [Primitives.Segment(E, i) for i in range(len(E.seg_cham))  ]
lcts   = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham))  ]
clcts  = [Primitives.CLCT   (E, i) for i in range(len(E.clct_cham)) ]
statusMsg('All primitives lists created.')

for seg in segs:
	if Aux.inPad(seg.halfStrip[3], seg.wireGroup[3], seg.cham):
		statusMsg('Found segment in pad.')
		break
for seg in segs:
	matched = False
	for lct in lcts:
		if seg.cham != lct.cham: continue
		if Aux.matchSegLCT(seg, lct):
			statusMsg('Matched segment to LCT.')
			matched = True
			break
	if matched: break
statusMsg('Test successful.')
