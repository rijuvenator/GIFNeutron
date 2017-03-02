''' Submission script for running the GIF Analysis code
Historammer and N-Tupler
'''
import sys,os
import commands
import fileinput


if __name__ == '__main__' and 'submit' in sys.argv:
	user = commands.getoutput('echo $USER')
	cmssw_base = commands.getoutput('echo $CMSSW_BASE')

	baseDir = cmssw_base+'/src/Gif/Production/run/'
	inDir = '/store/user/cschnaib/Neutron/MinBiasNeutron/MinBiasNeutronSim/170220_165229/0000/'
	inDir1000 = '/store/user/cschnaib/Neutron/MinBiasNeutron/MinBiasNeutronSim/170220_165229/0001/'
	outDir = '/afs/cern.ch/work/'+user[0]+'/'+user+'/public/GIF/Neutron_20Feb/'

	if not os.path.isdir(outDir):
		print "Directory", outDir, "does not exist; exiting."
		exit()
		
	dryrun = 'dryrun' in sys.argv

	nFiles = 1000
	for i in range(1,nFiles+1):

		inFile = 'mb_13TeV_mu_ALL_xs_'+str(i)+'.root'

		if i!=1000:
			inPath = inDir + inFile
		else:
			inPath = inDir1000 + inFile
		outFile = 'ana_neutronMC_'+str(i)+'.root'
		outPath = outDir + outFile

		gif_py = open('GifAnalysis.py').read()
		gif_py += '''
process.source.fileNames  = cms.untracked.vstring('%(inPath)s')
process.TFileService.fileName = cms.string('%(outPath)s')
''' % locals()

		open('py/submit_GifAnalysis_'+str(i)+'.py','wt').write(gif_py)
		if dryrun:
			print 'Input file : ',inPath
			print 'Output file : ',outPath
			print 'cmsRun py/submit_GifAnalysis_'+str(i)+'.py'
			print
		else: 
			# Submit via lxbatch
			print i
			cmd = 'cmsRun py/submit_GifAnalysis_'+str(i)+'.py'
			outF = open('sh/subGifAnalysis_'+str(i)+'.sh','w')
			outF.write('#!/bin/bash\n')
			outF.write('\n')
			outF.write('cd '+cmssw_base+'/src\n')
			outF.write('eval `scramv1 runtime -sh`\n')
			outF.write('cd '+cmssw_base+'/src/Gif/Production/run\n')
			outF.write(cmd+'\n')
			outF.close()
			os.system('bsub -q 8nh -J gifAna_'+str(i)+' < sh/subGifAnalysis_'+str(i)+'.sh')

