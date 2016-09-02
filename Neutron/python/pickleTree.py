import sys
from itertools import groupby
import cPickle as pickle
from Gif.Neutron.ParticleClass import Particle
import ROOT as R

# This is the same thing as pickle.py, except it uses the ROOT Tree to make the dictionaries.
# It's syntactically better, and it doesn't depend on the 'parts' file
# It seems to be slower, but this is to be expected since the entire tree is loaded...

ft = R.TFile.Open('partTree.root')
t = ft.Get('partTree')

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
for i in range(t.GetEntries()):
	t.GetEntry(i)

	nonZero = -1
	while t.energy[nonZero] < 1.0e-16:
		nonZero -= 1

	parts[str(t.ID)] = [\
		str(t.ID),
		str(t.name),
		str(t.parent),
		t.track[-1],
		t.process[-1],
		[],
		[t.x[0], t.y[0], t.z[0]],
		t.energy[0],
		[t.x[-1], t.y[-1], t.z[-1]],
		t.energy[-2]
	]

	plist.append((str(t.parent), str(t.ID)))
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
