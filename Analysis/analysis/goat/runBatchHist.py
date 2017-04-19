import subprocess as bash
import math

CMSSW_BASE = bash.check_output('echo $CMSSW_BASE', shell=True).rstrip('\n')+'/'
RUNDIR = CMSSW_BASE + 'src/Gif/Analysis/analysis/goat/'

bash.call('mkdir -p shH', shell=True)

TREESIZE = 5525880
SPLIT    = 10000

NJOBS    = int(math.ceil(float(TREESIZE)/SPLIT))
for NUM in xrange(NJOBS):
	START = NUM*SPLIT
	END = min(START+SPLIT-1, TREESIZE)

	submitScript = '''
cd {CMSSW_BASE}src
eval `scramv1 runtime -sh`
cd {RUNDIR}
python Batch_Histogrammer.py {NUM} {START} {END}
rm -f core.*
'''.format(**locals())

	open('shH/job_{NUM}.sh'.format(**locals()), 'w').write(submitScript)
	bash.call('bsub -q 1nh -J ana_{NUM} < shH/job_{NUM}.sh'.format(**locals()), shell=True)
