f = open('attenhut')

ranges = []
for line in f:
	s = line.split()
	r = range(int(s[1].split('-')[0]), int(s[1].split('-')[1])+1)
	ranges.append(r)

f = open('cleantmb')

for line in f:
	if line[0]=='%':
		continue
	ll = []
	ss = []
	for s in [int(i) for i in line.strip('\n').split()[2:6]]:
		for r in ranges:
			if s in r:
				ss.append(s)
				ll.append(r[0])
	print "%4s" % line.split()[0],
	for l in ll:
		print l,
	for s in ss:
		print s,
	print ""
