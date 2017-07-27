import ROOT as R
import Gif.Analysis.Plotter as Plotter

R.gROOT.SetBatch(True)

pretty = {
	'CSH1' : 'Charge per SimHit, ME1/1',
	'CSH2' : 'Charge per SimHit, non-ME1/1',
	'CPH1' : 'Charge per WireHit, ME1/1',
	'CPH2' : 'Charge per WireHit, non-ME1/1',
}

#f = R.TFile.Open('AQ_CPH.root')
f = R.TFile.Open('WD_AQ.root')
for suffix in pretty:
	h = f.Get('h'+suffix)

	plot = Plotter.Plot(h, option='hist')
	canvas = Plotter.Canvas(lumi=pretty[suffix])

	canvas.addMainPlot(plot)
	canvas.firstPlot.setTitles(X='Charge/Wire Hit [fC]', Y='Counts')

	canvas.drawText(text='Mean: {val:4.0f} fC'.format(val=h.GetMean()), pos=(0.8, 0.8), align='br')

	canvas.finishCanvas()
	canvas.save('cph'+'_'+suffix+'.png')
	canvas.deleteCanvas()
