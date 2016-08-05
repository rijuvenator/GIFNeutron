f = open("stuff")

isFirst = True
prev = []
current = []
for i,line in enumerate(f):
	s = line.strip("\n").split()
	if isFirst:
		prev = [s[1], s[2], s[5], s[6]]
		isFirst = False
	else:
		if s[3] == "0":
			current = [s[1], s[2], "0", "0"]
		else:
			current = [s[1], s[2], s[5], s[6]]
		if prev != current:
			print s[0]
			prev = current
