import subprocess as bash

COMMAND = 'python runTreeMaker.py -s {BATCH} -n {NUM} -c {CONFIG} -id {IDIR} -if {IFILE} -od {ODIR} -of {OFILE} &'.format(
		BATCH  = '-b',
		NUM    = 25,
		CONFIG = 'GifAnalysis.py',
		IDIR   = '/store/user/adasgupt/Neutron/MBReDigi/ReDigi_Nom2/',
		IFILE  = 'MinBias_HPThermalON_ALL.root',
		ODIR   = '$WS/public/Neutron/nomtrees2/',
		OFILE  = 'test.root'
)
print '\033[1m EXECUTING:\033[m\n'
print COMMAND, '\n'

bash.call(COMMAND, shell=True)
