import ROOT as R
import Gif.Analysis.Plotter as Plotter
import Gif.Analysis.ChamberHandler as CH
import logging

##########################################################################
## HISTOGRAMMER FOR USE WITH GOAT TREE                                  ##
##                                                                      ##
## A general purpose script for producing histograms                    ##
## A histogram is defined by its name using a mini-language             ##
## The general form of a histogram name is as follows:                  ##
##                                                                      ##
## E[+/-]_R##_D[comp/wire]_H[l/u/r]_B#:#_T#:#_L#:#_N[D/L]_A**_A**_A**   ##
##                                                                      ##
## E   = Endcap                                                         ##
## R   = Ring                                                           ##
## D   = Digi                                                           ##
## H   = Half                                                           ##
## B   = BX                                                             ##
## T   = Time bin                                                       ##
## L   = Layer                                                          ##
## ND  = nDigis, NL = nLCTs                                             ##
## A** = Axis code (in AXES dictionary below)                           ##
##                                                                      ##
## [] indicates "one of" (e.g. either + or -)                           ##
## # indicates a number                                                 ##
## * indicates a letter                                                 ##
## #:# indicates a range-type object:                                   ##
##    if just # is given, test for equality                             ##
##    if #: is given, test for at least #                               ##
##    if :# is given, test for at most #                                ##
##    if #:# is given, test for between # and # inclusive               ##
##                                                                      ##
## Example: ME+1/1 left comps in BX 1, TB 1-5 nDigis vs. lumi:          ##
## E+_R11_Dcomp_Hl_B1_T1:5_ND_ALU                                       ##
##                                                                      ##
## Any cut token (E, R, D, H, B, T, L) can be omitted                   ##
## ND vs NL specifies whether to fill once per LCT or once per digi     ##
## A specifies what to fill; so at least one axis required              ##
##                                                                      ##
##########################################################################

####################################
## SELECT FUNCTION AND HIST CLASS ##
####################################

# returns a bool; pass it a value and a cut token (e.g. T1:5, E+)
def select(value, fstr):
	param = fstr[0]
	test  = fstr[1:]
	if   param in ('E', 'R', 'D', 'H'):
		return value == test
	elif param in ('B', 'T', 'L'):
		if ':' in test:
			if ':' == test[0]:
				end = int(test[1:])
				return value <= end
			elif ':' == test[-1]:
				start = int(test[:-1])
				return value >= start
			else:
				start, end = [int(x) for x in test.split(':')]
				return value >= start and value <= end
		else:
			return value == int(test)
	return True

# histogram object storing TH(nAxes)F, axis arguments, and name
# flist will tokenize name and attempt to apply select using all tokens
# if any part of the name is not a cut token (e.g. ND, NL, ALU, AHS, etc.)
# add it to the flist list comprehension, just to be extra safe
class Hist(object):
	def __init__(self, nAxes, axisTags, axis, name):
		self.nAxes    = nAxes
		self.axisTags = axisTags
		self.axis     = axis
		self.name     = name
		self.flist    = [x for x in name.split('_') if x[0] not in ('A', 'N')]
		try:
			self.hist     = getattr(R, 'TH'+str(self.nAxes)+'F')(self.name, '', *self.axis)
		except:
			print self.name, self.axis

####################################
##         LOOP FUNCTION          ##
####################################

def loopFunction(t, HISTS):
	# test values: should correspond to possible cuts
	TVALUES = {
		'E' : str(t.ENDCAP),
		'R' : str(t.RING),
		'D' : str(t.DIGI),
		'H' : str(t.HALF),
		'B' : int(t.BX),
	}

	# axis values: should correspond to AXES
	AVALUES = {
		'RI' : (RINGLIST.index(str(t.RING))+1)*(-1 if str(t.ENDCAP)=='-' else 1),
		'LU' : float(t.LUMI),
		'BX' : int(t.BX),
		'HS' : int(t.POS),
		'WG' : int(t.POS),
	}

	# The model for filling histograms is to loop through them,
	# apply all the selections (tokens in flist), and fill all the axisTags values
	# the all takes the and of all the bools; the * in Fill just expands the axis values

	# nLCTs hists
	for name in HISTS:
		if 'NL' not in name: continue
		if not all([select(TVALUES[fname[0]], fname) for fname in HISTS[name].flist]): continue
		HISTS[name].hist.Fill(*[AVALUES[aname] for aname in HISTS[name].axisTags])

	# nDigis hists
	for TB, POS, LAY in zip(list(t.D_TIME), list(t.D_POS), list(t.D_LAYER)):
		# additional test values per digi
		TVALUES['T'] = TB
		TVALUES['L'] = LAY

		# additional/updated axis values per digi
		AVALUES['HS'] = POS
		AVALUES['WG'] = POS
		AVALUES['TB'] = TB

		for name in HISTS:
			if 'ND' not in name: continue
			if not all([select(TVALUES[fname[0]], fname) for fname in HISTS[name].flist]): continue
			HISTS[name].hist.Fill(*[AVALUES[aname] for aname in HISTS[name].axisTags])

####################################
##          MODULE CODE           ##
####################################

#########################
##    LOGGING SETUP    ##
#########################

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

##########################
##    MODULE GLOBALS    ##
##########################

RINGLIST = ('11', '12', '13', '21', '22', '31', '32', '41', '42')

# AXES encodes axis types and binning. A new fill value = a new axis.
AXES = {
	'BX' : (49, 1, 50),
	'LU' : (60, 0, 15.e33),
	'TB' : (),
	'HS' : (),
	'WG' : (),
#	'RI' : range(-9, 0) + range(1, 10)
	'RI' : (19, -9, 10)
}

#####################
## HISTOGRAM SETUP ##
#####################

HISTS = {}

####################
##    ONE OFFS    ##
####################

## TB distributions for individual BX: E_R_D_H_B_ND_ATB
#for BX in xrange(1, 50):
#	HCONFIGS['_B'+str(BX)+'_ND'] = (1, ['TB'])

## BX distributions for individual TB: E_R_D_H_T_ND_ABX
#for TB in xrange(0, 16):
#	HCONFIGS['_T'+str(TB)+'_ND'] = (1, ['BX'])

## ring integral distributions D_H_NDL_ARI
#DIGIDICT = {
#	'comp' : ('l', 'r'),
#	'wire' : ('u', 'l'),
#}
#for digi, HALFLIST in DIGIDICT.iteritems():
#	for half in HALFLIST:
#		for type_ in ('ND', 'NL'):
#			name = 'D{DIGI}_H{HALF}_{TYPE}_ARI'.format(DIGI=digi, HALF=half, TYPE=type_)
#			conf = (1, ['RI'], AXES['RI'], name)
#			HISTS[name] = Hist(*conf)

########################
##   HCONFIGS LOOP    ##
########################

# second half of every histogram; the axes will be appended
HCONFIGS = {
#	'_B1_T1:5_ND' : (1, ['LU']),       # digi money
#	'_B1_T1:5_ND' : (1, ['HS']),       # digi HS occupancy
#	'_B1_T1:5_ND' : (1, ['WG']),       # digi WG occupancy
#	'_B1_NL'      : (1, ['LU']),       # LCT money
#	'_B1_NL'      : (1, ['HS']),       # LCT HS occupancy
#	'_B1_NL'      : (1, ['WG']),       # LCT WG occupancy
	'_ND'         : (2, ['TB', 'BX']), # rainbow - TB is 16 for both
#	'_NL'         : (1, ['BX']),       # LCT rainbow
#	'_T{FLAT}_ND' : (1, ['LU']),       # flat time bin
#	'_NL'         : (1, ['LU']),       # nLCTs
}

# sets up E_R_D_H, then adds the second half from HCONFIGS
for endcap in ('+', '-'):
	for ring in RINGLIST:
		cham = CH.Chamber(CH.serialID(1, int(ring[0]), int(ring[1]), 1))
		binsComp = cham.nstrips*2+2
		binsWire = cham.nwires+2
		DIGIDICT = {
			'comp' : ('HS', ('l', 'r'), 10, binsComp, 7),
			'wire' : ('WG', ('u', 'l'), 16, binsWire, 8),
		}
		for digi, (DAXIS, HALFLIST, TBMAX, DBINS, FLAT) in DIGIDICT.iteritems():
			AXES['TB'] = (TBMAX, 0, TBMAX)
			AXES[DAXIS] = (DBINS, 0, DBINS)
			for half in HALFLIST:
				nameHead = '_'.join(('E'+endcap, 'R'+ring, 'D'+digi, 'H'+half))
				for nameTail, (nAxes, axisTags) in HCONFIGS.iteritems():
					if len(axisTags) != nAxes:
						print 'Axis mismatch; skipping'
						continue
					if (digi == 'comp' and 'WG' in axisTags) or (digi == 'wire' and 'HS' in axisTags): continue
					axis = []
					realNameTail = nameTail.format(**locals())
					for axisTag in axisTags:
						axis.extend(AXES[axisTag])
						realNameTail += '_A'+axisTag
					conf = (nAxes, axisTags, axis, nameHead+realNameTail)
					HISTS[nameHead+realNameTail] = Hist(*conf)

logger.warning('All histograms declared...')

####################################
##           MAIN CODE            ##
####################################

if __name__ == '__main__':
	#f = R.TFile.Open('SinatraTest.root')
	f = R.TFile.Open('/afs/cern.ch/work/c/cschnaib/public/goatees/GOAT_P5_14June2017.root')
	t = f.Get('t')

	logger.warning('File and tree gotten...')

	####################################
	##           TREE LOOP            ##
	####################################

	# loop over the tree and fill
	for i, entry in enumerate(t):

		#if i%1000==0: logger.warning(str(i)+' events completed')
		#if i == 10000: break

		loopFunction(t, HISTS)

	logger.warning('Tree loop completed...')

	####################################
	##            END CODE            ##
	####################################

	# write them all
	g = R.TFile('test.root', 'RECREATE')
	g.cd()
	for name in HISTS:
		HISTS[name].hist.Write()

	logger.warning('Histograms written.')
