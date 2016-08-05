#!/usr/bin/env python
import copy 

plotBase = {
    "name" : "plotBase", 
    "file1" : "outputPlots/STEP_40_000_160509_111100_UTC_analysis.root", 
    "file2" : "outputPlots/STEP_40_000_160506_222510_UTC_analysis.root",  
    "label1" : "Source off", 
    "label2" : "Source on (HL-LHC)", 
    "color1" : 1, 
    "color2" : 2, 
}

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

plots = [ ] # empty list 

for hist in hists:
    plot = copy.deepcopy(plotBase)
    plot["name"] = hist
    plots.append(plot)

title = "ME2/1 Test 40 (scintillator trigger)"  
outputDir = "ME21Test40/" 




