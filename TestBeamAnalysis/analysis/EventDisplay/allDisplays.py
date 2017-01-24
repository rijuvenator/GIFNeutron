#! /usr/bin/env python

import subprocess as bash

data = {}
f = open('rawlist')
for line in f:
	cols = line.strip('\n').split()
	data[int(cols[2])] = cols[4:]

f.close()

for cham in sorted(data.keys()):
	f = open('temp','w')
	for event in data[cham]:
		f.write(event + '\n')
	f.close()
	bash.call(['python', 'EventDisplay.py' , '--cham', str(cham), '--list', 'temp', '--file', '../test.root'])
	#bash.call(['python', 'RecHitDisplay.py', '--cham', str(cham), '--list', 'temp', '--file', '../test.root'])
	bash.call(['rm', 'temp'])
