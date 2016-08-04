import sys, os
import FWCore.ParameterSet.Config as cms
from Gif.TestBeamAnalysis.GIFTestBeamAnalysis_cfg import process
#from Gif.TestBeamAnalysis.GIFHistos_cfi import GIFHistos
#from Gif.TestBeamAnalysis.GIFTree_cfi import GIFTree

process.source = cms.Source('PoolSource', 
    fileNames = cms.untracked.vstring( 
        'file:doesnotexist.root',  
    ) 
)
process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

process.options = cms.untracked.PSet(
    SkipEvent = cms.untracked.vstring('LogicError','ProductNotFound')
)
process.maxEvents.input = -1
process.MessageLogger.cerr.FwkReport.reportEvery = -1

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

f = file('outfile', 'w')
f.write(process.dumpPython())
f.close()

if __name__ == '__main__' and 'submit' in sys.argv:
    plotsDir = '/afs/cern.ch/work/c/cschnaib/GIF/data/'
    dryrun = 'dryrun' in sys.argv
    from Gif.TestBeamAnalysis.TestBeamMeasurements import *
    measurements = [m2040,m2064]
    for TBM in measurements:
        print TBM.meas
        chamber = TBM.CSC
        fn = TBM.fn
        ana_dataset = plotsDir+'ana_%s.root'%TBM.meas
        print chamber
        print fn
        print ana_dataset

        gif_py = open('gif_histos.py').read()
        if not 'noHistos' in sys.argv:
            gif_py += '\ndoHistos(process)\n'
        if not 'noTree' in sys.argv:
            gif_py += '\ndoTree(process)\n'
        gif_py += '''
process.GIFHistos.chamberType = cms.untracked.string('%(chamber)s')
process.source.fileNames  = cms.untracked.vstring('%(fn)s')
process.TFileService.fileName = cms.string('%(ana_dataset)s')
''' % locals()

        open('submit_gif_histos.py','wt').write(gif_py)
        if dryrun:
            pass
        else: 
            cmd = 'cmsRun submit_gif_histos.py'
            print cmd
            os.system(cmd)

    if not dryrun:
        pass
        os.system('rm submit_gif_histos.py submit_gif_histos.pyc outfile')
