#!/usr/bin/env python
import os
import ROOT
from Gif.TestBeamAnalysis.TestBeamMeasurements import *
from Gif.TestBeamAnalysis.roottools import *

# List of hists from makeSegmentHistos to compare
hists = [
    "hSegChi2p2dof",
    "hSegChi2p4dof",
    "hSegChi2p6dof",
    "hSegChi2p8dof",
    "hSegChi2pdof",
    "hSegChi2pdofProb",
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
# Map for histogram axes labels
histAxesTitles = {
    "hSegChi2p2dof" : ('Fraction of segments','#chi^{2}/2 dof'),
    "hSegChi2p4dof" : ('Fraction of segments','#chi^{2}/4 dof'),
    "hSegChi2p6dof" : ('Fraction of segments','#chi^{2}/6 dof'),
    "hSegChi2p8dof" : ('Fraction of segments','#chi^{2}/8 dof'),
    "hSegChi2pdof" : ('Fraction of segments','#chi^{2}/ dof'),
    "hSegChi2pdofProb" : ('Fraction of segments','#chi^{2}/dof probability'),
    "hSegNhits" : ('<N(segments)>/event','N(hits) in segment'),
    "hSeg3hits" : ('ratio','N(hits) in segment'),
    "hSeg4hits" : ('ratio','N(hits) in segment'),
    "hSeg5hits" : ('ratio','N(hits) in segment'),
    "hSeg6hits" : ('ratio','N(hits) in segment'),
    "hSegXpos" : ('Fraction of segments','segment X pos [cm]'),
    "hSegYpos" : ('Fraction of segments','segment Y pos [cm]'),
    "hSegXslope" : ('Fraction of segments','segment slope dx/dz'),
    "hSegYslope" : ('Fraction of segments','segment slope dy/dz'),
    "hNSeg" : ('Fraction of events','N(segments)'),
    "hSegQual" : ('ratio','segment quality'),
    "hSegQualBest" : ('ratio','best segment quality'),
}
yLimits = {
    "hSegChi2p2dof" : (0,0.2),
    "hSegChi2p4dof" : (0,0.2),
    "hSegChi2p6dof" : (0,0.3),
    "hSegChi2p8dof" : (0,0.45),
    "hSegChi2pdof" : (0,0.3),
    "hSegChi2pdofProb" : (0,1.01),
    "hSegNhits" : (0,4.), # not used
    "hSeg3hits" : (0,2.5), # not used
    "hSeg4hits" : (0,7.5), # not used
    "hSeg5hits" : (0,6.), # not used
    "hSeg6hits" : (0,9.), # not used
    "hSegXpos" : (0,0.08),
    "hSegYpos" : (0,0.20),
    "hSegXslope" : (0,0.6),
    "hSegYslope" : (0,0.40),
    "hNSeg" : (0,1.01),
    "hSegQual" : (0,3.5),
    "hSegQualBest" : (0,4.5),
}

# Map measurements to styles
styles = {
    'm2250' : (1),
    'm1977' : (1),

    'm1966' : (1),
    'm2040' : (1),

    'm2306' : (1),
    'm2062' : (1),

    'm2312' : (1),
    'm2095' : (1),
    'm2262' : (2),
    'm2064' : (1),
    'm2079' : (1),
    'm2224' : (1),
    'm2333' : (1),
}

# Map attenuations to colors
colors = {
    'dOff'   : (ROOT.kBlack),
    'd10'    : (ROOT.kBlue),
    'd15'    : (ROOT.kOrange+1),
    'd22'    : (ROOT.kGreen+1),
    'd46'    : (ROOT.kRed),
    'd69'    : (ROOT.kViolet),
    'd100'   : (ROOT.kSpring),
    'd1000'  : (ROOT.kMagenta),
    'd46000' : (ROOT.kGray),
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
      - segEntry is also a container for histograms made from makeSegmentHistos.py 
      - Histograms to be analyzed are added to a list 'hists = []'
    - setStyle(color, legEntry, title)
      - Sets style options
    '''
    def __init__(self, gifMeas):
        self.m = gifMeas
        #self.setInfo()
        self.histos = {}
        self.setHistos()
        self.title = self.setTitle()
        self.legEntry = self.setLegEntry()
    def setHistos(self):
        f = ROOT.TFile('histos/ana_segHistos_%s_%s_%s_%s_%s_%s_%s.root'%(self.m.CSC,self.m.test,self.m.HV,self.m.beam,self.m.uAtt,self.m.dAtt,self.m.meas))
        #print f
        for hist in hists:
            #print hist
            if hist == 'hNSeg' or \
                hist == 'hSegChi2p2dof' or \
                hist == 'hSegChi2p4dof' or \
                hist == 'hSegChi2p6dof' or \
                hist == 'hSegChi2p8dof' or \
                hist == 'hSegChi2pdof':
                self.histos[hist] = DrawOverflow(f.Get(hist))
            else:
                self.histos[hist] = f.Get(hist).Clone()
            self.histos[hist].SetDirectory(0)
    def setTitle(self):
        '''
        Set title = "CSC, Test, HV"
        '''
        title = ''
        if self.m.CSC == 'ME11': title+='ME1/1, '
        else: title+= 'ME2/1, '
        if self.m.test == 'test27': title += 'Test 27, '
        else: title+= 'Test 40, '
        title += 'HV0'
        return title
    def setLegEntry(self):
        '''
        Set Legend entry = 'Att = XX'
        '''
        if self.m.dAtt == 'dOff': leg = 'No Source'
        else: 
            leg = 'Att = %s'%self.m.dAtt[1:]
            if self.m.dAtt == 'd10': leg += ' (%s)'%self.m.uAtt
        return leg


# debug and sample implementation
if __name__=='__main__':
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
        print entry.m.title
        print entry.m.legEntry
        if entry.m.ana_dataset: print entry.m.ana_dataset
        color, legEntry, title = styles[entry.m.meas]
        color2 = colors[entry.m.dAtt]
        print entry.histos["nSeg"]
        print 'old', title
        print 'old', legEntry
        print 'old', color
        print 'new', color2
