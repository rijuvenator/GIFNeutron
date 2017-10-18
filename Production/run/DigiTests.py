import subprocess as bash

#COMMAND = 'python runTreeMaker.py {SUBMIT} {BATCH} -n {NUM} -c {CONFIG} -id {IDIR} -if {IFILE} -od {ODIR} -of {OFILE} -nn {NSTART} {NEND} &'.format(
#		SUBMIT = '-s',
#		BATCH  = '-b',
#		NUM    = 79,
#		CONFIG = 'GifAnalysis.py',
#		IDIR   = 'file:/afs/cern.ch/work/c/cousins/public/riju/Hack3_TOF_1/',
#		IFILE  = 'MinBias_HPThermalON_ALL.root',
#		ODIR   = '$WS/public/Neutron/hack3TOFtrees1/',
#		OFILE  = 'test.root',
#		NSTART = 0,
#		NEND   = 78
#)
#print '\033[1m EXECUTING:\033[m\n'
#print COMMAND, '\n'
#
#bash.call(COMMAND, shell=True)

COMMAND = 'python runTreeMaker.py {SUBMIT} {BATCH} -n {NUM} -c {CONFIG} -id {IDIR} -if {IFILE} -od {ODIR} -of {OFILE} -nn {NSTART} {NEND} &'.format(
		SUBMIT = '-s',
		BATCH  = '-b',
		NUM    = 25,
		CONFIG = 'GifAnalysis.py',
		IDIR   = 'file:/afs/cern.ch/work/c/cousins/public/riju/SkySong_Good/',
		IFILE  = 'MinBias_HPThermalON_ALL.root',
		ODIR   = '$WS/public/Neutron/skysong_good/',
		OFILE  = 'test.root',
		NSTART = 1,
		NEND   = 25
)
print '\033[1m EXECUTING:\033[m\n'
print COMMAND, '\n'

bash.call(COMMAND, shell=True)
