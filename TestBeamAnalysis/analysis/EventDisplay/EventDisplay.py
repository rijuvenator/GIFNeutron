import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import DisplayHelper as ED # "Event Display"
import Patterns
import argparse

##########
# This file gets the data, makes the histograms, makes the objects, and makes the plots
# It is the true meat of the analysis; anything cosmetic or not directly relevant should
# be moved to one of the other files: Primitives for classes, DisplayHelper for cosmetics
##########

R.gROOT.SetBatch(True)
ED.setStyle('primitives') # holy crap! setStyle was taking up 99% of the computation time!

##### COMMAND LINE PARAMETERS
parser = argparse.ArgumentParser(description='Makes event displays for given event list file and chamber')
parser.add_argument('--cham',dest='CHAM',help='1 for ME1/1, 2 for ME2/1')
parser.add_argument('--list',dest='FILE',help='Event list text file')
parser.add_argument('--meas',dest='MEAS',help='Measurement number')
args = parser.parse_args()

##### PARAMETERS #####
# Measurement List, Chamber IDs (1, 110), Event List (1 indexed)
MEASLIST  = [int(args.MEAS)]
CHAMS     = [1 if int(args.CHAM)==1 else 110]
EVENTFILE = open(args.FILE)
ENTRIES   = []
for event in EVENTFILE:
	# Make display plots 1 indexed, tree is 0 indexed
	ENTRIES.append(int(event.strip('\n')))

# Which displays to plot
DOPATTERN  = True
DOSEGMENTS = True

##### BEGIN CODE #####
THRESHOLD = 13.3
SCINT = {1:{'HS':(25., 72.), 'WG':(37., 43.)}, 110:{'HS':(8., 38.), 'WG':(55., 65.)}}

for MEAS in MEASLIST:
	# Get file and tree
	f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/5Dec/ana_'+str(MEAS)+'.root')
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
			# Upper limits for wire group numbers and half strip numbers
			WIRE_MAX = 48   if CHAM == 1 else 112
			HS_MAX   = 224  if CHAM == 1 else 160

			##### PRIMITIVES DISPLAY #####

			# Instantiate canvas
			canvas = ED.Canvas('primitives')

			# Dark CFEBs
			hMissingH = R.TH1F('missingH', '', HS_MAX+2, 1, HS_MAX+3  ); hMissingH.SetFillColor(15)
			hMissingS = R.TH1F('missingS', '', HS_MAX+2, 1, HS_MAX/2+2); hMissingS.SetFillColor(15)
			#hNotReadH = R.TH1F('notReadH', '', HS_MAX+2, 1, HS_MAX+3  ); hNotReadH.SetFillColor(18)
			hNotReadS = R.TH1F('notReadS', '', HS_MAX+2, 1, HS_MAX/2+2); hNotReadS.SetFillColor(18)
			# Set everything to 1 to start with (bin content 1 is bottom of frame)
			for bin_ in range(1,HS_MAX+3): # it's okay to go over bin contents in histograms
				hMissingH.SetBinContent(bin_, 1)
				hMissingS.SetBinContent(bin_, 1)
				#hNotReadH.SetBinContent(bin_, 1)
				hNotReadS.SetBinContent(bin_, 1)
			# Loop through the strips to determine which CFEBs were read out
			ActiveCFEBs = [0] * (7 if CHAM == 1 else 5)
			for strip in strips:
				if strip.cham != CHAM: continue
				ActiveCFEBs[int(strip.number - 1) / 16] = 1 # Lol I'm cool
				#if strip.number >=  1 and strip.number <=  16: ActiveCFEBs[0] = 1
				#if strip.number >= 17 and strip.number <=  32: ActiveCFEBs[1] = 1
				#if strip.number >= 33 and strip.number <=  48: ActiveCFEBs[2] = 1
				#if strip.number >= 49 and strip.number <=  64: ActiveCFEBs[3] = 1
				#if strip.number >= 65 and strip.number <=  80: ActiveCFEBs[4] = 1
				#if strip.number >= 81 and strip.number <=  96: ActiveCFEBs[5] = 1
				#if strip.number >= 96 and strip.number <= 112: ActiveCFEBs[6] = 1
			# Shade out the CFEBs that weren't read out, and also the last two bins; bin content 7 is top of frame
			for cfeb, readOut in enumerate(ActiveCFEBs):
				if not readOut:
					for bin_ in range(cfeb * 32 + 1, (cfeb + 1) * 32 + 1):
						#hNotReadH.SetBinContent(bin_, 7)
						hNotReadS.SetBinContent(bin_, 7)
			if CHAM == 1 and ActiveCFEBs[6] == 0:
				for bin_ in range(HS_MAX+1, HS_MAX+3):
					#hNotReadH.SetBinContent(bin_, 7)
					hNotReadS.SetBinContent(bin_, 7)
			# Shade out the missing CFEB; bin content 7 is top of frame
			MISSING = (97, 127) if CHAM == 1 else (129, 162)
			for bin_ in range(MISSING[0], MISSING[1]+1):
				hMissingH.SetBinContent(bin_, 7)
				hMissingS.SetBinContent(bin_, 7)

			# Wires histogram: 2D, wire group vs. layer, weighted by time bin
			hWires = R.TH2F('wires', 'ANODE HIT TIMING;Wire Group Number;Layer;Timing', WIRE_MAX, 1, WIRE_MAX+1, 6, 1, 7)
			hWires.GetZaxis().SetRangeUser(0,16)
			hWires.GetXaxis().SetNdivisions(520 if CHAM==1 else 1020)
			for wire in wires:
				if wire.cham != CHAM: continue
				# Don't fill a histogram with 0 weight!
				hWires.Fill(wire.number, wire.layer, wire.timeBin if wire.timeBin!=0 else 0.1)
			canvas.pads[2].cd()
			hWires.Draw('colz')

			# Comparators histogram: 2D, staggered half strip vs. layer, weighted by time bin
			hComps = R.TH2F('comps', 'COMPARATOR HIT TIMING;Half Strip Number;Layer;Timing', HS_MAX+2, 1, HS_MAX+3, 6, 1, 7)
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
			hADC = R.TH2F('adc', 'CATHODE STRIP ADC COUNT;Strip Number;Layer;ADC Count', HS_MAX+2, 1, HS_MAX/2+2, 6, 1, 7)
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

			# Segment Dots
			if DOSEGMENTS:
				L = []
				for seg in segs:
					if seg.cham != CHAM: continue
					for lct in lcts:
						if lct.cham != CHAM: continue
						diffS = abs(seg.halfStrip - lct.keyHalfStrip)
						diffW = abs(seg.wireGroup - lct.keyWireGroup)
						if diffS <= 3 and diffW <= 3:
						#if True:
							RADII = {110: (1., 0.2, 0.7, 0.2), 1: (1.4, 0.2, 0.31, 0.2)}
							L.append(R.TEllipse(seg.strip     + 1 + 0.5, 3.5, RADII[CHAM][0]/2, RADII[CHAM][1]))
							canvas.pads[0].cd()
							L[-1].SetFillColor(R.kWhite)
							L[-1].Draw()
							L.append(R.TEllipse(seg.halfStrip + 2 + 0.5, 3.5, RADII[CHAM][0], RADII[CHAM][1]))
							canvas.pads[1].cd()
							L[-1].SetFillColor(R.kWhite)
							L[-1].Draw()
							L.append(R.TEllipse(seg.wireGroup     + 0.5, 3.5, RADII[CHAM][2], RADII[CHAM][3]))
							canvas.pads[2].cd()
							L[-1].SetFillColor(R.kWhite)
							L[-1].Draw()
							print '{:3d} {:3d} {:3d} {:3d}'.format(int(seg.halfStrip), int(seg.wireGroup), lct.keyHalfStrip, lct.keyWireGroup)

			##### CLEAN UP #####
			# scintillator region
			SL = (\
					R.TLine(SCINT[CHAM]['HS'][0]/2, 1, SCINT[CHAM]['HS'][0]/2, 7),
					R.TLine(SCINT[CHAM]['HS'][1]/2, 1, SCINT[CHAM]['HS'][1]/2, 7),
					R.TLine(SCINT[CHAM]['HS'][0]  , 1, SCINT[CHAM]['HS'][0]  , 7),
					R.TLine(SCINT[CHAM]['HS'][1]  , 1, SCINT[CHAM]['HS'][1]  , 7),
					R.TLine(SCINT[CHAM]['WG'][0]  , 1, SCINT[CHAM]['WG'][0]  , 7),
					R.TLine(SCINT[CHAM]['WG'][1]  , 1, SCINT[CHAM]['WG'][1]  , 7)
				)
			for line in SL:
				line.SetLineColor(R.kRed)
				line.SetLineWidth(2)
			canvas.pads[0].cd(); SL[0].Draw(); SL[1].Draw()
			canvas.pads[1].cd(); SL[2].Draw(); SL[3].Draw()
			canvas.pads[2].cd(); SL[4].Draw(); SL[5].Draw()

			for pad in canvas.pads:
				pad.cd()
				pad.RedrawAxis('')

			# lumi text: m#MEAS, MEX/1, Event # EVENT
			canvas.drawLumiText('m#'+str(MEAS)+', ME'+('1' if CHAM == 1 else '2')+'/1, Event #'+str(EVENT))

			# save as: ED_MEAS_MEX1_EVENT.pdf
			canvas.canvas.SaveAs('pdfs/ED_'+str(MEAS)+'_ME'+('1' if CHAM == 1 else '2')+'1_'+str(EVENT)+'.pdf')
			R.SetOwnership(canvas.canvas, False)
			print '\033[1mFILE \033[32m'+'ED_'+str(MEAS)+'_ME'+('1' if CHAM == 1 else '2')+'1_'+str(EVENT)+'.pdf'+'\033[30m CREATED\033[0m'

	f.Close()
