import subprocess as bash

CMSSW_BASE = bash.check_output('echo $CMSSW_BASE', shell=True).rstrip('\n')+'/'
RUNDIR = CMSSW_BASE + 'src/Gif/Analysis/analysis/pattern/'

bash.call('mkdir -p sh', shell=True)

for NUM in xrange(76):
	START = NUM*50000
	END = min(START+49999, 3790593)

	submitScript = '''
cd {CMSSW_BASE}src
eval `scramv1 runtime -sh`
cd {RUNDIR}
python Batch_BGCompPatterns.py -r P5 {NUM} {START} {END}
rm -f core.*
'''.format(**locals())

	open('sh/job_{NUM}.sh'.format(**locals()), 'w').write(submitScript)
	bash.call('bsub -q 8nh -J ana_{NUM} < sh/job_{NUM}.sh'.format(**locals()), shell=True)

	#bash.call('python Batch_BGDigiIntegrals.py -r P5 {NUM} {START} {END}'.format(**locals()), shell=True)
	#print 'Finished', NUM

