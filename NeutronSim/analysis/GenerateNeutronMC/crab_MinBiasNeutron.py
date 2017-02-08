from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

config.General.requestName = 'MinBiasNeutronSim_100K'
config.General.workArea = 'crab'
config.General.transferOutputs = True
# transferLogs to true to get all cmsRun output
config.General.transferLogs = True

config.JobType.pluginName = 'PrivateMC'
config.JobType.psetName = 'MinBias_13TeV_cfi_GEN_SIM_ALL_XS_crab.py'
config.JobType.allowUndistributedCMSSW = True

config.Data.outputPrimaryDataset = 'MinBiasNeutron'
config.Data.splitting = 'EventBased'
config.Data.unitsPerJob = 100
NJOBS = 1000  # This is not a configuration parameter, but an auxiliary variable that we use in the next line.
config.Data.totalUnits = config.Data.unitsPerJob * NJOBS
config.Data.outLFNDirBase = '/store/user/%s/Neutron/' % (getUsernameFromSiteDB())
config.Data.publication = False
config.Data.outputDatasetTag = 'MinBiasNeutronSim'

config.Site.storageSite = 'T2_CH_CERN'
