import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import Gif.TestBeamAnalysis.Auxiliary as Aux
import DisplayHelper as ED # "Event Display"
import Patterns
import argparse
import Gif.TestBeamAnalysis.ChamberHandler as CH

##########
# This file gets the data, makes the histograms, makes the objects, and makes the plots
# It is the true meat of the analysis; anything cosmetic or not directly relevant should
# be moved to one of the other files: Primitives for classes, DisplayHelper for cosmetics
##########

R.gROOT.SetBatch(True)
ED.setStyle('primitives') # holy crap! setStyle was taking up 99% of the computation time!

##### COMMAND LINE PARAMETERS
parser = argparse.ArgumentParser(description='Makes event displays for given event list file and chamber')
parser.add_argument('--cham'  ,dest='CHAM'  ,help='Chamber serial number')
parser.add_argument('--list'  ,dest='LIST'  ,help='Event list text file')
parser.add_argument('--file'  ,dest='FILE'  ,help='Data file name')
parser.add_argument('--outDir',dest='OUTDIR',help='Plot saving directory',default='pdfs')
args = parser.parse_args()

##### PARAMETERS #####
# Measurement List, Chamber IDs (1, 110), Event List (1 indexed)
FILES     = [args.FILE]
CHAMS     = [int(args.CHAM)]
EVENTFILE = open(args.LIST)
ENTRIES   = []
for event in EVENTFILE:
	# Make display plots 1 indexed, tree is 0 indexed
	ENTRIES.append(int(event.strip('\n')))
OUTDIR = args.OUTDIR

# Which displays to plot
DOPATTERN  = True
DOSEGMENTS = False
DRAWZTITLE = True

##### BEGIN CODE #####
THRESHOLD = 13.3

for FILE in FILES:
	# Get file and tree
	f = R.TFile.Open(FILE)
	t = f.Get('GIFTree/GIFDigiTree')

	for ENTRY in ENTRIES:
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

		for CHAM in CHAMS:
			CHAMBER = CH.Chamber(CHAM)
			# Upper limits for wire group numbers and half strip numbers
			WIRE_MAX = CHAMBER.nwires
			HS_MAX   = CHAMBER.nstrips*2

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
				#if strip.number >=  1 and strip.number <=  16: ActiveCFEBs[0] = 1
				#if strip.number >= 17 and strip.number <=  32: ActiveCFEBs[1] = 1
				#if strip.number >= 33 and strip.number <=  48: ActiveCFEBs[2] = 1
				#if strip.number >= 49 and strip.number <=  64: ActiveCFEBs[3] = 1
				#if strip.number >= 65 and strip.number <=  80: ActiveCFEBs[4] = 1
				#if strip.number >= 81 and strip.number <=  96: ActiveCFEBs[5] = 1
				#if strip.number >= 97 and strip.number <= 112: ActiveCFEBs[6] = 1
			# Shade out the CFEBs that weren't read out, and also the last two bins; bin content 7 is top of frame
			for cfeb, readOut in enumerate(ActiveCFEBs):
				if not readOut:
					for bin_ in range(cfeb * 32 + 1, (cfeb + 1) * 32 + 1):
						#hNotReadH.SetBinContent(bin_, 7)
						hNotReadS.SetBinContent(bin_, 7)
			#if CHAM == 1 and ActiveCFEBs[6] == 0:
			#	for bin_ in range(HS_MAX+1, HS_MAX+3):
			#		#hNotReadH.SetBinContent(bin_, 7)
			#		hNotReadS.SetBinContent(bin_, 7)
			# Shade out the missing CFEB; bin content 7 is top of frame

			# Wires histogram: 2D, wire group vs. layer, weighted by time bin
			hWires = R.TH2F('wires', 'ANODE HIT TIMING;Wire Group Number;Layer'+('' if not DRAWZTITLE else ';Timing'), WIRE_MAX, 1, WIRE_MAX+1, 6, 1, 7)
			hWires.GetZaxis().SetRangeUser(0,16)
			hWires.GetXaxis().SetNdivisions(520 if CHAM==1 else 1020)
			for wire in wires:
				if wire.cham != CHAM: continue
				# Don't fill a histogram with 0 weight!
				hWires.Fill(wire.number, wire.layer, wire.timeBin if wire.timeBin!=0 else 0.1)
			canvas.pads[2].cd()
			hWires.Draw('colz')

			# Comparators histogram: 2D, staggered half strip vs. layer, weighted by time bin
			hComps = R.TH2F('comps', 'COMPARATOR HIT TIMING;Half Strip Number;Layer'+('' if not DRAWZTITLE else ';Timing'), HS_MAX, 1, HS_MAX+1, 6, 1, 7)
			hComps.GetZaxis().SetRangeUser(0,16)
			hComps.GetXaxis().SetNdivisions(2020 if CHAM==1 else 1020)
			for comp in comps:
				if comp.cham != CHAM: continue
				# Don't fill a histogram with 0 weight!
				hComps.Fill(comp.staggeredHalfStrip, comp.layer, comp.timeBin if comp.timeBin!=0 else 0.1)
			canvas.pads[1].cd()
			hComps.Draw('colz') # to get the axes and titles
			#hNotReadH.Draw('B same')
			hMissingH.Draw('B same')
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
			hADC.GetXaxis().SetNdivisions(1020 if CHAM==1 else 520)
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
			hMissingS.Draw('B same')
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

			##### CLEAN UP #####
			for pad in canvas.pads:
				pad.cd()
				pad.RedrawAxis('')

			# lumi text: m#MEAS, MEX/1, Event # EVENT
			#canvas.drawLumiText('m#'+str(MEAS)+', ME'+('1' if CHAM == 1 else '2')+'/1, Event #'+str(EVENT))
			canvas.drawLumiTest(CHAMBER.display() + ', Event #'+str(EVENT)

			# save as: ED_MEAS_MEX1_EVENT.pdf
			#canvas.canvas.SaveAs(OUTDIR+'/ED_'+str(MEAS)+'_ME'+('1' if CHAM == 1 else '2')+'1_'+str(EVENT)+'.pdf')
			canvas.canvas.SaveAs(OUTDIR+'/ED_'+CHAMBER.display('ME{S}{R}_')+str(EVENT)+'.pdf')
			R.SetOwnership(canvas.canvas, False)
			#print '\033[1mFILE \033[32m'+'ED_'+str(MEAS)+'_ME'+('1' if CHAM == 1 else '2')+'1_'+str(EVENT)+'.pdf'+'\033[30m CREATED\033[0m'
			print '\033[1mFILE \033[32m'+'ED_'+CHAMBER.display('ME{S}{R}_')+str(EVENT)+'.pdf'+'\033[30m CREATED\033[0m'

			#del hWires, hComps, hADC, hMissingH, hMissingS, hNotReadS
			del hWires, hComps, hADC, hNotReadS

	f.Close()
