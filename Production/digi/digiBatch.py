''' Submission script for re-DIGI-ing GEN-SIM
'''
import sys,os
import commands
import fileinput


if __name__ == '__main__' and 'submit' in sys.argv:
	user = commands.getoutput('echo $USER')
	cmssw_base = commands.getoutput('echo $CMSSW_BASE')

	baseDir = cmssw_base+'/src/Gif/Production/digi/'

	# Warning, crab didn't finish some of the jobs in this directory (170228_114855)
	# cd into it and do
	# for i in {1..999}; do ls mb_13TeV_mu_all_hp_thermal_ON_${i}.root; done
	# to find out which ones didn't finish. Then make a text file list to loop on.
	inDir = '/store/user/cschnaib/Neutron/MinBiasNeutronHP/MinBiasNeutronHP_ThermalON/170228_114855/0000/'

	outDir = '/afs/cern.ch/work/'+user[0]+'/'+user+'/public/NeutronSim/HP_Thermal_ON_DIGI/'

	if not os.path.isdir(outDir):
		print "Directory", outDir, "does not exist; exiting."
		exit()
		
	dryrun = 'dryrun' in sys.argv

	nFiles = 1000
	#for i in range(1,nFiles+1):
	for i in [10]:
		#if i>1: break

		inFile = 'mb_13TeV_mu_gen_sim_hp_thermal_ON_'+str(i)+'.root'

		if i!=1000:
			inPath = inDir + inFile
		else:
			inPath = inDir1000 + inFile
		outFile = 'mb_13TeV_mu_all_hp_thermal_ON_'+str(i)+'.root'
		outPath = outDir + outFile

		gif_py = open('DIGI_TEST.py').read()
		gif_py += '''
process.source.fileNames  = cms.untracked.vstring('%(inPath)s')
process.FEVTDEBUGoutput.fileName = cms.untracked.string('%(outPath)s')
''' % locals()

		open('py/submit_reDIGI_'+str(i)+'.py','wt').write(gif_py)
		if dryrun:
			print 'Input file : ',inPath
			print 'Output file : ',outPath
			print 'cmsRun py/submit_reDIGI_'+str(i)+'.py'
			print
		else: 
			# Submit via lxbatch
			print i
			cmd = 'cmsRun py/submit_reDIGI_'+str(i)+'.py'
			outF = open('sh/sub_reDIGI_'+str(i)+'.sh','w')
			outF.write('#!/bin/bash\n')
			outF.write('\n')
			outF.write('cd '+cmssw_base+'/src\n')
			outF.write('eval `scramv1 runtime -sh`\n')
			outF.write('cd '+cmssw_base+'/src/Gif/Production/digi\n')
			outF.write(cmd+'\n')
			outF.close()
			os.system('bsub -q 8nh -J gifAna_'+str(i)+' < sh/sub_reDIGI_'+str(i)+'.sh')

