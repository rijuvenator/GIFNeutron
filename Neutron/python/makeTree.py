import sys
import ROOT as R

# Requires 2 arguments now: the event log file and a suffix
if len(sys.argv) < 3:
	print 'Usage: makeTree.py EVENTFILE SUFFIX'
	exit()

# Makes a TTree from a GEANT Event Log ending in a line with ***
#f = open('/afs/cern.ch/work/a/adasgupt/Neutron/E1')
f = open(sys.argv[1])

# Declare output file and tree
# Just to be safe, stop Python from managing the tree's memory
outfile = R.TFile('partTree_'+sys.argv[2]+'.root','RECREATE')
t = R.TTree('partTree','partTree')
R.SetOwnership(t, False)

# We need C++ classes to give to TTree::Branch; luckily ROOT
# loads in the STL, and we can access their constructors
# Then the variables are the relevant reference/pointer
name    = R.string()
ID      = R.string()
parent  = R.string()
x       = R.vector('float' )()
y       = R.vector('float' )()
z       = R.vector('float' )()
energy  = R.vector('float' )()
dE      = R.vector('float' )()
step    = R.vector('float' )()
track   = R.vector('float' )()
vol     = R.vector('string')()
process = R.vector('string')()

# Declare branches. Nothing new here.
t.Branch('name'   ,name   )
t.Branch('ID'     ,ID     )
t.Branch('parent' ,parent )
t.Branch('x'      ,x      )
t.Branch('y'      ,y      )
t.Branch('z'      ,z      )
t.Branch('energy' ,energy )
t.Branch('dE'     ,dE     )
t.Branch('step'   ,step   )
t.Branch('track'  ,track  )
t.Branch('vol'    ,vol    )
t.Branch('process',process)

# We will parse the Event Log by keeping track of the state: whether we're in the header or the body
# State 1 is AFTER the first row of stars; it's the header.
#   Grab the name, ID, and parent**
# State 2 is AFTER the second row of starts; it's the body.
#   Skip the first line which is the column list
#   Fill the vectors here.
#      Fill dE, Step, TrackL, and Process with blanks for the first line.
# State 3 is ON the third row of stars, which is the first row of the next particle
#   Fill the tree and clear** the branches
#   Reset to State 1 so that the next header can be filled
#
# ** See below for a note about a weird quirk involving strings and vectors.

count = 0
state = 0
for line in f:
	count += 1
	print 'Doing line #%i\r' % count,
	sys.stdout.flush()
	if '***' in line:
		state += 1
		if state < 3: continue
	if state == 1:
		l = line.strip('\n').lstrip('*').split()
		name   .assign(l[4].strip(','))
		ID     .assign(l[8].strip(','))
		parent .assign(l[12]          )
	elif state == 2:
		if line[0:4] == 'Step': continue
		l = line.strip('\n').split()
		x      .push_back(float(l[1]))
		y      .push_back(float(l[2]))
		z      .push_back(float(l[3]))
		energy .push_back(float(l[4]))
		if len(l)==6:
			dE     .push_back(0.0)
			step   .push_back(0.0)
			track  .push_back(0.0)
			vol    .push_back(l[5])
			process.push_back('')
		elif len(l)==10:
			dE     .push_back(float(l[5]))
			step   .push_back(float(l[6]))
			track  .push_back(float(l[7]))
			vol    .push_back(l[8])
			process.push_back(l[9])
	elif state == 3:
		state = 1
		t.Fill()
		name   .clear()
		ID     .clear()
		parent .clear()
		x      .clear()
		y      .clear()
		z      .clear()
		energy .clear()
		dE     .clear()
		step   .clear()
		track  .clear()
		vol    .clear()
		process.clear()

t.Write()
print ''

# The main thing to note here is how the branches are assigned and emptied
# The tree was segfaulting randomly on a particular particle. After a lot
# of Googling, what worked for me was a guy who said that since the variables
# are references/pointers, you cannot assign to them, as it is "deleting" the
# memory. So the trick is that instead of clearing a string by setting it equal
# to '', or even assigning to a string by setting it equal to something, you
# must use the underlying function calls. That way you do not assign to the
# address. It's really weird, but it's the only way I managed to get the tree filled.
