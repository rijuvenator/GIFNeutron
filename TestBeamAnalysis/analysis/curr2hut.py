f = open("currents")
for line in f:
	if line[0] == '#':
		rawmeas = line.split()[0].lstrip('#')
		print rawmeas, 
	if line[0] == 'A':
		atten = line.split()[0].split('=')[1]
		print "%5s" % atten,
	if line[0] == 'I':
		print "%5s" % line.split('=')[1].strip('\n'), 
	if line[0] == 'P':
		print ""
