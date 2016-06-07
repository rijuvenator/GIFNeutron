#!/usr/bin/env python
import os 

hists = [
    "hNStripHits",
    "hNWireHits",
    "hNRecHits",
    "nSeg",
    "hnRecHitsAll",
    "hnRecHitsMax",
    "hSegPos2D_1",
    "hSegPos2D_2",
    "hSegInBeam",
    "hSegPos2DBeam_1",
    "hSegPos2DBeam_2",
    "hSegPos2DBkgd_1",
    "hSegPos2DBkgd_2",
    "hSegSlopeBeam_1",
    "hSegSlopeBeam_2",
    "hSegSlopeBkgd_1",
    "hSegSlopeBkgd_2",
    "hSegChi2Beam",
    "hSegChi2Bkgd",
    "hSegNHitsBeam",
    "hSegNHitsBkgd",
    "hNSegGoodQuality",
    ]

dirs = [
    # "ME11Test27",
    # "ME11Test40", 
    "ME21Test27", 
    "ME21Test40", 
    ]  

for d in dirs:  
    outfile = "merged" + d + ".pdf" 
    cmd = "gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=" + outfile 
    for h in hists:  
        cmd += " " + d + "/" + h + ".pdf" 
    os.system(cmd)  
    print "executed cmd: " + cmd 





