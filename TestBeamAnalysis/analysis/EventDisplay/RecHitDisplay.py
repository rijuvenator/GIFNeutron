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
ED.setStyle('rechits') # holy crap! setStyle was taking up 99% of the computation time!

##### PARAMETERS #####
# Measurement List, Chamber IDs (1, 110), Event List (1 indexed)
MEASLIST = [3384, 3284]
CHAMS    = [1, 110]
EVENTS   = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

# RecHit Strip List (1 indexed; must be improper subset of [1, 2, 3])
RECHITSTRIPS = [2]

# Which displays to plot
DOSEGMENTS = True

##### BEGIN CODE #####
for MEAS in MEASLIST:
	# Get file and tree
	f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/5Dec/ana_'+str(MEAS)+'.root')
	t = f.Get('GIFTree/GIFDigiTree')

	for EVENT in EVENTS:
		# Get the event, make the ETree, and make lists of primitives objects
		t.GetEntry(EVENT-1)
		DecList = ['RECHIT']
		if DOSEGMENTS:
			DecList.extend(['SEGMENT', 'LCT'])

		E = Primitives.ETree(t, DecList)
		rechits = [Primitives.RecHit (E, i) for i in range(len(E.rh_cham   ))]
		if DOSEGMENTS:
			segs    = [Primitives.Segment(E, i) for i in range(len(E.seg_cham  ))]
			lcts    = [Primitives.LCT    (E, i) for i in range(len(E.lct_cham  ))]

		for CHAM in CHAMS:
			# Upper limits for wire group numbers and half strip numbers
			WIRE_MAX = 48   if CHAM == 1 else 112
			HS_MAX   = 224  if CHAM == 1 else 160

			##### RECHITS DISPLAY #####

			# Instantiate canvas
			canvas = ED.Canvas('rechits')

			# Wires histogram: 2D, wire group vs. layer, weighted by time bin
			hRHWG = R.TH2F('rhwg', 'RECHIT WIRE GROUPS;Wire Group Number;Layer;Multiplicity', WIRE_MAX, 1, WIRE_MAX+1, 6, 1, 7)
			hRHWG.GetXaxis().SetNdivisions(520 if CHAM==1 else 1020)
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
			hRHS = R.TH2F('rhs', 'RECHIT STRIPS'+addOn+';Strip Number;Layer;Multiplicity', HS_MAX/2, 1, HS_MAX/2+1, 6, 1, 7)
			hRHS.GetXaxis().SetNdivisions(1020 if CHAM==1 else 520)
			for rh in rechits:
				if rh.cham != CHAM: continue
				for STRIP in RECHITSTRIPS:
					hRHS.Fill(rh.strips[STRIP-1], rh.layer, 1)
			canvas.pads[0].cd()
			hRHS.Draw('colz')

			# Segment Dots
			if DOSEGMENTS:
				L = []
				for seg in segs:
					if seg.cham != CHAM: continue
					for lct in lcts:
						if lct.cham != CHAM: continue
						diffS = abs(seg.halfStrip - lct.keyHalfStrip)
						diffW = abs(int(seg.wireGroup) - lct.keyWireGroup)
						if diffS <= 3 and diffW <= 3:
						#if True:
							RADII = {110: (1., 0.2, 0.7, 0.2), 1: (1.4, 0.2, 0.31, 0.2)}
							L.append(R.TEllipse(seg.strip     + 1 + 0.5, 3.5, RADII[CHAM][0]/2, RADII[CHAM][1]))
							canvas.pads[0].cd()
							L[-1].SetFillColor(R.kWhite)
							L[-1].Draw()
							L.append(R.TEllipse(seg.wireGroup     + 0.5, 3.5, RADII[CHAM][2], RADII[CHAM][3]))
							canvas.pads[1].cd()
							L[-1].SetFillColor(R.kWhite)
							L[-1].Draw()
							print '{:3d} {:3d} {:3d} {:3d}'.format(seg.halfStrip, int(seg.wireGroup), lct.keyHalfStrip, lct.keyWireGroup)

			##### CLEAN UP #####
			# scintillator region
			if CHAM == 1:
				SL = [\
						R.TLine(12.5, 1, 12.5, 7),
						R.TLine(36, 1, 36, 7),
						R.TLine(37, 1, 37, 7),
						R.TLine(43, 1, 43, 7)
					]
			elif CHAM == 110:
				SL = [\
						R.TLine( 4, 1,  4, 7),
						R.TLine(19, 1, 19, 7),
						R.TLine(55, 1, 55, 7),
						R.TLine(65, 1, 65, 7)
					]
			for line in SL:
				line.SetLineColor(R.kRed)
				line.SetLineWidth(2)
			canvas.pads[0].cd(); SL[0].Draw(); SL[1].Draw()
			canvas.pads[1].cd(); SL[2].Draw(); SL[3].Draw()

			for pad in canvas.pads:
				pad.cd()
				pad.RedrawAxis()

			# lumi text: m#MEAS, MEX/1, Event # EVENT
			canvas.drawLumiText('m#'+str(MEAS)+', ME'+('1' if CHAM == 1 else '2')+'/1, Event #'+str(EVENT))

			# save as: RD_MEAS_MEX1_EVENT.pdf
			canvas.canvas.SaveAs('pdfs/RH_'+str(MEAS)+'_ME'+('1' if CHAM == 1 else '2')+'1_'+str(EVENT)+'.pdf')
			R.SetOwnership(canvas.canvas, False)
			print '\033[1mFILE \033[32m'+'RH_'+str(MEAS)+'_ME'+('1' if CHAM == 1 else '2')+'1_'+str(EVENT)+'.pdf'+'\033[30m CREATED\033[0m'

	f.Close()
