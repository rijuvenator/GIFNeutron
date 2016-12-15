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
ED.setStyle('rechits') # holy crap! setStyle was taking up 99% of the computation time!

##### COMMAND LINE PARAMETERS
parser = argparse.ArgumentParser(description='Makes event displays for given event list file and chamber')
parser.add_argument('--cham'  ,dest='CHAM'  ,help='1 for ME1/1, 2 for ME2/1')
parser.add_argument('--list'  ,dest='FILE'  ,help='Event list text file')
parser.add_argument('--meas'  ,dest='MEAS'  ,help='Measurement number')
parser.add_argument('--outDir',dest='OUTDIR',help='Plot saving directory',default='pdfs')
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
OUTDIR = args.OUTDIR

# Which displays to plot
DOSEGMENTS = False
DOSCINT    = False
DRAWZTITLE = False
TITLESON   = False
ORIGFORMAT = False

##### BEGIN CODE #####
SCINT = {1:{'HS':(25., 72.), 'WG':(37., 43.)}, 110:{'HS':(8., 38.), 'WG':(55., 65.)}}

for MEAS in MEASLIST:
	# Get file and tree
	f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/GIF/15Dec/ana_'+str(MEAS)+'.root')
	t = f.Get('GIFTree/GIFDigiTree')

	for ENTRY in ENTRIES:
		# Get the event, make the ETree, and make lists of primitives objects
		t.GetEntry(ENTRY)
		EVENT = t.Event_EventNumber
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
			canvas = ED.Canvas('rechits' if not ORIGFORMAT else 'origrechits')

			# Wires histogram: 2D, wire group vs. layer
			hRHWG = R.TH2F('rhwg', ('' if not TITLESON else 'RECHIT WIRE GROUPS')+';Wire Group Number;Layer'+('' if not DRAWZTITLE else ';Multiplicity'), WIRE_MAX, 1, WIRE_MAX+1, 6, 1, 7)
			hRHWG.GetXaxis().SetNdivisions(520 if CHAM==1 else 1020)
			for rh in rechits:
				if rh.cham != CHAM: continue
				hRHWG.Fill(rh.wireGroup, rh.layer, 1)
			canvas.pads[2 if not ORIGFORMAT else 1].cd()
			hRHWG.SetMarkerColor(R.kRed)
			hRHWG.Draw('')

			# Strips histogram: 2D, 3 strips vs. layer
			hRHS = R.TH2F('rhs', ('' if not TITLESON else 'RECHIT STRIPS')+';Strip Number;Layer'+('' if not DRAWZTITLE else ';Multiplicity'), HS_MAX/2, 1, HS_MAX/2+1, 6, 1, 7)
			hRHS.GetXaxis().SetNdivisions(1020 if CHAM==1 else 520)
			for rh in rechits:
				if rh.cham != CHAM: continue
				hRHS.Fill(rh.halfStrip/2, rh.layer, 1)
			canvas.pads[0].cd()
			hRHS.SetMarkerColor(R.kRed)
			hRHS.Draw('')

			# Segment Dots
			if DOSEGMENTS:
				L = []
				for seg in segs:
					if seg.cham != CHAM: continue
					for lct in lcts:
						if lct.cham != CHAM: continue
						diffS = abs(seg.halfStrip[3] - lct.keyHalfStrip)
						diffW = abs(seg.wireGroup[3] - lct.keyWireGroup)
						if diffS <= 3 and diffW <= 3:
						#if True:
							RADII = {110: (1., 0.2, 0.7, 0.2), 1: (1.4, 0.2, 0.31, 0.2)}
							L.append(R.TEllipse(seg.strip[3]     + 1 + 0.5, 3.5, RADII[CHAM][0]/2, RADII[CHAM][1]))
							canvas.pads[0].cd()
							L[-1].SetFillColor(R.kWhite)
							L[-1].Draw()
							L.append(R.TEllipse(seg.wireGroup[3]     + 0.5, 3.5, RADII[CHAM][2], RADII[CHAM][3]))
							canvas.pads[1].cd()
							L[-1].SetFillColor(R.kWhite)
							L[-1].Draw()
							print '{:3d} {:3d} {:3d} {:3d}'.format(int(seg.halfStrip[3]), int(seg.wireGroup[3]), lct.keyHalfStrip, lct.keyWireGroup)

			# Scintillator region
			if DOSCINT:
				SL = (\
						R.TLine(SCINT[CHAM]['HS'][0]/2, 1, SCINT[CHAM]['HS'][0]/2, 7),
						R.TLine(SCINT[CHAM]['HS'][1]/2, 1, SCINT[CHAM]['HS'][1]/2, 7),
						R.TLine(SCINT[CHAM]['WG'][0]  , 1, SCINT[CHAM]['WG'][0]  , 7),
						R.TLine(SCINT[CHAM]['WG'][1]  , 1, SCINT[CHAM]['WG'][1]  , 7)
					)
				for line in SL:
					line.SetLineColor(R.kRed)
					line.SetLineWidth(2)
				canvas.pads[0].cd(); SL[0].Draw(); SL[1].Draw()
				canvas.pads[1].cd(); SL[2].Draw(); SL[3].Draw()

			##### CLEAN UP #####
			for pad in canvas.pads:
				pad.cd()
				pad.RedrawAxis()

			# lumi text: m#MEAS, MEX/1, Event # EVENT
			canvas.drawLumiText('m#'+str(MEAS)+', ME'+('1' if CHAM == 1 else '2')+'/1, Event #'+str(EVENT))

			# save as: RH_MEAS_MEX1_EVENT.pdf
			canvas.canvas.SaveAs(OUTDIR+'/RH_'+str(MEAS)+'_ME'+('1' if CHAM == 1 else '2')+'1_'+str(EVENT)+'.pdf')
			R.SetOwnership(canvas.canvas, False)
			print '\033[1mFILE \033[32m'+'RH_'+str(MEAS)+'_ME'+('1' if CHAM == 1 else '2')+'1_'+str(EVENT)+'.pdf'+'\033[30m CREATED\033[0m'

			del hRHS, hRHWG

	f.Close()
