from itertools import groupby
from Gif.Neutron.Particle import parts

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

for n in captured:
	print 'Captured neutron #%-7s with final energy %.4e and daughters:' % (n.ID, n.energy_final)
	for d in n.daughters:
		#if parts[d].pos_init == n.pos_final:
		if parts[d].pos_init == n.pos_final and parts[d].name == 'gamma':
			#print " %13s #%-7s with energy %.4e" % (parts[d].name, parts[d].ID, parts[d].energy_init)
			print "Gammas %.4e" % (parts[d].energy_init),
	print ""
