import sys
from itertools import groupby
import cPickle as pickle
from Gif.Neutron.ParticleClass import Particle
import commands

# I think we're going to make this obsolete soon, so focus on pickleTree.py

user = commands.getoutput('echo $USER')
f = open('/afs/cern.ch/work/%s/%s/Neutron/parts'%(user[0],user))

# === Fill initial dictionary and "parent list"
# dictionary is indexed by the Track ID string, and contains a list:
# 0: track ID (redundant with the key, but good if the lists are split out, as they are later)
# 1: particle name
# 2: parent ID
# 3: integrated travel distance (for this segment only)
# 4: final process (check for nCapture)
# 5: list of daughters (will be filled a few lines down)
# 6: initial X Y Z
# 7: initial energy
# 8: final X Y Z
# 9: final nonzero energy

print "Filling initial dictionary..."
parts = {}
plist = []
parts['0'] = ['0', 'null', '0', None, None, [], [], 0, [], 0]
for line in f:
	l = line.strip('\n').split()
	if l[0] == 'Particle':
		thisID = l[6]
		thisName = l[2]
		thisParent = l[10]
		parts[thisID] = [thisID, thisName, thisParent, None, None, [], [], 0, [], 0]
		plist.append((thisParent,thisID))
	elif l[0] == '0':
		parts[thisID][6] = [float(l[1]), float(l[2]), float(l[3])]
		parts[thisID][7] = float(l[4])
		pass
	elif float(l[4])>0:
		parts[thisID][9] = float(l[4])
		parts[thisID][8] = [float(l[1]), float(l[2]), float(l[3])]
		parts[thisID][3] = float(l[7])
		parts[thisID][4] = l[9]
	else:
		parts[thisID][8] = [float(l[1]), float(l[2]), float(l[3])]
		parts[thisID][3] = float(l[7])
		parts[thisID][4] = l[9]
	prevLine = l
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
	parts[k][5] = [i[1] for i in j]

## Now save this dictionary using pickle
#print 'Pickling dictionary...'
#pickle.dump(parts, open('dict.pickle','wb'), 2)
#print 'Done.'

# make the classes
print 'Making classes...'
cparts = {}
for key in parts.keys():
	cparts[key] = Particle(parts[key])

# Now save this dictionary using pickle
print 'Pickling particles...'
pickle.dump(cparts, open('particles.pickle','wb'), 2)
print 'Done.'
