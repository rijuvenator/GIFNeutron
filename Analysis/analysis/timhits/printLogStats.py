import sys, argparse
import Gif.Analysis.ChamberHandler as CH

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('FILE'              ,                                        help='event log file'      )
parser.add_argument('-v', '--verbosity' , dest='VERBOSITY', action='count',      help='increase verbosity'  )
parser.add_argument('-e', '--explore'   , dest='EXPLORE'  , action='store_true', help='print explore lists' )
parser.add_argument('-s', '--nosummary' , dest='NOSUM'    , action='store_true', help='don\'t print summary')
args = parser.parse_args()

FILE = args.FILE
VERBOSITY = args.VERBOSITY
EXPLORE = args.EXPLORE
SUMMARIZE = not args.NOSUM

# N_ refers to a count
# _E refers to a per-event count
f = open(FILE)
STATE, EVENT = 0, 0
N_EVENTS, N_EVENTS_TIM, N_SIM, N_SKIPPED, N_SHORT, N_NTRY, N_OTHER, N_LOGS = 0, 0, 0, 0, 0, 0, 0, 0
GASLIST, TIMLIST = [], []
for line in f:
	# keep track of skipped SimHits
	if 'skipping' in line:
		N_SKIPPED   += 1
		N_SKIPPED_E += 1
		if 'too close' in line:
			N_SHORT   += 1
			N_SHORT_E += 1
		elif 'n_try' in line:
			N_NTRY   += 1
			N_NTRY_E += 1
		else:
			N_OTHER   += 1
			N_OTHER_E += 1
	# keep track of SimHits with detailed logging
	if 'AFTER' in line:
		N_LOGS += 1
	# new event header -- prints PREVIOUS data, be careful
	if '[CSCDigiProducer::produce]' in line:
		if STATE == 1:
			if VERBOSITY > 0:
				print 'Event {EVENT:<3d} had {TIM:<3d} TimHits : {SKIP:<3d} skips ({SHORT:<3d} short {NTRY:<3d} ntry)'.format(
					EVENT=EVENT,
					TIM=N_SIM_E,
					SKIP=N_SKIPPED_E,
					SHORT=N_SHORT_E,
					NTRY=N_NTRY_E
				)
			if VERBOSITY > 1:
				print DETAILED
			GASLIST.append(EVENT)
			TIMLIST.append(N_SIM_E)
		N_EVENTS += 1
		DETAILED = ''
		STATE    = 0
		EVENT    = int(line.split()[3])
		N_SIM_E, N_SKIPPED_E, N_SHORT_E, N_NTRY_E, N_OTHER_E = 0, 0, 0, 0, 0
	# CSCDigitizer found SimHits
	if '[CSCDigitizer]' in line:
		if STATE == 0:
			N_EVENTS_TIM += 1
		N_SIM_CH   = int(line.split()[2])
		N_SIM_E   += N_SIM_CH
		N_SIM     += N_SIM_CH
		STATE      = 1

		CHAMRAW = line.split()[6:11]
		S = int(CHAMRAW[1][2:])
		R = int(CHAMRAW[2][2:])
		C = int(CHAMRAW[3][2:])
		CHAM = 'ME{E}{S}/{R}/{C:>02d}, L{L}'.format(
			E = '+' if CHAMRAW[0] == 'E:1' else '-',
			S = S,
			R = R,
			C = C,
			L = int(CHAMRAW[4][2:])
		)
		E = 1 if CHAMRAW[0] == 'E:1' else -1
		DETAILED += '  {N:>3d} in {C} ({ID})\n'.format(N=N_SIM_CH, C=CHAM, ID=CH.serialID(E, S, R, C))

# print basic stats
if EXPLORE:
	#print 'gaslist =', GASLIST
	#print 'timlist =', TIMLIST
	for g, t in zip(GASLIST, TIMLIST):
		print g, t

if SUMMARIZE:
	print N_EVENTS, 'events'
	print N_EVENTS_TIM, 'events with TimHits'
	print N_SIM, 'TimHits'
	if N_OTHER == 0:
		print '{0} skipped: {1} too short, {2} too many electrons'.format(N_SKIPPED, N_SHORT, N_NTRY)
	else:
		print '{0} skipped: {1} too short, {2} too many electrons, {3} (other)'.format(N_SKIPPED, N_SHORT, N_NTRY, N_OTHER)
	print N_LOGS, 'TimHits with details'
