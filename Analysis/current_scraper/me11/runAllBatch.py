'''
Created on 17 Feb 2017

@author: kkuzn
Edited for batch on LXBatch with RunH2016 fills by cschnaib
'''

import commands,sys,os
from helper11 import fills

user = commands.getoutput('echo $USER')
cmssw_base = commands.getoutput('echo $CMSSW_BASE')

for i,fill in enumerate(fills.keys()):
	timestampMin = fills[fill][0]
	timestampMax = fills[fill][1]
	cmd = 'python runAll.py -f {fill} -min \'{timestampMin}\' -max \'{timestampMax}\''.format(fill=fill,timestampMin=timestampMin,timestampMax=timestampMax)
	print cmd
	os.system('mkdir -p results/fill'+str(fill))
	outF = open('sh/submitRunAll_'+str(fill)+'.sh','w')
	outF.write('#!/bin/bash')
	outF.write('\n')
	outF.write('cd '+cmssw_base+'/src\n')
	outF.write('eval `scramv1 runtime -sh`\n')
	outF.write('cd '+cmssw_base+'/src/Gif/Analysis/current_scraper/me11\n')
	outF.write(cmd+'\n')
	outF.close()
	os.system('bsub -q 1nh -J curr11_f'+str(fill)+' < sh/submitRunAll_'+str(fill)+'.sh')
	continue
