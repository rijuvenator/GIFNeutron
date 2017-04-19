import ROOT as R
import argparse
import subprocess as bash

# parse arguments
FCHOICES = ['500_3', '1000_3', '1000_1', '1000_Hack1_1', '25000_HPT_1', '25000_HPT_Hack2_1', '25000_HPT_Hack3_1', '25000_HPT_NomTOF_1']

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file'   , dest='FILE'   , default='1000_1'   , choices=FCHOICES, help='which data file to use'   )
parser.add_argument('-d', '--digioff', dest='DIGIOFF', action='store_true',                   help='suppress digi printing'   )
parser.add_argument('-c', '--chamoff', dest='CHAMOFF', action='store_true',                   help='suppress cham printing'   )
parser.add_argument('-s', '--sumoff' , dest='SUMOFF' , action='store_true',                   help='suppress summary printing')
args = parser.parse_args()

PRINTDIGI     = not args.DIGIOFF
PRINTCHAMDICT = not args.CHAMOFF
PRINTSUMMARY  = not args.SUMOFF

# make gaslist and timlist
eventHitList = bash.check_output('python printLogStats.py logs/log'+args.FILE+'Layer.log -e -s', shell=True)
lines = eventHitList.split('\n')
gaslist, timlist = [], []
for line in lines:
	if line == '': continue
	cols = line.split()
	gaslist.append(int(cols[0]))
	timlist.append(int(cols[1]))
gas = dict(zip(gaslist, timlist))

# run over the tree
f = R.TFile.Open('roots/output'+args.FILE+'Layer.root')
t = f.Get('GIFTree/GIFDigiTree')

t.SetBranchStatus('*', 0)
BranchList = ['sim_id', 'comp_id', 'wire_id', 'strip_id', 'lct_id', 'alct_id', 'clct_id']
for br in BranchList:
	t.SetBranchStatus(br, 1)

N_SIM          = 0
N_SIM_WITH_TIM = 0
N_EVENTS_SIM   = 0
for idx, entry in enumerate(t):
	if len(t.sim_id) > 0:
		N_EVENTS_SIM += 1
		N_SIM += len(t.sim_id)
		if idx+1 in gaslist:
			N_SIM_WITH_TIM += len(t.sim_id)

			if PRINTCHAMDICT:
				fullchamlist = []
				for br in BranchList[1:4]:
					fullchamlist.extend(list(getattr(t, br)))
				digichamlist = list(set([str(cham) for cham in list(t.sim_id) if cham in fullchamlist]))
				if digichamlist != []:
					print idx+1, ' '.join(digichamlist)

			if PRINTDIGI:
				print '{idx:3d}: {sim} {tim} {comp} {wire} {strip} {alct} {clct} {lct}'.format(
					idx   = idx+1,
					sim   = '  SIM: '+'{0:3d}'.format(len(t.sim_id  )),
					tim   = '  TIM: '+'{0:3d}'.format(gas[idx+1]     ),
					comp  = ' COMP: '+'{0:3d}'.format(len(t.comp_id )) if len(t.comp_id )>0 else '{0:10s}'.format(' '),
					wire  = ' WIRE: '+'{0:3d}'.format(len(t.wire_id )) if len(t.wire_id )>0 else '{0:10s}'.format(' '),
					strip = 'STRIP: '+'{0:3d}'.format(len(t.strip_id)) if len(t.strip_id)>0 else '{0:10s}'.format(' '),
					alct  = ' ALCT: '+'{0:3d}'.format(len(t.alct_id )) if len(t.alct_id )>0 else '{0:10s}'.format(' '),
					clct  = ' CLCT: '+'{0:3d}'.format(len(t.clct_id )) if len(t.clct_id )>0 else '{0:10s}'.format(' '),
					lct   = '  LCT: '+'{0:3d}'.format(len(t.lct_id  )) if len(t.lct_id  )>0 else '{0:10s}'.format(' ')
				)
		else:
			if PRINTDIGI:
				pass
				#print '{idx:3d}: {sim} {tim}'.format(
				#	idx   = idx+1,
				#	sim   = '  SIM: '+'{0:3d}'.format(len(t.sim_id)),
				#	tim   = '  TIM: '+'{0:3d}'.format(0),
				#)


if PRINTSUMMARY:
	print 'TOTAL: {0} SimHits, {1} TimHits'.format(N_SIM_WITH_TIM, sum(timlist))
	print '{0} events with {1} SimHits'.format(N_EVENTS_SIM, N_SIM)
