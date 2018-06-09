import numpy as np
import ROOT as R
import Gif.Analysis.Plotter as Plotter

R.gROOT.SetBatch(True)

# histogram configurations
#fn = 'LastEvsTOF.pdf'
fn = 'LastEvsTOF_All.pdf'
configs = {
	'Cap' : ('Capture'                   , R.kRed    , True ),
	'Ine' : ('Inelastic Scatter'         , R.kAzure+7, True ),
	'Nuc' : ('SimHit By Ion'             , R.kGreen  , True ),
	'Pro' : ('Neutron #rightarrow Proton', R.kMagenta, True ),
}
keylist = ('Cap', 'Ine', 'Nuc', 'Pro')

hists = {}
for key in keylist:
	#hists[key] = R.TH2F('h'+key, '', 100, np.logspace(3-6, 15-6, 101), 100, np.logspace(1-9, 7-9, 101) )
	hists[key] = R.TH2F('h'+key, '', 100, np.logspace(1-9, 7-9, 101) , 100, np.logspace(3-6, 15-6, 101))

# loop over the mythologies and fill histograms
# a SimHit will get plotted either as a Nucleus, a Proton, an nCapture, or a neutronInelastic
f = open('capetof/fulllog.log')
state = ''
isProton = False
for line in f:
	if state == 'nCapture':
		cols = line.strip('\n').split()
		tof  = float(cols[-3])/1e9
		cape = float(cols[-1])/1e6

		if isProton:
			#hists['Pro'].Fill(cape, tof)
			hists['Pro'].Fill(tof, cape)
			isProton = False
		elif 'ionIoni' in line:
			#hists['Nuc'].Fill(cape, tof)
			hists['Nuc'].Fill(tof, cape)
		else:
			#hists['Cap'].Fill(cape, tof)
			hists['Cap'].Fill(tof, cape)

	elif state == 'neutronInelastic':
		cols = line.strip('\n').split()
		tof  = float(cols[-3])/1e9
		inee = float(cols[-1])/1e6

		if isProton:
			#hists['Pro'].Fill(inee, tof)
			hists['Pro'].Fill(tof, inee)
			isProton = False
		elif 'ionIoni' in line:
			#hists['Nuc'].Fill(inee, tof)
			hists['Nuc'].Fill(tof, inee)
		else:
			#hists['Ine'].Fill(inee, tof)
			hists['Ine'].Fill(tof, inee)

	# here's where the state gets set
	if '(nCapture)' in line:
		state = 'nCapture'
		if 'proton <= neutron' in line:
			isProton = True
	elif '(neutronInelastic)' in line:
		state = 'neutronInelastic'
		if 'proton <= neutron' in line:
			isProton = True
	else:
		state = ''

# make the actual plot
#canvas  = Plotter.Canvas(lumi='SimHit TOF vs. Last Recorded Neutron Energy', logy=True)
#canvas  = Plotter.Canvas(lumi='Last Recorded Neutron Energy vs. SimHit TOF', logy=True, extra='Preliminary')
canvas  = Plotter.Canvas(lumi='', logy=True, extra='Simulation Preliminary')

plots = {}
for key in keylist:
	legName, color, actuallyPlot = configs[key]
	if not actuallyPlot: continue
	plots[key] = Plotter.Plot(hists[key], legName=legName, legType='l', option='')
	canvas.addMainPlot(plots[key])
	plots[key].SetMarkerColor(color)
	plots[key].SetLineColor(color)
canvas.mainPad.SetLogx(True)

#canvas.firstPlot.setTitles(X='Energy [eV]', Y='Time of Flight [s]')
canvas.firstPlot.setTitles(Y='Energy [eV]', X='Time [s]')
canvas.firstPlot.scaleTitleOffsets(1.25, 'X')
canvas.makeTransparent()
canvas.makeLegend()
canvas.legend.moveEdges(L=-.16)
canvas.legend.resizeHeight()
canvas.finishCanvas()
#canvas.save('TOFvLastE.pdf')
canvas.save(fn)
