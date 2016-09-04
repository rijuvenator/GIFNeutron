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

captured.sort()

THERMAL = 0.025e-9
thermals = []
rests = []
for nID in captured:
	#print "Considering #%-7s : top energy %.4e" % (nID, parts[nID].energy_init)
	thermalID = nID
	while THERMAL > parts[thermalID].energy_init:
		thermalID = parts[thermalID].parent
		#print '    -> Now #%-7s : top energy %.4e' % (thermalID, parts[thermalID].energy_init)
		if thermalID == '0':
			break
	thermals.append(thermalID)

	restDist = parts[nID].dist
	dID = nID
	while dID != thermalID:
		dID = parts[dID].parent
		restDist += parts[dID].dist
	rests.append(restDist)

import ROOT as R

f = R.TFile.Open('../../python/partTree.root')
t = f.Get('partTree')

count = 0
for i in range(t.GetEntries()):
	t.GetEntry(i)
	if t.ID in thermals:
		count += 1
		nID = captured[thermals.index(t.ID)]
		if t.energy[-2] > THERMAL:
			continue
		idx = -2
		while t.energy[idx] < THERMAL:
			idx -= 1
		# it turns out for all relevant cases, they go from thermal to capture in one particle
		#print '%s %s %.4e' % (t.ID, nID, t.track[-1] - t.track[idx] + rests[thermals.index(t.ID)])
		print '%.4e' % (t.track[-1] - t.track[idx] + rests[thermals.index(t.ID)])
		sys.stdout.flush()
	if count == 9050:
		break
