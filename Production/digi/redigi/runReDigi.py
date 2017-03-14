import subprocess as bash
import argparse

#### CONFIGURATION ####
#
# Note that file.root will be replaced with file_number.root in sequence if nfiles > 0
#
parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=43))
parser.add_argument('-s' , '--submit'    , action='store_true'            , help='submit immediately'         )
parser.add_argument('-b' , '--batch'     , action='store_true'            , help='submit to lxbatch'          )
parser.add_argument('-rm', '--cleanup'   , action='store_true'            , help='remove .py and .sh files'   )
parser.add_argument('-c' , '--config'    , default='GifAnalysis.py'       , help='cmsRun configuration script')
parser.add_argument('-n' , '--nfiles'    , default=0, type=int            , help='number of files in this set')
parser.add_argument('-id', '--inputDir'  , default=''                     , help='input directory for config' )
parser.add_argument('-if', '--inputFile' , default='input.root'           , help='input file pattern'         )
parser.add_argument('-od', '--outputDir' , default='output/'              , help='output directory'           )
parser.add_argument('-of', '--outputFile', default='ana.root'             , help='output file pattern'        )
parser.add_argument('-nn', '--nbounds'   , default=None, type=int, nargs=2, help='file number bounds'         )
args = parser.parse_args()

SUBMIT       = args.submit
BATCH        = args.batch
CLEANUP      = args.cleanup
CONFIGSCRIPT = args.config
NFILES       = args.nfiles
INDIR        = args.inputDir
INFILE_P     = args.inputFile  # for "pattern"
OUTDIR       = args.outputDir
OUTFILE_P    = args.outputFile # for "pattern"
if args.nbounds is None:
	if NFILES == 0:
		NBOUNDS = (1, 2)
	else:
		NBOUNDS = (1, NFILES+1)
else:
	NBOUNDS = (args.nbounds[0], args.nbounds[1]+1)
	if NBOUNDS[1] - NBOUNDS[0] != NFILES:
		print 'nFiles and nBounds don\'t seem to match; did you intend this?'
		while True:
			response = raw_input('Type YES or NO: ')
			if response in ['YES', 'NO']: break
		if response == 'YES':
			pass
		elif response == 'NO':
			exit()

#### RUN TREE MAKER ####

# Get useful environment variables
#USER       = bash.check_output('echo $USER'      , shell=True).rstrip('\n')
CMSSW_BASE = bash.check_output('echo $CMSSW_BASE', shell=True).rstrip('\n')+'/'
RUNDIR     = CMSSW_BASE + 'src/Gif/Production/digi/redigi/'

# ensure output directories exist
if SUBMIT: bash.call('mkdir -p '+OUTDIR, shell=True)

# make the appropriate file names with _number if NFILES > 0
# make py/ and sh/ folders to hold multiple .py and .sh files
if NFILES > 0:
	bash.call('mkdir -p py sh'  , shell=True)
	INFILE    = INFILE_P .replace('.root', '_{NUM}.root')
	OUTFILE   = OUTFILE_P.replace('.root', '_{NUM}.root')
	CONFIG_PY = 'py/config_{NUM}.py'
	SUBMIT_SH = 'sh/submit_{NUM}.sh'
	CSCDIGIL  = 'cscDigiLog_{NUM}'
else:
	INFILE    = INFILE_P
	OUTFILE   = OUTFILE_P
	CONFIG_PY = 'config.py'
	SUBMIT_SH = 'submit.sh'
	CSCDIGIL  = 'cscDigiLog'
	NFILES    = 1

# color codes
BOLD    = '\033[1m'
RED     = '\033[31m'
GREEN   = '\033[32m'
BLUE    = '\033[34m'
PURPLE  = '\033[35m'
CYAN    = '\033[36m'
END     = '\033[m'

# loop over the files and submit
for i in range(NBOUNDS[0], NBOUNDS[1]):
	# make the literal paths, replacing any NUM fields
	# format will not replace a field it does not find, so this is safe
	INPATH     = INDIR  + INFILE .format(NUM=i)
	OUTPATH    = OUTDIR + OUTFILE.format(NUM=i)
	CONFIGPATH = CONFIG_PY       .format(NUM=i)
	SUBMITPATH = SUBMIT_SH       .format(NUM=i)
	CSCDIGILOG = CSCDIGIL        .format(NUM=i)
	
	# write the cmsRun configuration script
	configScript = open(CONFIGSCRIPT).read()
	configScript = configScript.replace('cscDigiLog',CSCDIGILOG)
	configScript += '''
process.source.fileNames = cms.untracked.vstring('{INPATH}')
process.FEVTDEBUGoutput.fileName = cms.untracked.string('{OUTPATH}')
'''.format(**locals())
	
	open(CONFIGPATH, 'w').write(configScript)

	# write the shell script that actually submits the job
	submitScript = '''
#!/bin/bash
cd {CMSSW_BASE}src
eval `scramv1 runtime -sh`
cd {RUNDIR}
cmsRun {CONFIGPATH}
rm -f core.*
mv {CSCDIGILOG}.txt {OUTDIR}
'''.format(**locals())

	open(SUBMITPATH, 'w').write(submitScript)

	# submit, either locally or on lxbatch
	if SUBMIT and not BATCH:
		print ''
		print BOLD, 'Input  File: ', END, RED,    INPATH    , END
		print BOLD, 'Output File: ', END, GREEN,  OUTPATH   , END
		print BOLD, 'Shell Script:', END, PURPLE, SUBMITPATH, END,
		print '(cmsRun {0})'.format(CYAN+CONFIGPATH+END)
		print ''
		bash.call('bash {SUBMITPATH}'.format(**locals()), shell=True)
	elif SUBMIT and BATCH:
		print i
		bash.call('bsub -q 8nh -J ana_{NUM} < {SUBMITPATH}'.format(NUM=i,**locals()), shell=True)
	
	if CLEANUP:
		bash.call('rm {SUBMITPATH} {CONFIGPATH}'.format(**locals()), shell=True)
