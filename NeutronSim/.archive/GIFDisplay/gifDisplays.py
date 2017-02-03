import sys,os
import FWCore.ParameterSet.Config as cms

process = cms.Process('GifDisplay')

process.load('Configuration/Geometry/GeometryIdeal2015Reco_cff')
#process.load('Configuration/Geometry/IdealGeometry_cff')
#process.load('Configuration/StandardSequences/Geometry_cff')
process.load('Configuration/StandardSequences/MagneticField_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.load('Configuration/StandardSequences/RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('RecoMuon.MuonSeedGenerator.standAloneMuonSeeds_cff')
#process.load('RecoMuon.GlobalMuonProducer.globalMuons_cff')

process.GlobalTag.globaltag = '74X_dataRun2_Prompt_v0'

process.options = cms.untracked.PSet(
    SkipEvent = cms.untracked.vstring('LogicError','ProductNotFound')
)

process.MessageLogger = cms.Service('MessageLogger',
    destinations   = cms.untracked.vstring('myDebugOutputFile.txt'),
    debugModules = cms.untracked.vstring('*'),
    message = cms.untracked.PSet(
        threshold = cms.untracked.vstring('DEBUG')
    )
)

process.source = cms.Source('PoolSource',
    fileNames = cms.untracked.vstring('file:me21_test27_oct30.root')
)

process.maxEvents = cms.untracked.PSet(
    #input = cms.untracked.int32(100)
    input = cms.untracked.int32(-1)
)

process.load('FWCore.MessageLogger.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

process.GifDisplay = cms.EDAnalyzer('GifDisplay',
    # Output file name
    rootFileName      = cms.untracked.string('doesnotexist.root'),
    # Input Tags
    stripDigiTag      = cms.InputTag('muonCSCDigis', 'MuonCSCStripDigi'),
    wireDigiTag       = cms.InputTag('muonCSCDigis', 'MuonCSCWireDigi'),
    comparatorDigiTag = cms.InputTag('muonCSCDigis',  'MuonCSCComparatorDigi'),
    cscRecHitTag      = cms.InputTag('csc2DRecHits', ''),
    alctDigiTag       = cms.InputTag('muonCSCDigis', 'MuonCSCALCTDigi'),
    clctDigiTag       = cms.InputTag('muonCSCDigis', 'MuonCSCCLCTDigi'),
    corrlctDigiTag    = cms.InputTag('muonCSCDigis', 'MuonCSCCorrelatedLCTDigi'),
    #directory for eventdisplay
    eventDisplayDir = cms.untracked.string('does/not/exist'),
    # Event list file
    eventListFile = cms.untracked.string('doesnotexist.txt'),
    #chamber type: ME1/1-11, ME2/1-21
    chamberType = cms.untracked.string('CSC'),
)

process.p = cms.Path(process.muonCSCDigis * process.csc2DRecHits * process.GifDisplay)

