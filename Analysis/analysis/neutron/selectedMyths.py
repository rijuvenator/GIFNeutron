import ROOT as R
import Gif.Analysis.roottools as RT
import threading, logging, sys

# ==== GET DATA FILE ====
f = open('shorttracks.log')
data = {}
for line in f:
	if line[0] == '#': continue
	cols = line.strip('\n').split()
	event = int(cols[0])
	if event not in data:
		data[event] = []
	ID = cols[1]
	ds = float(cols[2])
	eloss = float(cols[3])
	data[event].append((ID, ds, eloss))

# ==== HELPER FUNCTIONS ====
def atSamePos(p1, p2):
	return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)**0.5 < 0.0001

def printChain(pt, dic, log, headstring=None):
	if headstring is None:
		headstring = '  '
	trackID = str(pt.ID)
	while True:
		pt.GetEntry(dic[trackID])
		headstring += str(pt.name) + ' '
		if pt.name == 'neutron':
			log.info(headstring)
			break
		if pt.parent == '0':
			headstring += '<= 0'
			log.info(headstring)
			break
		headstring += '<= '
		trackID = str(pt.parent)

def printLogHead(pt, log):
	log.info('{ID:s} {NAME:s}'.format(ID=pt.ID, NAME=pt.name))
	log.info('{x:>11s} {y:>11s} {z:>11s} {e:>13s} {de:>13s} {ds:>11s} {tr:>11s} {proc:20s} {vol:s}'.format(
		x    = 'X',
		y    = 'Y',
		z    = 'Z',
		e    = 'E',
		de   = 'DE',
		ds   = 'DS',
		tr   = 'L',
		proc = 'PROC',
		vol  = 'VOL',
	))

def printLogLine(pt, i, log):
	log.info('{x:11.4f} {y:11.4f} {z:11.4f} {e:13.4f} {de:13.4f} {ds:11.4f} {tr:11.4f} {proc:20s} {vol:s}'.format(
		x    = pt.x      [i],
		y    = pt.y      [i],
		z    = pt.z      [i],
		e    = pt.energy [i] * 1e6,
		de   = pt.dE     [i] * 1e6,
		ds   = pt.step   [i],
		tr   = pt.track  [i],
		proc = pt.process[i],
		vol  = pt.vol    [i],
	))

def printProvenance(ID, pt, dic, log, headstring):
	headstring += '{:8.4f}   '.format(pt.energy[0]*1e6)
	printChain(pt, dic, log)

	trackID = ID
	pt.GetEntry(dic[trackID])
	epos = (pt.x[0], pt.y[0], pt.z[0])
	printLogHead(pt, log)
	printLogLine(pt, 0, log)

	trackID = str(pt.parent)
	pt.GetEntry(dic[trackID])
	while True:
		i = len(pt.x)-1
		while True:
			pos = (pt.x[i], pt.y[i], pt.z[i])
			if atSamePos(pos, epos):
				break
			i -= 1
		printLogHead(pt, log)
		printLogLine(pt, i, log)
		epos = (pt.x[0], pt.y[0], pt.z[0])
		trackID = str(pt.parent)
		if trackID == '0':
			break
		pt.GetEntry(dic[trackID])

	#trackID = ID
	#pt.GetEntry(dic[trackID])
	#while True:
	#	printLogHead(pt, log)
	#	for i in list(reversed(range(len(pt.x)))):
	#		printLogLine(pt, i, log)
	#	trackID = str(pt.parent)
	#	if trackID == '0':
	#		break
	#	pt.GetEntry(dic[trackID])

	log.info('\n')


# ==== EXECUTE AND THREAD ====

#for event in data.keys():
def execute(event):
	log = logging.getLogger('log'+str(event))
	log.setLevel(logging.INFO)
	fh = logging.FileHandler('trimProv/log_'+str(event)+'.log',mode='w')
	fh.setFormatter(logging.Formatter('%(message)s'))
	log.addHandler(fh)

	simhits = data[event]
	fpart = R.TFile.Open('forest/partTree_{NUMBER}.root'.format(NUMBER=event))
	pt = fpart.Get('partTree')
	dic = RT.getTreeDict(scanarg=r'"ID"',num=event)
	for ID, ds, eloss in simhits:
		headstring = '===== {:8.4f} {:8.4f} '.format(ds, eloss)
		pt.GetEntry(dic[ID])
		printProvenance(ID, pt, dic, log, headstring)
	
	dlog.warning('Finished Event {EVENT}'.format(EVENT=event))

threads = []
dlog = logging.getLogger('debug')
dlog.addHandler(logging.FileHandler('joblog.log',mode='w'))
for event in data.keys():
	t = threading.Thread(target=execute, args=(event,))
	threads.append(t)
	t.start()

