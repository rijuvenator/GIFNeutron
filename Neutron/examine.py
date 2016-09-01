import sys
from itertools import groupby
import cPickle as pickle

print 'Unpickling...'
parts = pickle.load(open('saved','rb'))

print 'Starting analysis'
# === Work with Neutrons
# find neutrons, "unique" neutrons, and captured neutrons
# print information about captured neutrons
neutrons = [parts[p] for p in parts.keys() if parts[p][0]=='neutron']
uneutrons = []
captured = []
for n in neutrons:
	foundN = False
	for nd in n[2]:
		if parts[nd][0] == 'neutron':
			foundN = True
			break
	if not foundN:
		uneutrons.append(n)
		if n[3] is not None:
			captured.append(n)

print len(neutrons), "neutrons, but only", len(uneutrons), "neutrons without neutron daughters"
print "Of THOSE neutrons,", len(captured), "were captured."

for n in captured:
	print "Neutron (ID %7s) with energy %.4e, daughter of a %13s (ID %7s), with %2i daughters" % (n[4], n[3], parts[n[1]][0], n[1], len(n[2]))

