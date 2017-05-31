
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

config.General.requestName = 'ana_CSCDigis_P5'
config.General.workArea = 'crab'
config.General.transferOutputs = True
# transferLogs to true to get all cmsRun output
config.General.transferLogs = False

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'submit_GifAnalysis_crab.py'
config.JobType.maxMemoryMB = 8000

config.Data.inputDBS = 'global'
config.Data.inputDataset = '/SingleMuon/Run2016H-PromptReco-v2/AOD'
config.Data.useParent = True
config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = 50
config.Data.totalUnits = -1
config.Data.lumiMask = 'json/MuonPhys2016.json'
config.Data.outLFNDirBase = '/store/user/%s/Neutron/' % (getUsernameFromSiteDB())
config.Data.publication = False
config.Data.outputDatasetTag = 'ana_P5_Run2016H'
config.Data.ignoreLocality = True

config.Site.storageSite = 'T2_CH_CERN'
