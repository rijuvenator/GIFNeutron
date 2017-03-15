import numpy as np
import ROOT as R
import re
import Gif.Analysis.Plotter as Plotter

R.gROOT.SetBatch(True)

class SimHit(object):
	def __init__(self, *args):
		self.event       = args[0]
		self.cham        = args[1]
		self.track       = args[2]
		self.eloss       = args[3]
		self.ds          = args[4]
		self.pid         = args[5]
		self.name        = args[6]
		self.proc        = args[7]
		self.vol         = args[8]
		self.fromNeutron = args[9]

f = open('output/fulllog.log')
simhits = []
num = re.compile(r'\d')
arr = re.compile(r'<=')
for line in f:
	cols = line.strip('\n').split()
	if cols[0] == 'Event':
		event = int(cols[1])
	elif re.match(num, cols[0]):
		cham  = int  (cols[0])
		track = int  (cols[1])
		eloss = float(cols[2])
		ds    = float(cols[3])
		pid   = int  (cols[4])
		name  = str  (cols[5])
		proc  = str  (cols[6])
		vol   = str  (cols[7])
	elif re.search(arr, line):
		if cols[-1] == 'neutron':
			fromNeutron = True
		elif cols[-1] == '0':
			fromNeutron = False
		simhits.append(SimHit(event, cham, track, eloss, ds, pid, name, proc, vol, fromNeutron))


for simhit in simhits:
	if simhit.ds < 0.1:
		print '{:3d} {:8d} {:.4f} {:.4f}'.format(simhit.event, simhit.track, simhit.ds, simhit.eloss)


h = {}
h['DS_EL_Neutron'] = R.TH2F('h'+'DS_EL_Neutron', '', 100, 0, .02, 45, 0, 15)
h['DS_EL_Other'  ] = R.TH2F('h'+'DS_EL_Other'  , '', 100, 0, .02, 45, 0, 15)

for simhit in simhits:
	if simhit.fromNeutron:
		h['DS_EL_Neutron'].Fill(simhit.ds, simhit.eloss)
	else:
		h['DS_EL_Other'  ].Fill(simhit.ds, simhit.eloss)

def makePlot():
	plotN = Plotter.Plot(h['DS_EL_Neutron'])
	plotO = Plotter.Plot(h['DS_EL_Other'  ])
	canvas = Plotter.Canvas(lumi='Energy Loss vs. Track Length')
	canvas.addMainPlot(plotN)
	canvas.addMainPlot(plotO)
	plotN.SetMarkerColor(R.kRed)
	canvas.firstPlot.setTitles(X='#Deltas [cm]', Y='Energy Loss [keV]')
	canvas.finishCanvas()
	canvas.save('plot.pdf')
makePlot()
