import sys
from itertools import groupby
from Gif.Neutron.Particle import Unpickle

# Requires 1 argument, the suffix used when making the tree
if len(sys.argv) < 2:
	print 'Usage: script.py SUFFIX'
	exit()

parts = Unpickle(sys.argv[1])

# prints stuff out about daughters

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

#daughts = []
#for n in uneutrons:
#	print "ID: %7s: Energy = %.4e" % (n.ID, n.energy_final)
#	dnlist = [(parts[k].name,k) for k in n.daughters]
#	dnlist.sort()
#	for k, g in groupby(dnlist, lambda x: x[0]):
#		j = list(g)
#		print '%8s: %2i' % (k, len(j)),
#		for l in j:
#			if l[0]=='gamma':
#				print '%.4e' % parts[l[1]].energy_final,
#		print ''
#		#daughts.append(k)
#	print ""
#
#daughts.sort()
#for k, g in groupby(daughts):
#	print '%13s: %i' % (k, len(list(g)))

others = []
for n in uneutrons:
	if n.process != 'nCapture':
		others.append(n.process)
print "End neutrons that weren't captured underwent one of these processes:"
for i in list(set(others)):
	print "   ", i

print "\n\n"

def isWithin(r1, r2, thres=1.0):
	return (sum([(i-j)**2 for i,j in zip(r1,r2)]))**0.5 < thres	

for n in captured:
	#print 'Captured neutron #%-7s with final energy %.4e and daughters:' % (n.ID, n.energy_final)
	#print 'Gammas ',
	for d in parts[n].daughters:
		if isWithin(parts[n].pos_final, parts[d].pos_init):
			print parts[d].name, parts[d].ID, parts[d].energy_init
		#if parts[d].pos_init == n.pos_final:
		#if parts[d].pos_init == n.pos_final and parts[d].name == 'gamma' and parts[d].energy_init > 3.5e-3 and parts[d].energy_init < 5.0e-3:
			#print parts[d].name, parts[d].ID, parts[d].energy_init
			#break
			#print " %13s #%-7s with energy %.4e" % (parts[d].name, parts[d].ID, parts[d].energy_init)
			#print "%.4e" % (parts[d].energy_init),
	print ""
