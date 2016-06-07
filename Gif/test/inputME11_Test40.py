#!/usr/bin/env python
import copy 

from inputME21_Test40 import hists

plotBase = {
    "name" : "plotBase", 
    "file1" : "outputPlots/STEP_40_000_160506_015143_UTC_analysis.root", 
    "file2" : "outputPlots/STEP_40_000_160506_125054_UTC_analysis.root", 
    "label1" : "Source off", 
    "label2" : "Source on (HL-LHC)", 
    "color1" : 1, 
    "color2" : 2, 
}

plots = [ ] # empty list 

for hist in hists:
    plot = copy.deepcopy(plotBase)
    plot["name"] = hist
    plots.append(plot)

title = "ME1/1 Test 40 (scintillator trigger)"  
outputDir = "ME11Test40/" 




