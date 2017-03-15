#!/usr/bin/env python
import subprocess as bash
import argparse

COMMAND = 'cmsDriver.py'

def addOption(flag, value=None):
	global COMMAND
	if value is not None:
		COMMAND += ' ' + flag + ' ' + value
	else:
		COMMAND += ' ' + flag

#addOption('MinBias_13TeV_cfi'                                                           )
#addOption('--step'            ,'GEN,SIM,DIGI,L1,DIGI2RAW,RAW2DIGI,L1Reco,RECO'          )
addOption('--step'            ,        'DIGI,L1,DIGI2RAW,RAW2DIGI,L1Reco,RECO'          )
addOption('--conditions'      ,'auto:run2_mc'                                           )
addOption('--eventcontent'    ,'FEVTDEBUG'                                              )
addOption('--mc'                                                                        )
addOption('--no_exec'                                                                   )
addOption('--filein'          ,'file:input.root'                                        )
addOption('--fileout'         ,'file:output.root'                                       )
addOption('--number'          ,'1000'                                                   )
addOption('--python_filename' ,'test.py'                                                )
addOption('--pileup'          ,'NoPileUp'                                               )
addOption('--geometry'        ,'DB'                                                     )
#addOption('--beamspot'        ,'Realistic50ns13TeVCollision'                            )
#addOption('--geometry'        ,'Extended2015,Extended2015Reco'                          )
#addOption('--magField'        ,'38T_PostLS1'                                            )
#addOption('--datatier'        ,'GEN-SIM'                                                )
#addOption('--customise'       ,'SimG4Core/Application/NeutronBGforMuonsXS_cff.customise')

bash.call(COMMAND, shell=True)
