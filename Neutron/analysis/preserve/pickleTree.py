import os
import sys
from itertools import groupby
import cPickle as pickle
from Gif.Neutron.ParticleClass import Particle, Daughter
import ROOT as R

# Requires 1 argument: the suffix given to makeTree.py
if len(sys.argv) < 2:
	print 'Usage: pickleTree.py SUFFIX'
	exit()

# get the path and get the tree
scriptdir = os.path.dirname(__file__)
relpath = '../../forest/partTree_'+sys.argv[1]+'.root'
ft = R.TFile.Open(os.path.join(scriptdir, relpath))
t = ft.Get('partTree')

# get daughters function
# Lists of daughter meta data are made:
# 0: ID
# 1: name
# 2: (initial) X Y Z
# 3: (initial) energy
# 4: (initial) time
# 5: (initial) volume
# 6: whether or not it has a track (i.e. its own key in the final dictionary)
def getDaughters(t):
	dlists = []
	# types of daughters to save for various mothers
	saveLists = {\
		'neutron' : ['neutron', 'gamma'],
		'gamma'   : ['e+', 'e-']
	}
	# loop through daughters and save the relevant ones
	if t.name in saveLists.keys():
		for i in range(len(t.Dname)):
			if t.Dname[i] in saveLists[str(t.name)]:
				dlists.append(\
					[\
						t.DID[i],
						t.Dname[i],
						[t.Dx[i], t.Dy[i], t.Dz[i]],
						t.Denergy[i],
						t.Dtime[i],
						t.Dvol[i],
						t.DhasTrack[i]
					]
				)
	# additionally, save the last daughter for neutron captures
	if t.name == 'neutron' and t.process[-1] == 'nCapture':
		dlists.append(\
			[\
				t.DID[-1],
				t.Dname[-1],
				[t.Dx[-1], t.Dy[-1], t.Dz[-1]],
				t.Denergy[-1],
				t.Dtime[-1],
				t.Dvol[-1],
				t.DhasTrack[-1]
			]
		)
	
	# make classes and return
	daughters = [Daughter(dl) for dl in dlists]
	return daughters

# === Fill initial dictionary and "parent list"
# dictionary is indexed by the Track ID string, and contains a list:
#  0: track ID (redundant with the key, but good if the lists are split out, as they are later)
#  1: particle name
#  2: parent ID
#  3: integrated travel distance (for this segment only)
#  4: final process (check for nCapture)
#  5: final volume
#  6: list of daughters
#  7: initial X Y Z
#  8: initial energy
#  9: final X Y Z
# 10: final nonzero energy

print "Filling initial dictionary..."
parts = {}
#plist = []
parts['0'] = ['0', 'null', '0', None, None, None, [], [], 0, [], 0]
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
		t.vol[-1],
		getDaughters(t),
		[t.x[0], t.y[0], t.z[0]],
		t.energy[0],
		[t.x[-1], t.y[-1], t.z[-1]],
		t.energy[-2]
	]

	#plist.append((str(t.parent), str(t.ID)))
print "Done filling initial dictionary."

# ==== Commenting out the old way of getting the daughter list (including plist)
## === Make Daughter Lists
## this is very important for efficiently making lists of daughters
## python's sort sorts by the first element of a tuple by default
#print "Sorting by parent..."
#plist.sort()
#
## now for the magic: itertools groupby cuts up the list by unique key
## the resulting list is the list of daughters; just stick it in the list
#print "Making daughter lists..."
#for k, g in groupby(plist, lambda x: x[0]):
#	j = list(g)
#	parts[k][5] = [i[1] for i in j]

# No longer saving the raw lists as pickles
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
picklepath = '../../pantry/particles_'+sys.argv[1]+'.pickle'
pickle.dump(cparts, open(os.path.join(scriptdir, picklepath),'wb'), 2)
print 'Done.'
