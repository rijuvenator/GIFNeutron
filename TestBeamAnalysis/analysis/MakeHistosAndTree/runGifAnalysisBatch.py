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
	if not os.path.isdir(outDir):
		print "Directory", outDir, "does not exist; exiting."
		exit()
	dryrun = 'dryrun' in sys.argv

	# all the runs
	# Fill 5423
	#     runs = [283407,  283413, 283415, 283416] # skip 283414 since no data taken
	# Fill 5405
	#    runs = [283040, 283041, 283042, 283043]
	# Fill 5443
	#    runs = [283884, 283885]
	# Fill 5338
	#    runs = [281638, 281639, 281641] # skip 281640
	# Fill 5386
	#    runs = [282663]

	#runList = [283407, 283408, 283413, 283415, 283416, 283040, 283041, 283042, 
	#		283043, 283884, 283885, 281638, 281639, 281641, 282663]
	runList = [283416]

	for run in runList:
		# commented out since we only want trees (histos are chamber dependent)

		runFile = open('runFiles/'+str(run)+'.txt','r')
		parentFile = open('parentFiles/parent_'+str(run)+'.txt','r')

		ana_dataset = 'ana_'+str(run)+'.root'
		outPath = outDir+ana_dataset

		gif_py = open('GifAnalysis.py').read()
		# commented out since we only want trees (histos are chamber dependent)
		#if not 'noHistos' in sys.argv:
		#    gif_py += '\ndoHistos(process)\n'
		#if not 'noTree' in sys.argv:
		gif_py += '\ndoTree(process)\n'
		# commented out since we only want trees (histos are chamber dependent)
		#process.GIFHistos.chamberType = cms.untracked.string('%(chamber)s')
		gif_py += '''
process.source.fileNames  = cms.untracked.vstring(%(fn)s)
process.TFileService.fileName = cms.string(%(outPath)s)
''' % locals()

		open('py/submit_GifAnalysis'+str(run)+'.py','wt').write(gif_py)
		if dryrun:
			pass
		else: 
			# Submit via lxbatch
			cmd = 'cmsRun py/submit_GifAnalysis'+str(run)+'.py'
			outF = open('sh/subGifAnalysis'+str(run)+'.sh','w')
			outF.write('#!/bin/bash\n')
			outF.write('\n')
			outF.write('cd '+cmssw_base+'/src\n')
			outF.write('eval `scramv1 runtime -sh`\n')
			outF.write('cd '+cmssw_base+'/src/Gif/TestBeamAnalysis/analysis/MakeHistosAndTree\n')
			outF.write(cmd+'\n')
			outF.close()
			os.system('bsub -q 8nh -J gifAna'+str(run)+' < sh/subGifAnalysis'+str(run)+'.sh')

