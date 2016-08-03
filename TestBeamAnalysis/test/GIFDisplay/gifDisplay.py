import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing ('analysis')
options.parseArguments()
process = cms.Process("GifDisplay")

process.load("Configuration/Geometry/GeometryIdeal2015Reco_cff")
#process.load("Configuration/Geometry/IdealGeometry_cff")
#process.load("Configuration/StandardSequences/Geometry_cff")
process.load("Configuration/StandardSequences/MagneticField_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.load("Configuration/StandardSequences/RawToDigi_Data_cff")
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.load("RecoMuon.MuonSeedGenerator.standAloneMuonSeeds_cff")
#process.load("RecoMuon.GlobalMuonProducer.globalMuons_cff")

process.GlobalTag.globaltag = '74X_dataRun2_Prompt_v0'

process.options = cms.untracked.PSet(
	SkipEvent = cms.untracked.vstring('LogicError','ProductNotFound')
)

process.MessageLogger = cms.Service("MessageLogger",
       destinations   = cms.untracked.vstring('myDebugOutputFile.txt'),
       debugModules = cms.untracked.vstring('*'),
       message = cms.untracked.PSet(
                                   threshold = cms.untracked.vstring('DEBUG')
                                   )
)


process.source = cms.Source("PoolSource",
  fileNames = cms.untracked.vstring('file:me21_test27_oct30.root')
)



process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(100)
    )

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1
process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

process.GifDisplay = cms.EDAnalyzer('GifDisplay',
#rootFileName = cms.untracked.string("output_me11_test27_oct30.root"),
rootFileName = cms.untracked.string("output_me21_test27_oct30.root"),
stripDigiTag = cms.InputTag("muonCSCDigis","MuonCSCStripDigi"),
wireDigiTag = cms.InputTag("muonCSCDigis","MuonCSCWireDigi"),
comparatorDigiTag = cms.InputTag("muonCSCDigis", "MuonCSCComparatorDigi"),
cscRecHitTag = cms.InputTag("csc2DRecHits",""),
alctDigiTag = cms.InputTag('muonCSCDigis', 'MuonCSCALCTDigi'),
clctDigiTag = cms.InputTag('muonCSCDigis', 'MuonCSCCLCTDigi'),
corrlctDigiTag = cms.InputTag('muonCSCDigis', 'MuonCSCCorrelatedLCTDigi'),

#directory for eventdisplay
eventDisplayDir = cms.untracked.string("/afs/cern.ch/user/w/wulsin/workspace/public/gif/CMSSW_7_5_1/src/tmpDisplay"),
#chamber type: ME1/1-11, ME2/1-21
chamberType = cms.untracked.string('21')
)

baseDir = "/afs/cern.ch/user/w/wulsin/workspace/public/gif/CMSSW_6_2_12_patch1/src/outputRoot/"
# process.source.fileNames        = cms.untracked.vstring('file:' + baseDir + 'STEP_27_000_160509_094700_UTC.root')             
# process.GifDisplay.rootFileName = cms.untracked.string         ('outputPlots/STEP_27_000_160509_094700_UTC_display.root')    
# process.GifDisplay.eventDisplayDir = cms.untracked.string("tmpDisplay/ME21Test27sourceOff/")  

# process.source.fileNames        = cms.untracked.vstring('file:' + baseDir + 'STEP_40_000_160509_111100_UTC.root')             
# process.GifDisplay.rootFileName = cms.untracked.string         ('outputPlots/STEP_40_000_160509_111100_UTC_display.root')    
# process.GifDisplay.eventDisplayDir = cms.untracked.string("tmpDisplay/ME21Test40sourceOff/")  

# process.source.fileNames        = cms.untracked.vstring('file:' + baseDir + 'STEP_27_000_160506_220324_UTC.root')             
# process.GifDisplay.rootFileName = cms.untracked.string         ('outputPlots/STEP_27_000_160506_220324_UTC_display.root')    
# process.GifDisplay.eventDisplayDir = cms.untracked.string("tmpDisplay/ME21Test27sourceOn/")  

# process.source.fileNames        = cms.untracked.vstring('file:' + baseDir + 'STEP_40_000_160506_222510_UTC.root')             
# process.GifDisplay.rootFileName = cms.untracked.string         ('outputPlots/STEP_40_000_160506_222510_UTC_display.root')    
# process.GifDisplay.eventDisplayDir = cms.untracked.string("tmpDisplay/ME21Test40sourceOn/")


# process.GifDisplay.chamberType = cms.untracked.string('11')  
# process.source.fileNames        = cms.untracked.vstring('file:' + baseDir + 'STEP_27_000_160508_163702_UTC.root')  
# process.GifDisplay.rootFileName = cms.untracked.string         ('outputPlots/STEP_27_000_160508_163702_UTC_display.root')    
# process.GifDisplay.eventDisplayDir = cms.untracked.string("tmpDisplay/ME11Test27sourceOff/")

# process.GifDisplay.chamberType = cms.untracked.string('11')  
# process.source.fileNames        = cms.untracked.vstring('file:' + baseDir + 'STEP_40_000_160506_015143_UTC.root')             
# process.GifDisplay.rootFileName = cms.untracked.string         ('outputPlots/STEP_40_000_160506_015143_UTC_display.root')    
# process.GifDisplay.eventDisplayDir = cms.untracked.string("tmpDisplay/ME11Test40sourceOff/")

# process.GifDisplay.chamberType = cms.untracked.string('11')  
# process.source.fileNames        = cms.untracked.vstring('file:' + baseDir + 'STEP_27_000_160506_025710_UTC.root')             
# process.GifDisplay.rootFileName = cms.untracked.string         ('outputPlots/STEP_27_000_160506_025710_UTC_display.root')    
# process.GifDisplay.eventDisplayDir = cms.untracked.string("tmpDisplay/ME11Test27sourceOn/")

process.GifDisplay.chamberType = cms.untracked.string('11')  
process.source.fileNames        = cms.untracked.vstring('file:' + baseDir + 'STEP_40_000_160506_125054_UTC.root')
process.GifDisplay.rootFileName = cms.untracked.string         ('outputPlots/STEP_40_000_160506_125054_UTC_display.root')
process.GifDisplay.eventDisplayDir = cms.untracked.string("tmpDisplay/ME11Test40sourceOn/")


process.p = cms.Path(process.muonCSCDigis  *process.csc2DRecHits * process.GifDisplay)

