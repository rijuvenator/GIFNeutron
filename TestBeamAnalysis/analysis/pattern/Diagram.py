import ROOT as R
import Gif.TestBeamAnalysis.Plotter as Plotter

R.gROOT.SetBatch(True)

class Canvas(R.TCanvas):
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
		for x in range(self.LAYOUT['x']):
			for y in range(self.LAYOUT['y']):
				x1 = x     * self.WIDTH  / float(self.CWIDTH )
				y1 = y     * self.HEIGHT / float(self.CHEIGHT)
				x2 = (x+1) * self.WIDTH  / float(self.CWIDTH )
				y2 = (y+1) * self.HEIGHT / float(self.CHEIGHT)
				self.PADS[(x,y)] = R.TPad(str(x)+str(y),'',x1,y1,x2,y2)
				self.PADS[(x,y)].Draw()

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
	
	def drawGrid(self, pair, pid):
			self.cd()
			self.PADS[pair].cd()
			boxes = {\
				0 : (3., 3.),
				1 : (4., 3.),
				2 : (5., 3.),
				3 : (5., 2.),
				4 : (5., 1.),
				5 : (4., 1.),
				6 : (3., 1.),
				7 : (3., 2.),
				8 : (4., 2.),
			}
			for box in boxes:
				x1 = (boxes[box][0] * 100.        ) / self.WIDTH
				y1 = (boxes[box][1] * 100.        ) / self.HEIGHT
				x2 = (boxes[box][0] * 100. + 100. ) / self.WIDTH
				y2 = (boxes[box][1] * 100. + 100. ) / self.HEIGHT
				self.BOXES.append(R.TBox(x1,y1,x2,y2))
				self.BOXES[-1].SetLineWidth(1)
				if pid & (1<<box) or box == 8:
					self.BOXES[-1].SetFillColor(R.kGray)
				else:
					self.BOXES[-1].SetFillColor(R.kWhite)
				self.BOXES[-1].Draw('l')
	
	def drawLines(self):
		self.cd()
		self.LINES = [\
			R.TLine((1. -0.05)/self.LAYOUT['x'], 0, (1. -0.05)/self.LAYOUT['x'], 1),
			R.TLine((3. -0.05)/self.LAYOUT['x'], 0, (3. -0.05)/self.LAYOUT['x'], 1),
			R.TLine((12.-0.05)/self.LAYOUT['x'], 0, (12.-0.05)/self.LAYOUT['x'], 1)
		]
		for line in self.LINES:
			line.SetLineWidth(1)
			line.Draw()
	
	def save(self):
		self.SaveAs('test.pdf')

c = Canvas(layout={'x':13,'y':4})
labels = [\
	0,                   # 1 isolated
	1, 16, 4, 64,        # 2 diag: neg neg pos pos
		2, 32,           # 2 vert
		8, 128,          # 2 horiz
	3, 24, 160,          # 3 Gamma
		6, 40, 192,      # 3 Corner
		9, 72, 132, 144, # 3 knight: TL BL TR BR
		10, 48, 129,     # 3 L
		12, 96, 130,     # 3 J
		17, 68,          # 3 diag: neg pos
		18, 33, 36, 66,  # 3 periscope: BR TL TR BR
		5, 20, 80, 65,   # 3 C: U R B L
		34,              # 3 vert
		136,             # 3 horiz
	161                  # 4 S
]
names = [\
	'Lonely',
	'2#minusDiag-U', '2#minusDiag-D', '2+Diag-U', '2+Diag-D',
	'2-Vert-U', '2-Vert-D', '2-Horiz-U', '2-Horiz-D',
	'Corner-U', 'Corner-R', 'Corner-L',
	'Gamma-U', 'Gamma-R', 'Gamma-L',
	'Knight-TL', 'Knight-BL', 'Knight-TR', 'Knight-BR',
	'L-R', 'L-D', 'L-L',
	'J-R', 'J-D', 'J-L',
	'3#minusDiag', '3+Diag',
	'Peri-BR', 'Peri-TL', 'Peri-TR', 'Peri-BR',
	'C-U', 'C-R', 'C-B', 'C-L',
	'3-Vert', '3-Horiz',
	'S'
]
pairlist = [\
	(0,  3),
	(1,  3), (1,  2), (1,  1), (1,  0),
	(2,  3), (2,  2), (2,  1), (2,  0),
	(3,  3), (3,  2), (3,  1),
	(4,  3), (4,  2), (4,  1),
	(5,  3), (5,  2), (5,  1), (5,  0),
	(6,  3), (6,  2), (6,  1),
	(7,  3), (7,  2), (7,  1),
	(8,  3), (8,  2),
	(9,  3), (9,  2), (9,  1), (9,  0),
	(10, 3), (10, 2), (10, 1), (10, 0),
	(11, 3), (11, 2),
	(12, 3)
]
pairdict = dict(zip(pairlist, zip(labels, names)))

for pair in pairlist:
	c.drawGrid(pair, pairdict[pair][0])
	c.drawText(text='PID '+str(pairdict[pair][0]), pos=(10./c.WIDTH, 300./c.HEIGHT), fontcode='b', fontscale=1.25)
	c.drawText(text=       str(pairdict[pair][1]), pos=( 0./c.WIDTH, 200./c.HEIGHT), fontcode='b', fontscale=1.25)
c.drawLines()
c.save()

