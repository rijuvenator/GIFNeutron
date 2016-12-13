import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.Plotter as Plotter

##### PARAMETERS #####
# Which chambers to do
CHAMLIST = [1, 110]
MEASLIST = [3284, 3250, 3384]

##### SEMI-PARAMETERS #####
SCINT = {1:{'HS':(25,72),'WG':(37,43)},110:{'HS':(8,38),'WG':(55,65)}}

##### BEGIN CODE #####
R.gROOT.SetBatch(True)

# defines a paddle region
def inPad(hs, wg, CHAM):
	if      hs >= SCINT[CHAM]['HS'][0]\
		and hs <= SCINT[CHAM]['HS'][1]\
		and wg >= SCINT[CHAM]['WG'][0]\
		and wg <= SCINT[CHAM]['WG'][1]:
		return True
	else:
		return False

# determines if a segment and an lct match each other
def matchSegLCT(seg, lct):
	if abs(seg.halfStrip - lct.keyHalfStrip) <= 2 and abs(seg.wireGroup - lct.keyWireGroup) <= 2:
		return True
	else:
		return False

BINS = 300
CHIMIN = 0
CHIMAX = 5
h = {}
for MEAS in MEASLIST:
	f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/5Dec/ana_'+str(MEAS)+'.root')
	t = f.Get('GIFTree/GIFDigiTree')

	h[MEAS] = {1: {}, 110: {}}
	h[MEAS][1  ][0] = R.TH1F('h'+str(MEAS)+'10'  , '', BINS, CHIMIN, CHIMAX)
	h[MEAS][110][0] = R.TH1F('h'+str(MEAS)+'1100', '', BINS, CHIMIN, CHIMAX)
	for entry in t:
		E = Primitives.ETree(t, DecList=['SEGMENT', 'LCT'])
		segs = [Primitives.Segment(E, i) for i in range(len(E.seg_cham))]
		lcts = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham))]
		for CHAM in CHAMLIST:
			for seg in segs:
				if seg.cham != CHAM: continue
				for lct in lcts:
					if lct.cham != CHAM: continue
					if inPad(seg.halfStrip, seg.wireGroup, CHAM) and matchSegLCT(seg, lct):
						if seg.dof not in h[MEAS][CHAM].keys():
							h[MEAS][CHAM][seg.dof] = R.TH1F('h'+str(MEAS)+str(CHAM)+str(seg.dof), '', BINS, CHIMIN, CHIMAX)
						h[MEAS][CHAM][seg.dof].Fill(seg.chisq/seg.dof)
						h[MEAS][CHAM][0      ].Fill(seg.chisq/seg.dof)
	for DOF in [0, 2, 4, 6, 8]:
		for CHAM in CHAMLIST:
			h[MEAS][CHAM][DOF].SetDirectory(0)
	f.Close()

##### MAKE PLOTS #####
for CHAM in CHAMLIST:
	for DOF in [0, 2, 4, 6, 8]:
	
		xtitle = '#chi^{2}/' + str(DOF) + ' dof' if DOF != 0 else '#chi^{2}/dof'
		ytitle = 'Counts'

		hMax = 0

		# Step 1
		plots = []
		for MEAS in MEASLIST:
			h[MEAS][CHAM][DOF].Scale(1./h[MEAS][CHAM][DOF].Integral())
			plots.append(Plotter.Plot(h[MEAS][CHAM][DOF], legName='', legType='', option='hist'))
			for i in range(1, h[MEAS][CHAM][DOF].GetNbinsX()):
				hMax = max(hMax, h[MEAS][CHAM][DOF].GetBinContent(i))

		# Step 2
		canvas = Plotter.Canvas(lumi='ME'+str(CHAM/110+1)+'/1 External Trigger', logy=False, extra='Internal', cWidth=800, cHeight=700)

		# Step 3
		canvas.makeLegend()

		# Step 4
		for i, plot in enumerate(plots):
			canvas.addMainPlot(plot, isFirst=(i==0), addToLegend=False)

		# Step 5
		R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")
		plots[0].setTitles(X=xtitle, Y=ytitle)
		plots[0].scaleTitles(0.8)
		plots[0].scaleLabels(0.8)
		plots[0].plot.SetMaximum(hMax)
		plots[0].scaleTitleOffsets(1.3, 'Y')

		plots[1].plot.SetLineColor(R.kRed)
		plots[2].plot.SetLineColor(R.kBlue)
		canvas.makeTransparent()

		text = R.TLatex()
		text.SetTextAlign(11)
		text.SetTextFont(42)
		text.SetTextSize(0.04)
		text.DrawLatexNDC(.7, .85, '#color[1]{' + '#mu: '    + '{:.4f}'.format(plots[0].plot.GetMean  ()) + '}')
		text.DrawLatexNDC(.7, .80, '#color[1]{' + '#sigma: ' + '{:.4f}'.format(plots[0].plot.GetStdDev()) + '}')
		text.DrawLatexNDC(.7, .75, '#color[2]{' + '#mu: '    + '{:.4f}'.format(plots[1].plot.GetMean  ()) + '}')
		text.DrawLatexNDC(.7, .70, '#color[2]{' + '#sigma: ' + '{:.4f}'.format(plots[1].plot.GetStdDev()) + '}')
		text.DrawLatexNDC(.7, .65, '#color[4]{' + '#mu: '    + '{:.4f}'.format(plots[2].plot.GetMean  ()) + '}')
		text.DrawLatexNDC(.7, .60, '#color[4]{' + '#sigma: ' + '{:.4f}'.format(plots[2].plot.GetStdDev()) + '}')

		# Step 6

		# Step 7

		# Step 8
		canvas.finishCanvas()
		canvas.c.SaveAs('pdfs/SegChiSq_ME'+str(CHAM/110+1)+'1_'+str(DOF)+'DOF'+'.pdf')
		R.SetOwnership(canvas.c, False)
