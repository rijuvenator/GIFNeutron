''' Submission script for running the GIF Analysis code
Historammer and N-Tupler
'''
import sys,os
import commands


run = 283416

if __name__ == '__main__' and 'submit' in sys.argv:
	user = commands.getoutput('echo $USER')
	#plotsDir = '/afs/cern.ch/work/'+user[0]+'/'+user+'/public/GIF/TestBeam5/'
	#plotsDir = '/afs/cern.ch/work/'+user[0]+'/'+user+'/public/GIF/test/'
	cmssw_base = commands.getoutput('echo $CMSSW_BASE')
	plotsDir = cmssw_base+'/src/Gif/TestBeamAnalysis/analysis/MakeHistosAndTree/'
	#outPath = '/afs/cern.ch/work/'+user[0]+'/'+user+'/public/GIF/23Jan/'
	outPath = plotsDir
	dryrun = 'dryrun' in sys.argv

	gif_py = open('GifAnalysis.py').read()

	# Fill 5423
	runs5423 = [283407, 283408,  283413, 283415, 283416] # skip 283414 since no data taken
	# Fill 5405
	runs5405 = [283041, 283042, 283043]# skip 283040 not in good run list
	# Fill 5443
	runs5443 = [283884, 283885]
	# Fill 5338
	runs5338 = [281638, 281639,  281641] # skip 281640 not in good run list
	# Fill 5386 (low-PU run)
	runs5386 = [282663]
	runList = runs5423 + runs5405 + runs5443 + runs5338 + runs5386

	for run in runList:
		run_fn = open('runFiles/'+str(run)+'.txt')
		for i,line in enumerate(run_fn):
			if i>0: break
			runFile = line.strip('\n').strip(',').strip('\'')
			parent_fn = open('parentFiles/parent_'+str(run)+'_'+str(i)+'.txt').read().strip('\n')
			outFile = 'test_'+str(run)+'_'+str(i)+'.root'
			output = outPath + outFile

			if run==282663:
				lumiList = plotsDir+'json/MuonPhys2016_lowPU.json'
			else:
				lumiList = plotsDir+'json/MuonPhys2016.json'

			# customizations for a particular submission
			gif_py = open('GifAnalysis.py').read()
			gif_py += '''
doTree(process)
process.source.lumisToProcess = LumiList.LumiList(filename = '%(lumiList)s').getVLuminosityBlockRange()
process.GlobalTag.globaltag = '80X_dataRun2_Prompt_v14'
process.source.fileNames  = cms.untracked.vstring('%(runFile)s')
process.source.secondaryFileNames  = cms.untracked.vstring(%(parent_fn)s)
process.TFileService.fileName = cms.string('%(output)s')
		''' % locals()

			open('submit_GifAnalysis.py','wt').write(gif_py)
			if dryrun:
				print 'AOD file : ',runFile
				print 'RAW files : ',parent_fn
				print 'Lumi List : ',lumiList
				print 'Output : ',outPath
				print 'cmsRun submit_GifAnalysis.py'
				print
			else: 
				cmd = 'cmsRun submit_GifAnalysis.py'
				print "\033[1mEXECUTING:\033[m", cmd
				os.system(cmd)

			if not dryrun:
				pass
				#os.system('rm submit_GifAnalysis.py submit_GifAnalysis.pyc')
