import subprocess as bash

COMMAND = 'python runTreeMaker.py -s {BATCH} -n {NUM} -c {CONFIG} -id {IDIR} -if {IFILE} -od {ODIR} -of {OFILE} -nn {NSTART} {NEND} &'.format(
		BATCH  = '-b',
		NUM    = 300,
		CONFIG = 'SimAnalysis.py',
		IDIR   = '/store/user/cschnaib/Neutron/MinBiasNeutronHP/MinBiasNeutronHP_ThermalON_LOG/',
		IFILE  = 'mb_13TeV_mu_GEN_SIM_hp.root',
		ODIR   = '$WS/public/Neutron/simtrees/',
		OFILE  = 'ana_simTree.root',
		NSTART = 1,
		NEND   = 300,
)
print '\033[1m EXECUTING:\033[m\n'
print COMMAND, '\n'

bash.call(COMMAND, shell=True)
