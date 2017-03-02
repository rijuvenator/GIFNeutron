# Test Beam Analysis

## Documentation

### analysis

#### Active
  - MakeHistosAndTree
    - cmsRun config files for running MakeSimpleGIFTree
  - EventDisplay
    - replacement event display code
  - DQM
    - quick exploratory plots
  - Everything else
    - see README

### current_scraper
  - Scripts for getting current measurement data at GIF

### database_scraper
  - Scripts for getting tables of CSC GIF test beam measurements

### python
  - Plotter class
  - Measurement class and dictionary
  - Tools
  - Primitives
  - Auxiliary

### include, plugins, src
  - CMSSW directory structure for histogram and tree making plugins and display plugins

### GenerateNeutronMC
	- Directory meant to include all relevant CMSSW & CRAB configruation files to generate neutron-enhanced MC
	- CMSSW configuration scripts are auto-generated with cmsDriver
		- For full GEN-SIM-DIGI-RECO execute : 
			cmsDriver.py MinBias_13TeV_cfi -s GEN,SIM,DIGI,L1,DIGI2RAW,RAW2DIGI,L1Reco,RECO --customise SimG4Core/Application/NeutronBGforMuonsXS_cff.customise --pileup=NoPileUp --geometry DB --conditions auto:run2_mc --eventcontent=FEVTDEBUG --datatier GEN-SIM --dirout=./ -n 50 --fileout file:mb_13TeV_mu_ALL_xs_test.root --beamspot Realistic50ns13TeVCollision --mc --python_filename=MinBias_13TeV_cfi_GEN_SIM_ALL_XS_test.py --no_exec --geometry Extended2015,Extended2015Reco --magField 38T_PostLS1
		- For only GEN-SIM execute : 
			cmsDriver.py MinBias_13TeV_cfi -s GEN,SIM --customise SimG4Core/Application/NeutronBGforMuonsXS_cff.customise --pileup=NoPileUp --geometry DB --conditions auto:run2_mc --eventcontent=FEVTDEBUG --datatier GEN-SIM --dirout=./ -n 250 --fileout file:mb_13TeV_mu_xs.root --beamspot Realistic50ns13TeVCollision --mc --python_filename=MinBias_13TeV_cfi_GEN_SIM_XS.py --no_exec --geometry Extended2015,Extended2015Reco --magField 38T_PostLS1
		- We add extra customizations to extend the generation eta range, increase tracking time, and decrease tracking energy thresholds
			# customize to extend tracking time
			# process.load('SimG4Core.Application.NeutronBGforMuonsXS_cff')
			process.common_maximum_time.MaxTrackTime = cms.double(10000000000.0)
			process.g4SimHits.StackingAction.MaxTrackTime = cms.double(10000000000.0)
			process.g4SimHits.SteppingAction.MaxTrackTime = cms.double(10000000000.0)
			# default eta range [-7,7] does not include fully TAS (in rotating shielding)
			process.g4SimHits.Generator.MinEtaCut = cms.double(-8.0)
			process.g4SimHits.Generator.MaxEtaCut = cms.double(8.0)
		- For Geant4 event logging add these lines : 
			# Track 1 neutron background hit
			process.g4SimHits.SteppingVerbosity = cms.int32(2)
			process.g4SimHits.StepVerboseThreshold = cms.double(0.0)
			process.g4SimHits.VerboseEvents = cms.vint32()
			process.g4SimHits.VerboseTracks = cms.vint32()
			process.MessageLogger.destinations = cms.untracked.vstring('eventG4log.txt')
	- To run these execute : 
		- cmsRun [output_cfg].py # where [output_cfg].py is created by previous step
	- For CRAB, there are two files :
		- crab_MinBiasNeutron.py : Submits jobs to CRAB to generate EDM output
		- crab_MinBiasNeutron_LOG.py : Submits jobs to CRAB to generate EDM output AND Geant4 logging
