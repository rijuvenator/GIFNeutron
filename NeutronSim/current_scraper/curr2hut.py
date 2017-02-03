import sys

# Take the output of sel.py, strip the semicolons, [i], and _m; leave the pressure (it induces a newline)
f = open(sys.argv[1])
for line in f:
	if line[0] == '#':
		rawmeas = line.split()[0].lstrip('#')
		print rawmeas, 
	if line[0] == 'A':
		atten = line.split()[0].split('=')[1]
		print "%5s" % atten,
	if line[0] == 'I':
		if 'no data' not in line:
			print "%5s" % line.split('=')[1].strip('\n'), 
		else:
			print "     ",
	if line[0] == 'P':
		print ""
