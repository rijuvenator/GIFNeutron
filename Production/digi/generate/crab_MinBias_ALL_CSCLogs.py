from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

config.General.requestName = 'EventLog2'
config.General.workArea = 'crab'
config.General.transferOutputs = True
# transferLogs to true to get all cmsRun output
config.General.transferLogs = True

config.JobType.pluginName = 'PrivateMC'
config.JobType.psetName = 'MinBias_ALL_LOG_CSCDigi.py'
config.JobType.disableAutomaticOutputCollection = True
config.JobType.outputFiles = ['eventG4log.txt','mb_13TeV_mu_xs_crab.root']

config.Data.outputPrimaryDataset = 'MinBiasNeutron'
config.Data.splitting = 'EventBased'
config.Data.unitsPerJob = 1
NJOBS = 1000 # This is not a configuration parameter, but an auxiliary variable that we use in the next line.
config.Data.totalUnits = config.Data.unitsPerJob * NJOBS
config.Data.outLFNDirBase = '/store/user/%s/Neutron/' % (getUsernameFromSiteDB())
config.Data.publication = False
config.Data.outputDatasetTag = 'MinBiasNeutronLog'

config.Site.storageSite = 'T2_CH_CERN'
