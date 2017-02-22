def statusMsg(string):
	print '\033[32m' + string + '\033[31m'
def errorMsg(string):
	print '\033[31m' + string + '\033[31m'
statusMsg('Running TreeTest...')

import numpy as np
import ROOT as R
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Auxiliary as Aux
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.MegaStruct as MS
statusMsg('All modules imported.')

datalist = (\
	('GIF 3284', MS.F_GIFDATA.replace('XXXX','3284'), 'GIFDigi', 3 ),
	('P5'      , MS.F_P5DATA                        , 'GIFDigi', 1 ),
	('MC'      , MS.F_MCDATA                        , 'GIFDigi', 93)
)

for NAME, FN, TN, ENTRY in datalist:
	statusMsg('\nNow doing '+NAME+'.')
	f = R.TFile.Open(FN)
	t = f.Get('GIFTree/'+TN+'Tree')

	if type(t) != R.TTree:
		errorMsg('File obtained, but not tree.')
		exit()

	statusMsg('File and tree obtained.')

	t.GetEntry(ENTRY)
	E = Primitives.ETree(t)
	statusMsg('Entry '+str(ENTRY))
	statusMsg('All ETree members declared.')
	comps  = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham)) ]
	wires  = [Primitives.Wire   (E, i) for i in range(len(E.wire_cham)) ]
	strips = [Primitives.Strip  (E, i) for i in range(len(E.strip_cham))]
	rhs    = [Primitives.RecHit (E, i) for i in range(len(E.rh_cham))   ]
	if NAME == 'MC':
		shs    = [Primitives.SimHit (E, i) for i in range(len(E.rh_cham))   ]
	segs   = [Primitives.Segment(E, i) for i in range(len(E.seg_cham))  ]
	lcts   = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham))  ]
	clcts  = [Primitives.CLCT   (E, i) for i in range(len(E.clct_cham)) ]
	statusMsg('All primitives lists created.')

	if NAME == 'GIF 3284':
		for seg in segs:
			if Aux.inPad(seg.halfStrip[3], seg.wireGroup[3], seg.cham):
				statusMsg('Found segment in pad.')
				break
	for seg in segs:
		matched = False
		for lct in lcts:
			if seg.cham != lct.cham: continue
			if Aux.matchSegLCT(seg, lct, thresh=(2,2)):
				statusMsg('Matched segment to LCT.')
				matched = True
				break
		if matched: break
	statusMsg('Test successful.')
