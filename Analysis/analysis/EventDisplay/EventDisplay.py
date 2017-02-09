import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Auxiliary as Aux
import DisplayHelper as ED # "Event Display"
import Patterns
import argparse
import Gif.Analysis.ChamberHandler as CH

##########
# This file gets the data, makes the histograms, makes the objects, and makes the plots
# It is the true meat of the analysis; anything cosmetic or not directly relevant should
# be moved to one of the other files: Primitives for classes, DisplayHelper for cosmetics
##########

R.gROOT.SetBatch(True)
ED.setStyle('primitives') # holy crap! setStyle was taking up 99% of the computation time!

##### COMMAND LINE PARAMETERS
parser = argparse.ArgumentParser(description='Makes event displays')
parser.add_argument('--config',dest='CONFIG',help='Configuration file'   ,default='ED.config')
parser.add_argument('--outDir',dest='OUTDIR',help='Plot saving directory',default='pdfs'     )
args = parser.parse_args()

##### PARAMETERS #####
OUTDIR = args.OUTDIR
# CONFIG dictionary: CONFIG[FN][ENTRY] = [CHAMLIST]
CONFIG = {}
F_CONFIG = open(args.CONFIG)
for line in F_CONFIG:
	# skip empty lines and comments
	if line[0] == '#' or line == '\n':
		continue
	cols = line.strip('\n').split()
	if cols[0] == 'GIF':
		MEAS = cols[1]
		KEY = ('../../trees/ana_'+MEAS+'.root', 'GIF')
		CONFIG[KEY] = {}
	elif cols[0] == 'P5':
		KEY = (cols[1],'P5')
		CONFIG[KEY] = {}
	elif cols[0] == 'MC':
		KEY = (cols[1],'MC')
		CONFIG[KEY] = {}
	else:
		ENTRY = int(cols[0])
		CHAM  = int(cols[1])
		if ENTRY not in CONFIG[KEY].keys():
			CONFIG[KEY][ENTRY] = []
		CONFIG[KEY][ENTRY].append(CHAM)

# Which displays to plot
DOSEGMENTS = False
DOPATTERN  = True
DRAWZTITLE = True
DOSCINT    = True

##### BEGIN CODE #####
THRESHOLD = 13.3

for FILE,TYPE in CONFIG.keys():
	# Get file and tree
	f = R.TFile.Open(FILE)
	t = f.Get('GIFTree/GIFDigiTree')

	for ENTRY in CONFIG[(FILE,TYPE)].keys():
		# Get the event, make the ETree, and make lists of primitives objects
		t.GetEntry(ENTRY)
		EVENT = t.Event_EventNumber
		DecList = ['WIRE', 'STRIP', 'COMP']
		if DOPATTERN or DOSEGMENTS:
			DecList.extend(['LCT'])
		if DOSEGMENTS:
			DecList.extend(['SEGMENT'])

		E = Primitives.ETree(t, DecList)
		wires   = [Primitives.Wire   (E, i) for i in range(len(E.wire_cham ))]
		strips  = [Primitives.Strip  (E, i) for i in range(len(E.strip_cham))]
		comps   = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham ))]
		if DOPATTERN or DOSEGMENTS:
			lcts    = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham  ))]
		if DOSEGMENTS:
			segs    = [Primitives.Segment(E, i) for i in range(len(E.seg_cham  ))]

		for CHAM in CONFIG[(FILE,TYPE)][ENTRY]:
			CHAMBER = CH.Chamber(CHAM)
			# Upper limits for wire group numbers and half strip numbers
			WIRE_MAX = CHAMBER.nwires
			HS_MAX   = CHAMBER.nstrips*2

			# Ndivisions codes
			ND = {\
				'st' : { 64 : 520,  80 : 520, 112 : 1020            },
				'hs' : {128 :1020, 160 :1020, 224 : 2020            },
				'wg' : { 48 : 510,  64 : 520,  96 :  520, 112 : 1020}
			}

			##### PRIMITIVES DISPLAY #####

			# Instantiate canvas
			canvas = ED.Canvas('primitives')

			# Dark CFEBs
			#hNotReadH = R.TH1F('notReadH', '', HS_MAX, 1, HS_MAX  +1); hNotReadH.SetFillColor(18)
			hNotReadS = R.TH1F('notReadS', '', HS_MAX, 1, HS_MAX/2+1); hNotReadS.SetFillColor(18)
			# Set everything to 1 to start with (bin content 1 is bottom of frame)
			for bin_ in range(1,HS_MAX+3): # it's okay to go over bin contents in histograms
				#hNotReadH.SetBinContent(bin_, 1)
				hNotReadS.SetBinContent(bin_, 1)
			# Loop through the strips to determine which CFEBs were read out
			ActiveCFEBs = [0] * (CHAMBER.nstrips/16)
			for strip in strips:
				if strip.cham != CHAM: continue
				ActiveCFEBs[int(strip.number - 1) / 16] = 1 # Lol I'm cool
			# Shade out the CFEBs that weren't read out, and also the last two bins; bin content 7 is top of frame
			for cfeb, readOut in enumerate(ActiveCFEBs):
				if not readOut:
					for bin_ in range(cfeb * 32 + 1, (cfeb + 1) * 32 + 1):
						#hNotReadH.SetBinContent(bin_, 7)
						hNotReadS.SetBinContent(bin_, 7)

			# Wires histogram: 2D, wire group vs. layer, weighted by time bin
			hWires = R.TH2F('wires', 'ANODE HIT TIMING;Wire Group Number;Layer'+('' if not DRAWZTITLE else ';Timing'), WIRE_MAX, 1, WIRE_MAX+1, 6, 1, 7)
			hWires.GetZaxis().SetRangeUser(0,16)
			hWires.GetXaxis().SetNdivisions(ND['wg'][WIRE_MAX])
			for wire in wires:
				if wire.cham != CHAM: continue
				# Don't fill a histogram with 0 weight!
				hWires.Fill(wire.number, wire.layer, wire.timeBin if wire.timeBin!=0 else 0.1)
			canvas.pads[2].cd()
			hWires.Draw('colz')

			# Comparators histogram: 2D, staggered half strip vs. layer, weighted by time bin
			hComps = R.TH2F('comps', 'COMPARATOR HIT TIMING;Half Strip Number;Layer'+('' if not DRAWZTITLE else ';Timing'), HS_MAX, 1, HS_MAX+1, 6, 1, 7)
			hComps.GetZaxis().SetRangeUser(0,16)
			hComps.GetXaxis().SetNdivisions(ND['hs'][HS_MAX])
			for comp in comps:
				if comp.cham != CHAM: continue
				# Don't fill a histogram with 0 weight!
				hComps.Fill(comp.staggeredHalfStrip, comp.layer, comp.timeBin if comp.timeBin!=0 else 0.1)
			canvas.pads[1].cd()
			hComps.Draw('colz') # to get the axes and titles
			#hNotReadH.Draw('B same')
			#hMissingH.Draw('B same')
			hComps.Draw('colz same')

			# CLCT Pattern Boxes: staggered half strip vs. layer
			if DOPATTERN:
				canvas.pads[1].cd()
				B = []
				LUMI = 'PID '
				for lct in lcts:
					if lct.cham != CHAM: continue
					LUMI += str(lct.pattern) + ' '
					x1, y1, x2, y2 = Patterns.Pattern(lct.pattern, lct.keyHalfStrip)
					for pos in zip(x1, y1, x2, y2):
						B.append(R.TBox(pos[0], pos[1], pos[2], pos[3]))
						B[-1].SetFillStyle(0)
						B[-1].Draw('same')
				if B != []: canvas.drawLumiText(LUMI, PAD=1)

			# ADC Count histogram: 2D, staggered strip vs. layer, weighted by ADC count (max ADC[2:] minus pedestal: average ADC[0:2])
			hADC = R.TH2F('adc', 'CATHODE STRIP ADC COUNT;Strip Number;Layer'+('' if not DRAWZTITLE else ';ADC Count'), HS_MAX, 1, HS_MAX/2+1, 6, 1, 7)
			hADC.GetZaxis().SetRangeUser(0,500)
			hADC.GetXaxis().SetNdivisions(ND['st'][HS_MAX/2])
			for strip in strips:
				if strip.cham != CHAM: continue
				PEDESTAL = 0.5 * (strip.ADC[0] + strip.ADC[1])
				ADC_COUNT = max([x-PEDESTAL for x in strip.ADC[2:]])
				if ADC_COUNT < THRESHOLD: continue
				hADC.Fill(strip.staggeredNumber      , strip.layer, ADC_COUNT)
				hADC.Fill(strip.staggeredNumber + 0.5, strip.layer, ADC_COUNT)
			canvas.pads[0].cd()
			hADC.Draw('colz') # to get the axes and titles
			hNotReadS.Draw('B same')
			#hMissingS.Draw('B same')
			hADC.Draw('colz same')

			# Segments
			if DOSEGMENTS:
				SegDrawList = []
				for seg in segs:
					if seg.cham != CHAM: continue
					for lct in lcts:
						if lct.cham != CHAM: continue
						if Aux.matchSegLCT(seg, lct, thresh=(3., 3.)):
							SegDrawList.append(seg)
				SEGLAYERS = [1, 2, 3, 4, 5, 6]
				layZ = np.array([float(i) + 0.5 for i in SEGLAYERS])
				segGraphs = []
				for seg in SegDrawList:
					segGraphs.append({})
					hsX = np.array([seg.staggeredHalfStrip[lay]+1.5 for lay in SEGLAYERS])
					stX = np.array([seg.staggeredStrip    [lay]+0.5 for lay in SEGLAYERS])
					wgX = np.array([seg.wireGroup         [lay] for lay in SEGLAYERS])
					segGraphs[-1]['hs'] = {'fill' : R.TGraph(len(layZ), hsX, layZ), 'empt' : R.TGraph(len(layZ), hsX, layZ), 'pad' : 1}
					segGraphs[-1]['st'] = {'fill' : R.TGraph(len(layZ), stX, layZ), 'empt' : R.TGraph(len(layZ), stX, layZ), 'pad' : 0}
					segGraphs[-1]['wg'] = {'fill' : R.TGraph(len(layZ), wgX, layZ), 'empt' : R.TGraph(len(layZ), wgX, layZ), 'pad' : 2}
				for gr in segGraphs:
					for key in ['hs', 'st', 'wg']:
						gr[key]['fill'].SetMarkerColor(R.kWhite)
						gr[key]['fill'].SetMarkerStyle(R.kFullCircle)
						gr[key]['empt'].SetMarkerColor(R.kBlack)
						gr[key]['empt'].SetMarkerStyle(R.kOpenCircle)
						for which in ['fill', 'empt']:
							gr[key][which].SetMarkerSize(1)
							gr[key][which].SetLineWidth(3)
							gr[key][which].SetLineColor(R.kBlue)
						canvas.pads[gr[key]['pad']].cd()
						gr[key]['fill'].Draw('P same')
						gr[key]['empt'].Draw('P same')

			# Scintillator region
			if DOSCINT and TYPE == 'GIF':
				SL = (\
						R.TLine(Aux.SCINT[CHAM]['HS'][0]/2, 1, Aux.SCINT[CHAM]['HS'][0]/2, 7),
						R.TLine(Aux.SCINT[CHAM]['HS'][1]/2, 1, Aux.SCINT[CHAM]['HS'][1]/2, 7),
						R.TLine(Aux.SCINT[CHAM]['HS'][0]  , 1, Aux.SCINT[CHAM]['HS'][0]  , 7),
						R.TLine(Aux.SCINT[CHAM]['HS'][1]  , 1, Aux.SCINT[CHAM]['HS'][1]  , 7),
						R.TLine(Aux.SCINT[CHAM]['WG'][0]  , 1, Aux.SCINT[CHAM]['WG'][0]  , 7),
						R.TLine(Aux.SCINT[CHAM]['WG'][1]  , 1, Aux.SCINT[CHAM]['WG'][1]  , 7)
					)
				for line in SL:
					line.SetLineColor(R.kRed)
					line.SetLineWidth(2)
				canvas.pads[0].cd(); SL[0].Draw(); SL[1].Draw()
				canvas.pads[1].cd(); SL[2].Draw(); SL[3].Draw()
				canvas.pads[2].cd(); SL[4].Draw(); SL[5].Draw()

			##### CLEAN UP #####
			for pad in canvas.pads:
				pad.cd()
				pad.RedrawAxis()

			if TYPE == 'P5':
				# lumi text
				RUN = t.Event_RunNumber
				LS  = t.Event_LumiSection
				canvas.drawLumiText('{CS}, REL =({R}, {E}, {L})'.format(CS=CHAMBER.display('ME{E}{S}/{R}/{C}'), R=str(RUN), E=str(EVENT), L=str(LS)))

				# save as
				canvas.canvas.SaveAs('{}/ED_P5_{}_{}.pdf'.format(OUTDIR, CHAMBER.display('ME{E}{S}{R}{C}'), EVENT))
				R.SetOwnership(canvas.canvas, False)
				print '\033[1;31m'          + 'P5 ENTRY {} CHAMBER {}'.format(ENTRY, CHAMBER.id)                        + '\033[m'
				print '\033[1mFILE \033[32m'+ 'ED_P5_{}_{}.pdf'       .format(CHAMBER.display('ME{E}{S}{R}{C}'), EVENT) + '\033[30m CREATED\033[0m'
			elif TYPE == 'GIF':
				# lumi text
				MEAS = FILE[-9:-5]
				canvas.drawLumiText('m#{MEAS}, {CS}, Event #{EVENT}'.format(MEAS=MEAS, CS=CHAMBER.display('ME{S}/{R}'), EVENT=EVENT))

				# save as
				canvas.canvas.SaveAs('{}/ED_GIF_{}_{}_{}.pdf'.format(OUTDIR, MEAS, CHAMBER.display('ME{S}{R}'), EVENT))
				R.SetOwnership(canvas.canvas, False)
				print '\033[1;31m'           + 'GIF ENTRY {} CHAMBER {}'.format(ENTRY, CHAMBER.id)                        + '\033[m'
				print '\033[1mFILE \033[32m' + 'ED_GIF_{}_{}_{}.pdf'    .format(MEAS, CHAMBER.display('ME{S}{R}'), EVENT) + '\033[30m CREATED\033[0m'

			del hWires, hComps, hADC, hNotReadS
			canvas.deleteCanvas()

	f.Close()
