''' Submission script for running the GIF Analysis code
N-Tupler
ASSUMES INPUT EDM IS GEN-SIM DON'T USE OTHERWISE
'''
import sys,os
import commands
import fileinput


if __name__ == '__main__' and 'submit' in sys.argv:
	user = commands.getoutput('echo $USER')
	cmssw_base = commands.getoutput('echo $CMSSW_BASE')

	baseDir = cmssw_base+'/src/Gif/Production/run/'
	#inDir = '/store/user/cschnaib/Neutron/MinBiasNeutron/MinBiasNeutronSim/170220_165229/0000/' # DOES NOT EXIST
	#inDir1000 = '/store/user/cschnaib/Neutron/MinBiasNeutron/MinBiasNeutronSim/170220_165229/0001/' # DOES NOT EXIST

	# 300 'unbiased' events
	#inDir0 = '/store/user/cschnaib/Neutron/MinBiasNeutron/MinBiasNeutronLog/160928_120829/0000/' # 300 'unbiased' events
	#outDir = '/afs/cern.ch/work/'+user[0]+'/'+user+'/public/NeutronSim/trees_300/' # 300 'unbiased' events

	# 3124/4000 finished HP Thermal ON events
	#inDir0 = '/store/user/cschnaib/Neutron/MinBiasNeutronHP/MinBiasNeutronHP_ThermalON/170228_114855/0000/' # GEN-SIM HP with thermal scattering ON
	#inDir1 = '/store/user/cschnaib/Neutron/MinBiasNeutronHP/MinBiasNeutronHP_ThermalON/170228_114855/0001/' # GEN-SIM HP with thermal scattering ON
	#inDir2 = '/store/user/cschnaib/Neutron/MinBiasNeutronHP/MinBiasNeutronHP_ThermalON/170228_114855/0002/' # GEN-SIM HP with thermal scattering ON
	#inDir3 = '/store/user/cschnaib/Neutron/MinBiasNeutronHP/MinBiasNeutronHP_ThermalON/170228_114855/0003/' # GEN-SIM HP with thermal scattering ON
	#inDir4 = '/store/user/cschnaib/Neutron/MinBiasNeutronHP/MinBiasNeutronHP_ThermalON/170228_114855/0004/' # GEN-SIM HP with thermal scattering ON
	#outDir = '/afs/cern.ch/work/'+user[0]+'/'+user+'/public/NeutronSim/HP_Thermal_ON/ana/' # GEN-SIM HP with thermal scattering ON

	# 999/1000 finished HP Thermal ON events
	inDir0 = '/store/user/cschnaib/Neutron/MinBiasNeutronHP/MinBiasNeutronHP_ThermalON/170305_110232/0000/' # GEN-SIM HP with thermal scattering ON
	inDir1 = '/store/user/cschnaib/Neutron/MinBiasNeutronHP/MinBiasNeutronHP_ThermalON/170305_110232/0001/' # GEN-SIM HP with thermal scattering ON
	outDir = '/afs/cern.ch/work/'+user[0]+'/'+user+'/public/NeutronSim/HP_Thermal_ON/ana2/' # GEN-SIM HP with thermal scattering ON

	if not os.path.isdir(outDir):
		print "Directory", outDir, "does not exist; exiting."
		exit()
		
	dryrun = 'dryrun' in sys.argv
	inputFile = open('finishedFiles_999')
	for l,line in enumerate(inputFile):
		if l==0: continue
		i = l+1
		job = line.strip('\n')
		#job = str(line)
		jobN = int(job)
		inFile = 'mb_13TeV_mu_gen_sim_hp_thermal_ON_'+job+'.root'
		if jobN<1000:
			inPath = inDir0 + inFile
		elif jobN<2000:
			inPath = inDir1 + inFile
		elif jobN<3000:
			inPath = inDir2 + inFile
		elif jobN<4000:
			inPath = inDir3 + inFile
		else:
			inPath = inDir4 + inFile

		outFile = 'ana_neutronMC_HPThermalON_'+job+'.root'
		outPath = outDir + outFile

		gif_py = open('GifAnalysis.py').read()
		gif_py += '''
process.source.fileNames  = cms.untracked.vstring('%(inPath)s')
process.TFileService.fileName = cms.string('%(outPath)s')
''' % locals()

		open('py/submit_GifAnalysis_'+job+'.py','wt').write(gif_py)
		cmd = 'cmsRun py/submit_GifAnalysis_'+job+'.py'
		if dryrun:
			print 'Input file : ',inPath
			print 'Output file : ',outPath
			print cmd
			print
		else: 
			# Submit via lxbatch
			print i
			outF = open('sh/subGifAnalysis_'+job+'.sh','w')
			outF.write('#!/bin/bash\n')
			outF.write('\n')
			outF.write('cd '+cmssw_base+'/src\n')
			outF.write('eval `scramv1 runtime -sh`\n')
			outF.write('cd '+cmssw_base+'/src/Gif/Production/run\n')
			outF.write(cmd+'\n')
			outF.close()
			os.system('bsub -q 8nh -J gifAna_'+job+' < sh/subGifAnalysis_'+job+'.sh')
			#os.system(cmd) # run locally

