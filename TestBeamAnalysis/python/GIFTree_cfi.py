import FWCore.ParameterSet.Config as cms

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
