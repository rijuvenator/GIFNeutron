import ROOT as R
import Gif.Analysis.Plotter as Plotter

R.gROOT.SetBatch(True)

class Canvas(R.TCanvas):
	# layout defines the sub-pad structure: x=cols, y=rows
	def __init__(self, layout={'x':1,'y':1}):
		self.HEIGHT = 500
		self.WIDTH  = 700
		self.LAYOUT = layout
		self.CWIDTH = self.LAYOUT['x']*self.WIDTH
		self.CHEIGHT = self.LAYOUT['y']*self.HEIGHT
		self.BOXES = []
		self.PADS = {}

		Plotter.setStyle(self.CWIDTH, self.CHEIGHT, 42, 0.04)
		R.TCanvas.__init__(self, 'c', '', self.CWIDTH, self.CHEIGHT)
		self.SetFillStyle(4000)
		# Make pads
		for x in range(self.LAYOUT['x']):
			for y in range(self.LAYOUT['y']):
				x1 = x     * self.WIDTH  / float(self.CWIDTH )
				y1 = y     * self.HEIGHT / float(self.CHEIGHT)
				x2 = (x+1) * self.WIDTH  / float(self.CWIDTH )
				y2 = (y+1) * self.HEIGHT / float(self.CHEIGHT)
				self.PADS[(x,y)] = R.TPad(str(x)+str(y),'',x1,y1,x2,y2)
				self.PADS[(x,y)].SetFillStyle(4000)
				self.PADS[(x,y)].Draw()

	# ~generic drawText function
	def drawText(self, text='', pos=(0., 0.), align='bl', fontcode='', fontscale=1.):
		latex = R.TLatex()
		AlignDict = {'l' : 1, 'c' : 2, 'r' : 3, 'b' : 1, 't' : 3}
		FontDict = {'' : 4, 'i' : 5, 'b' : 6, 'bi' : 7}
		RAlign = 10 * AlignDict[align[1]] + AlignDict[align[0]]
		RFont = 10 * FontDict[fontcode] + 2
		latex.SetTextAlign(RAlign)
		latex.SetTextFont(RFont)
		latex.SetTextSize(0.1 * fontscale)
		latex.DrawLatexNDC(pos[0], pos[1], text)
	
	# draw a pattern pad
	def drawGrid(self, pair, pid):
			self.cd()
			self.PADS[pair].cd()
			# mapping from box bit number to lower left corner pixel position / 100
			boxes = {
				0 : (3., 3.),
				1 : (4., 3.),
				2 : (5., 3.),
				3 : (3., 2.),
				4 : (4., 2.),
				5 : (5., 2.),
				6 : (3., 1.),
				7 : (4., 1.),
				8 : (5., 1.),
			}
			# draw the boxes; fill the ON boxes (defined by pid) with gray, and also the middle
			for box in boxes:
				x1 = (boxes[box][0] * 100.        ) / self.WIDTH
				y1 = (boxes[box][1] * 100.        ) / self.HEIGHT
				x2 = (boxes[box][0] * 100. + 100. ) / self.WIDTH
				y2 = (boxes[box][1] * 100. + 100. ) / self.HEIGHT
				if pid & (1<<box):
					self.BOXES.append(R.TBox(x1,y1,x2,y2))
					self.BOXES[-1].SetLineWidth(1)
					self.BOXES[-1].SetFillColor(R.kWhite)
					self.BOXES[-1].Draw('l')
	
	# draw visual boundary lines
	def drawLines(self):
		self.cd()
		self.LINES = [\
			R.TLine((1. - 0.15)/self.LAYOUT['x'], 0, (1. - 0.15)/self.LAYOUT['x'], 1),
			R.TLine((2. - 0.15)/self.LAYOUT['x'], 0, (2. - 0.15)/self.LAYOUT['x'], 1),
		]
		for line in self.LINES:
			line.SetLineWidth(1)
			line.Draw()
	
	# save
	def save(self):
		self.SaveAs('patterns_clustered_LS.pdf')

# instantiate canvas
c = Canvas(layout={'x':7, 'y':4})
# pids
labels = [\
	1,                # Lonely
	3, 9,             # 2-Horiz, 2-Vert
	10, 17,           # 2+Diag, 2-Diag
	11, 19, 25, 26,   # Gamma, Corner, L, J
	14, 28, 35, 49,   # Gun-R, Dog-R, Gun-L, Dog-L
	21, 42, 81, 138,  # Mickey-U, Mickey-D, Mickey-L, Mickey-R
	56, 73, 84, 273,  # 3-Horiz, 3-Vert, 3+Diag, 3-Diag
	74, 82, 137, 145, # Peri-TR, Peri-BL, Peri-BR, Peri-TL
]
# names
names = [\
	'Lonely',
	'2-Horiz', '2-Vert', '2+Diag', '2#minusDiag',
	'Gamma', 'Corner', 'L', 'J',
	'Gun-R', 'Dog-R', 'Gun-L', 'Dog-L',
	'Mickey-U', 'Mickey-D', 'Mickey-L', 'Mickey-R',
	'3-Horiz', '3-Vert', '3+Diag', '3#minusDiag',
	'Peri-TR', 'Peri-BL', 'Peri-BR', 'Peri-TL',
]
# ordered pad pairs
pairlist_ = [\
	(0, 6),
	(0, 5), (1, 5), (2, 5), (3, 5),
	(0, 4), (1, 4), (2, 4), (3, 4),
	(0, 3), (1, 3), (2, 3), (3, 3),
	(0, 2), (1, 2), (2, 2), (3, 2),
	(0, 1), (1, 1), (2, 1), (3, 1),
	(0, 0), (1, 0), (2, 0), (3, 0),
]
pairlist = [(6-pair[1], 3-pair[0]) for pair in pairlist_]
# { (pad pair) : (PID, name) }
pairdict = dict(zip(pairlist, zip(labels, names)))

for pair in pairlist:
	c.drawGrid(pair, pairdict[pair][0])
	c.drawText(text='PID '+str(pairdict[pair][0]), pos=(10./c.WIDTH, 300./c.HEIGHT), fontcode='b', fontscale=1.25)
	c.drawText(text=       str(pairdict[pair][1]), pos=( 0./c.WIDTH, 200./c.HEIGHT), fontcode='b', fontscale=1.25)
c.drawLines()
c.save()
