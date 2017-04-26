import FWCore.ParameterSet.Config as cms
from Gif.Production.GIFTestBeamAnalysis_cfg import process

process.source = cms.Source('PoolSource', 
    fileNames = cms.untracked.vstring( 
        'file:doesnotexist.root',  
    ) 
)

process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

process.options = cms.untracked.PSet(
    SkipEvent = cms.untracked.vstring('LogicError','ProductNotFound','PluginNotFound')
)
process.maxEvents.input = -1
process.MessageLogger.cerr.FwkReport.reportEvery = 10000

#process.p = cms.Path(process.muonCSCDigis * process.csc2DRecHits * process.cscSegments)

"""Customise digi/reco geometry to use unganged ME1/a channels"""
process.CSCGeometryESModule.useGangedStripsInME1a = False
process.idealForDigiCSCGeometry.useGangedStripsInME1a = False

process.GIFTree = cms.EDAnalyzer('MakeOnlySimTree',
						# CSC
						#rawDataTag = cms.InputTag("rawDataCollector"),# FOR RAW RUNS
						#wireDigiTag = cms.InputTag("simMuonCSCDigis","MuonCSCWireDigi"),
						#stripDigiTag = cms.InputTag("simMuonCSCDigis","MuonCSCStripDigi"),
						#alctDigiTag = cms.InputTag("simCscTriggerPrimitiveDigis",""),
						#clctDigiTag = cms.InputTag("simCscTriggerPrimitiveDigis",""),
						#lctDigiTag =  cms.InputTag("simCscTriggerPrimitiveDigis",""),
						#compDigiTag = cms.InputTag("simMuonCSCDigis","MuonCSCComparatorDigi"),
						#segmentTag = cms.InputTag("cscSegments"),
						#recHitTag = cms.InputTag("csc2DRecHits"),
						simHitTag = cms.InputTag("g4SimHits","MuonCSCHits")
)
process.p = cms.Path(process.GIFTree)

