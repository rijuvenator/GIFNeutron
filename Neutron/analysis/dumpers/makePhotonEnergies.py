import sys
from Gif.Neutron.Particle import parts

# For printing to stderr. Use to print anything you don't want in output.
def eprint(string):
	sys.stderr.write(string+'\n')
	sys.stderr.flush()

eprint('Starting analysis.')

# fill lists of IDs of neutrons, end neutrons, and captured
neutrons = [parts[p].ID for p in parts.keys() if parts[p].name == 'neutron']
endneutrons = []
captured = []

for nID in neutrons:
	foundN = False
	for dID in parts[nID].daughters:
		if parts[dID].name == 'neutron':
			foundN = True
			break
	if not foundN:
		endneutrons.append(nID)
		if parts[nID].process == 'nCapture':
			captured.append(nID)

eprint("%i neutrons; %i end neutrons; %i captured neutrons" % (len(neutrons), len(endneutrons), len(captured)))

# for cutting on some threshold distance thresh in cm
def isWithin(r1, r2, thresh=0.05):
	return (sum([(i-j)**2 for i,j in zip(r1,r2)]))**0.5 < thresh

# make photon energy list
for nID in captured:
	for dID in parts[nID].daughters:
		if isWithin(parts[nID].pos_final, parts[dID].pos_init) and parts[dID].name == 'gamma':
			print '%.4e' % (parts[dID].energy_init),
	print ''
