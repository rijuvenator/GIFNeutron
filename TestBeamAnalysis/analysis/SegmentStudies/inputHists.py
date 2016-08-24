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
    "hSegSlope",
    "hSegdSlope",
    "hSegSlopeIN",
    "hSegdSlopeIN",
    "hSegSlopeOUT",
    "hSegdSlopeOUT",
    "hNSeg",
    "hSegQual",
    "hSegQualSlope",
    "hSegQualSlopePen",
    "hSegQualSlopePenFrac",
    "hSegQualBest",
    "hSegQualNorm",
    "hSegQualSlopeNorm",
    "hSegQualSlopePenNorm",
    "hSegQualBestNorm",
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
    "hSegSlope" : ('Fraction of segments','segment #sqrt{(dx/dz)^{2} + (dy/dz)^{2}}'),
    "hSegdSlope" : ('Fraction of segments','segment #sqrt{(#Delta(dx/dz))^{2} + (#Delta(dy/dz))^{2}}'),
    "hSegSlopeIN" : ('Fraction of segments','segment #sqrt{(dx/dz)^{2} + (dy/dz)^{2}}'),
    "hSegdSlopeIN" : ('Fraction of segments','segment #sqrt{(#Delta(dx/dz))^{2} + (#Delta(dy/dz))^{2}}'),
    "hSegSlopeOUT" : ('Fraction of segments','segment #sqrt{(dx/dz)^{2} + (dy/dz)^{2}}'),
    "hSegdSlopeOUT" : ('Fraction of segments','segment #sqrt{(#Delta(dx/dz))^{2} + (#Delta(dy/dz))^{2}}'),
    "hNSeg" : ('Fraction of events','N(segments)'),
    "hSegQual" : ('Fraction of segments','segment quality'),
    "hSegQualNorm" : ('ratio','segment quality'),
    "hSegQualBest" : ('Fraction of segments','best segment quality'),
    "hSegQualBestNorm" : ('ratio','best segment quality'),
    "hSegQualSlope" : ('Fraction of segments','segment quality with slope penalty'),
    "hSegQualSlopeNorm" : ('ratio','segment quality with slope penalty'),
    "hSegQualSlopePen" : ('Fraction of segments','segment quality'),
    "hSegQualSlopePenFrac" : ('Fraction of segments per quality','segment quality'),
    "hSegQualSlopePenNorm" : ('ratio','segment quality'),
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
    "hSegSlope" : (0,0.5),
    "hSegdSlope" : (0,0.5),
    "hSegSlopeIN" : (0,0.5),
    "hSegdSlopeIN" : (0,0.5),
    "hSegSlopeOUT" : (0,0.5),
    "hSegdSlopeOUT" : (0,0.5),
    "hNSeg" : (0,1.01),
    "hSegQual" : (0,1.01),
    "hSegQualNorm" : (0,5.),
    "hSegQualBest" : (0,1.01),
    "hSegQualBestNorm" : (0,5.),
    "hSegQualSlope" : (0,1.01),
    "hSegQualSlopeNorm" : (0,5.),
    "hSegQualSlopePen" : (0,1.01),
    "hSegQualSlopePenFrac" : (0,1.01),
    "hSegQualSlopePenNorm" : (0,5.),
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
        self.ana_dataset = 'histos/ana_segHistos_%s_%s_%s_%s_%s_%s_%s.root'%(self.m.CSC,self.m.test,self.m.HV,self.m.beam,self.m.uAtt,self.m.dAtt,self.m.meas)
        f = ROOT.TFile(self.ana_dataset)
        #f = ROOT.TFile('histos/ana_segHistos_%s_%s_%s_%s_%s_%s_%s.root'%(self.m.CSC,self.m.test,self.m.HV,self.m.beam,self.m.uAtt,self.m.dAtt,self.m.meas))
        #print f
        for hist in hists:
            #print hist
            if hist == 'hNSeg' or \
                hist == 'hSegChi2p2dof' or \
                hist == 'hSegChi2p4dof' or \
                hist == 'hSegChi2p6dof' or \
                hist == 'hSegChi2p8dof' or \
                hist == 'hSegChi2pdof' or \
                hist == 'hSegSlope' or \
                hist == 'hSegdSlope' or \
                hist == 'hSegSlopeIN' or \
                hist == 'hSegdSlopeIN' or \
                hist == 'hSegSlopeOUT' or \
                hist == 'hSegdSlopeOUT':
                self.histos[hist] = DrawOverflow(f.Get(hist))
            else:
                self.histos[hist] = f.Get(hist).Clone()
            self.histos[hist].SetDirectory(0)
    def setTitle(self):
        '''
        Set title = "CSC, Test, HV, TB"
        '''
        title = ''
        if self.m.CSC == 'ME11': title+='ME1/1, '
        else: title+= 'ME2/1, '
        if self.m.test == 'test27': title += 'Test 27, '
        else: title+= 'Test 40, '
        title += '%s, '%self.m.HV
        title += 'TB%s'%self.m.TB
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
    measList = [segHisto(m) for m in measurements if m.CSC=='ME21' and m.test=='Test40']
    for entry in measList:
        print 'CSC:',entry.m.CSC
        print 'Measurement #',entry.m.meas
        print 'STEP Test',entry.m.test
        print 'High Voltage:',entry.m.HV
        print 'Beam status:',entry.m.beam
        print 'Upstream attenuation:',entry.m.uAtt
        print 'Downstream attenuation:',entry.m.dAtt
        print 'Time Stamp:',entry.m.time
        print 'Unpacked file path:',entry.m.fn
        print 'Test Beam:',entry.m.TB
        print 'Title:',entry.title
        print entry.legEntry
        print entry.histos["hNSeg"]
        if entry.ana_dataset: print entry.ana_dataset
        lineStyle = styles[entry.m.meas]
        print lineStyle
        color = colors[entry.m.dAtt]
        print color
        yLimitLow,yLimitHigh = yLimits["hNSeg"]
        print yLimitLow, yLimitHigh
        xAxisTitle,yAxisTitle = histAxesTitles["hNSeg"]
        print xAxisTitle,yAxisTitle
        print
