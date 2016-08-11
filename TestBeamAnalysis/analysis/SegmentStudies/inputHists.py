#!/usr/bin/env python
import os
import ROOT
from Gif.TestBeamAnalysis.TestBeamMeasurements import *

# List of hists from GIFAnalysis to compare
hists = [
    "hSegChi2p2dof",
    "hSegChi2p4dof",
    "hSegChi2p6dof",
    "hSegChi2p8dof",
    "hSegChi2pdof",
    #"hSegChi2pdofProb",
    "hSegNhits",
    "hSeg3hits",
    "hSeg4hits",
    "hSeg5hits",
    "hSeg6hits",
    "hSegXpos",
    "hSegYpos",
    "hSegXslope",
    "hSegYslope",
    "hNSeg",
    "hSegQual",
    "hSegQualBest",
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


class segHisto:
    '''
    - segHisto class is designed to be a python class container for all relevant 
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
        #f = ROOT.TFile('data/ana_%s_%s_%s_%s_%s_%s_%s.root'%(self.m.CSC,self.m.test,self.m.HV,self.m.beam,self.m.uAtt,self.m.dAtt,self.m.meas))
        f = ROOT.TFile('histos/ana_segHistos_%s_%s_%s_%s_%s_%s_%s.root'%(self.m.CSC,self.m.test,self.m.HV,self.m.beam,self.m.uAtt,self.m.dAtt,self.m.meas))
        print f
        for hist in hists:
            #self.histos[hist] = f.Get("GIFHistos").Get(hist).Clone()
            self.histos[hist] = f.Get(hist).Clone()
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
    measList = [segHisto(m) for m in measurements]
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
