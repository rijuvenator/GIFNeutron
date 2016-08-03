import FWCore.ParameterSet.Config as cms
import subprocess

process = cms.Process("TEST")

process.load("Configuration/StandardSequences/GeometryDB_cff")
process.load("Configuration/StandardSequences/MagneticField_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.load("Configuration/StandardSequences/RawToDigi_Data_cff")
process.load("Configuration.StandardSequences.Reconstruction_cff")


from Configuration.AlCa.GlobalTag import GlobalTag

process.GlobalTag.globaltag = '74X_dataRun2_Prompt_v0'

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.options = cms.untracked.PSet( SkipEvent =
cms.untracked.vstring('ProductNotFound') )

process.source = cms.Source ("PoolSource",
        fileNames = cms.untracked.vstring(
            #'/store/group/dpg_csc/comm_csc/gif/may16/ME11/d46/test40/ME11_Test40_2900V_bOn_u46_d46_m1986_t160506041146.root',
            #'/store/group/dpg_csc/comm_csc/gif/may16/ME11/d46/test40/ME11_Test40_2700V_bOn_u46_d46_m1997_t160506055021.root',
            '/store/group/dpg_csc/comm_csc/gif/may16/ME11/d46/test40/ME11_Test40_2900V_bOn_u46_d46_m1986_t160506041146.root',
            #'/store/group/dpg_csc/comm_csc/gif/may16/ME11/d46/test40/ME11_Test40_2950V_bOn_u46_d46_m1983_t160506034552.root',
            #'/store/group/dpg_csc/comm_csc/gif/may16/ME11/d46/test40/ME11_Test40_HV0_bOn_u46000_d46_m2040_t160506125054.root',
            #'/store/group/dpg_csc/comm_csc/gif/may16/ME11/d46/test40/ME11_Test40_HV0_bOn_u46_d46_m1979_t160506031324.root',
            #'/store/group/dpg_csc/comm_csc/gif/may16/ME11/sourceOFF/test40/ME11_Test40_2600V_bOn_uOff_dOff_m1953_t160505232803.root',
            #'/store/group/dpg_csc/comm_csc/gif/may16/ME11/sourceOFF/test40/ME11_Test40_2700V_bOn_uOff_dOff_m1955_t160505234216.root',
            #'/store/group/dpg_csc/comm_csc/gif/may16/ME11/sourceOFF/test40/ME11_Test40_2800V_bOn_uOff_dOff_m1957_t160505235619.root',
            #'/store/group/dpg_csc/comm_csc/gif/may16/ME11/sourceOFF/test40/ME11_Test40_2850V_bOn_uOff_dOff_m1959_t160506001012.root',
            #'/store/group/dpg_csc/comm_csc/gif/may16/ME11/sourceOFF/test40/ME11_Test40_2900V_bOn_uOff_dOff_m1961_t160506002459.root',
            #'/store/group/dpg_csc/comm_csc/gif/may16/ME11/sourceOFF/test40/ME11_Test40_2950V_bOn_uOff_dOff_m1964_t160506004204.root',
            #'/store/group/dpg_csc/comm_csc/gif/may16/ME11/sourceOFF/test40/ME11_Test40_HV0_bOff_uOff_dOff_m2317_t160509124353.root',
            #'/store/group/dpg_csc/comm_csc/gif/may16/ME11/sourceOFF/test40/ME11_Test40_HV0_bOn_uOff_dOff_m1966_t160506015143.root',
#            'file://csc_straight_mask.root'
)        

)
process.MessageLogger = cms.Service("MessageLogger",
    cout = cms.untracked.PSet(
        default = cms.untracked.PSet( limit = cms.untracked.int32(100) ),
        FwkJob = cms.untracked.PSet( limit = cms.untracked.int32(0) )
    ),
    categories = cms.untracked.vstring('FwkJob'),
    destinations = cms.untracked.vstring('cout')
)



"""Customise digi/reco geometry to use unganged ME1/a channels"""
process.CSCGeometryESModule.useGangedStripsInME1a = False
process.idealForDigiCSCGeometry.useGangedStripsInME1a = False



process.MakeNtuple = cms.EDAnalyzer("MakeSimpleCSCTree",
        #NtupleFileName = cms.untracked.string('output_ME11_Test40_2900V_bOn_u46_d46_m1986_t160506041146.root'),
        #NtupleFileName = cms.untracked.string('output_ME11_Test40_2700V_bOn_u46_d46_m1997_t160506055021.root'),
        NtupleFileName = cms.untracked.string('output_ME11_Test40_2900V_bOn_u46_d46_m1986_t160506041146.root'),
        #NtupleFileName = cms.untracked.string('output_ME11_Test40_2950V_bOn_u46_d46_m1983_t160506034552.root'),
        #NtupleFileName = cms.untracked.string('output_ME11_Test40_HV0_bOn_u46000_d46_m2040_t160506125054.root'),
        #NtupleFileName = cms.untracked.string('output_ME11_Test40_HV0_bOn_u46_d46_m1979_t160506031324.root'),
        #NtupleFileName = cms.untracked.string('output_ME11_Test40_2600V_bOn_uOff_dOff_m1953_t160505232803.root'),
        #NtupleFileName = cms.untracked.string('output_ME11_Test40_2700V_bOn_uOff_dOff_m1955_t160505234216.root'),
        #NtupleFileName = cms.untracked.string('output_ME11_Test40_2800V_bOn_uOff_dOff_m1957_t160505235619.root'),
        #NtupleFileName = cms.untracked.string('output_ME11_Test40_2850V_bOn_uOff_dOff_m1959_t160506001012.root'),
        #NtupleFileName = cms.untracked.string('output_ME11_Test40_2900V_bOn_uOff_dOff_m1961_t160506002459.root'),
        #NtupleFileName = cms.untracked.string('output_ME11_Test40_2950V_bOn_uOff_dOff_m1964_t160506004204.root'),
        #NtupleFileName = cms.untracked.string('output_ME11_Test40_HV0_bOff_uOff_dOff_m2317_t160509124353.root'),
        #NtupleFileName = cms.untracked.string('output_ME11_Test40_HV0_bOn_uOff_dOff_m1966_t160506015143.root'),
        wireDigiTag = cms.InputTag("muonCSCDigis", "MuonCSCWireDigi"),
        stripDigiTag = cms.InputTag("muonCSCDigis", "MuonCSCStripDigi"),
        alctDigiTag = cms.InputTag("muonCSCDigis", "MuonCSCALCTDigi"),
        clctDigiTag = cms.InputTag("muonCSCDigis", "MuonCSCCLCTDigi"),
        lctDigiTag = cms.InputTag("muonCSCDigis", "MuonCSCCorrelatedLCTDigi"),
        compDigiTag = cms.InputTag("muonCSCDigis", "MuonCSCComparatorDigi"),
        segmentTag = cms.InputTag("cscSegments"),
        
        recHitTag = cms.InputTag("csc2DRecHits"),
        
        )



process.p = cms.Path(process.muonCSCDigis * process.csc2DRecHits * process.cscSegments *  process.MakeNtuple)

