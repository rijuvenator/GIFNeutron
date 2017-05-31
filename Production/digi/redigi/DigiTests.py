import subprocess as bash

COMMAND = 'python runReDigi.py {SUBMIT} {BATCH} -n {NUM} -c {CONFIG} -id {IDIR} -if {IFILE} -od {ODIR} -of {OFILE} -nn {NSTART} {NEND} &'.format(
		SUBMIT = '-s',
		BATCH  = '-b',
		NUM    = 25,
		CONFIG = 'REDIGITIZE.py',
		IDIR   = '/store/user/cschnaib/Neutron/MinBiasNeutronHP/MinBiasNeutronHP_ThermalON/Merged2/',
		IFILE  = 'MinBias_HPThermalON_GENSIM.root',
		ODIR   = '/afs/cern.ch/work/c/cousins/public/riju/SkySong_NoBoth/',
		OFILE  = 'MinBias_HPThermalON_ALL.root',
		NSTART = 1,
		NEND   = 25
)
print '\033[1m EXECUTING:\033[m\n'
print COMMAND, '\n'

bash.call(COMMAND, shell=True)

COMMAND = 'python runReDigi.py {SUBMIT} {BATCH} -n {NUM} -c {CONFIG} -id {IDIR} -if {IFILE} -od {ODIR} -of {OFILE} -nn {NSTART} {NEND} &'.format(
		SUBMIT = '-s',
        BATCH  = '-b',
        NUM    = 79,
        CONFIG = 'REDIGITIZE.py',
        IDIR   = '/store/user/cschnaib/Neutron/MinBiasNeutronHP/MinBiasNeutronHP_ThermalON/Merged1/',
        IFILE  = 'MinBias_HPThermalON_GENSIM.root',
		ODIR   = '/afs/cern.ch/work/c/cousins/public/riju/Hack4_TOF_1/',
        OFILE  = 'MinBias_HPThermalON_ALL.root',
        NSTART = 0,
        NEND   = 78
)
print '\033[1m EXECUTING:\033[m\n'
print COMMAND, '\n'

bash.call(COMMAND, shell=True)
