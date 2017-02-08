''' Submission script for running the GIF Analysis code
Historammer and N-Tupler
'''
import sys,os
import commands

if __name__ == '__main__' and 'submit' in sys.argv:
	user = commands.getoutput('echo $USER')
	cmssw_base = commands.getoutput('echo $CMSSW_BASE')
	plotsDir = cmssw_base+'/src/Gif/Production/run/'
	dryrun = 'dryrun' in sys.argv

	gif_py = open('GifAnalysis.py').read()

	#lumi_mask = plotsDir+'json/MuonPhys2016_lowPU.json'
	#lumi_mask = plotsDir+'json/MuonPhys2016.json'

	# customizations for a particular submission
	gif_py = open('GifAnalysis.py').read()
	gif_py += '''
doTree(process)
process.GlobalTag.globaltag = '80X_dataRun2_Prompt_v14'
process.TFileService.fileName = cms.string('ana_P5_Run2016H.root')
'''

	open('submit_GifAnalysis_crab.py','wt').write(gif_py)

	crab_cfg = '''
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

config.General.requestName = 'tree_1'
config.General.workArea = 'crab'
config.General.transferOutputs = True
# transferLogs to true to get all cmsRun output
config.General.transferLogs = False

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'submit_GifAnalysis_crab.py'

config.Data.inputDBS = 'global'
config.Data.inputDataset = '/SingleMuon/Run2016H-PromptReco-v2/AOD'
config.Data.useParent = True
config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = 200
config.Data.totalUnits = -1
config.Data.lumiMask = 'json/MuonPhys2016.json'
config.Data.outLFNDirBase = '/store/user/%s/Neutron/' % (getUsernameFromSiteDB())
config.Data.publication = False
config.Data.outputDatasetTag = 'ana_P5_Run2016H'
config.Data.ignoreLocality = True

config.Site.storageSite = 'T2_CH_CERN'
'''
	
	open('crabConfig.py','wt').write(crab_cfg)

	if dryrun:
		pass
	else: 
		cmd = 'crab submit crabConfig.py'
		print "\033[1mEXECUTING:\033[m", cmd
		os.system(cmd)

	if not dryrun:
		pass
		#os.system('rm submit_GifAnalysis.py submit_GifAnalysis.pyc')
