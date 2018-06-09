import numpy as np
import ROOT as R
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.ChamberHandler as CH

FILE = '/afs/cern.ch/work/c/cschnaib/public/goatees/GOAT_P5_14June2017.root'
f = R.TFile.Open(FILE)
t = f.Get('t')

# define BX-TB selection
RConfig = {
	'wire' : {
		'LB': lambda bx, tb : bx>=1  and bx<=5  and tb>=1  and tb<=5  and bx+tb<=6,
		'UB': lambda bx, tb : bx>=46 and bx<=48 and tb>=13 and tb<=15 and bx+tb>=61,
		'IT': lambda bx, tb : bx>=12 and bx<=40 and tb>=1  and tb<=5
	},
	'comp' : {
		'LB': lambda bx, tb : bx>=1  and bx<=3  and tb>=2  and tb<=4  and bx+tb<=5,
		'UB': lambda bx, tb : bx==48 and tb==9,
		'IT': lambda bx, tb : bx>=12 and bx<=40 and tb>=2  and tb<=4
	}
}
def RSelect(DIGI, BX, TB, REGION): return RConfig[DIGI][REGION](BX,TB)

hOcc = {'wire' : {}, 'comp' : {}}
hLum = {'wire' : {}, 'comp' : {}}
hLCT = {'wire' : {}, 'comp' : {}}
LCT  = {'wire' : {}, 'comp' : {}}

# declare histograms and LCT counter
RINGLIST = ('11', '12', '13', '21', '22', '31', '32', '41', '42')
for ring in RINGLIST:
	c = CH.Chamber(CH.serialID(1, int(ring[0]), int(ring[1]), 1))
	bins = {'comp' : c.nstrips*2+2, 'wire' : c.nwires+2}
	for digi in ('wire',):
		hOcc[digi][ring] = {}
		hLum[digi][ring] = {}
		hLCT[digi][ring] = {}
		LCT [digi][ring] = {}
		for half in ('u', 'l'):
			hOcc[digi][ring][half] = R.TH1F('hOcc'+ring+digi+half, '', bins[digi], 0, bins[digi])
			hOcc[digi][ring][half].SetDirectory(0)
			hLum[digi][ring][half] = R.TH1F('hLum'+ring+digi+half, '', 30, 0, 1.5e34)
			hLum[digi][ring][half].SetDirectory(0)
			hLCT[digi][ring][half] = R.TH1F('hLCT'+ring+digi+half, '', 30, 0, 1.5e34)
			hLCT[digi][ring][half].SetDirectory(0)
			LCT [digi][ring][half] = 0

# loop over tree. divide by pileup here; divide by area and LCTs later
n = t.GetEntries()
for i,entry in enumerate(t):
	#if i==100000: break
	if i%100000==0: print i, 'of', n, '\r',
	ENDCAP  = str  (t.ENDCAP )
	RING    = str  (t.RING   )
	DIGI    = str  (t.DIGI   )
	HALF    = str  (t.HALF   )
	BX      = int  (t.BX     )
	LUMI    = float(t.LUMI   )
	POS     = int  (t.POS    )
	CHAM    = int  (t.CHAM   )
	PILEUP  = float(t.PILEUP )
	D_TIME  = list (t.D_TIME )
	D_LAYER = list (t.D_LAYER)
	D_POS   = list (t.D_POS  )

	# divide by pileup
	weight = 1./PILEUP

	# no for loop here. just explicitly skip comps.
	if DIGI != 'wire': continue
	if BX >= 1 and BX <= 5:
		LCT [DIGI][RING][HALF] +=         (5-BX+1) if DIGI=='wire' else (3-BX+1)
		hLCT[DIGI][RING][HALF].Fill(LUMI, (5-BX+1) if DIGI=='wire' else (3-BX+1))
	for j in range(len(D_TIME)):
		if not RSelect(DIGI, BX, D_TIME[j], 'LB'): continue
		hOcc[DIGI][RING][HALF].Fill(D_POS[j], weight)
		hLum[DIGI][RING][HALF].Fill(LUMI)
print ''

for digi in ('wire',):
	for ring in ('21',):
		# divide by areas
		cham = CH.Chamber(CH.serialID(1,int(ring[0]),int(ring[1]),1))
		lim = cham.nwires if digi == 'wire' else cham.nstrips*2+1
		for i in range(1,lim+1):
			if ring != '11':
				area = 6*(((cham.t[ring]-cham.b[ring])/cham.h[ring] * cham.h[ring]/lim * 0.5*(i*2-1)) + cham.b[ring])*cham.h[ring]/lim
			hOcc[digi][ring]['u'].SetBinContent(i+1, hOcc[digi][ring]['u'].GetBinContent(i+1)/area)
			hOcc[digi][ring]['l'].SetBinContent(i+1, hOcc[digi][ring]['l'].GetBinContent(i+1)/area)

		# final scale by LCT and time
		f = R.TFile('lol.root', 'RECREATE')
		hOcc[digi][ring]['u'].Scale(1./LCT[digi][ring]['u'] * 1./25. * 1.e9)
		hOcc[digi][ring]['l'].Scale(1./LCT[digi][ring]['l'] * 1./25. * 1.e9)
		hOcc[digi][ring]['u'].Write()
		hOcc[digi][ring]['l'].Write()

		hLum[digi][ring]['u'].Divide(hLCT[digi][ring]['u'])
		hLum[digi][ring]['l'].Divide(hLCT[digi][ring]['l'])
		hLum[digi][ring]['u'].Scale(1./cham.area * 1./25. * 1.e9)
		hLum[digi][ring]['l'].Scale(1./cham.area * 1./25. * 1.e9)
		hLum[digi][ring]['all'] = hLum[digi][ring]['u'].Clone()
		hLum[digi][ring]['all'].Add(hLum[digi][ring]['l'])
		hLum[digi][ring]['all'].Write()
