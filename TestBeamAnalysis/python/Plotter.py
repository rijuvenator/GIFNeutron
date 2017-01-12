import ROOT as R
import numpy as n

# setStyle function, based on TDRStyle, but more flexible
def setStyle(width=800, height=600, font=42, tsize=0.04):
	style = R.TStyle("style","Style")

	width = width
	height = height
	font = font
	tMargin = 0.1
	lMargin = 0.125
	tsize = float(tsize)

	rMargin = tMargin * float(height) / float(width)
	bMargin = lMargin
	titleX = lMargin + (1-lMargin-rMargin)/2
	titleY = 1 - (tMargin/2)

	# generic line thicknesses
	style.SetLineWidth(2)

	# canvas
	style.SetCanvasBorderMode(0)             # off
	style.SetCanvasColor(R.kWhite)           # white
	style.SetCanvasDefW(width)               # width
	style.SetCanvasDefH(height)              # height

	# pad
	style.SetPadBorderMode(0)                # off
	style.SetPadColor(R.kWhite)              # white
	style.SetPadGridX(R.kFALSE)              # grid x
	style.SetPadGridY(R.kFALSE)              # grid y
	style.SetGridColor(R.kGray)              # gray
	style.SetGridStyle(3)                    # dotted
	style.SetGridWidth(1)                    # pixels

	# pad margins
	style.SetPadTopMargin(tMargin)           # default 0.1
	style.SetPadBottomMargin(bMargin)        # default 0.1
	style.SetPadLeftMargin(lMargin)          # default 0.1
	style.SetPadRightMargin(rMargin)         # default 0.1

	# frame
	style.SetFrameBorderMode(0)              # off
	style.SetFrameFillColor(R.kWhite)        # white
	style.SetFrameFillStyle(0)               # hollow
	style.SetFrameLineColor(R.kWhite)        # white
	style.SetFrameLineStyle(1)               # solid
	style.SetFrameLineWidth(0)               # pixels

	# legend
	style.SetLegendBorderSize(0)             # off
	style.SetLegendFont(font)                # helvetica normal

	# hist
	style.SetHistLineColor(R.kBlack)         # black
	style.SetHistLineStyle(1)                # solid
	style.SetHistLineWidth(2)                # pixels
	style.SetMarkerStyle(R.kFullDotLarge)    # marker
	style.SetMarkerColor(R.kBlack)           # black
	style.SetEndErrorSize(0)                 # no little lines on errors

	# stats box
	style.SetOptStat(0)                      # off

	# fit box
	style.SetOptFit(1)                       # on

	# title
	style.SetOptTitle(0)                     # off
	style.SetTitleFont(font,"")              # helvetica normal
	style.SetTitleTextColor(R.kBlack)        # black
	style.SetTitleFontSize(tsize+0.02)       # default 0
	style.SetTitleStyle(0)                   # hollow
	style.SetTitleFillColor(R.kWhite)        # white
	style.SetTitleBorderSize(0)              # default 2
	style.SetTitleAlign(22)                  # center top
	style.SetTitleX(titleX)                  # center title horizontally with respect to frame
	style.SetTitleY(titleY)                  # center title vertically within margin

	# axis titles
	style.SetTitleFont(font, "XYZ")          # helvetica normal
	style.SetTitleColor(R.kBlack, "XYZ")     # black
	style.SetTitleSize(tsize+0.005,"XYZ")    # default 0.02
	style.SetTitleOffset(1,"X")              # default 1
	style.SetTitleOffset(1,"Y")              # default 1

	# axis labels
	style.SetLabelFont(font, "XYZ")          # helvetica normal
	style.SetLabelColor(R.kBlack, "XYZ")     # black
	style.SetLabelSize(tsize, "XYZ")         # default 0.04
	style.SetLabelOffset(0.005,"XYZ")        # default 0.005

	# axis
	style.SetAxisColor(R.kBlack, "XYZ")      # black
	style.SetStripDecimals(R.kTRUE)          # strip decimals
	style.SetPadTickX(1)                     # opposite x ticks
	style.SetPadTickY(1)                     # opposite y ticks

	style.cd()

# holds a plot object; expected to be a hist, graph, or hstack
# legName is the legend display name, legType is the legend symbol draw option, option is the draw option
class Plot:
	def __init__(self, plot, legName="hist", legType="felp", option=""):
		self.plot = plot
		self.legName = legName
		self.legType = legType
		self.option = option

	def scaleTitles(self, factor, axes='XY'):
		if 'X' in axes: self.plot.GetXaxis().SetTitleSize(self.plot.GetXaxis().GetTitleSize() * float(factor))
		if 'Y' in axes: self.plot.GetYaxis().SetTitleSize(self.plot.GetYaxis().GetTitleSize() * float(factor))
		if 'Z' in axes: self.plot.GetZaxis().SetTitleSize(self.plot.GetZaxis().GetTitleSize() * float(factor))

	def scaleLabels(self, factor, axes='XY'):
		if 'X' in axes: self.plot.GetXaxis().SetLabelSize(self.plot.GetXaxis().GetLabelSize() * float(factor))
		if 'Y' in axes: self.plot.GetYaxis().SetLabelSize(self.plot.GetYaxis().GetLabelSize() * float(factor))
		if 'Z' in axes: self.plot.GetZaxis().SetLabelSize(self.plot.GetZaxis().GetLabelSize() * float(factor))
	
	def scaleTitleOffsets(self, factor, axes='XY'):
		if 'X' in axes: self.plot.GetXaxis().SetTitleOffset(self.plot.GetXaxis().GetTitleOffset() * float(factor))
		if 'Y' in axes: self.plot.GetYaxis().SetTitleOffset(self.plot.GetYaxis().GetTitleOffset() * float(factor))
		if 'Z' in axes: self.plot.GetZaxis().SetTitleOffset(self.plot.GetZaxis().GetTitleOffset() * float(factor))
	
	def setTitles(self, X=None, Y=None, Z=None):
		if X is not None: self.plot.GetXaxis().SetTitle(X)
		if Y is not None: self.plot.GetYaxis().SetTitle(Y)
		if Z is not None: self.plot.GetZaxis().SetTitle(Z)

# canvas class
# lumi is lumi text (top right), logy is if canvas should be log y scale, ratiofactor is fraction of canvas devoted to ratio plot
# extra is text that follows CMS (top left), cWidth is canvas width, cHeight is canvas height, font is font
class Canvas:
#	TCanvas *c;
#	TPad *mainPad;
#	TPad *ratPad;
#	int cWidth;
#	int cHeight;
#	int font;
#	float tsize;
#	std::string lumi;
#	std::string extra;
#	bool logy;
#	float ratioFactor;
#	TLegend *leg;
#	TH1F *rat;
#	TGraph *gr;

	# the user calls this constructor
	def __init__(self, lumi="30 fb^{-1} (13 TeV)", logy=0, ratioFactor=0, extra="Internal", cWidth=800, cHeight=600, font=42, tsize=0.05):
		self.cWidth = cWidth
		self.cHeight = cHeight
		self.font = font
		self.tsize = float(tsize)
		self.lumi = lumi
		self.extra = extra
		self.logy = logy
		self.ratioFactor = float(ratioFactor)

		self.axesDrawn = False

		setStyle(self.cWidth,self.cHeight,self.font,self.tsize)

		self.c = R.TCanvas("c","Canvas",self.cWidth,self.cHeight)

		self.prepareCanvas()

	# the user doesn't call this.
	def prepareCanvas(self):
		tMargin = self.c.GetTopMargin()
		lMargin = self.c.GetLeftMargin()
		rMargin = self.c.GetRightMargin()

		self.mainPad = R.TPad("main","Main",0,self.ratioFactor,1,1)
		
		if (self.ratioFactor != 0):
			self.mainPad.SetBottomMargin(0.04)
			self.mainPad.SetRightMargin(tMargin * (self.cHeight * (1 - self.ratioFactor)) / self.cWidth)
			self.ratPad = R.TPad("ratio","Ratio",0,0,1,self.ratioFactor)
			self.ratPad.SetTopMargin(0.04)
			self.ratPad.SetBottomMargin(lMargin * (1 - self.ratioFactor)/self.ratioFactor)
			self.ratPad.SetRightMargin(tMargin * (self.cHeight * (1 - self.ratioFactor)) / self.cWidth)
			self.ratPad.Draw()

		self.mainPad.Draw()
		self.mainPad.SetLogy(self.logy)

	# the user calls this; it "initializes" the legend
	# lWidth is width as fraction of pad, lHeight is height as fraction of pad, lOffset is offset from corner as fraction of pad
	# pos can be tr, tl, br, bl for each of the four corners. if it doesn't suit, just grab it and move it
	# fontsize defaults to 0.04
	def makeLegend(self, lWidth=0.125, lHeight=0.2, pos="tr", lOffset=0.02, fontsize=0.04):
		tMargin = float(self.mainPad.GetTopMargin())
		lMargin = float(self.mainPad.GetLeftMargin())
		rMargin = float(self.mainPad.GetRightMargin())
		bMargin = float(self.mainPad.GetBottomMargin())

		self.c.cd()
		self.mainPad.cd()

		if (pos == "tr"):
			self.leg = R.TLegend(1-rMargin-lOffset-lWidth, 1-tMargin-lOffset-lHeight, 1-rMargin-lOffset,          1-tMargin-lOffset        )
		elif (pos == "tl"):
			self.leg = R.TLegend(  lMargin+lOffset,        1-tMargin-lOffset-lHeight,   lMargin+lOffset+lWidth,   1-tMargin-lOffset        )
		elif (pos == "br"):
			self.leg = R.TLegend(1-rMargin-lOffset-lWidth,   bMargin+lOffset,         1-rMargin-lOffset,            bMargin+lOffset+lHeight)
		elif (pos == "bl"):
			self.leg = R.TLegend(  lMargin+lOffset,          bMargin+lOffset,           lMargin+lOffset+lWidth,     bMargin+lOffset+lHeight)
		else:
			print "Invalid legend position string; defaulting to top-right"
			self.leg = R.TLegend(1-rMargin-lOffset-lWidth, 1-tMargin-lOffset-lHeight, 1-rMargin-lOffset, 1-tMargin-lOffset)

		self.leg.SetTextSize(fontsize)
		self.leg.SetFillStyle(0)

	# the user may call this, but only if addToLegend=0 in addMainPlot (see below)
	def addLegendEntry(self, plot):
		self.leg.AddEntry(plot.plot, plot.legName, plot.legType)
	
	# the user calls this; adds a plot Plot to the main pad
	# isFirst is if the main pad should get its draw information from this plot (axis titles and ranges)
	# addToLegend is if this plot should be added to the legend right away
	# I added this option because perhaps the "first" plot isn't intended to also be the first legend entry
	def addMainPlot(self, plot, isFirst=1, addToLegend=1):
		plot.plot.UseCurrentStyle()
		self.c.cd()
		self.mainPad.cd()

		if (isFirst):
			plot.plot.Draw(plot.option)
			plot.plot.GetXaxis().CenterTitle()
			plot.plot.GetYaxis().CenterTitle()
		else:
			plot.plot.Draw((plot.option+" same"))

		if (self.ratioFactor != 0):
			plot.plot.GetXaxis().SetLabelSize(0)

		if (addToLegend):
			self.addLegendEntry(plot)
	
	# trying out a new way of drawing
	def addMainPlotExp(self, plot, addToLegend=1):
		plot.plot.UseCurrentStyle()
		self.c.cd()
		self.mainPad.cd()

		if not self.axesDrawn:
			self.axesDrawn = True
			self.firstPlot = plot
			if type(plot.plot) is R.TGraph:
				plot.plot.Draw('A'+plot.option)
			else:
				plot.plot.Draw(plot.option)
			plot.plot.GetXaxis().CenterTitle()
			plot.plot.GetYaxis().CenterTitle()
		else:
			plot.plot.Draw(plot.option+' same')

		if self.ratioFactor != 0:
			plot.plot.GetXaxis().SetLabelSize(0)

		if addToLegend:
			self.addLegendEntry(plot)

	# the user calls this; sets style for the stats box, if there is one.
	# owner is the TGraph or TH1 that generated the stats box
	# lWidth is width as fraction of pad, lHeight is height as fraction of pad, lOffset is offset from corner as fraction of pad
	# pos can be tr, tl, br, bl for each of the four corners. if it doesn't suit, just grab it and move it
	# fontsize defaults to 0.03
	def setFitBoxStyle(self,owner,lWidth=0.3, lHeight=0.15, pos="tl", lOffset=0.05, fontsize=0.03):
		tMargin = float(self.mainPad.GetTopMargin())
		lMargin = float(self.mainPad.GetLeftMargin())
		rMargin = float(self.mainPad.GetRightMargin())
		bMargin = float(self.mainPad.GetBottomMargin())

		self.c.cd()
		self.mainPad.cd()
		self.mainPad.Update()

		sbox = owner.FindObject("stats")

		sbox.SetFillStyle(0)
		sbox.SetBorderSize(0)
		sbox.SetTextFont(self.font)
		sbox.SetTextSize(fontsize)

		if (pos == "tr"):
			sbox.SetX1NDC(1-rMargin-lOffset-lWidth )
			sbox.SetY1NDC(1-tMargin-lOffset-lHeight)
			sbox.SetX2NDC(1-rMargin-lOffset        )
			sbox.SetY2NDC(1-tMargin-lOffset        )
		elif (pos == "tl"):
			sbox.SetX1NDC(  lMargin+lOffset        )
			sbox.SetY1NDC(1-tMargin-lOffset-lHeight)
			sbox.SetX2NDC(  lMargin+lOffset+lWidth )
			sbox.SetY2NDC(1-tMargin-lOffset        )
		elif (pos == "br"):
			sbox.SetX1NDC(1-rMargin-lOffset-lWidth )
			sbox.SetY1NDC(  bMargin+lOffset        )
			sbox.SetX2NDC(1-rMargin-lOffset        )
			sbox.SetY2NDC(  bMargin+lOffset+lHeight)
		elif (pos == "bl"):
			sbox.SetX1NDC(  lMargin+lOffset        )
			sbox.SetY1NDC(  bMargin+lOffset        )
			sbox.SetX2NDC(  lMargin+lOffset+lWidth )
			sbox.SetY2NDC(  bMargin+lOffset+lHeight)
		else:
			print "Invalid fit box position string; defaulting to top-left"
			sbox.SetX1NDC(  lMargin+lOffset        )
			sbox.SetY1NDC(1-tMargin-lOffset-lHeight)
			sbox.SetX2NDC(  lMargin+lOffset+lWidth )
			sbox.SetY2NDC(1-tMargin-lOffset        )

	# the user calls this; makes ratio plot given a top hist and a bottom hist
	# plusminus is the window around 1, i.e. 0.5 means plot from 0.5 to 1.5
	# ytit is the y axis title, xtit is the x axis title, option is the draw option
	def makeRatioPlot(self, topHist, bottomHist, plusminus=0.5, option="", ytit="Data/MC", xtit=""):
		self.c.cd()
		self.ratPad.cd()
		self.ratPad.SetGridy(R.kTRUE)

		self.rat = topHist.Clone()
		bot = bottomHist.Clone()
		self.rat.Divide(bot)

		factor = (1 - self.ratioFactor)/self.ratioFactor

		if (xtit != ""):
			self.rat.GetXaxis().SetTitle(xtit)

		self.rat.GetXaxis().SetTitleSize(self.rat.GetXaxis().GetTitleSize() * factor)
		self.rat.GetXaxis().SetLabelSize(self.rat.GetYaxis().GetLabelSize() * factor)
		self.rat.GetXaxis().SetTickLength(self.rat.GetXaxis().GetTickLength() * factor)
		self.rat.GetXaxis().CenterTitle()

		self.rat.GetYaxis().SetTitle(ytit)
		self.rat.GetYaxis().SetTitleOffset(self.rat.GetYaxis().GetTitleOffset() / factor)
		self.rat.GetYaxis().SetTitleSize(self.rat.GetYaxis().GetTitleSize() * factor)
		self.rat.GetYaxis().SetLabelSize(self.rat.GetYaxis().GetLabelSize() * factor)
		self.rat.GetYaxis().SetNdivisions(5)
		self.rat.GetYaxis().SetRangeUser(1-plusminus,1+plusminus)
		self.rat.GetYaxis().SetTickLength(0.01)
		self.rat.GetYaxis().CenterTitle()
		self.rat.Draw(option)

		low = float(self.rat.GetXaxis().GetXmin())
		up = float(self.rat.GetXaxis().GetXmax())
		x = n.array([ low, up ])
		y = n.array([ 1., 1. ])
		self.gr = R.TGraph(2,x,y)
		self.gr.SetLineColor(R.kRed)
		self.gr.SetLineStyle(3)
		self.gr.SetLineWidth(2)
		self.gr.Draw("C same")

		self.rat.Draw((option+" same"))
		self.rat.SetMarkerColor(R.kBlack)
		self.rat.SetLineColor(R.kBlack)

		self.ratPad.RedrawAxis()

	# the user calls this; makes background transparent
	def makeTransparent(self):
		self.c.SetFillStyle(4000)
		self.mainPad.SetFillStyle(4000)

	# the user calls this last; it draws the lumi text, "CMS", extra text, and legend 
	def finishCanvas(self):
		tMargin = float(self.mainPad.GetTopMargin())
		lMargin = float(self.mainPad.GetLeftMargin())
		rMargin = float(self.mainPad.GetRightMargin())

		tOffset = 0.02
		fontsize = 0.04
		if (self.ratioFactor != 0):
			fontsize /= (1-self.ratioFactor)

		self.c.cd()
		self.mainPad.cd()

		latex = R.TLatex()
		latex.SetTextFont(self.font)
		latex.SetTextSize(fontsize)
		latex.SetTextAlign(31)
		latex.DrawLatexNDC(1-rMargin,1-tMargin+tOffset,self.lumi)
		latex.SetTextFont(self.font+20)
		latex.SetTextSize(fontsize*1.25)
		latex.SetTextAlign(11)
		latex.DrawLatexNDC(lMargin,1-tMargin+tOffset,"CMS")
		latex.SetTextFont(self.font+10)
		latex.SetTextSize(fontsize)
		latex.DrawLatexNDC(lMargin + fontsize*self.cHeight*(1-self.ratioFactor)*2.75/self.cWidth,1-tMargin+tOffset,self.extra)

		self.leg.Draw()
		self.mainPad.RedrawAxis()
	
	# save canvas as file
	def save(self, name, extList=''):
		if type(extList) == str:
			if extList == '':
				self.c.SaveAs(name)
			else:
				self.c.SaveAs(name+extList)
		if type(extList) == list:
			for ext in extList:
				self.c.SaveAs(name+ext)
	
	def scaleMargins(self, factor, edges=''):
		if 'L' in edges:
			self.mainPad.SetLeftMargin  (self.mainPad.GetLeftMargin  () * factor)
		if 'R' in edges:
			self.mainPad.SetRightMargin (self.mainPad.GetRightMargin () * factor)
		if 'T' in edges:
			self.mainPad.SetTopMargin   (self.mainPad.GetTopMargin   () * factor)
		if 'B' in edges:
			self.mainPad.SetBottomMargin(self.mainPad.GetBottomMargin() * factor)
