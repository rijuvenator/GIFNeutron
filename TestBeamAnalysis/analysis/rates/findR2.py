import commands as c
f = open('attenhut')

ranges = []
for line in f:
	s = line.split()
	r = range(int(s[1].split('-')[0]), int(s[1].split('-')[1])+1)
	ranges.append(r)

f = open('goodtmb')

startHere = False
for line in f:
	if 'SOURCE' not in line and not startHere:
		continue
	if 'SOURCE' in line:
		startHere = True
		continue
	if startHere:
		if 'ME' in line:
			continue
		if line == '\n':
			print ''
			continue
		m = int(line.split()[0])
		for r in ranges:
			if m in r:
				rs = c.getoutput('awk \'/'+str(r[0])+'-/ {$1=""; $2=""; print}\' attenhut').split()
				cc = sum([float(i) for i in rs])/len(rs)
				print "%4i : %5.2f :: " % (m, cc),

startHere = False
for line in f:
	if 'SOURCE' not in line and not startHere:
		continue
	if 'SOURCE' in line:
		startHere = True
		continue
	if startHere:
		if 'ME' in line:
			continue
		if line == '\n':
			print ''
			continue
		m = int(line.split()[0])
		print c.getoutput('grep ^'+str(m)+' trigdata')
