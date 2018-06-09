import ROOT as R
import Gif.Analysis.ChamberHandler as CH
R.gROOT.SetBatch(True)

DIGILIST = ['wire','comp']
RINGLIST = ['11','12','13','21','22','31','32','41','42']
me11 = {
	1:12649.632,   2:6799.681,   3:6987.932,   4:7176.184,   5:7364.436,   6:7552.688,   7:7740.939,   8:7929.191,
	9:8117.443,   10:8305.694,  11:8493.946,  12:8682.198,  13:8870.450,  14:9058.701,  15:9246.953,  16:9435.205,
	17:9623.456,  18:9811.708,  19:9999.960,  20:10188.212, 21:10376.463, 22:10564.715, 23:10752.967, 24:10941.218,
	25:11129.470, 26:11317.722, 27:11505.974, 28:11694.225, 29:11882.477, 30:12070.729, 31:12258.980, 32:12447.232,
	33:12635.484, 34:12823.736, 35:13011.987, 36:13200.239, 37:13388.491, 38:13576.742, 39:13764.994, 40:13953.246,
	41:14141.498, 42:14329.749, 43:14412.107, 44:13133.524, 45:11439.189, 46:9744.854,  47:8050.519,  48:15212.992,
	} # fuck yeah, victor is the best
areaHists = {digi:{ring:{} for ring in RINGLIST} for digi in DIGILIST}
for digi in DIGILIST:
	for ring in RINGLIST:
		cham = CH.Chamber(CH.serialID(1,int(ring[0]),int(ring[1]),1))
		# Wire histogram goes from 1,nWG
		# Comp histogram goes from 2,2*s+1
		nhs = cham.nstrips*2+1
		nwg = cham.nwires
		lim = nhs if digi=='comp' else nwg
		plotlim = cham.nwires+2 if digi=='wire' else (cham.nstrips)*2+2
		#lim = cham.nwires if digi=='wire' else (cham.nstrips-1)*2+1
		#low = 0
		low = 1 if digi=='wire' else 1
		#high = lim+1 if digi=='wire' else lim+2
		areaHists[digi][ring] = R.TH1D(digi+'_'+ring,'',plotlim,0,plotlim)
		#print digi, ring, low,lim,areaHists[digi][ring].GetNbinsX()
		for idx,idigi in enumerate(range(low,lim+1)):
			if digi=='wire':
				if ring!='11': # non me11
					a = 6*(((cham.t[ring]-cham.b[ring])/cham.h[ring] * cham.h[ring]/lim * 0.5*(idigi*2-1)) + cham.b[ring])*cham.h[ring]/lim
					areaHists[digi][ring].Fill(idigi,a)
				else: # me11
					areaHists[digi][ring].Fill(idigi,6*me11[idigi]*0.01) # convert me11 dict from mm^2 to cm^2
			else: # comp
				# hs = 2*s + c in primitives
				# this means hs = [2,2*ns+1], since s = [1,ns]
				# add 1 to i so that the limits of the area histogram 
				# matches the limits of the primitives
				if ring!='11': # non me11
					a = 6*0.5*(cham.t[ring]+cham.b[ring])*cham.h[ring]/lim # area/half-strip
					areaHists[digi][ring].Fill(idigi,a)
				else: # me11
					if idigi<=127: # me11b
						a = 6*0.5*(47.4+27.4)*107.5/64. # area per strip
						areaHists[digi][ring].Fill(idigi,0.5*a)
					else: # me11a
						a = 6*0.5*(27.4+19.14)*44.5/48. # area per strip
						areaHists[digi][ring].Fill(idigi,0.5*a)

if __name__=='__main__':
	import Gif.Analysis.Plotter as Plotter
	for digi in DIGILIST:
		for ring in RINGLIST:
			plot = Plotter.Plot(areaHists[digi][ring])
			canvas = Plotter.Canvas(lumi='Area per '+('wire group' if digi=='wire' else 'half strip')+' in ME'+ring)
			canvas.addMainPlot(plot)
			canvas.firstPlot.setTitles(X='Wire Group Number' if digi=='wire' else 'Comparator Half Strip', Y='cm^{2}')
			integral = plot.Integral()
			canvas.drawText(text='Integral = '+str(integral),pos=(0.6,0.7))
			canvas.makeTransparent()
			canvas.finishCanvas('BOB')
			canvas.save('plots/areas/'+ring+'_'+digi+'_area.pdf')

