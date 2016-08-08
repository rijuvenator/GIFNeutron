import FWCore.ParameterSet.Config as cms
from Gif.TestBeamAnalysis.GIFTestBeamAnalysis_cfg import process

process.source = cms.Source('PoolSource', 
    fileNames = cms.untracked.vstring( 
        'file:doesnotexist.root',  
    ) 
)
process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

process.options = cms.untracked.PSet(
    SkipEvent = cms.untracked.vstring('LogicError','ProductNotFound')
)
process.maxEvents.input = 100
process.MessageLogger.cerr.FwkReport.reportEvery = 10000

process.p = cms.Path(process.muonCSCDigis * process.csc2DRecHits * process.cscSegments)

"""Customise digi/reco geometry to use unganged ME1/a channels"""
process.CSCGeometryESModule.useGangedStripsInME1a = False
process.idealForDigiCSCGeometry.useGangedStripsInME1a = False

def doTree(process):
    process.GIFTree = cms.EDAnalyzer('MakeSimpleGIFTree',
                            wireDigiTag = cms.InputTag('muonCSCDigis', 'MuonCSCWireDigi'),
                            stripDigiTag = cms.InputTag('muonCSCDigis', 'MuonCSCStripDigi'),
                            alctDigiTag = cms.InputTag('muonCSCDigis', 'MuonCSCALCTDigi'),
                            clctDigiTag = cms.InputTag('muonCSCDigis', 'MuonCSCCLCTDigi'),
                            lctDigiTag = cms.InputTag('muonCSCDigis', 'MuonCSCCorrelatedLCTDigi'),
                            compDigiTag = cms.InputTag('muonCSCDigis', 'MuonCSCComparatorDigi'),
                            segmentTag = cms.InputTag('cscSegments'),
                            recHitTag = cms.InputTag('csc2DRecHits'),
    )
    process.p *= process.GIFTree

def doHistos(process):
    process.GIFHistos = cms.EDAnalyzer('Gif',
                            stripDigiTag = cms.InputTag('muonCSCDigis','MuonCSCStripDigi'),
                            wireDigiTag = cms.InputTag('muonCSCDigis','MuonCSCWireDigi'),
                            cscRecHitTag = cms.InputTag('csc2DRecHits'),#,''),
                            cscSegTag = cms.InputTag('cscSegments'),
                            chamberType = cms.untracked.string('ME21'), #chamber type: ME1/1-11, ME2/1-21  
    )
    process.p *= process.GIFHistos

