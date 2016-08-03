import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing


options = VarParsing ('analysis')
options.parseArguments()
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
    rootFileName      = cms.untracked.string('output_me11_test27.root'),
    # Input Tags
    stripDigiTag      = cms.InputTag('muonCSCDigis', 'MuonCSCStripDigi'),
    wireDigiTag       = cms.InputTag('muonCSCDigis', 'MuonCSCWireDigi'),
    comparatorDigiTag = cms.InputTag('muonCSCDigis',  'MuonCSCComparatorDigi'),
    cscRecHitTag      = cms.InputTag('csc2DRecHits', ''),
    alctDigiTag       = cms.InputTag('muonCSCDigis', 'MuonCSCALCTDigi'),
    clctDigiTag       = cms.InputTag('muonCSCDigis', 'MuonCSCCLCTDigi'),
    corrlctDigiTag    = cms.InputTag('muonCSCDigis', 'MuonCSCCorrelatedLCTDigi'),
    #directory for eventdisplay
    eventDisplayDir = cms.untracked.string('/afs/cern.ch/work/c/cschnaib/GIF/eventDisplay'),
    # Event list file
    eventListFile = cms.untracked.string('/afs/cern.ch/user/c/cschnaib/Work/CMSSW_7_5_1/src/GIF/TestBeamAnalysis/test/GIFDisplay/listTest_notEmpty.txt'),
    #chamber type: ME1/1-11, ME2/1-21
    chamberType = cms.untracked.string('11'),
)

# Overwrite initial definitions
baseDir = '/store/group/dpg_csc/comm_csc/gif/may16/'
plotDir = '/afs/cern.ch/work/c/cschnaib/GIF/eventDisplay/'

# ME11, Att = 46, Test 40, HV = 2900V
#process.GifDisplay.chamberType     = cms.untracked.string  ('11')  
#process.source.fileNames           = cms.untracked.vstring (baseDir + 'ME11/d46/test40/ME11_Test40_2900V_bOn_u46_d46_m1986_t160506041146.root')
#process.GifDisplay.rootFileName    = cms.untracked.string  (plotDir + 'ME11/d46/test40/2900V/m1986/displays_m1986.root')
#process.GifDisplay.eventDisplayDir = cms.untracked.string  (plotDir + 'ME11/d46/test40/2900V/m1986/')
# ME11, Att = off, Test 40, HV = 2900V
#process.GifDisplay.chamberType     = cms.untracked.string  ('11')  
#process.source.fileNames           = cms.untracked.vstring (baseDir + 'ME11/sourceOFF/test40/ME11_Test40_2900V_bOn_uOff_dOff_m1961_t160506002459.root')
#process.GifDisplay.rootFileName    = cms.untracked.string  (plotDir + 'ME11/sourceOFF/test40/2900V/m1961/displays_m1961.root')
#process.GifDisplay.eventDisplayDir = cms.untracked.string  (plotDir + 'ME11/sourceOFF/test40/2900V/m1961/')

# ME21, Att = 15, Test 40, HV = 3600V
#process.GifDisplay.chamberType     = cms.untracked.string  ('21')
#process.source.fileNames           = cms.untracked.vstring (baseDir + 'ME21/d15/test40/ME21_Test40_3600V_bOn_u46_d15_m2073_t160507005834.root')
#process.GifDisplay.rootFileName    = cms.untracked.string  (plotDir + 'ME21/d15/test40/3600V/m2073/displays_m2073.root')
#process.GifDisplay.eventDisplayDir = cms.untracked.string  (plotDir + 'ME21/d15/test40/3600V/m2073/')
# ME21, Att = off, Test 40, HV = 3600V
#process.GifDisplay.chamberType     = cms.untracked.string  ('21')
#process.source.fileNames           = cms.untracked.vstring (baseDir + 'ME21/sourceOFF/test40/ME21_Test40_3600V_bOn_uOff_dOff_m2109_t160507112347.root')
#process.GifDisplay.rootFileName    = cms.untracked.string  (plotDir + 'ME21/sourceOFF/test40/3600V/m2109/displays_m2109.root')
#process.GifDisplay.eventDisplayDir = cms.untracked.string  (plotDir + 'ME21/sourceOFF/test40/3600V/m2109/')
# ME2/1, HL-LHC, HV0:
#process.source.fileNames  = cms.untracked.vstring(baseDir + 'ME21/d15/test27/ME21_Test27_HV0_bOn_u46_d15_m2062_t160506220324.root')
#process.TFileService.fileName = cms.string(plotsDir + 'ana_ME21_Test27_HV0_bOn_u46_d15_m2062.root')
process.source.fileNames  = cms.untracked.vstring(baseDir + 'ME21/d15/test40/ME21_Test40_HV0_bOn_u46_d15_m2064_t160506222510.root')
process.GifDisplay.rootFileName = cms.untracked.string(plotDir + 'displays_ME21_Test40_HV0_bOn_u46_d15_m2064.root')
process.GifDisplay.chamberType = cms.untracked.string('21')

process.p = cms.Path(process.muonCSCDigis * process.csc2DRecHits * process.GifDisplay)

