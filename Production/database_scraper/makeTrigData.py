import sys

class Dump():
	def __init__(self):
		self.meas = 0
		self.time = ""
		self.duration = 0
		self.cham = ""
		self.alct0 = 0
		self.alct1 = 0
		self.cfeb0 = 0
		self.cfeb1 = 0
		self.cfeb2 = 0
		self.cfeb3 = 0
		self.cfeb4 = 0
		self.cfeb5 = 0
		self.cfeb6 = 0
		self.clct0 = 0
		self.clct1 = 0
		self.lct = 0
		self.l1a = 0
		self.window = 0
	
	def Print(self):
		print "%4s %1s %9s %9s %9s %9s %9s %9s %9s %9s %9s %9s %9s %9s %9s %.1f %9s" % (\
				self.meas,
				'1' if 'ME+1' in self.cham else '2',
				self.alct0,
				self.alct1,
				self.cfeb0,
				self.cfeb1,
				self.cfeb2,
				self.cfeb3,
				self.cfeb4,
				self.cfeb5,
				self.cfeb6,
				self.clct0,
				self.clct1,
				self.lct,
				self.l1a,
				self.duration,
				self.window
				)
		if 'ME+2' in self.cham: print ""

f = open(sys.argv[1])
dumplist = []
dump = Dump()
dump.meas = sys.argv[1][0:4]

goodlist = []
goodlist.extend(range(3284,3292))
goodlist.extend(range(3222,3230))
goodlist.extend(range(3308,3316))
goodlist.extend(range(3295,3304))
goodlist.extend(range(3317,3326))
goodlist.extend(range(3232,3241))
goodlist.extend(range(3241,3250))
goodlist.extend(range(3250,3258))
goodlist.extend(range(3339,3347))
goodlist.extend(range(3347,3355))
goodlist.extend(range(3384,3392))
goodlist.sort()

if int(dump.meas) not in goodlist:
	exit()

for line in f:
	cols = line.strip('\n').split()
	if cols[0] == 'Time:':
		dump.time = cols[1]+" "+cols[2]
	elif cols[0] == 'Period':
		dump.duration = float(cols[-1])
	elif cols[0] == 'Chamber:':
		dump.cham = cols[-1]
	elif cols[0] == '0ALCT:':
		dump.alct0 = int(cols[-1])
	elif cols[0] == '1ALCT:':
		dump.alct1 = int(cols[-1])
	elif cols[0] == '14CLCT:':
		dump.cfeb0 = int(cols[-1])
	elif cols[0] == '15CLCT:':
		dump.cfeb1 = int(cols[-1])
	elif cols[0] == '16CLCT:':
		dump.cfeb2 = int(cols[-1])
	elif cols[0] == '17CLCT:':
		dump.cfeb3 = int(cols[-1])
	elif cols[0] == '18CLCT:':
		dump.cfeb4 = int(cols[-1])
	elif cols[0] == '19CLCT:':
		dump.cfeb5 = int(cols[-1])
	elif cols[0] == '20CLCT:':
		dump.cfeb6 = int(cols[-1])
	elif cols[0] == '29CLCT:':
		dump.clct0 = int(cols[-1])
	elif cols[0] == '30CLCT:':
		dump.clct1 = int(cols[-1])
	elif cols[0] == '32TMB:':
		dump.lct = int(cols[-1])
	elif cols[0] == '55L1A:':
		dump.l1a = int(cols[-1])
	elif cols[0] == '56L1A:':
		dump.window = int(cols[-1])
		dumplist.append(dump)
		dump.Print()

print '---'
