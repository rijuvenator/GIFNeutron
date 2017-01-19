import FWCore.ParameterSet.Config as cms

process = cms.Process('GIFAnalysis')

#process.load('Configuration/Geometry/GeometryIdeal2015Reco_cff')
#process.load('Configuration/Geometry/IdealGeometry_cff')
#process.load('Configuration/StandardSequences/Geometry_cff')
process.load('Configuration/StandardSequences/GeometryDB_cff')
process.load('Configuration/StandardSequences/MagneticField_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.load('Configuration/StandardSequences/RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
#process.load('RecoMuon.MuonSeedGenerator.standAloneMuonSeeds_cff')
#process.load('RecoMuon.GlobalMuonProducer.globalMuons_cff')

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))
process.GlobalTag.globaltag = '74X_dataRun2_Prompt_v0'

process.load('FWCore.MessageLogger.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
#process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

process.TFileService = cms.Service('TFileService', fileName=cms.string('gif_histos.root'))

