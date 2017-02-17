import ROOT as R

##########
# This file deals with ALL cosmetic aspects of the event displays
# Avoid explicitly doing any cosmetic work in EventDisplay.py, and do it here instead
# There could be histogram-specific considerations there, but try to avoid it
# Use setStyle for anything global; apply the rest to the pads with options
##########

def setStyle(mode):
	if mode == 'primitives' or 'rechits' or 'simhits':
		width   = 800
		height  = 600
	elif mode == 'origrechits' or 'origsimhits':
		width   = 800
		height  = 400

	style = R.TStyle("style","Style")

	# generic line thicknesses
	style.SetLineWidth(1)

	# canvas
	style.SetCanvasBorderMode(0)             # off
	style.SetCanvasColor(R.kWhite)           # white

	# pad
	style.SetPadBorderMode(0)                # off
	style.SetPadColor(R.kWhite)              # white 
	style.SetPadGridX(R.kFALSE)              # grid x
	style.SetPadGridY(R.kTRUE)               # grid y
	style.SetGridColor(R.kGray)              # gray
	style.SetGridStyle(3)                    # dotted
	style.SetGridWidth(1)                    # pixels

	# frame
	style.SetFrameBorderMode(0)              # off
	style.SetFrameFillColor(R.kWhite)        # white
	style.SetFrameFillStyle(0)               # hollow
	style.SetFrameLineColor(R.kWhite)        # white
	style.SetFrameLineStyle(1)               # solid
	style.SetFrameLineWidth(0)               # pixels

	# legend
	style.SetLegendBorderSize(0)             # off
	style.SetLegendFont(42)                  # helvetica normal

	# hist
	style.SetHistLineColor(R.kBlack)         # black
	style.SetHistLineStyle(1)                # solid
	style.SetHistLineWidth(2)                # pixels
	style.SetMarkerStyle(R.kFullDotLarge)    # marker
	style.SetMarkerColor(R.kBlack)           # black
	style.SetEndErrorSize(0)                 # no little lines on errors

	# stats box
	style.SetOptStat(0)                      # off

	# title
	style.SetOptTitle(1)                     # on
	style.SetTitleFont(62,"")                # helvetica normal
	style.SetTitleTextColor(R.kBlack)        # black
	style.SetTitleFontSize(20./200.)         # default 0
	style.SetTitleStyle(0)                   # hollow
	style.SetTitleFillColor(R.kWhite)        # white
	style.SetTitleBorderSize(0)              # default 2
	style.SetTitleAlign(11)                  # bottom left

	# axis labels
	style.SetLabelSize(20./200., "XYZ")      # size 16
	style.SetLabelFont(42, "XYZ")            # helvetica normal

	# axis titles
	style.SetTitleSize(20./200., "XYZ" )     # size 16
	style.SetTitleFont(62, "XYZ")            # helvetica bold  

	# axis
	style.SetAxisColor(R.kBlack, "XYZ")      # black
	style.SetStripDecimals(R.kTRUE)          # strip decimals
	style.SetPadTickX(1)                     # opposite x ticks
	style.SetPadTickY(1)                     # opposite y ticks
	style.SetNdivisions(10, "Y")             # nDivisions (primary + 100*secondary + 10000*tertiary)
	style.SetTickLength(0, "Y")              # no Layer ticks

	# palette
	style.SetPalette(55)

	style.cd()

##########
# Defines a Canvas class to create pads, set margins, draw text, etc
# Pads are 0 indexed from bottom to top (it's easier to define coordinates wrt bottom left that way)
# Feel free to add cosmetic functions here if you find yourself repeating something laboriously and tediously
##########

# give it a width, height, and a number of pads
class Canvas():
	def __init__(self, mode):
		self.mode = mode
		if self.mode == 'primitives' or 'rechits' or 'simhits':
			self.width   = 800
			self.height  = 600
			self.numPads = 3
		elif self.mode == 'origrechits' or 'origsimhits':
			self.width   = 800
			self.height  = 400
			self.numpads = 2

		self.frac = 1./self.numPads

		self.canvas = R.TCanvas('c', 'c', self.width, self.height)
		self.canvas.SetFillStyle(4000)

		self.pads = []
		for i in range(self.numPads):
			self.pads.append(R.TPad('p'+str(i), 'p'+str(i), 0, i*self.frac, 1, (i+1)*self.frac))
			self.pads[i].SetFillStyle(4000)

			self.pads[i].SetBottomMargin(self.pads[i].GetBottomMargin() * 2.2 )
			#self.pads[i].SetTopMargin   (self.pads[i].GetTopMargin()    * 1.6 )
			self.pads[i].SetLeftMargin  (self.pads[i].GetLeftMargin()   * 0.5 )
			self.pads[i].SetRightMargin (self.pads[i].GetRightMargin()  * 1.25)

			R.gStyle.SetTitleOffset(0.20, 'Y')
			R.gStyle.SetTitleOffset(0.35, 'Z')

			R.gStyle.SetTitleX(self.pads[i].GetLeftMargin())
			R.gStyle.SetTitleY(1 - self.pads[i].GetTopMargin())

			self.pads[i].Draw()

	def drawLumiText(self, TEXT, PAD=None):
		if PAD is None:
			PAD = self.numPads-1
		self.pads[PAD].cd()
		text = R.TLatex()
		text.SetTextFont(62)
		text.SetTextAlign(31)
		text.SetTextSize(20./200.)
		text.DrawLatexNDC(1-self.pads[PAD].GetRightMargin(), 1-self.pads[PAD].GetTopMargin() + 10./self.height, TEXT)
	
	def deleteCanvas(self):
		R.gROOT.ProcessLine('delete gROOT->FindObject("c");')

