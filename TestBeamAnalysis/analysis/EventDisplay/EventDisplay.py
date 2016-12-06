import numpy as np
import ROOT as R
import Gif.TestBeamAnalysis.Primitives as Primitives
import DisplayHelper as ED # "Event Display"
import Patterns

##########
# This file gets the data, makes the histograms, makes the objects, and makes the plots
# It is the true meat of the analysis; anything cosmetic or not directly relevant should
# be moved to one of the other files: Primitives for classes, DisplayHelper for cosmetics
##########

R.gROOT.SetBatch(True)

##### PARAMETERS #####
# Measurement List, Chamber IDs (1, 110), Event List (1 indexed)
MEASLIST = [3284, 3384]
CHAMS    = [1, 110]
EVENTS   = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# RecHit Strip List (1 indexed; must be improper subset of [1, 2, 3])
RECHITSTRIPS = [2]

# Which displays to plot
DODISPLAYS = True
DOPATTERN  = True
DORECHITS  = False
DOSEGMENTS = True

##### BEGIN CODE #####
THRESHOLD = 13.3

for MEAS in MEASLIST:
	# Get file and tree
	f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/5Dec/ana_'+str(MEAS)+'.root')
	t = f.Get('GIFTree/GIFDigiTree')

	for EVENT in EVENTS:
		# Get the event, make the ETree, and make lists of primitives objects
		t.GetEntry(EVENT-1)
		DecList = []
		if DODISPLAYS:
			DecList.extend(['WIRE', 'STRIP', 'COMP'])
		if DORECHITS:
			DecList.extend(['RECHIT'])
		if DOPATTERN:
			DecList.extend(['LCT'])
		if DOSEGMENTS:
			DecList.extend(['SEGMENT'])

		E = Primitives.ETree(t, DecList)

		if DODISPLAYS:
			wires   = [Primitives.Wire   (E, i) for i in range(len(E.wire_cham ))]
			strips  = [Primitives.Strip  (E, i) for i in range(len(E.strip_cham))]
			comps   = [Primitives.Comp   (E, i) for i in range(len(E.comp_cham ))]
		if DORECHITS:
			rechits = [Primitives.RecHit (E, i) for i in range(len(E.rh_cham   ))]
		if DOPATTERN:
			lcts    = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham  ))]
		if DOSEGMENTS:
			segs    = [Primitives.Segment(E, i) for i in range(len(E.seg_cham  ))]

		for CHAM in CHAMS:
			# Upper limits for wire group numbers and half strip numbers
			WIRE_MAX = 50   if CHAM == 1 else 113
			HS_MAX   = 230  if CHAM == 1 else 164

			if DODISPLAYS:
				##### PRIMITIVES DISPLAY #####

				# Instantiate canvas
				canvas = ED.Canvas('primitives')

				# Wires histogram: 2D, wire group vs. layer, weighted by time bin
				hWires = R.TH2F('wires', 'ANODE HIT TIMING;Wire Group Number;Layer;Timing', WIRE_MAX, 0, WIRE_MAX, 6, 1, 7)
				hWires.GetZaxis().SetRangeUser(0,16)
				hWires.GetXaxis().SetNdivisions(520 if CHAM==1 else 1020)
				for wire in wires:
					if wire.cham != CHAM: continue
					hWires.Fill(wire.number, wire.layer, wire.timeBin)
				canvas.pads[2].cd()
				hWires.Draw('colz')

				# Comparators histogram: 2D, staggered half strip vs. layer, weighted by time bin
				hComps = R.TH2F('comps', 'COMPARATOR HIT TIMING;Half Strip Number;Layer;Timing', HS_MAX, 0, HS_MAX, 6, 1, 7)
				hComps.GetZaxis().SetRangeUser(0,16)
				hComps.GetXaxis().SetNdivisions(2020 if CHAM==1 else 1020)
				for comp in comps:
					if comp.cham != CHAM: continue
					hComps.Fill(comp.staggeredHalfStrip, comp.layer, comp.timeBin)
				canvas.pads[1].cd()
				hComps.Draw('colz')

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
					canvas.drawLumiText(LUMI, PAD=1)


				# Segment Dots
				if DOSEGMENTS:
					L = []
					i = -1
					for seg in segs:
						if seg.cham != CHAM: continue
						i += 1
						for lct in lcts:
							if lct.cham != CHAM: continue
							diffS = abs(seg.halfStrip - lct.keyHalfStrip)
							diffW = abs(int(seg.wireGroup) - lct.keyWireGroup)
							if diffS <= 3 and diffW <= 3:
							#if True:
								RADII = {110: (1, 0.2, 0.7, 0.2), 1: (1.4, 0.2, 0.31, 0.2)}
								L.append(R.TEllipse(    seg.halfStrip  + 2 + 0.5, 3.5, RADII[CHAM][0], RADII[CHAM][1]))
								canvas.pads[1].cd()                                                                  
								L[-1].SetFillColor(i)
								L[-1].Draw()                                                                         
								L.append(R.TEllipse(int(seg.wireGroup)     + 0.5, 3.5, RADII[CHAM][2], RADII[CHAM][3]))
								canvas.pads[2].cd()
								L[-1].SetFillColor(i)
								L[-1].Draw()
								print '{:3d} {:3d} {:3d} {:3d}'.format(seg.halfStrip, int(seg.wireGroup), lct.keyHalfStrip, lct.keyWireGroup)

				# ADC Count histogram: 2D, staggered strip vs. layer, weighted by ADC count (max ADC[2:] minus pedestal: average ADC[0:2])
				hADC = R.TH2F('adc', 'CATHODE STRIP ADC COUNT;Strip Number;Layer;ADC Count', HS_MAX, 0, HS_MAX/2, 6, 1, 7)
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
				hADC.Draw('colz')

				##### CLEAN UP #####
				# scintillator region
				if CHAM == 1:
					SL = [\
							R.TLine(25, 1, 25, 7),
							R.TLine(72, 1, 72, 7),
							R.TLine(37, 1, 37, 7),
							R.TLine(43, 1, 43, 7)
						]
				elif CHAM == 110:
					SL = [\
							R.TLine( 8, 1,  8, 7),
							R.TLine(38, 1, 38, 7),
							R.TLine(55, 1, 55, 7),
							R.TLine(65, 1, 65, 7)
						]
				for line in SL:
					line.SetLineColor(R.kRed)
				canvas.pads[1].cd(); SL[0].Draw(); SL[1].Draw()
				canvas.pads[2].cd(); SL[2].Draw(); SL[3].Draw()

				for pad in canvas.pads:
					pad.cd()
					pad.RedrawAxis('')

				# lumi text: m#MEAS, MEX/1, Event # EVENT
				canvas.drawLumiText('m#'+str(MEAS)+', ME'+('1' if CHAM == 1 else '2')+'/1, Event #'+str(EVENT))

				# save as: ED_MEAS_MEX1_EVENT.pdf
				canvas.canvas.SaveAs('pdfs/ED_'+str(MEAS)+'_ME'+('1' if CHAM == 1 else '2')+'1_'+str(EVENT)+'.pdf')
				print '\033[1mFILE \033[32m'+'EH_'+str(MEAS)+'_ME'+('1' if CHAM == 1 else '2')+'1_'+str(EVENT)+'.pdf'+'\033[30m CREATED\033[0m'

			if DORECHITS:
				##### RECHITS DISPLAY #####

				# Instantiate canvas
				canvas = ED.Canvas('rechits')

				# Wires histogram: 2D, wire group vs. layer, weighted by time bin
				hRHWG = R.TH2F('rhwg', 'RECHIT WIRE GROUPS;Wire Group Number;Layer;Multiplicity', WIRE_MAX, 0, WIRE_MAX, 6, 1, 7)
				#hRHWG.GetZaxis().SetRangeUser(0,16)
				for rh in rechits:
					if rh.cham != CHAM: continue
					hRHWG.Fill(rh.wireGroup, rh.layer, 1)
				canvas.pads[1].cd()
				hRHWG.Draw('colz')

				# Strips histogram: 2D, 3 strips vs. layer, weighted by time bin
				addOn = ', STRIP'
				if len(RECHITSTRIPS) == 1:
					addOn += ' ' + str(RECHITSTRIPS[0])
				else:
					addOn += 'S '
					for i,STRIP in enumerate(RECHITSTRIPS):
						addOn += str(STRIP) + (', ' if i<len(RECHITSTRIPS)-1 else '')
				hRHS = R.TH2F('rhs', 'RECHIT STRIPS'+addOn+';Strip Number;Layer;Multiplicity', HS_MAX/2, 0, HS_MAX/2, 6, 1, 7)
				#hRHS.GetZaxis().SetRangeUser(0,16)
				for rh in rechits:
					if rh.cham != CHAM: continue
					for STRIP in RECHITSTRIPS:
						hRHS.Fill(rh.strips[STRIP-1], rh.layer, 1)
				canvas.pads[0].cd()
				hRHS.Draw('colz')

				##### CLEAN UP #####
				for pad in canvas.pads:
					pad.cd()
					pad.RedrawAxis()

				# lumi text: m#MEAS, MEX/1, Event # EVENT
				canvas.drawLumiText('m#'+str(MEAS)+', ME'+('1' if CHAM == 1 else '2')+'/1, Event #'+str(EVENT))

				# save as: RD_MEAS_MEX1_EVENT.pdf
				canvas.canvas.SaveAs('pdfs/RH_'+str(MEAS)+'_ME'+('1' if CHAM == 1 else '2')+'1_'+str(EVENT)+'.pdf')
				print '\033[1mFILE \033[32m'+'RH_'+str(MEAS)+'_ME'+('1' if CHAM == 1 else '2')+'1_'+str(EVENT)+'.pdf'+'\033[30m CREATED\033[0m'

	f.Close()
