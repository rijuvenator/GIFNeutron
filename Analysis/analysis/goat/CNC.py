import ROOT as R
import Gif.Analysis.Plotter as Plotter

################################################
## "Combine 'n Canvas", or CNC.               ##
## Nothing but plotter scripts here that open ##
## up a histogram file, combine them, pretty  ##
## them up, and save them or display them     ##
################################################

#R.gROOT.SetBatch(True)

f = R.TFile.Open('$WS/public/hists/hists.root')

###################
##  SKYSCRAPERS  ##
###################

def Skyscrapers(digi, half, norm=True):
	ERINGLIST = ['-42', '-41', '-32', '-31', '-22', '-21', '-13', '-12', '-11', '+11', '+12', '+13', '+21', '+22', '+31', '+32', '+41', '+42']
	RINGDICT  = dict(zip(ERINGLIST, range(-9,0) + range(1,10)))

	h = f.Get('D{DIGI}_H{HALF}_ND_ARI'.format(DIGI=digi,HALF=half)).Clone()
	if norm:
		h.Divide(f.Get('D{DIGI}_H{HALF}_NL_ARI'.format(DIGI=digi,HALF=half)))
	
	plot = Plotter.Plot(h, option='hist')

	nameDict = {
		('comp', 'l') : ('Comparators', 'Left' ),
		('comp', 'r') : ('Comparators', 'Right'),
		('wire', 'l') : ('Wires'      , 'Lower'),
		('wire', 'u') : ('Wires'      , 'Upper'),
	}
	Digi, Half = nameDict[(digi, half)]
	lumiText = 'Background {HALF} {DIGI} by Ring, P5'.format(DIGI=Digi, HALF=Half)
	
	canvas = Plotter.Canvas(lumi=lumiText, cWidth=1000)

	canvas.addMainPlot(plot)

	canvas.makeTransparent()
	h.GetXaxis().SetRangeUser(-9,10)
	for ring in ERINGLIST:
		bin_ = RINGDICT[ring] + 10
		h.GetXaxis().SetBinLabel(bin_, ring.replace('-','#minus'))
	plot.SetLineColor(0)
	plot.SetFillColor(R.kOrange)
	plot.scaleLabels(1.25, 'X')
	plot.setTitles(X='CSC Ring', Y='Counts')
	plot.SetMinimum(0)

	canvas.finishCanvas()
	canvas.save('pdfs/Skyscrapers_{DIGI}_{HALF}_P5.pdf'.format(DIGI=digi,HALF=Half))
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

#for digi, half in (('comp', 'l'), ('comp', 'r'), ('wire', 'l'), ('wire', 'u')):
#	Skyscrapers(digi, half)

################
##   FLAT 7   ##
################

f = R.TFile.Open('Flat7.root')

RINGLIST = ('11', '12', '13', '21', '22', '31', '32', '41', '42')
def Flat7(ring, digi, half, norm=True):
	print ring, digi, half
	h = f.Get('E+_R{RING}_D{DIGI}_H{HALF}_T7_ND_ALU'.format(RING=ring, DIGI=digi, HALF=half)).Clone()
	h.Add(f.Get('E-_R{RING}_D{DIGI}_H{HALF}_T7_ND_ALU'.format(RING=ring, DIGI=digi, HALF=half)))
	if norm:
		l = f.Get('E+_R{RING}_D{DIGI}_H{HALF}_NL_ALU'.format(RING=ring, DIGI=digi, HALF=half)).Clone()
		l.Add(f.Get('E-_R{RING}_D{DIGI}_H{HALF}_NL_ALU'.format(RING=ring, DIGI=digi, HALF=half)))
		h.Divide(l)

	nameDict = {
		('comp', 'l') : ('Comparators', 'Left' ),
		('comp', 'r') : ('Comparators', 'Right'),
		('wire', 'l') : ('Wires'      , 'Lower'),
		('wire', 'u') : ('Wires'      , 'Upper'),
	}
	Digi, Half = nameDict[(digi, half)]
	
	plot = Plotter.Plot(h, option='hist P')

	canvas = Plotter.Canvas(lumi='{HALF} {DIGI}, ME{RING}, Time Bin 7 vs. L'.format(DIGI=Digi, HALF=Half, RING=ring))

	canvas.addMainPlot(plot)

	canvas.makeTransparent()
	plot.SetMinimum(0)
	plot.setTitles(X='Luminosity [cm^{-2}s^{-1}]', Y='Background Digi Rate')

	canvas.finishCanvas()
	canvas.save('pdfs/Flat7_{RING}_{DIGI}_{HALF}_P5.pdf'.format(RING=ring, DIGI=digi, HALF=Half))
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

for ring in RINGLIST:
	for digi, half in (('comp', 'l'), ('comp', 'r'), ('wire', 'l'), ('wire', 'u')):
		Flat7(ring, digi, half)
