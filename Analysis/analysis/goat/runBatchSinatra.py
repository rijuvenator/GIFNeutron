import subprocess as bash
import math

CMSSW_BASE = bash.check_output('echo $CMSSW_BASE', shell=True).rstrip('\n')+'/'
RUNDIR = CMSSW_BASE + 'src/Gif/Analysis/analysis/goat/'

bash.call('mkdir -p sh', shell=True)

TREESIZE = 3790593
SPLIT    = 10000

NJOBS    = int(math.ceil(float(TREESIZE)/SPLIT))
for NUM in xrange(NJOBS):
	START = NUM*SPLIT
	END = min(START+SPLIT-1, TREESIZE)

	submitScript = '''
cd {CMSSW_BASE}src
eval `scramv1 runtime -sh`
cd {RUNDIR}
python Batch_Sinatra.py -r P5 {NUM} {START} {END}
#python Batch_Histogrammer.py {NUM} {START} {END}
rm -f core.*
'''.format(**locals())

	open('sh/job_{NUM}.sh'.format(**locals()), 'w').write(submitScript)
	bash.call('bsub -q 8nm -J ana_{NUM} < sh/job_{NUM}.sh'.format(**locals()), shell=True)
