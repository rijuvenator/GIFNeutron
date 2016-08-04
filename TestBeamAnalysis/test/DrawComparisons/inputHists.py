#!/usr/bin/env python
import os
import ROOT
from Gif.TestBeamAnalysis.TestBeamMeasurements import *

# List of hists from GIFAnalysis to compare
hists = [
    "hNStripHits",
    "hNWireHits",
    "hNRecHits",
    "nSeg",
    "hnRecHitsAll",
    "hnRecHitsMax",
    "hSegInBeam",
    "hSegPos2D",
    "hSegPos2DBeam",
    "hSegPos2DBkgd",
    "hSegSlopeBeam",
    "hSegSlopeBkgd",
    "hSegChi2Beam",
    "hSegChi2Bkgd",
    "hSegNHitsBeam",
    "hSegNHitsBkgd",
    "hNSegGoodQuality",
]

# Map measurements to colors
# measurement : (color, legEntry, title),
styles = {
    'm2250' : (ROOT.kBlue, 'No Source', 'ME1/1, Test 27, HV0'),
    'm1966' : (ROOT.kBlue, 'No Source', 'ME1/1, Test 40, HV0'),
    'm1977' : (ROOT.kOrange+1, 'Att = 46', 'ME1/1, Test 27, HV0'),
    'm2040' : (ROOT.kOrange+1, 'Att = 46', 'ME1/1, Test 40, HV0'),
    'm2306' : (ROOT.kBlue, 'No Source', 'ME2/1, Test 27, HV0'),
    'm2312' : (ROOT.kBlue, 'No Source', 'ME2/1, Test 40, HV0'),
    'm2062' : (ROOT.kOrange+1, 'Att = 15', 'ME2/1, Test 27, HV0'),
    'm2064' : (ROOT.kOrange+1, 'Att = 15', 'ME2/1, Test 40, HV0'),
}


class gifHisto:
    '''
    - gifHisto class is designed to be a python class container for all relevant 
      histogram information associated with a measurement: 
      *** Others ***
      - color : color applied to histograms
      - legEntry : legend entry for histograms
      - title : common title
    - setHistos()
      - gifEntry is also a container for the histograms made from Gif.cc
      - Histograms to be analyzed are added to a list 'hists = []'
    - setStyle(color, legEntry, title)
      - Sets style options
    '''
    def __init__(self, gifMeas):
        self.m = gifMeas
        #self.setInfo()
        self.histos = {}
        self.setHistos()
    def setHistos(self):
        if self.m.ana_dataset is not None:
            f = ROOT.TFile(self.m.ana_dataset)
            for hist in hists:
                self.histos[hist] = f.Get("GIFAnalysis").Get(hist).Clone()
                self.histos[hist].SetDirectory(0)


# debug and sample implementation
if __name__=='__main__':
    '''
    m1966 = gifEntry('data/ana_ME11_Test40_HV0_bOn_uOff_dOff_m1966.root')
    m1966.setStyle(ROOT.kBlue,'Source off','ME1/1, Test40 (Scintillator Trigger), HV0')
    #m2040 = gifEntry('ana_ME11_Test40_HV0_bOn_u46000_d46_m2040.root')
    print m1966.CSC, m1966.meas, m1966.legEntry
    print m1966.histos["nSeg"]
    m1966.histos["nSeg"].Draw()
    '''
    measList = [gifHisto(m) for m in measurements]
    for entry in measList:
        print entry.m.CSC
        print entry.m.meas
        print entry.m.test
        print entry.m.HV
        print entry.m.beam
        print entry.m.uAtt
        print entry.m.dAtt
        print entry.m.time
        print entry.m.fn
        if entry.m.ana_dataset: print entry.m.ana_dataset
        color, legEntry, title = styles[entry.m.meas]
        print entry.histos["nSeg"]
        print title
        print legEntry
        print color
        print
