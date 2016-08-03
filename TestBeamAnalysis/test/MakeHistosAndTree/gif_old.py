# Usage:
# cmsRun gif.py input=NUM
# where NUM = [1, 8], to specify which input/output files to use 
# Can do multiple jobs in series with:
# source gif.src 


import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
import sys


options = VarParsing ('analysis')
options.register ('input',
                  0, # default value
                  VarParsing.multiplicity.singleton, # singleton or list
                  VarParsing.varType.int,          # string, int, or float
                  "Integer that controls input/output files.  Set to [1-8]."  
              )
options.parseArguments()
process = cms.Process("Demo")

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

process.source = cms.Source("PoolSource",
                            # fileNames = cms.untracked.vstring('file:../../CMSSW_6_2_12/src/output.root'	  
                            fileNames = cms.untracked.vstring(
        'file:../../CMSSW_6_2_12_patch1/src/test.root', 
        )
                            )
                            
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(10000)
    )


process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 100
process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

process.demo = cms.EDAnalyzer('Gif',
                              #rootFileName = cms.untracked.string(options.outputFile),
                              rootFileName = cms.untracked.string("output_res.root"),                              
                              stripDigiTag = cms.InputTag("muonCSCDigis","MuonCSCStripDigi"),
                              wireDigiTag = cms.InputTag("muonCSCDigis","MuonCSCWireDigi"),
                              cscRecHitTag = cms.InputTag("csc2DRecHits",""),
                              cscSegTag = cms.InputTag("cscSegments"),                              
                              chamberType = cms.untracked.string('21'), #chamber type: ME1/1-11, ME2/1-21  
                              )   

baseDir = "/afs/cern.ch/user/w/wulsin/workspace/public/gif/CMSSW_6_2_12_patch1/src/outputRoot/"


# ME2/1, source off:
if options.input == 1:
    process.source.fileNames  = cms.untracked.vstring('file:' + baseDir + 'STEP_27_000_160509_094700_UTC.root') 
    process.demo.rootFileName = cms.untracked.string         ('outputPlots/STEP_27_000_160509_094700_UTC_analysis.root')
if options.input == 2:
    process.source.fileNames  = cms.untracked.vstring('file:' + baseDir + 'STEP_40_000_160509_111100_UTC.root') 
    process.demo.rootFileName = cms.untracked.string         ('outputPlots/STEP_40_000_160509_111100_UTC_analysis.root')

# ME2/1, source on:
if options.input == 3:
    process.source.fileNames  = cms.untracked.vstring('file:' + baseDir + 'STEP_27_000_160506_220324_UTC.root') 
    process.demo.rootFileName = cms.untracked.string         ('outputPlots/STEP_27_000_160506_220324_UTC_analysis.root')
if options.input == 4:
    process.source.fileNames  = cms.untracked.vstring('file:' + baseDir + 'STEP_40_000_160506_222510_UTC.root') 
    process.demo.rootFileName = cms.untracked.string         ('outputPlots/STEP_40_000_160506_222510_UTC_analysis.root')

# ME1/1, source off:
if options.input == 5:
    process.demo.chamberType = cms.untracked.string('11') 
    process.source.fileNames  = cms.untracked.vstring('file:' + baseDir + 'STEP_27_000_160508_163702_UTC.root')  
    process.demo.rootFileName = cms.untracked.string         ('outputPlots/STEP_27_000_160508_163702_UTC_analysis.root')
if options.input == 6:
    process.demo.chamberType = cms.untracked.string('11') 
    process.source.fileNames  = cms.untracked.vstring('file:' + baseDir + 'STEP_40_000_160506_015143_UTC.root') 
    process.demo.rootFileName = cms.untracked.string         ('outputPlots/STEP_40_000_160506_015143_UTC_analysis.root')

# ME1/1, source on:  
if options.input == 7:
    process.demo.chamberType = cms.untracked.string('11') 
    process.source.fileNames  = cms.untracked.vstring('file:' + baseDir + 'STEP_27_000_160506_025710_UTC.root') 
    process.demo.rootFileName = cms.untracked.string         ('outputPlots/STEP_27_000_160506_025710_UTC_analysis.root')
if options.input == 8:
    process.demo.chamberType = cms.untracked.string('11')
    process.source.fileNames  = cms.untracked.vstring('file:' + baseDir + 'STEP_40_000_160506_125054_UTC.root') 
    process.demo.rootFileName = cms.untracked.string         ('outputPlots/STEP_40_000_160506_125054_UTC_analysis.root')


#
#process.cscValidation = cms.EDAnalyzer("CSCValidation",
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
#     rawDataTag = cms.InputTag("source"),
#     alctDigiTag = cms.InputTag("muonCSCDigis","MuonCSCALCTDigi"),
#     clctDigiTag = cms.InputTag("muonCSCDigis","MuonCSCCLCTDigi"),
#     corrlctDigiTag = cms.InputTag("muonCSCDigis","MuonCSCCorrelatedLCTDigi"),
#     stripDigiTag = cms.InputTag("muonCSCDigis","MuonCSCStripDigi"),
#     wireDigiTag = cms.InputTag("muonCSCDigis","MuonCSCWireDigi"),
#     compDigiTag = cms.InputTag("muonCSCDigis","MuonCSCComparatorDigi"),
#     cscRecHitTag = cms.InputTag("csc2DRecHits"),
#     cscSegTag = cms.InputTag("cscSegments"),
#     saMuonTag = cms.InputTag("standAloneMuons"),
#     globMuonTag = cms.InputTag("globalMuons"),
#     l1aTag = cms.InputTag("gtDigis"),
#     hltTag = cms.InputTag("TriggerResults::HLT"),
#     makeHLTPlots = cms.untracked.bool(False),
#     simHitTag = cms.InputTag("g4SimHits", "MuonCSCHits")
#)

#process.p = cms.Path(process.gtDigis * process.muonCSCDigis  *process.csc2DRecHits * process.demo)
process.p = cms.Path(process.muonCSCDigis * process.csc2DRecHits * process.cscSegments * process.demo)


