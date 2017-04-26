import subprocess as bash

COMMAND = 'python runTreeMaker.py -s {BATCH} -n {NUM} -c {CONFIG} -id {IDIR} -if {IFILE} -od {ODIR} -of {OFILE} &'.format(
		BATCH  = '-b',
		NUM    = 79,
		CONFIG = 'GifAnalysis.py',
		IDIR   = 'file:/afs/cern.ch/work/c/cousins/public/riju/Nom_TOF_1/',
		IFILE  = 'MinBias_HPThermalON_ALL.root',
		ODIR   = '$WS/public/Neutron/nomTOFtrees1/',
		OFILE  = 'test.root',
)
print '\033[1m EXECUTING:\033[m\n'
print COMMAND, '\n'

bash.call(COMMAND, shell=True)
