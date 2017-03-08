import subprocess as bash

COMMAND = 'python runReDigi.py -s {BATCH} -n {NUM} -c {CONFIG} -id {IDIR} -if {IFILE} -od {ODIR} -of {OFILE}'.format(
		BATCH  = '-b',
		NUM    = 2,
		CONFIG = 'REDIGITIZE.py',
		IDIR   = '/store/user/cschnaib/Neutron/MinBiasNeutronHP/MinBiasNeutronHP_ThermalON/170228_114855/0000/',
		IFILE  = 'mb_13TeV_mu_gen_sim_hp_thermal_ON.root',
		ODIR   = '$WS/public/Neutron/ReDigi',
		OFILE  = 'mb_13TeV_mu_all_hp_thermal_ON.root'
)
print '\033[1m EXECUTING:\033[m\n'
print COMMAND, '\n'

bash.call(COMMAND, shell=True)
