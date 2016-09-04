from itertools import groupby
from Gif.Neutron.Particle import parts

# Print out final positions

print 'Starting analysis'
neutrons = [parts[p] for p in parts.keys() if parts[p].name == 'neutron']
uneutrons = []
captured = []
for n in neutrons:
	foundN = False
	for nd in n.daughters:
		if parts[nd].name == 'neutron':
			foundN = True
			break
	if not foundN:
		uneutrons.append(n)
		if n.process == 'nCapture':
			captured.append(n)

for n in captured:
    deut = False
    for nd in n.daughters:
        if parts[nd].name == 'deuteron': deut = True
    if deut:
        print n.pos_final[0], n.pos_final[1], n.pos_final[2], parts[nd].name
    else:
        print n.pos_final[0], n.pos_final[1], n.pos_final[2], 'No'
