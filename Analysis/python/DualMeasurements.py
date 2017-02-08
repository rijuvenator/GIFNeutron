''' Class for storing test beam measurements
'''
import os

# ------- Measurement Class from ../database_scraper/meta -------
class Meas():
	'''
	- GIFMeasurement class is designed to be a python class container for all relevant meta data associated with a measurement: 
	  - meas   : Measurement number (1966, 1977, etc.)
	  - cham   : chamber type (Dual or 1 or 2)
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
		self.cham    = 'ME'+l[1]+'1' if l[1] != 'D' else 'Dual'
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
		measNum = int(self.meas)
		if measNum >= 1926 and measNum <=2432 and self.cham=='ME11':
			self.TB = '1'
		elif measNum >= 2062 and measNum <=2432 and self.cham=='ME21':
			self.TB = '1'
		elif measNum >=2433 and measNum <=2588:
			self.TB = '2'
		elif measNum >=2590 and measNum <= 3134:
			self.TB = '3'
		elif measNum >=3219 and measNum <= 3399:
			self.TB = '4'
		else:
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

# for testing
if __name__ == '__main__':
	print 'Meas has', len(meas.keys()), 'classes'
	print meas['3377']
	print meas['3380']
	print meas['3399']
