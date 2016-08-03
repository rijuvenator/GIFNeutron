import FWCore.ParameterSet.Config as cms

process.GIFAnalysis = cms.EDAnalyzer('Gif',
                            stripDigiTag = cms.InputTag('muonCSCDigis','MuonCSCStripDigi'),
                            wireDigiTag = cms.InputTag('muonCSCDigis','MuonCSCWireDigi'),
                            cscRecHitTag = cms.InputTag('csc2DRecHits'),#,''),
                            cscSegTag = cms.InputTag('cscSegments'),
                            chamberType = cms.untracked.string('21'), #chamber type: ME1/1-11, ME2/1-21  
                            )
