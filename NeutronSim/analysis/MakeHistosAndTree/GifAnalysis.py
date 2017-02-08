import FWCore.ParameterSet.Config as cms
from Gif.NeutronSim.GIFNeutronSim_cfg import process

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

process.p = cms.Path(process.muonCSCDigis * process.csc2DRecHits * process.cscSegments)

"""Customise digi/reco geometry to use unganged ME1/a channels"""
process.CSCGeometryESModule.useGangedStripsInME1a = False
process.idealForDigiCSCGeometry.useGangedStripsInME1a = False


#MuonDigiCollection<CSCDetId,CSCALCTDigi>    "simCscTriggerPrimitiveDigis"   ""                "RECO"    
#MuonDigiCollection<CSCDetId,CSCCLCTDigi>    "simCscTriggerPrimitiveDigis"   ""                "RECO"    
#MuonDigiCollection<CSCDetId,CSCComparatorDigi>    "simMuonCSCDigis"           "MuonCSCComparatorDigi"   "RECO"    
#MuonDigiCollection<CSCDetId,CSCCorrelatedLCTDigi>    "csctfDigis"                ""                "RECO"    
#MuonDigiCollection<CSCDetId,CSCCorrelatedLCTDigi>    "simCscTriggerPrimitiveDigis"   ""                "RECO"    
#MuonDigiCollection<CSCDetId,CSCCorrelatedLCTDigi>    "simCscTriggerPrimitiveDigis"   "MPCSORTED"       "RECO"    
#MuonDigiCollection<CSCDetId,CSCStripDigi>    "simMuonCSCDigis"           "MuonCSCStripDigi"   "RECO"    
#MuonDigiCollection<CSCDetId,CSCWireDigi>    "simMuonCSCDigis"           "MuonCSCWireDigi"   "RECO"    
#MuonDigiCollection<CSCDetId,GEMCSCLCTDigi>    "simCscTriggerPrimitiveDigis"   ""                "RECO"    
#MuonDigiCollection<CSCDetId,int>      "simCscTriggerPrimitiveDigis"   ""                "RECO"    


def doTree(process):
    process.GIFTree = cms.EDAnalyzer('MakeSimpleNeutronSimTree',
							# CSC
							#rawDataTag = cms.InputTag("rawDataCollector"),# FOR RAW RUNS
							wireDigiTag = cms.InputTag("simMuonCSCDigis","MuonCSCWireDigi"),
							stripDigiTag = cms.InputTag("simMuonCSCDigis","MuonCSCStripDigi"),
							alctDigiTag = cms.InputTag("simCscTriggerPrimitiveDigis",""),
							clctDigiTag = cms.InputTag("simCscTriggerPrimitiveDigis",""),
							lctDigiTag =  cms.InputTag("simCscTriggerPrimitiveDigis",""),
							compDigiTag = cms.InputTag("simMuonCSCDigis","MuonCSCComparatorDigi"),
							segmentTag = cms.InputTag("cscSegments"),
							recHitTag = cms.InputTag("csc2DRecHits"),
							simHitTag = cms.InputTag("g4SimHits","MuonCSCHits")
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

