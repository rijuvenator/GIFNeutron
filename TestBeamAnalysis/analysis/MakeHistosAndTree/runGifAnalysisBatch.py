''' Submission script for running the GIF Analysis code
Historammer and N-Tupler
'''
import sys,os
import commands
import fileinput


if __name__ == '__main__' and 'submit' in sys.argv:
	user = commands.getoutput('echo $USER')
	cmssw_base = commands.getoutput('echo $CMSSW_BASE')
	outDir = '/afs/cern.ch/work/'+user[0]+'/'+user+'/public/GIF/23Jan/'
	baseDir = cmssw_base+'/src/Gif/TestBeamAnalysis/analysis/MakeHistosAndTree/'
	if not os.path.isdir(outDir):
		print "Directory", outDir, "does not exist; exiting."
		exit()
	dryrun = 'dryrun' in sys.argv

	# Fill 5423
	runs5423 = [283407, 283408,  283413, 283415, 283416] # skip 283414 since no data taken #283408, already done
	# Fill 5405
	runs5405 = [283040, 283041, 283042, 283043]
	# Fill 5443
	runs5443 = [283884, 283885]
	# Fill 5338
	runs5338 = [281638, 281639,  281641] # skip 281640,
	# Fill 5386
	runs5386 = [282663]
	#runList = runs5423 + runs5405 + runs5443 + runs5338 + runs5386
	runList = [282663]

	for run in runList:
		if run==282663:
			lumiList = baseDir+'json/MuonPhys2016_lowPU.json'
		else:
			lumiList = baseDir+'json/MuonPhys2016.json'
		runFileList = open('runFiles/'+str(run)+'.txt','r')
		for l,line in enumerate(runFileList):
			runFile = line.strip('\n').strip(',')
			parentFiles = open('parentFiles/parent_'+str(run)+'_'+str(l)+'.txt').read().strip('\n')

			ana_dataset = 'ana_'+str(run)+'_'+str(l)+'.root'
			outPath = outDir+ana_dataset

			gif_py = open('GifAnalysis.py').read()
			gif_py += '''
doTree(process)
process.source.lumisToProcess = LumiList.LumiList(filename = '%(lumiList)s').getVLuminosityBlockRange()
process.GlobalTag.globaltag = '80X_dataRun2_Prompt_v14'
process.source.fileNames  = cms.untracked.vstring(%(runFile)s)
process.source.secondaryFileNames  = cms.untracked.vstring(%(parentFiles)s)
process.TFileService.fileName = cms.string(%(outPath)s)
''' % locals()

			open('py/submit_GifAnalysis_'+str(run)+'_'+str(l)+'.py','wt').write(gif_py)
			if dryrun:
				print run,i
				print runFile
				print parentFiles
				print lumiList
				print outPath
			else: 
				# Submit via lxbatch
				print run,i
				cmd = 'cmsRun py/submit_GifAnalysis_'+str(run)+'_'+str(i)+'.py'
				outF = open('sh/subGifAnalysis_'+str(run)+'_'+str(i)+'.sh','w')
				outF.write('#!/bin/bash\n')
				outF.write('\n')
				outF.write('cd '+cmssw_base+'/src\n')
				outF.write('eval `scramv1 runtime -sh`\n')
				outF.write('cd '+cmssw_base+'/src/Gif/TestBeamAnalysis/analysis/MakeHistosAndTree\n')
				outF.write(cmd+'\n')
				outF.close()
				os.system('bsub -q 8nh -J gifAna_'+str(run)+'_'+str(i)+' < sh/subGifAnalysis'+str(run)+'_'+str(i)+'.sh')

