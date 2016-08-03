#!/usr/bin/env python
import os
import ROOT
#from ROOT import gROOT, gStyle, TCanvas, TFile, TH1F, TLegend, TMath, TPaveLabel

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

class gifEntry:
    '''
    - gifEntry class is designed to be a python class container for all relevant 
      meta data associated with a measurement: 
      - CSC  : chamber type (ME11 or ME21)
      - test : STEP Test type (27, 27s, 40)
      - HV   : Chamber high voltage (HV0V, 2900V, 3600V, etc.)
      - beam : Beam status (bOn, bOff)
      - uAtt : Upsteam source attenuation (u46, uOff, etc.)
      - dAtt : Downstream source attenuation (d15, dOff, etc.)
      - meas : Measurement number (m1966, m1977, etc.)
      *** Others ***
      - color : color applied to histograms
      - legEntry : legend entry for histograms
      - title : common title
    - setInfo()
      - Since all relevant info is already associated with the file name (I'm willing
        to assume everyone is analyzing data from /eos/cms/store/group/dpg_csc/csc_comm/gif/)
        I have a setInfo() function which parses the file name with the assumption it is of the form
        path/to/ana_ME11_Test40_HV0_bOn_uOff_dOff_m1966.root (I've stripped off the time stamp from 
        the end of the file name)
    - setHistos()
      - gifEntry is also a container for the histograms made from Gif.cc
      - Histograms to be analyzed are added to a list 'hists = []'
    - setStyle(color, legEntry, title)
      - Sets style options
    '''
    def __init__(self, fn):
        self.fn = fn
        self.setInfo()
        self.histos = {}
        self.setHistos()
    def setInfo(self):
        fileName  = os.path.basename(self.fn)
        nameList  = fileName.split('_')
        self.CSC  = nameList[1]
        self.test = nameList[2]
        self.HV   = nameList[3]
        self.beam = nameList[4]
        self.uAtt = nameList[5]
        self.dAtt = nameList[6]
        self.meas = nameList[7].strip('.root')
    def setHistos(self):
        if self.fn is not None:
            f = ROOT.TFile(self.fn)
            for hist in hists:
                self.histos[hist] = f.Get("GIFAnalysis").Get(hist).Clone()
                self.histos[hist].SetDirectory(0)
    def setStyle(self, color, legEntry, title):
        self.color = color
        self.legEntry = legEntry
        self.title = title

# Measurement instantiations
m2250 = gifEntry('data/ana_ME11_Test27_HV0_bOn_uOff_dOff_m2250.root')
m2250.setStyle(ROOT.kBlue,'Source off','ME1/1, Test27 (Self Trigger), HV0')

m1966 = gifEntry('data/ana_ME11_Test40_HV0_bOn_uOff_dOff_m1966.root')
m1966.setStyle(ROOT.kBlue,'Source off','ME1/1, Test40 (Scintillator Trigger), HV0')

m1977 = gifEntry('data/ana_ME11_Test27_HV0_bOn_u46_d46_m1977.root')
m1977.setStyle(ROOT.kOrange+1,'Source on (HL-LHC, 7E34)','ME1/1, Test27 (Self Trigger), HV0')

m2040 = gifEntry('data/ana_ME11_Test40_HV0_bOn_u46000_d46_m2040.root')
m2040.setStyle(ROOT.kOrange+1,'Source on (HL-LHC, 7E34)','ME1/1, Test40 (Scintillator Trigger), HV0')

m2306 = gifEntry('data/ana_ME21_Test27_HV0_bOn_uOff_dOff_m2306.root')
m2306.setStyle(ROOT.kBlue,'Source off','ME2/1, Test27 (Self Trigger), HV0')

m2312 = gifEntry('data/ana_ME21_Test40_HV0_bOn_uOff_dOff_m2312.root')
m2312.setStyle(ROOT.kBlue,'Source off','ME2/1, Test40 (Scintillator Trigger), HV0')

m2062 = gifEntry('data/ana_ME21_Test27_HV0_bOn_u46_d15_m2062.root')
m2062.setStyle(ROOT.kOrange+1,'Source on (HL-LHC, 7E34)','ME2/1, Test27 (Self Trigger), HV0')

m2064 = gifEntry('data/ana_ME21_Test40_HV0_bOn_u46_d15_m2064.root')
m2064.setStyle(ROOT.kOrange+1,'Source on (HL-LHC, 7E34)','ME2/1, Test40 (Self Trigger), HV0')

# debug and sample implementation
if __name__=='__main__':
    m1966 = gifEntry('data/ana_ME11_Test40_HV0_bOn_uOff_dOff_m1966.root')
    m1966.setStyle(ROOT.kBlue,'Source off','ME1/1, Test40 (Scintillator Trigger), HV0')
    #m2040 = gifEntry('ana_ME11_Test40_HV0_bOn_u46000_d46_m2040.root')
    print m1966.CSC, m1966.meas, m1966.legEntry
    print m1966.histos["nSeg"]
    m1966.histos["nSeg"].Draw()
