import sys
from Gif.Neutron.Particle import Unpickle
from Gif.Neutron.Tools import eprint

# Requires 1 argument, the suffix used when making the tree
if len(sys.argv) < 2:
	eprint('Usage: script.py SUFFIX')
	exit()

parts = Unpickle(sys.argv[1])

# Print out final positions

# Changed to have IDs instead of copying classes
eprint('Starting analysis')
neutrons = [parts[p].ID for p in parts.keys() if parts[p].name == 'neutron']
uneutrons = []
captured = []
for nID in neutrons:
	foundN = False
	for d in parts[nID].daughters:
		if d.name == 'neutron':
			foundN = True
			break
	if not foundN:
		uneutrons.append(nID)
		if parts[nID].process == 'nCapture':
			captured.append(nID)

for nID in captured:
    deut = False
	# Changed for new daughter class
    if parts[nID].daughters[-1].name == 'deuteron':
        deut = True
	# Bug in your code, Chris; nd should be out of scope by now. However, it is always the last daughter in python.
	# Check an older commit or ask me if you don't know what I'm talking about. I'm fixing it.
    if deut:
        print '%.4f %.4f %.4f %s' % (parts[nID].pos_final[0], parts[nID].pos_final[1], parts[nID].pos_final[2], 'deuteron')
    else:
        print '%.4f %.4f %.4f %s' % (parts[nID].pos_final[0], parts[nID].pos_final[1], parts[nID].pos_final[2], 'No')
