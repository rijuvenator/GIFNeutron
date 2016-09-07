import sys
from Gif.Neutron.Particle import Unpickle
from Gif.Neutron.Tools import eprint

# Requires 1 argument, the suffix used when making the tree
if len(sys.argv) < 2:
	eprint('Usage: script.py SUFFIX')
	exit()

parts = Unpickle(sys.argv[1])

eprint('Starting analysis.')

# fill lists of IDs of neutrons, end neutrons, and captured
neutrons = [parts[p].ID for p in parts.keys() if parts[p].name == 'neutron']
endneutrons = []
captured = []

for nID in neutrons:
	foundN = False
	for d in parts[nID].daughters:
		if d.name == 'neutron':
			foundN = True
			break
	if not foundN:
		endneutrons.append(nID)
		if parts[nID].process == 'nCapture':
			captured.append(nID)

eprint("%i neutrons; %i end neutrons; %i captured neutrons" % (len(neutrons), len(endneutrons), len(captured)))

# for cutting on some threshold distance thresh in cm
def isWithin(r1, r2, thresh=0.1):
	return (sum([(i-j)**2 for i,j in zip(r1,r2)]))**0.5 < thresh

f = open('../files/ZADict','r')
ZADict = {}
for line in f:
	l = line.strip('\n').split()
	ZADict[l[0]] = (int(l[1]), int(l[2]))

# make photon energy list
for nID in captured:
	cap = str(parts[nID].daughters[-1].name)
	if cap == 'gamma':
		eprint('%10s: Track ID = %s' % ('No nucleus', parts[nID].ID))
	if not isWithin(parts[nID].pos_final, parts[nID].daughters[-1].pos):
		eprint('%10s: Track ID = %s' % ('Estranged' , parts[nID].ID))
	#print '%s' % cap
	print "%3i %3i" % (ZADict[cap][0], ZADict[cap][1])
