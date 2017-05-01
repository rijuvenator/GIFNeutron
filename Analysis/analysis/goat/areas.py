import ROOT as R
import Gif.Analysis.ChamberHandler as CH

DIGILIST = ['wire']
RINGLIST = ['11','12','13','21','22','31','32','41','42']
areaHists = {digi:{ring:{} for ring in RINGLIST} for digi in DIGILIST}
for digi in DIGILIST:
	for ring in RINGLIST:
		cham = CH.Chamber(CH.serialID(1,int(ring[0]),int(ring[1]),1))
		lim = cham.nwires if digi=='wire' else cham.nstrips*2
		areaHists[digi][ring] = R.TH1D(ring,'',lim+2,0,lim+2)
		for i in range(1,lim+1):
			if digi=='wire':
				a = 6*(((cham.t[ring]-cham.b[ring])/cham.h[ring] * cham.h[ring]/lim * 0.5*(i*2+1)) + cham.b[ring])*cham.h[ring]/lim
				areaHists[digi][ring].SetBinContent(i,a)
			else:
				pass

if __name__=='__main__':
	import Gif.Analysis.Plotter as Plotter
	for digi in DIGILIST:
		for ring in RINGLIST:
			plot = Plotter.Plot(areaHists[digi][ring])
			canvas = Plotter.Canvas(lumi='Area per '+('wire group' if digi=='wire' else 'half strip')+' in ME'+ring)
			canvas.addMainPlot(plot)
			canvas.firstPlot.setTitles(X='Wire Group Number' if digi=='wire' else 'Comparator Half Strip', Y='cm^{2}')
			canvas.makeTransparent()
			canvas.finishCanvas('BOB')
			canvas.save('pdfs/'+ring+'_'+digi+'_area.pdf')

