import sys
from itertools import groupby
import cPickle as pickle

f = open('/afs/cern.ch/work/a/adasgupt/Neutron/parts')

# === Fill initial dictionary and "parent list"
# dictionary is indexed by the Track ID string, and contains a list with 5 elements:
# 0: particle name
# 1: parent ID
# 2: list of daughters (will be filled a few lines down)
# 3: energy (iff this is a captured neutron, i.e. check against None is a bool for isCaptured)
# 4: track ID (redundant with the key, but good if the lists are split out, as they are later
#
# Classes are too slow for now and their only benefit is improving readability
# i.e. they let you do neutron.name instead of neutron[0]

print "Filling initial dictionary..."
parts = {}
plist = []
parts['0'] = ['null', '0', [], None]
for line in f:
	l = line.strip('\n').split()
	if l[0] == 'Particle':
		thisName = l[2]
		thisID = l[6]
		thisParent = l[10]
		parts[thisID] = [thisName, thisParent, [], None, thisID]
		plist.append((thisParent,thisID))
	elif l[0] != '0' and l[-1] != 'nCapture':
		parts[thisID][3] = float(l[4])
	else:
		continue
f.close()
print "Done filling initial dictionary."

# === Make Daughter Lists
# this is very important for efficiently making lists of daughters
# python's sort sorts by the first element of a tuple by default
print "Sorting by parent..."
plist.sort()

# now for the magic: itertools groupby cuts up the list by unique key
# the resulting list is the list of daughters; just stick it in the list
print "Making daughter lists..."
for k, g in groupby(plist, lambda x: x[0]):
	j = list(g)
	parts[k][2] = [i[1] for i in j]

# Now save this dictionary using pickle
print 'Pickling...'
pickle.dump(parts, open('saved','wb'), 2)
print 'Done!'
