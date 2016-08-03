# Usage:
# cmsRun gif.py input=NUM
# where NUM = [1, 12], to specify which input/output files to use 
# Can do multiple jobs in series with:
# source gif.src 


import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
import sys


options = VarParsing ('analysis')
options.register('input',
                 0, # default value
                 VarParsing.multiplicity.singleton, # singleton or list
                 VarParsing.varType.int,          # string, int, or float
                 'Integer that controls input/output files.  Set to [1-8].'  
)

options.parseArguments()
process = cms.Process('GIFAnalysis')

process.load('Configuration/Geometry/GeometryIdeal2015Reco_cff')
#process.load('Configuration/Geometry/IdealGeometry_cff')
#process.load('Configuration/StandardSequences/Geometry_cff')
#process.load('Configuration/StandardSequences/GeometryDB_cff')
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

process.source = cms.Source('PoolSource',
    fileNames = cms.untracked.vstring(
        'file:doesnotexist.root', 
    )
)
                            
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)


process.load('FWCore.MessageLogger.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = -1
process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

process.TFileService = cms.Service('TFileService', fileName=cms.string('gif_histos.root'))

process.GIFAnalysis = cms.EDAnalyzer('Gif',
                            stripDigiTag = cms.InputTag('muonCSCDigis','MuonCSCStripDigi'),
                            wireDigiTag = cms.InputTag('muonCSCDigis','MuonCSCWireDigi'),
                            cscRecHitTag = cms.InputTag('csc2DRecHits'),#,''),
                            cscSegTag = cms.InputTag('cscSegments'),                              
                            chamberType = cms.untracked.string('21'), #chamber type: ME1/1-11, ME2/1-21  
                            )

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

process.p = cms.Path(process.muonCSCDigis * process.csc2DRecHits * process.cscSegments)
process.p *= process.GIFAnalysis 
process.p *= process.GIFTree

plotsDir = '/afs/cern.ch/work/c/cschnaib/GIF/data/'
baseDir = '/store/group/dpg_csc/comm_csc/gif/may16/'
process.source.fileNames = cms.untracked.vstring(baseDir+'ME11/d46/test40/ME11_Test40_2900V_bOn_u46_d46_m1986_t160506041146.root')





# ME2/1, source off, HV0:
if options.input == 1:
    process.source.fileNames  = cms.untracked.vstring(baseDir + 'ME21/sourceOFF/test27/ME21_Test27_HV0_bOn_uOff_dOff_m2306_t160509094700.root') 
    process.TFileService.fileName = cms.string(plotsDir + 'ana_ME21_Test27_HV0_bOn_uOff_dOff_m2306.root')
if options.input == 2:
    process.source.fileNames  = cms.untracked.vstring(baseDir + 'ME21/sourceOFF/test40/ME21_Test40_HV0_bOn_uOff_dOff_m2312_t160509111100.root') 
    process.TFileService.fileName = cms.string(plotsDir + 'ana_ME21_Test40_HV0_bOn_uOff_dOff_m2312.root')

# ME2/1, LHC, HV0
if options.input == 3:
    process.source.fileNames = cms.untracked.vstring(baseDir + 'ME21/d1000/test27/')
    process.TFileService.fileName = cms.string(plotsDir + 'ana_')
if options.input == 4:
    process.source.fileNames = cms.untracked.vstring(baseDir + 'ME21/d1000/test40/')
    process.TFileService.fileName = cms.string(plotsDir + 'ana_')

# ME2/1, HL-LHC, HV0:
if options.input == 5:
    process.source.fileNames  = cms.untracked.vstring(baseDir + 'ME21/d15/test27/ME21_Test27_HV0_bOn_u46_d15_m2062_t160506220324.root') 
    process.TFileService.fileName = cms.string(plotsDir + 'ana_ME21_Test27_HV0_bOn_u46_d15_m2062.root')
if options.input == 6:
    process.source.fileNames  = cms.untracked.vstring(baseDir + 'ME21/d15/test40/ME21_Test40_HV0_bOn_u46_d15_m2064_t160506222510.root') 
    process.TFileService.fileName = cms.string(plotsDir + 'ana_ME21_Test40_HV0_bOn_u46_d15_m2064.root')

# ME1/1, source off, HV0:
if options.input == 7:
    process.GIFAnalysis.chamberType = cms.untracked.string('11') 
    process.source.fileNames  = cms.untracked.vstring(baseDir + 'ME11/sourceOFF/test27/ME11_Test27_HV0_bOn_uOff_dOff_m2250_t160508163702.root') 
    process.TFileService.fileName = cms.string(plotsDir + 'ana_ME11_Test27_HV0_bOn_uOff_dOff_m2250.root')
if options.input == 8:
    process.GIFAnalysis.chamberType = cms.untracked.string('11') 
    process.source.fileNames  = cms.untracked.vstring(baseDir + 'ME11/sourceOFF/test40/ME11_Test40_HV0_bOn_uOff_dOff_m1966_t160506015143.root') 
    process.TFileService.fileName = cms.string(plotsDir + 'ana_ME11_Test40_HV0_bOn_uOff_dOff_m1966.root')

# ME1/1, LHC, HV0:  
if options.input == 9:
    process.GIFAnalysis.chamberType = cms.untracked.string('11') 
    process.source.fileNames  = cms.untracked.vstring(baseDir + 'ME11/d46/test27/') 
    process.TFileService.fileName = cms.string(plotsDir + 'ana_')
if options.input == 10:
    process.GIFAnalysis.chamberType = cms.untracked.string('11')
    process.source.fileNames  = cms.untracked.vstring(baseDir + 'ME11/d46/test40/') 
    process.TFileService.fileName = cms.string(plotsDir + 'ana_')

# ME1/1, HL-LHC, HV0:  
if options.input == 11:
    process.GIFAnalysis.chamberType = cms.untracked.string('11') 
    process.source.fileNames  = cms.untracked.vstring(baseDir + 'ME11/d46/test27/ME11_Test27_HV0_bOn_u46_d46_m1977_t160506025710.root') 
    process.TFileService.fileName = cms.string(plotsDir + 'ana_ME11_Test27_HV0_bOn_u46_d46_m1977.root')
if options.input == 12:
    process.GIFAnalysis.chamberType = cms.untracked.string('11')
    process.source.fileNames  = cms.untracked.vstring(baseDir + 'ME11/d46/test40/ME11_Test40_HV0_bOn_u46000_d46_m2040_t160506125054.root') 
    process.TFileService.fileName = cms.string(plotsDir + 'ana_ME11_Test40_HV0_bOn_u46000_d46_m2040.root')


#
#process.cscValidation = cms.EDAnalyzer('CSCValidation',
#     rootFileName = cms.untracked.string('validHists.root'),
#     isSimulation = cms.untracked.bool(False),
#     writeTreeToFile = cms.untracked.bool(False),
#     useDigis = cms.untracked.bool(True),
#     detailedAnalysis = cms.untracked.bool(False),
#     useTriggerFilter = cms.untracked.bool(False),
#     useQualityFilter = cms.untracked.bool(True),
#     makeStandalonePlots = cms.untracked.bool(False),
#     makeStripPlots = cms.untracked.bool(False),
#     makeWirePlots = cms.untracked.bool(False),
#     makeOccupancyPlots = cms.untracked.bool(False),
#     makeTimeMonitorPlots = cms.untracked.bool(False),
#     rawDataTag = cms.InputTag('source'),
#     alctDigiTag = cms.InputTag('muonCSCDigis','MuonCSCALCTDigi'),
#     clctDigiTag = cms.InputTag('muonCSCDigis','MuonCSCCLCTDigi'),
#     corrlctDigiTag = cms.InputTag('muonCSCDigis','MuonCSCCorrelatedLCTDigi'),
#     stripDigiTag = cms.InputTag('muonCSCDigis','MuonCSCStripDigi'),
#     wireDigiTag = cms.InputTag('muonCSCDigis','MuonCSCWireDigi'),
#     compDigiTag = cms.InputTag('muonCSCDigis','MuonCSCComparatorDigi'),
#     cscRecHitTag = cms.InputTag('csc2DRecHits'),
#     cscSegTag = cms.InputTag('cscSegments'),
#     saMuonTag = cms.InputTag('standAloneMuons'),
#     globMuonTag = cms.InputTag('globalMuons'),
#     l1aTag = cms.InputTag('gtDigis'),
#     hltTag = cms.InputTag('TriggerResults::HLT'),
#     makeHLTPlots = cms.untracked.bool(False),
#     simHitTag = cms.InputTag('g4SimHits', 'MuonCSCHits')
#)

#process.p = cms.Path(process.gtDigis * process.muonCSCDigis  *process.csc2DRecHits * process.demo)
