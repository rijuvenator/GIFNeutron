import numpy as np
import ROOT as R
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.Auxiliary as Aux
import DisplayHelper as ED # "Event Display"
import Patterns
import argparse
import Gif.Analysis.ChamberHandler as CH
from Gif.Analysis.MegaStruct import F_MCDATA

##########
# This file gets the data, makes the histograms, makes the objects, and makes the plots
# It is the true meat of the analysis; anything cosmetic or not directly relevant should
# be moved to one of the other files: Primitives for classes, DisplayHelper for cosmetics
##########

R.gROOT.SetBatch(True)
ED.setStyle('simhits') # holy crap! setStyle was taking up 99% of the computation time!

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
		print "Cannot make SimHits at GIF++ !"
		exit()
	elif cols[0] == 'P5':
		print "Cannot make SimHits at P5 !"
		exit()
	elif cols[0] == 'MC':
		KEY = (F_MCDATA,'MC')
		CONFIG[KEY] = {}
	else:
		ENTRY = int(cols[0])
		CHAM  = int(cols[1])
		if ENTRY not in CONFIG[KEY].keys():
			CONFIG[KEY][ENTRY] = []
		CONFIG[KEY][ENTRY].append(CHAM)

# Which displays to plot
DOSEGMENTS = False
DRAWZTITLE = False
TITLESON   = True
ORIGFORMAT = False
DOSCINT    = True
DOENERGY   = True

##### BEGIN CODE #####

for FILE,TYPE in CONFIG.keys():
	# Get file and tree
	f = R.TFile.Open(FILE)
	TREENAME = 'GIFTree/GIFDigiTree'
	t = f.Get(TREENAME)

	for ENTRY in CONFIG[(FILE,TYPE)].keys():
		# Get the event, make the ETree, and make lists of primitives objects
		t.GetEntry(ENTRY)
		EVENT = t.Event_EventNumber
		DecList = ['SIMHIT']

		E = Primitives.ETree(t, DecList)
		simhits = [Primitives.SimHit (E, i) for i in range(len(E.sim_cham))]

		for CHAM in CONFIG[(FILE,TYPE)][ENTRY]:
			CHAMBER = CH.Chamber(CHAM)
			# Upper limits for wire group numbers and half strip numbers

			##### SIMHITS DISPLAY #####
			WIRE_MAX = CHAMBER.nwires
			HS_MAX   = CHAMBER.nstrips*2

			# Ndivisions codes
			ND = {\
				'st' : { 64 : 520,  80 : 520, 112 : 1020            },

				'wg' : { 48 : 510,  64 : 520,  96 :  520, 112 : 1020}
			}

			# Instantiate canvas
			if DOENERGY:
				canvas = ED.Canvas('primitives')
			else:
				canvas = ED.Canvas('simhits' if not ORIGFORMAT else 'origsimhits')

			'''
			shL = { 'all'      : [8.],
					'electron' : [8.],
					'muon'     : [8.],
					'proton'   : [8.],
					'pion'     : [8.],
					'other'    : [8.]
					}
			shS = { 'all' : [float(HS_MAX)],
					'electron' : [float(HS_MAX)],
					'muon' : [float(HS_MAX)],
					'proton' : [float(HS_MAX)],
					'pion' : [float(HS_MAX)],
					'other' : [float(HS_MAX)]}
			shW = { 'all' : [float(WIRE_MAX)+10],
					'electron' : [float(WIRE_MAX)+10],
					'muon' : [float(WIRE_MAX)+10],
					'proton' : [float(WIRE_MAX)+10],
					'pion' : [float(WIRE_MAX)+10],
					'other' : [float(WIRE_MAX)+10]}
			'''

			particleList = ['all','electron','muon','proton','pion','other']
			shL = {particle:[8.] for particle in particleList}
			shS = {particle:[float(HS_MAX)] for particle in particleList}
			shW = {particle:[float(WIRE_MAX)+10] for particle in particleList}

			for sh in simhits:
				if sh.cham != CHAM: continue
				shS['all'].append(float(sh.stripPos)  + 0.5)
				shW['all'].append(float(sh.wirePos)   + 0.5)
				shL['all'].append(float(sh.layer)     + 0.5)
				if abs(sh.particleID)==11:
					shS['electron'].append(float(sh.stripPos)  + 0.5)
					shW['electron'].append(float(sh.wirePos)   + 0.5)
					shL['electron'].append(float(sh.layer)     + 0.5)
				elif abs(sh.particleID)==13:
					print '***** Found Muon!!! *****'
					shS['muon'].append(float(sh.stripPos)  + 0.5)
					shW['muon'].append(float(sh.wirePos)   + 0.5)
					shL['muon'].append(float(sh.layer)     + 0.5)
				elif abs(sh.particleID)==2212:
					print '***** Found Proton!!! *****'
					shS['proton'].append(float(sh.stripPos)  + 0.5)
					shW['proton'].append(float(sh.wirePos)   + 0.5)
					shL['proton'].append(float(sh.layer)     + 0.5)
				elif abs(sh.particleID)==221:
					print '***** Found Pion!!! *****'
					shS['pion'].append(float(sh.stripPos)  + 0.5)
					shW['pion'].append(float(sh.wirePos)   + 0.5)
					shL['pion'].append(float(sh.layer)     + 0.5)
				else:
					print '***** Found Other!!! *****'
					shS['other'].append(float(sh.stripPos)  + 0.5)
					shW['other'].append(float(sh.wirePos)   + 0.5)
					shL['other'].append(float(sh.layer)     + 0.5)


			particleDict = {
					'electron':R.kBlack,
					'muon':R.kRed,
					'proton':R.kBlue,
					'pion':R.kGreen,
					'other':R.kOrange+1,
			}
			gSHS = R.TGraph(len(shS['all']), np.array(shS['all']), np.array(shL['all']))
			canvas.pads[1 if DOENERGY else 0].cd()
			gSHS.Draw('AP')
			gSHS.SetMarkerColor(R.kBlack)
			gSHS.GetXaxis().SetNdivisions(ND['st'][HS_MAX/2])
			gSHS.SetTitle(('' if not TITLESON else 'SIMHIT STRIPS')+';Strip Number;Layer'+('' if not DRAWZTITLE else ';Multiplicity'))
			gSHS.SetMinimum(1.)
			gSHS.SetMaximum(7.)
			gSHS.GetXaxis().SetLimits(1., HS_MAX/2+1.)
			gSHS.Draw('AP')
			canvas.canvas.Update()

			gSHW = R.TGraph(len(shW['all']), np.array(shW['all']), np.array(shL['all']))
			canvas.pads[2 if not ORIGFORMAT else 1].cd()
			gSHW.Draw('AP')
			gSHW.SetMarkerColor(R.kBlack)
			gSHW.GetXaxis().SetNdivisions(ND['wg'][WIRE_MAX])
			gSHW.SetTitle(('' if not TITLESON else 'SIMHIT WIRE GROUPS')+';Wire Group Number;Layer'+('' if not DRAWZTITLE else ';Multiplicity'))
			gSHW.SetMinimum(1.)
			gSHW.SetMaximum(7.)
			gSHW.GetXaxis().SetLimits(1., WIRE_MAX+1.)
			gSHW.Draw('AP')
			canvas.canvas.Update()

			particleGraphs = []
			for particle in particleDict.keys():
				gSRHS = R.TGraph(len(shS[particle]), np.array(shS[particle]), np.array(shL[particle]))
				canvas.pads[1 if DOENERGY else 0].cd()
				gSRHS.Draw('P')
				gSRHS.SetMarkerColor(particleDict[particle])
				gSRHW = R.TGraph(len(shW[particle]), np.array(shW[particle]), np.array(shL[particle]))
				canvas.pads[2 if not ORIGFORMAT else 1].cd()
				gSRHW.Draw('P')
				gSRHW.SetMarkerColor(particleDict[particle])
				particleGraphs.append(gSRHS)
				particleGraphs.append(gSRHW)


			if DOENERGY:
				# SimHit energy loss histogram: 2D, staggered strip vs. layer, weighted by simhit energy loss
				hEDep = R.TH2F('adc', 'ENERGY DEPOSITED BY SIMHIT [keV];Strip Number;Layer'+('' if not DRAWZTITLE else ';[keV]'), HS_MAX, 1, HS_MAX/2+1, 6, 1, 7)
				hEDep.GetZaxis().SetRangeUser(0,150)
				hEDep.GetXaxis().SetNdivisions(ND['st'][HS_MAX/2])
				for simhit in simhits:
					if simhit.cham != CHAM: continue
					energyLoss = simhit.energyLoss*10**6 # energyLoss in [GeV] convert to [keV]
					hEDep.Fill(int(simhit.stripPos), simhit.layer, energyLoss) 
					hEDep.Fill(int(simhit.stripPos) + 0.5, simhit.layer, energyLoss)
				canvas.pads[0].cd()
				hEDep.Draw('colz') # to get the axes and titles


			##### CLEAN UP #####
			for pad in canvas.pads:
				pad.cd()
				pad.RedrawAxis()

			if TYPE == 'MC':
				# lumi text
				canvas.drawLumiText('{CS}, Event #{EVENT}'.format(CS=CHAMBER.display('ME{E}{S}/{R}/{C}'), EVENT=EVENT))

				# save as
				canvas.canvas.SaveAs('{}/SH_MC_{}_{}.pdf'.format(OUTDIR, CHAMBER.display('ME{E}{S}{R}{C}'), EVENT))
				R.SetOwnership(canvas.canvas, False)
				print '\033[1;31m'          + 'MC ENTRY {} CHAMBER {}'.format(ENTRY, CHAMBER.id)                        + '\033[m'
				print '\033[1mFILE \033[32m'+ 'SH_MC_{}_{}.pdf'       .format(CHAMBER.display('ME{E}{S}{R}{C}'), EVENT) + '\033[30m CREATED\033[0m'

			del gSHS, gSHW
			if DOENERGY: del hEDep
			canvas.deleteCanvas()

	f.Close()
