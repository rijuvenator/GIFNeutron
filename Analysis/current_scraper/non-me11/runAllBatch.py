'''
Created on 17 Feb 2017

@author: kkuzn
Edited for batch on LXBatch with RunH2016 fills by cschnaib
'''

import commands,sys,os
from helper21 import fills

user = commands.getoutput('echo $USER')
cmssw_base = commands.getoutput('echo $CMSSW_BASE')
OFFSET = False
fitmin, fitmax = 0.5, 1.5
where = 'data/no_offset_high_lumi'

for i,fill in enumerate(fills.keys()):
	timestampMin = fills[fill][0]
	timestampMax = fills[fill][1]
	cmd = 'python runAll.py -f {fill} -min \'{timestampMin}\' -max \'{timestampMax}\' -fmin \'{fitmin}\' -fmax \'{fitmax}\' -where \'{where}\''.format(fill=fill,timestampMin=timestampMin,timestampMax=timestampMax,fitmin=fitmin,fitmax=fitmax,where=where)
	cmd += ' -o' if OFFSET else ''
	print cmd
	os.system('mkdir -p '+where+'/fill'+str(fill))
	outF = open('sh/submitRunAll_'+str(fill)+'.sh','w')
	outF.write('#!/bin/bash')
	outF.write('\n')
	outF.write('cd '+cmssw_base+'/src\n')
	outF.write('eval `scramv1 runtime -sh`\n')
	outF.write('cd '+cmssw_base+'/src/Gif/Analysis/current_scraper/non-me11\n')
	outF.write(cmd+'\n')
	outF.close()
	os.system('bsub -q 8nh -J curr11_f'+str(fill)+' < sh/submitRunAll_'+str(fill)+'.sh')
