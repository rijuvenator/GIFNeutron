# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: MinBias_13TeV_cfi -s GEN,SIM --customise SimG4Core/Application/NeutronBGforMuonsXS_cff.customise --pileup=NoPileUp --geometry DB --conditions auto:run2_mc --eventcontent=FEVTDEBUG --datatier GEN-SIM --dirout=./ -n 250 --fileout file:mb_13TeV_mu_xs.root --beamspot Realistic50ns13TeVCollision --mc --python_filename=MinBias_13TeV_cfi_GEN_SIM_XS.py --no_exec --geometry Extended2015,Extended2015Reco --magField 38T_PostLS1
import FWCore.ParameterSet.Config as cms

process = cms.Process('RECO')

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtended2015Reco_cff')
process.load('Configuration.Geometry.GeometryExtended2015_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_PostLS1_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic50ns13TeVCollision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.SimIdeal_cff')
process.load('Configuration.StandardSequences.Digi_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.DigiToRaw_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1000)
)

# Input source
process.source = cms.Source("EmptySource")

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('MinBias_13TeV_cfi nevts:250'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.FEVTDEBUGoutput = cms.OutputModule("PoolOutputModule",
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('generation_step')
    ),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN-SIM'),
        filterName = cms.untracked.string('')
    ),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    #fileName = cms.untracked.string('./file:mb_13TeV_mu_xs.root'),
    fileName = cms.untracked.string('mb_13TeV_mu_xs_crab.root'),
    outputCommands = process.FEVTDEBUGEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

# Additional output definition

# Other statements
process.genstepfilter.triggerConditions=cms.vstring("generation_step")
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')

process.generator = cms.EDFilter("Pythia6GeneratorFilter",
    PythiaParameters = cms.PSet(
        parameterSets = cms.vstring('pythiaUESettings', 
            'processParameters'),
        processParameters = cms.vstring('MSEL=0         ! User defined processes', 
            'MSUB(11)=1     ! Min bias process', 
            'MSUB(12)=1     ! Min bias process', 
            'MSUB(13)=1     ! Min bias process', 
            'MSUB(28)=1     ! Min bias process', 
            'MSUB(53)=1     ! Min bias process', 
            'MSUB(68)=1     ! Min bias process', 
            'MSUB(92)=1     ! Min bias process, single diffractive', 
            'MSUB(93)=1     ! Min bias process, single diffractive', 
            'MSUB(94)=1     ! Min bias process, double diffractive', 
            'MSUB(95)=1     ! Min bias process'),
        pythiaUESettings = cms.vstring('MSTU(21)=1     ! Check on possible errors during program execution', 
            'MSTJ(22)=2     ! Decay those unstable particles', 
            'PARJ(71)=10 .  ! for which ctau  10 mm', 
            'MSTP(33)=0     ! no K factors in hard cross sections', 
            'MSTP(2)=1      ! which order running alphaS', 
            'MSTP(51)=10042 ! structure function chosen (external PDF CTEQ6L1)', 
            'MSTP(52)=2     ! work with LHAPDF', 
            'PARP(82)=1.921 ! pt cutoff for multiparton interactions', 
            'PARP(89)=1800. ! sqrts for which PARP82 is set', 
            'PARP(90)=0.227 ! Multiple interactions: rescaling power', 
            'MSTP(95)=6     ! CR (color reconnection parameters)', 
            'PARP(77)=1.016 ! CR', 
            'PARP(78)=0.538 ! CR', 
            'PARP(80)=0.1   ! Prob. colored parton from BBR', 
            'PARP(83)=0.356 ! Multiple interactions: matter distribution parameter', 
            'PARP(84)=0.651 ! Multiple interactions: matter distribution parameter', 
            'PARP(62)=1.025 ! ISR cutoff', 
            'MSTP(91)=1     ! Gaussian primordial kT', 
            'PARP(93)=10.0  ! primordial kT-max', 
            'MSTP(81)=21    ! multiple parton interactions 1 is Pythia default', 
            'MSTP(82)=4     ! Defines the multi-parton model')
    ),
    comEnergy = cms.double(13000.0),
    filterEfficiency = cms.untracked.double(1.0),
    maxEventsToPrint = cms.untracked.int32(0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    pythiaPylistVerbosity = cms.untracked.int32(0)
)


# Path and EndPath definitions
process.generation_step = cms.Path(process.pgen)
process.simulation_step = cms.Path(process.psim)
process.digitisation_step = cms.Path(process.pdigi)
process.L1simulation_step = cms.Path(process.SimL1Emulator)
process.digi2raw_step = cms.Path(process.DigiToRaw)
process.raw2digi_step = cms.Path(process.RawToDigi)
process.L1Reco_step = cms.Path(process.L1Reco)
process.reconstruction_step = cms.Path(process.reconstruction)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.FEVTDEBUGoutput_step = cms.EndPath(process.FEVTDEBUGoutput)

# Schedule definition
process.schedule = cms.Schedule(
		process.generation_step,
		process.genfiltersummary_step,
		process.simulation_step,
		process.digitisation_step,
		process.L1simulation_step,
		process.digi2raw_step,
		process.raw2digi_step,
		process.L1Reco_step,
		process.reconstruction_step,
		process.endjob_step,
		process.FEVTDEBUGoutput_step)
# filter all path with the production filter sequence
for path in process.paths:
	getattr(process,path)._seq = process.generator * getattr(process,path)._seq 

# customisation of the process.

# Automatic addition of the customisation function from SimG4Core.Application.NeutronBGforMuonsXS_cff
from SimG4Core.Application.NeutronBGforMuonsXS_cff import customise 

#call to customisation function customise imported from SimG4Core.Application.NeutronBGforMuonsXS_cff
process = customise(process)

# customize to extend tracking time
# process.load('SimG4Core.Application.NeutronBGforMuonsXS_cff')
process.common_maximum_time.MaxTrackTime = cms.double(10000000000.0)
process.g4SimHits.StackingAction.MaxTrackTime = cms.double(10000000000.0)
process.g4SimHits.SteppingAction.MaxTrackTime = cms.double(10000000000.0)
# default eta range [-7,7] does not include fully TAS (in rotating shielding)
process.g4SimHits.Generator.MinEtaCut = cms.double(-8.0)
process.g4SimHits.Generator.MaxEtaCut = cms.double(8.0)


# Track 1 neutron background hit
#process.g4SimHits.SteppingVerbosity = cms.int32(2)
#process.g4SimHits.StepVerboseThreshold = cms.double(0.0)
#process.g4SimHits.VerboseEvents = cms.vint32()
#process.g4SimHits.VerboseTracks = cms.vint32()

process.MessageLogger = cms.Service('MessageLogger',
		destinations = cms.untracked.vstring('eventG4log','cout'),
		categories = cms.untracked.vstring('CSCDigitizer','CSCGasCollisions'),
		eventG4log = cms.untracked.PSet(
			extension=cms.untracked.string('.txt'),
			threshold=cms.untracked.string('DEBUG'),
			debugModules=cms.untracked.vstring('CSCDigitizer','CSCGasCollisions'),
			default=cms.untracked.PSet(limit = cms.untracked.int32(0)),
			CSCDigitizer=cms.untracked.PSet(limit = cms.untracked.int32(100000000)),
			CSCGasCollisions=cms.untracked.PSet(limit = cms.untracked.int32(100000000))
		),
		cout = cms.untracked.PSet(
			threshold=cms.untracked.string('DEBUG'),
			debugModules=cms.untracked.vstring('CSCDigitizer','CSCGasCollisions'),
			default=cms.untracked.PSet(limit = cms.untracked.int32(0)),
			CSCDigitizer=cms.untracked.PSet(limit = cms.untracked.int32(1000000000)),
			CSCGasCollisions=cms.untracked.PSet(limit = cms.untracked.int32(100000000))
		)
)

# End of customisation functions

