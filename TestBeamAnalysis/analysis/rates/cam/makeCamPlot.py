from ROOT import *
import numpy as np
import commands as cmd
import Gif.TestBeamAnalysis.Plotter as Plotter

f = open('data')
print "File opened"

class Meas:
	def __init__(self, line):
		l = line.strip('\n').split()
		self.meas    = int(l[0])
		self.source  = bool(int(l[1]))
		self.up      = int(l[2])
		self.down    = int(l[3])
		self.pretrig = int(l[4])
		self.trig    = int(l[5])
		self.cfebs   = [float(l[6]), float(l[7]), float(l[8]), float(l[9])]
		#if self.cfebs[0] < 1000:
		#	tmpcfebs = self.cfebs[:]
		#	self.cfebs = [1000.*i for i in tmpcfebs]


meas = []
for line in f:
	meas.append(Meas(line))
print "Measurement classes made"

atten = np.array([10., 15., 22., 33., 46., 0.])
#atten = np.array([10., 15., 22., 33., 46.])
curr = np.array([23.4838888889, 19.0733333333, 12.2422222222, 9.49944444444, 7.95222222222, 0.0238888888889])
#curr = np.array([23.4838888889, 19.0733333333, 12.2422222222, 9.49944444444, 7.95222222222])
modes = np.array([
		[0,0   ],
		[2,0   ],
		[4,0   ],
		[6,0   ],
		[8,0   ],
		[10,0  ],
		[2,2   ],
		[4,4   ],
		[6,6   ],
		[8,8   ],
		[10,10 ]
		]
		)

rate = []
rmax = 0.
rmin = float("inf")
for i, mode in enumerate(modes):
	rate.append([])
	for a in atten:
		for m in meas:
			if m.pretrig == mode[0] and m.trig == mode[1] and m.down == a:
				val = sum(m.cfebs)
				rate[i].append(val)
				break

rate = np.array(rate)
print "Rate array made"

#nrate = rate / np.tile(np.array([rate[:,-1]]).transpose(), (1,rate.shape[1]))
nrate = rate / np.tile(rate[0,:], (rate.shape[0],1))

rmax = np.amax(rate)
rmin = np.amin(rate)
#rmax = np.amax(nrate)
#rmin = np.amin(nrate)

graphs = []
plots = []
for i, mode in enumerate(modes):
	graphs.append(TGraph(len(atten), curr * 5.e33, np.array(rate[i,:])))
#	graphs.append(TGraph(len(atten), curr * 5.e33, np.array(nrate[i,:])))
	plots.append(Plotter.Plot(graphs[i], "("+str(mode[0])+","+str(mode[1])+")", "p", "AP" if i==0 else "P"))

canvas = Plotter.Canvas("ME2/1, Self-Triggered Cosmics", True, 0., "Internal", 800, 700)
#canvas = Plotter.Canvas("ME2/1, Self-Triggered Cosmics", False, 0., "Internal", 800, 700)

canvas.makeLegend(.125,.37,'br',0.02,0.03)
#canvas.makeLegend(.125,.37,'tl',0.05,0.03)

#cols =  [1, 2, 3, 4, kOrange, 6, 7, 8, 46, kCyan+1, kGray]
#marks = [kOpenCircle, kOpenSquare, kOpenTriangleUp, kOpenTriangleDown, kOpenCircle, kOpenSquare, kOpenTriangleUp, kOpenTriangleDown, kOpenStar, kOpenCross, kOpenDiamond]
cols = [kBlack, kRed, kOrange, kGreen-2, kBlue+3, kMagenta, kRed, kOrange, kGreen-2, kBlue+3, kMagenta]
marks = [kOpenCircle, kOpenSquare, kOpenSquare, kOpenSquare, kOpenSquare, kOpenSquare, kPlus, kPlus, kPlus, kPlus, kPlus] 
for i, p in enumerate(plots):
	canvas.addMainPlot(p, i==0, True)
	p.plot.SetLineColor(cols[i])
	p.plot.SetMarkerColor(cols[i])
	p.plot.SetMarkerStyle(marks[i])
	p.plot.SetMarkerSize(2 if i==0 else 1)

plots[0].scaleTitles(0.8)
plots[0].scaleLabels(0.8)
#graphs[0].GetYaxis().SetTitle("CFEB Sum")
graphs[0].GetYaxis().SetTitle("Normalized CFEB Sum")
graphs[0].GetXaxis().SetTitle("Luminosity [cm^{-2} s^{-1}]")
graphs[0].GetXaxis().SetLimits(-2.e33,13.e34)
graphs[0].GetYaxis().SetRangeUser(rmin*0.8,rmax*1.2)
#graphs[0].GetYaxis().SetRangeUser(rmin*0.7,rmax*1.3)
TGaxis.SetExponentOffset(-0.08, 0.02, "y")
graphs[0].GetYaxis().SetDecimals()
graphs[0].GetYaxis().SetTitleOffset(graphs[0].GetYaxis().GetTitleOffset() * 1.35)
canvas.mainPad.SetRightMargin(canvas.mainPad.GetRightMargin() * 1.05)

canvas.leg.SetBorderSize(1)
canvas.finishCanvas()

canvas.c.SaveAs("cam.pdf")
