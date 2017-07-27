import ROOT as R
import Gif.Analysis.Plotter as Plotter

################################################
## "Combine 'n Canvas", or CNC.               ##
## Nothing but plotter scripts here that open ##
## up a histogram file, combine them, pretty  ##
## them up, and save them or display them     ##
################################################

R.gROOT.SetBatch(True)
RINGLIST = ('11', '12', '13', '21', '22', '31', '32', '41', '42')

###################
##  SKYSCRAPERS  ##
###################

def Skyscrapers(digi, half, norm=True):
	ERINGLIST = ['-'+ring for ring in list(reversed(RINGLIST))] + ['+'+ring for ring in RINGLIST]
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

#f = R.TFile.Open('rings.root')
#for digi, half in (('comp', 'l'), ('comp', 'r'), ('wire', 'l'), ('wire', 'u')):
#	Skyscrapers(digi, half)

################
##   FLAT 7   ##
################

def Flat7(ring, digi, half, norm=True):
	nameDict = {
		('comp', 'l') : ('Comparators', 'Left' ),
		('comp', 'r') : ('Comparators', 'Right'),
		('wire', 'l') : ('Wires'      , 'Lower'),
		('wire', 'u') : ('Wires'      , 'Upper'),
	}
	SUBS = {
		'DIGI' : digi,
		'DIGIU': nameDict[(digi, half)][0],
		'RING' : ring,
		'HALF' : half,
		'HALFU': nameDict[(digi, half)][1],
		'FLAT' : 7 if digi == 'comp' else 8
	}

	HNAME = 'E{EC}_R{RING}_D{DIGI}_H{HALF}_T{FLAT}_N{DORL}_ALU'
	h =   f.Get(HNAME.format(EC='+', DORL='D', **SUBS)).Clone()
	h.Add(f.Get(HNAME.format(EC='-', DORL='D', **SUBS)))
	if norm:
		l =   f.Get(HNAME.format(EC='+', DORL='L', **SUBS)).Clone()
		l.Add(f.Get(HNAME.format(EC='-', DORL='L', **SUBS)))
		h.Divide(l)

	plot = Plotter.Plot(h, option='hist P')

	canvas = Plotter.Canvas(lumi='{HALFU} {DIGIU}, ME{RING}, Time Bin {FLAT} vs. L'.format(**SUBS))

	canvas.addMainPlot(plot)

	canvas.makeTransparent()
	plot.SetMinimum(0)
	plot.setTitles(X='Luminosity [cm^{-2}s^{-1}]', Y='Background Digi Rate')

	canvas.finishCanvas()
	canvas.save('pdfs/Flat7_{RING}_{DIGI}_{HALFU}_P5.pdf'.format(**SUBS))
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

#f = R.TFile.Open('Flat7.root')
#for ring in RINGLIST:
#	for digi, half in (('comp', 'l'), ('comp', 'r'), ('wire', 'l'), ('wire', 'u')):
#		Flat7(ring, digi, half)

#############
##  LOOKS  ##
#############

def Looks(ring, digi, whichHalf=None):
	nameDict = {
		('comp', 'l') : ('Comparators', 'Left' ),
		('comp', 'r') : ('Comparators', 'Right'),
		('wire', 'l') : ('Wires'      , 'Lower'),
		('wire', 'u') : ('Wires'      , 'Upper'),
	}
	SUBS = {
		'DIGI' : digi,
		'DIGIU': nameDict[(digi, 'l')][0],
		'RING' : ring,
		'HALFU': None if whichHalf is None else nameDict[(digi, whichHalf)][1]
	}
	# if whichHalf is specified, then make the plot only for a specific half
	# otherwise, combine the two (and make the file and title names reflect that)
	if whichHalf is None:
		HALFLIST = ('l', 'r') if digi=='comp' else ('l', 'u')
	else:
		HALFLIST = (whichHalf,)

	# gets/normalizes the histograms. it was originally developed for combining halves,
	# hence the dictionary which is redundant if there's just one histogram,
	# but the same code works for both, now
	DLNAME = 'E{EC}_R{RING}_D{DIGI}_H{HALF}_NL_ABX'
	LHISTS = {}
	for half in HALFLIST:
		LHISTS[half] =   f.Get(DLNAME.format(EC='+', HALF=half, **SUBS)).Clone()
		LHISTS[half].Add(f.Get(DLNAME.format(EC='-', HALF=half, **SUBS)))

	# make "h" the final histogram that goes into Plotter; also make the title and fn
	if len(HALFLIST) == 1:
		h = LHISTS[HALFLIST[0]].Clone()
		title = 'nLooks vs. BX After Gap: {HALFU} {DIGIU}, ME{RING}'.format(**SUBS)
		fn    = 'pdfs/Looks_{DIGI}_{HALFU}_{RING}.pdf'.format(**SUBS)
	elif len(HALFLIST) == 2:
		h = LHISTS[HALFLIST[0]].Clone()
		h.Add(LHISTS[HALFLIST[1]])
		title = 'nLooks vs. BX After Gap: {DIGIU}, ME{RING}'.format(**SUBS)
		fn    = 'pdfs/Looks_{DIGI}_{RING}.pdf'.format(**SUBS)

	# text file dumps of the histograms
	if True:
		fout = open(fn.replace('.pdf', '.txt'), 'w')
		cleartext = ''
		for BX in xrange(48, 0, -1):
			cleartext += '{:4d} '.format(int(h.GetBinContent(BX))) + '\n'
		fout.write(cleartext)

	# plotting code begins here
	plot = Plotter.Plot(h, option='hist')
	canvas = Plotter.Canvas(lumi=title)

	canvas.addMainPlot(plot)
	canvas.makeTransparent()
	plot.SetLineColor(0)
	plot.SetFillColor(R.kOrange)
	plot.setTitles(X='BX After Gap', Y='Number of Looks')
	plot.SetMinimum(0)
	h.GetXaxis().SetRangeUser(1, 49)

	canvas.finishCanvas()
	canvas.save(fn)
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

#f = R.TFile.Open('rainbow.root')
#for ring in RINGLIST:
#	for digi in ('comp', 'wire'):
#		Looks(ring, digi)
#		for half in ('l', 'r') if digi=='comp' else ('l', 'u'):
#			Looks(ring, digi, half)

#############
## RAINBOW ##
#############

def Rainbow(ring, digi, whichHalf=None, norm=True):
	nameDict = {
		('comp', 'l') : ('Comparators', 'Left' ),
		('comp', 'r') : ('Comparators', 'Right'),
		('wire', 'l') : ('Wires'      , 'Lower'),
		('wire', 'u') : ('Wires'      , 'Upper'),
	}
	SUBS = {
		'DIGI' : digi,
		'DIGIU': nameDict[(digi, 'l')][0],
		'RING' : ring,
		'HALFU': None if whichHalf is None else nameDict[(digi, whichHalf)][1]
	}
	# if whichHalf is specified, then make the plot only for a specific half
	# otherwise, combine the two (and make the file and title names reflect that)
	if whichHalf is None:
		HALFLIST = ('l', 'r') if digi=='comp' else ('l', 'u')
	else:
		HALFLIST = (whichHalf,)

	# gets/normalizes the histograms. it was originally developed for combining halves,
	# hence the dictionary which is redundant if there's just one histogram,
	# but the same code works for both, now
	DHNAME = 'E{EC}_R{RING}_D{DIGI}_H{HALF}_ND_ATB_ABX'
	DLNAME = 'E{EC}_R{RING}_D{DIGI}_H{HALF}_NL_ABX'
	DHISTS = {}
	LHISTS = {}
	for half in HALFLIST:
		DHISTS[half] =   f.Get(DHNAME.format(EC='+', HALF=half, **SUBS)).Clone()
		DHISTS[half].Add(f.Get(DHNAME.format(EC='-', HALF=half, **SUBS)))
	if norm:
		for half in HALFLIST:
			LHISTS[half] =   f.Get(DLNAME.format(EC='+', HALF=half, **SUBS)).Clone()
			LHISTS[half].Add(f.Get(DLNAME.format(EC='-', HALF=half, **SUBS)))

		DIVVALS = {}
		for BX in xrange(1, 49):
			for half in HALFLIST:
				DIVVALS[half] = LHISTS[half].GetBinContent(BX)/(LHISTS[half].Integral(1, 48)/48.)
			for TB in xrange(0, 16):
				for half in HALFLIST:
					DHISTS[half].SetBinContent(TB+1, BX, DHISTS[half].GetBinContent(TB+1, BX)/DIVVALS[half])
	
	# make "h" the final histogram that goes into Plotter; also make the title and fn
	if len(HALFLIST) == 1:
		h = DHISTS[HALFLIST[0]].Clone()
		title = 'BX After Gap vs. Time Bin: {HALFU} {DIGIU}, ME{RING}'.format(**SUBS)
		fn    = 'pdfs/Rainbow_{DIGI}_{HALFU}_{RING}.pdf'.format(**SUBS)
	elif len(HALFLIST) == 2:
		h = DHISTS[HALFLIST[0]].Clone()
		h.Add(DHISTS[HALFLIST[1]])
		title = 'BX After Gap vs. Time Bin: {DIGIU}, ME{RING}'.format(**SUBS)
		fn    = 'pdfs/Rainbow_{DIGI}_{RING}.pdf'.format(**SUBS)

	# text file dumps of the histograms
	if True:
		fout = open(fn.replace('.pdf', '.txt'), 'w')
		cleartext = ''
		for BX in xrange(48, 0, -1):
			for TB in xrange(0, 16):
				cleartext += '{:4d} '.format(int(h.GetBinContent(TB+1, BX)))
			cleartext += '\n'
		fout.write(cleartext)

	# plotting code begins here
	plot = Plotter.Plot(h, option='colz')
	#canvas = Plotter.Canvas(lumi=title)
	canvas = Plotter.Canvas(lumi='Run 2016H, 8.73 fb^{-1} (13 TeV)', extra='Preliminary')

	canvas.addMainPlot(plot)
	canvas.makeTransparent()
	#plot.SetLineColor(0)
	plot.SetFillColor(R.kOrange)
	plot.setTitles(X='Time Bin', Y='BX After Gap')
	plot.SetMinimum(0)
	canvas.scaleMargins(1.7, 'R')
	h.GetYaxis().SetRangeUser(1, 49)

	canvas.finishCanvas()
	canvas.save(fn)
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

#f = R.TFile.Open('rainbow.root')
#for ring in RINGLIST:
#	for digi in ('comp', 'wire'):
#		Rainbow(ring, digi)
#		for half in ('l', 'r') if digi=='comp' else ('l', 'u'):
#			Rainbow(ring, digi, half)
#for ring in ['11']:
#	for digi in ['wire']:
#		Rainbow(ring, digi)

#################
## PROJECTIONS ##
#################

def Projection(ring, digi, bx=None, tb=None, whichHalf=None, norm=True):
	#### This part is the same as rainbow ####
	nameDict = {
		('comp', 'l') : ('Comps', 'Left' ),
		('comp', 'r') : ('Comps', 'Right'),
		('wire', 'l') : ('Wires', 'Lower'),
		('wire', 'u') : ('Wires', 'Upper'),
	}
	SUBS = {
		'DIGI' : digi,
		'DIGIU': nameDict[(digi, 'l')][0],
		'RING' : ring,
		'HALFU': None if whichHalf is None else nameDict[(digi, whichHalf)][1]
	}
	# if whichHalf is specified, then make the plot only for a specific half
	# otherwise, combine the two (and make the file and title names reflect that)
	if whichHalf is None:
		HALFLIST = ('l', 'r') if digi=='comp' else ('l', 'u')
	else:
		HALFLIST = (whichHalf,)

	# gets/normalizes the histograms. it was originally developed for combining halves,
	# hence the dictionary which is redundant if there's just one histogram,
	# but the same code works for both, now
	DHNAME = 'E{EC}_R{RING}_D{DIGI}_H{HALF}_ND_ATB_ABX'
	DLNAME = 'E{EC}_R{RING}_D{DIGI}_H{HALF}_NL_ABX'
	DHISTS = {}
	LHISTS = {}
	for half in HALFLIST:
		DHISTS[half] =   f.Get(DHNAME.format(EC='+', HALF=half, **SUBS)).Clone()
		DHISTS[half].Add(f.Get(DHNAME.format(EC='-', HALF=half, **SUBS)))
	if norm:
		for half in HALFLIST:
			LHISTS[half] =   f.Get(DLNAME.format(EC='+', HALF=half, **SUBS)).Clone()
			LHISTS[half].Add(f.Get(DLNAME.format(EC='-', HALF=half, **SUBS)))

		DIVVALS = {}
		for BX in xrange(1, 50):
			for half in HALFLIST:
				DIVVALS[half] = LHISTS[half].GetBinContent(BX)
			for TB in xrange(0, 16):
				for half in HALFLIST:
					DHISTS[half].SetBinContent(TB+1, BX, DHISTS[half].GetBinContent(TB+1, BX)/DIVVALS[half])

	# make h2 the final histogram that gets projected
	if len(HALFLIST) == 1:
		h2 = DHISTS[HALFLIST[0]].Clone()
	elif len(HALFLIST) == 2:
		h2 = DHISTS[HALFLIST[0]].Clone()
		h2.Add(DHISTS[HALFLIST[1]])

	##### Projection time! #####
	if bx is None:
		h = h2.ProjectionY('_TB'+str(tb), tb+1, tb+1)
		title = 'BG {DIGIU} in ME{RING} vs. BX After Gap, Time Bin {TB}'.format(TB=tb, **SUBS)
		fn = 'pdfs/BX_{DIGI}_{RING}_{TB}.pdf'.format(TB=tb, **SUBS)
	elif tb is None:
		h = h2.ProjectionX('_BX'+str(bx), bx, bx)
		title = 'BG {DIGIU} in ME{RING} vs. Time Bin, BX {BX}'.format(BX=bx, **SUBS)
		fn = 'pdfs/TimeBin_{DIGI}_{RING}_{BX}.pdf'.format(BX=bx, **SUBS)

	# Plotter starts here
	plot = Plotter.Plot(h, option='hist')
	canvas = Plotter.Canvas(lumi=title)

	canvas.addMainPlot(plot)
	canvas.makeTransparent()
	plot.SetLineColor(0)
	plot.SetFillColor(R.kOrange)
	plot.setTitles(X='BX After Gap' if bx is None else 'Time Bin', Y='Counts')
	plot.SetMinimum(0)

	canvas.finishCanvas()
	canvas.save(fn)
	R.SetOwnership(canvas, False)
	canvas.deleteCanvas()

#f = R.TFile.Open('rainbow.root')
#Projection('11', 'comp', bx=23)
#Projection('11', 'comp', bx=1)
#Projection('11', 'comp', tb=7)
#Projection('11', 'comp', tb=1)
