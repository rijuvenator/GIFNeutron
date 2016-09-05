import sys
from Gif.Neutron.Particle import Unpickle

# Requires 1 argument, the suffix used when making the tree
if len(sys.argv) < 2:
	print 'usage: script.py suffix'
	exit()

parts = Unpickle(sys.argv[1])

print 'Starting analysis'
# === Work with Neutrons
# find neutrons, "unique" neutrons, and captured neutrons
# print information about captured neutrons
neutrons = [parts[p] for p in parts.keys() if parts[p].name == 'neutron']
endneutrons = []
captured = []
for n in neutrons:
	foundN = False
	for nd in n.daughters:
		if parts[nd].name == 'neutron':
			foundN = True
			break
	if not foundN:
		endneutrons.append(n)
		if n.process == 'nCapture':
			captured.append(n)

print len(neutrons), "neutrons, but only", len(endneutrons), "neutrons without neutron daughters"
print "Of THOSE neutrons,", len(captured), "were captured."

#for n in captured:
#	if n.energy_final < 1.19e-6 and n.energy_final > 1.10e-6:
#		print "Neutron (ID %7s) with energy %.4e, daughter of a %13s (ID %7s), with daughters:" % (\
#				n.ID, n.energy_final, parts[n.parent].name, n.parent)
#		for nd in n.daughters:
#			print "   %13s (ID %7s)" % (parts[nd].name, nd)
#		print ""
#
#for n in captured:
#	print "Neutron (ID %7s) with energy %.4e, daughter of a %13s (ID %7s), with daughters:" % (\
#			n.ID, n.energy_final, parts[n.parent].name, n.parent, len(n.daughters))

for n in endneutrons:
	currn = n
	dist = currn.dist
	while parts[currn.parent]=='neutron':
		currn = parts[currn.parent]
		dist += currn.dist
	print dist


