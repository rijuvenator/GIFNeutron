''' Submission script for running the GIF Analysis code
Historammer and N-Tupler
'''
import sys,os
import commands

if __name__ == '__main__' and 'submit' in sys.argv:
	user = commands.getoutput('echo $USER')
	cmssw_base = commands.getoutput('echo $CMSSW_BASE')

	inDir = cmssw_base+'/src/Gif/NeutronSim/analysis/GenerateNeutronMC/crab/crab_MinBiasNeutronSim_test_1/results/'
	outDir = cmssw_base+'/src/Gif/NeutronSim/analysis/MakeHistosAndTree/output/'
	#outDir = '/afs/cern.ch/work/'+user[0]+'/'+user+'/public/Neutron/6Feb/'
	#plotsDir = cmssw_base+'/src/Gif/NeutronSim/analysis/MakeHistosAndTree/'

	dryrun = 'dryrun' in sys.argv

	gif_py = open('GifAnalysis.py').read()

	nFiles = 10
	#inputMCfile = 'mb_13TeV_mu_ALL_xs_test.root'
	for i in range(1,nFiles+1):
		inputMCfile = 'mb_13TeV_mu_ALL_xs_test_'+str(i)+'.root'
		inPath = inDir + inputMCfile

		outFile = 'test_crab_'+str(i)+'.root'
		outPath = outDir + outFile


		# customizations for a particular submission
		gif_py = open('GifAnalysis.py').read()
		gif_py += '''
doTree(process)
process.source.fileNames  = cms.untracked.vstring('file:%(inPath)s')
process.TFileService.fileName = cms.string('%(outPath)s')
''' % locals()

		open('submit_GifAnalysis.py','wt').write(gif_py)
		if dryrun:
			pass
		else: 
			cmd = 'cmsRun submit_GifAnalysis.py'
			print "\033[1mEXECUTING:\033[m", cmd
			os.system(cmd)

		if not dryrun:
			pass
			#os.system('rm submit_GifAnalysis.py submit_GifAnalysis.pyc')
