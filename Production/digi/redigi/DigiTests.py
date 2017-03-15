import subprocess as bash

COMMAND = 'python runReDigi.py -s {BATCH} -n {NUM} -c {CONFIG} -id {IDIR} -if {IFILE} -od {ODIR} -of {OFILE} -nn {NSTART} {NEND} &'.format(
		BATCH  = '-b',
		NUM    = 25,
		CONFIG = 'REDIGITIZE.py',
		IDIR   = '/store/user/cschnaib/Neutron/MinBiasNeutronHP/MinBiasNeutronHP_ThermalON/Merged2/',
		IFILE  = 'MinBias_HPThermalON_GENSIM.root',
		ODIR   = '$WS/public/Neutron/Nom_2/',
		OFILE  = 'MinBias_HPThermalON_ALL.root',
		NSTART = 1,
		NEND   = 25
)
print '\033[1m EXECUTING:\033[m\n'
print COMMAND, '\n'

bash.call(COMMAND, shell=True)
