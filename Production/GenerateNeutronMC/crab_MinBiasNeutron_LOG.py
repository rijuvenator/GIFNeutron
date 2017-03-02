from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

config.General.requestName = 'MinBiasNeutronSim_HP_Thermal'
config.General.workArea = 'crab'
config.General.transferOutputs = True
# transferLogs to true to get all cmsRun output
config.General.transferLogs = True

config.JobType.pluginName = 'PrivateMC'
config.JobType.psetName = 'MinBias_13TeV_cfi_GEN_SIM_ALL_HP_crab.py'
config.JobType.allowUndistributedCMSSW = True
config.JobType.disableAutomaticOutputCollection = True
config.JobType.outputFiles = ['eventG4log.txt','mb_13TeV_mu_ALL_hp_test.root']
config.JobType.maxMemoryMB = 8000

config.Data.outputPrimaryDataset = 'MinBiasNeutron_HP'
config.Data.splitting = 'EventBased'
config.Data.unitsPerJob = 1
NJOBS = 10  # This is not a configuration parameter, but an auxiliary variable that we use in the next line.
config.Data.totalUnits = config.Data.unitsPerJob * NJOBS
config.Data.outLFNDirBase = '/store/user/%s/Neutron/' % (getUsernameFromSiteDB())
config.Data.publication = False
config.Data.outputDatasetTag = 'MinBiasNeutronLog_HP_Thermal'

config.Site.storageSite = 'T2_CH_CERN'
