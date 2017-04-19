import ROOT as R
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.ChamberHandler as CH
import logging

#######################################################################
## Batch version of Histogrammer                                     ##
from Histogrammer import select, loopFunction, HISTS, RINGLIST, AXES ##
#######################################################################

##### LOGGING SETUP #####
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

####################################
##           MAIN CODE            ##
####################################

if __name__ == '__main__':
	f = R.TFile.Open('SinatraTest.root')
	t = f.Get('t')

	logger.warning('File and tree gotten...')

	import sys
	NUM   = sys.argv[1]
	START = int(sys.argv[2])
	END   = int(sys.argv[3])

	####################################
	##           TREE LOOP            ##
	####################################

	# loop over the tree and fill
	#for i, entry in enumerate(t):
	for i in xrange(START, END+1):
		#if i%1000==0: logger.warning(str(i)+' events completed')
		t.GetEntry(i)

		loopFunction(t, HISTS)

	logger.warning('Tree loop completed...')

	####################################
	##            END CODE            ##
	####################################

	# write them all
	#g = R.TFile('$WS/public/hists/test_'+NUM+'.root', 'RECREATE')
	g = R.TFile('test_'+NUM+'.root', 'RECREATE')
	g.cd()
	for name in HISTS:
		HISTS[name].hist.Write()

	logger.warning('Histograms written.')
