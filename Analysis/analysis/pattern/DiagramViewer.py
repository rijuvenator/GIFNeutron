##### DIAGRAM VIEWER #####
# Prints the pattern for a given pattern ID in [0,511]
# Enter q to exit.

# 40 + (0:Black 1:Red 2:Green 3:Yellow 4:Blue 5:Magenta 6:Cyan 7:Grey) (+60 for brighter)
COLOR = 46

def printPattern(pattern):
	ON = '\033['+str(COLOR)+'m  \033[m'
	OFF= '  '
	# e.g. 4: 0b100 -> 100 -> 000000100 -> 001000000 -> [001],[000],[000]
	bitstring = list('{:0>9s}'.format(bin(pattern)[2:]))[::-1]
	output = [[ON if i=='1' else OFF for i in bitstring[b:b+3]] for b in (0, 3, 6)]
	for line in output:
		print ''.join(line)

while True:
	try:
		rawstring = raw_input('Enter Pattern ID (or q to Quit): ')
		if rawstring == 'q': break
		pattern = int(rawstring)
		assert(pattern>=0 and pattern<=511)
	except:
		print 'Pattern ID must be a number between 0 and 511.'
		continue
	printPattern(pattern)
