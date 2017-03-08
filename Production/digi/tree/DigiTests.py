import subprocess as bash

EOSDIR = '/store/user/adasgupt/Neutron/MinBiasNeutron/MinBiasNeutronLog/'

COMMAND = 'python runTreeMaker.py -s {BATCH} -n {NUM} -c {CONFIG} -id {IDIR} -if {IFILE} -od {ODIR} -of {OFILE}'.format(
		BATCH  = '',
		NUM    = 2,
		CONFIG = 'GifAnalysis.py',
#		IDIR   = EOSDIR + '170227_105455/0000/',
#		IDIR   = EOSDIR + '170227_161757/0000/',
		IDIR   = EOSDIR + '170307_190454/0000/',
		IFILE  = 'mb_13TeV_mu_xs_crab.root',
		ODIR   = 'output/',
		OFILE  = 'test.root'
)
print '\033[1m EXECUTING:\033[m\n'
print COMMAND, '\n'

bash.call(COMMAND, shell=True)
