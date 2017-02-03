''' Class for storing test beam measurements
'''
import os

# ------- Measurement Class from ../database_scraper/meta -------
class Meas():
	'''
	- GIFMeasurement class is designed to be a python class container for all relevant meta data associated with a measurement: 
	  - meas   : Measurement number (1966, 1977, etc.)
	  - cham   : chamber type (1 or 2)
	  - HV     : Chamber high voltage (HV0, 2900, 3600, etc.)
	  - source : Source status (1 or 0)
	  - beam   : Beam status (1 or 0)
	  - uAtt   : Upsteam source attenuation (46, 0, etc.)
	  - dAtt   : Downstream source attenuation (15, 0, etc.)
	  - runtype: STEP Test type (STEP_27, STEP_27s, STEP_40, Other)
	- Constructor requires one argument: the relevant line in the 'meta' file located in database_scraper
	  - Or just give it a string with the same format.
	- ROOTFile() method returns Riju's unpacked root file (test_MEAS.root)
	  - prefix keyword changes the dirname (e.g. for use with CRAB)
	  - starnum keyword specifies which file in a starnum group to use (returns test_MEAS_STARNUM.root)
	- SetCentralFN(fn) sets self.fn to fn
	  - So that Chris can use the copy of Riju's root file that has a different name
	'''

	# --- constructor; fills metadata given line from meta file
	def __init__(self, line):
		l = line.strip('\n').split()
		self.meas    = l[0]
		self.cham    = 'ME'+l[1]+'1'
		self.HV      = l[2]
		self.source  = bool(int(l[3]))
		self.beam    = bool(int(l[4]))
		self.uAtt    = l[5]
		self.dAtt    = l[6]
		self.FF      = l[7]

		endname = l[8]
		# get run type
		if 'TMB' in endname:
			self.runtype = 'TMB'
		elif 'STEP_40' in endname:
			self.runtype = 'Test40'
		elif 'STEP_27s' in endname:
			self.runtype = 'Test27s'
		elif 'STEP_27' in endname:
			self.runtype = 'Test27'
		else:
			self.runtype = 'Other'

		# get timestamp
		if 'emugif2' in endname:
			rawtime = endname[-21:-8]
			self.time = '20'+rawtime[0:2]+'/'+rawtime[2:4]+'/'+rawtime[4:6]+' '+rawtime[7:9]+':'+rawtime[9:11]+':'+rawtime[11:13]
		else:
			self.time = '0'

		# check if star
		if '*' in endname:
			self.star = True
		else:
			self.star = False
                
		# get test beam #
		try:
			measNum = int(self.meas)
			if measNum >= 1926 and measNum <=2432 and self.cham=='ME11':
				self.TB = '1'
			elif measNum >= 2062 and measNum <=2432 and self.cham=='ME21':
				self.TB = '1'
			elif measNum >=2433 and measNum <=2588:
				self.TB = '2'
			elif measNum >=2590 and measNum <= 3134:
				self.TB = '3'
			else:
				self.TB = 'bad'
		except:
			self.TB = 'bad'
	
	# --- repr; what to print
	def __repr__(self):
		pstr = """
		\033[1mMeasurement #%s\033[m
		   Chamber   : %s
		   Run Type  : %s
		   HV        : %s
		   Beam      : %s
		   Source    : %s
		   Atten.    : %s
		   FF        : %s
		   Time      : %s
		   Test Beam : %s
		  """
		pstr = pstr.lstrip('\n')
		pstr = pstr.replace('\t','')

		return pstr % (\
			self.meas,
			self.cham,
			self.runtype.replace('_',' '),
			self.HV if self.HV=='HV0' else self.HV+' V',
			'ON' if self.beam else 'OFF',
			'OFF' if not self.source else 'ON',
			'%s/%s' % (self.uAtt,self.dAtt),
			self.FF,
			self.time,
			self.TB
				)

	# --- returns path to unpacked ROOT file
	# ------ prefix keyword lets you change the prefix (e.g. for use in CRAB config files)
	# ------ starnum appends a number to the name, for the starfiles
	def ROOTFile(self, prefix=None, starnum=None):
		if starnum is None:
			meas = self.meas
		else:
			meas = self.meas+'_'+starnum

		if prefix is None:
			return 'root://eoscms//eos/cms/store/user/adasgupt/GIF/test_'+meas+'.root'
		else:
			return prefix+'test_'+meas+'.root'
	
	# --- sets central file name
	def SetCentralFN(self, fn):
		self.fn = fn

# get all measurements and fill a dictionary indexed by measurement number
scriptdir = os.path.dirname(__file__)
relpath = '../database_scraper/meta'
metafile = open(os.path.join(scriptdir, relpath))
meas = {}
for line in metafile:
	m = Meas(line)
	meas[m.meas] = m
metafile.close()

# for Chris
measDirMay16 = '/store/group/dpg_csc/comm_csc/gif/may16/'
# ME11 Test27
meas['2250'].SetCentralFN(measDirMay16+'ME11/sourceOFF/test27/ME11_Test27_HV0_bOn_uOff_dOff_m2250_t160508163702.root')
meas['1977'].SetCentralFN(measDirMay16+'ME11/d46/test27/ME11_Test27_HV0_bOn_u46_d46_m1977_t160506025710.root')
# ME11 Test40
meas['1966'].SetCentralFN(measDirMay16+'ME11/sourceOFF/test40/ME11_Test40_HV0_bOn_uOff_dOff_m1966_t160506015143.root')
meas['1930'].SetCentralFN(measDirMay16+'ME11/d10/test40/ME11_Test40_HV0_bOn_u6.9_d10_m1930_t160505172039.root')
meas['2009'].SetCentralFN(measDirMay16+'ME11/d22/test40/ME11_Test40_HV0_bOn_u4.6_d22_m2009_t160506075655.root')
meas['2010'].SetCentralFN(measDirMay16+'ME11/d22/test40/ME11_Test40_HV0_bOn_u4.6_d22_m2010_t160506081406.root')
meas['2040'].SetCentralFN(measDirMay16+'ME11/d46/test40/ME11_Test40_HV0_bOn_u46000_d46_m2040_t160506125054.root')
meas['1979'].SetCentralFN(measDirMay16+'ME11/d46/test40/ME11_Test40_HV0_bOn_u46_d46_m1979_t160506031324.root')
meas['2131'].SetCentralFN(measDirMay16+'ME11/d69/test40/ME11_Test40_HV0_bOn_u3.3_d69_m2131_t160507181505.root')
meas['2132'].SetCentralFN(measDirMay16+'ME11/d69/test40/ME11_Test40_HV0_bOn_u3.3_d69_m2132_t160507183006.root')
meas['2051'].SetCentralFN(measDirMay16+'ME11/d100/test40/ME11_Test40_HV0_bOn_u46000_d100_m2051_t160506155933.root')
meas['2276'].SetCentralFN(measDirMay16+'ME11/d100/test40/ME11_Test40_HV0_bOn_u69_d100_m2276_t160508233519.root')
meas['2357'].SetCentralFN(measDirMay16+'ME11/d1000/test40/ME11_Test40_HV0_bOn_u6.9_d1000_m2357_t160510002250.root')
meas['2322'].SetCentralFN(measDirMay16+'ME11/d46000/test40/ME11_Test40_HV0_bOn_u10_d46000_m2322_t160509153759.root')
# ME21 Test27
meas['2306'].SetCentralFN(measDirMay16+'ME21/sourceOFF/test27/ME21_Test27_HV0_bOn_uOff_dOff_m2306_t160509094700.root')
meas['2062'].SetCentralFN(measDirMay16+'ME21/d15/test27/ME21_Test27_HV0_bOn_u46_d15_m2062_t160506220324.root')
# ME21 Test40
meas['2312'].SetCentralFN(measDirMay16+'ME21/sourceOFF/test40/ME21_Test40_HV0_bOn_uOff_dOff_m2312_t160509111100.root')
meas['2095'].SetCentralFN(measDirMay16+'ME21/d10/test40/ME21_Test40_HV0_bOn_u100_d10_m2095_t160507075643.root')
meas['2262'].SetCentralFN(measDirMay16+'ME21/d10/test40/ME21_Test40_HV0_bOn_u46_d10_m2262_t160508194955.root')
meas['2064'].SetCentralFN(measDirMay16+'ME21/d15/test40/ME21_Test40_HV0_bOn_u46_d15_m2064_t160506222510.root')
meas['2079'].SetCentralFN(measDirMay16+'ME21/d46/test40/ME21_Test40_HV0_bOn_u69_d46_m2079_t160507020959.root')
meas['2224'].SetCentralFN(measDirMay16+'ME21/d100/test40/ME21_Test40_HV0_bOn_u46_d100_m2224_t160508122530.root')
meas['2333'].SetCentralFN(measDirMay16+'ME21/d1000/test40/ME21_Test40_HV0_bOn_u69_d1000_m2333_t160509200512.root')
# Test for Cameron
# Giving it a fake meta string with a fake file name so that the class gets initialized correctly
#meas['CAM'] = Meas('CAM 1 HV0 0 0 0 0 C emugif2_STEP_40_000000_000000_UTC.raw')
#meas['CAM'].SetCentralFN('file:/afs/cern.ch/user/c/cschnaib/Work/CMSSW_7_5_1/src/Gif/TestBeamAnalysis/analysis/MakeHistosAndTree/test_CAM.root')

# for testing
if __name__ == '__main__':
	print 'Meas has', len(meas.keys()), 'classes'
	print meas['2040']
	print meas['2064']
	#print meas['CAM']
