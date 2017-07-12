'''
Created on 17 Feb 2017

@author: kkuzn
'''
import ME11.ME11DBinfo as ME11DBinfo
import Lumi.LumiDBinfo as LumiDBinfo
from connectPVSSdb import connectPVSSdb

from ROOT import gROOT

import os
from datetime import datetime

if __name__ == '__main__':
    
    gROOT.SetBatch()
    
    orac    = connectPVSSdb()
    
    ME11info = ME11DBinfo.ME11DBInfo(orac.curs)
    #ME11info.printDP_NAME2ID("CAEN/HVME11P", False)
    
#    fill = 5423
#    timestampMin='17.10.16 19:30:00'
#    timestampMax='18.10.16 18:00:00'
##    fill = 5416
#    timestampMin='14.10.16 18:00:00'
#    timestampMax='15.10.16 20:00:00'
#     fill = 5394
#     timestampMin='10.10.16 13:00:00'
#     timestampMax='11.10.16 08:00:00'
#    ??????   fill = 5393
#    timestampMin='09.10.16 10:00:00'
#    timestampMax='10.10.16 08:00:00'
#     fill = 5355
#     timestampMin='02.10.16 13:00:00'
#    timestampMax='03.10.16 07:00:00'
#    fill = 5451
#    timestampMin='26.10.16 08:50:00'
#    timestampMax='26.10.16 23:00:00'
    

    Lumi = LumiDBinfo.LumiDBinfo(orac.curs)
    Lumi.querryLumi(fill, timestampMin, timestampMax, plot=True, verbouse=False, mean=False, printout=False)
    pdfname = "tmp.pdf"
    newpdfname = "f"+str(fill)
    if(len(timestampMax)>0 or len(timestampMin)>0):
        newpdfname+= "_["+timestampMin.replace(" ","_")+"-"+timestampMax.replace(" ","_")+"]"
    newpdfname+=".pdf"    
    print "creating pdf: "+pdfname

    Lumi.canvas.Print(pdfname+"(","pdf");
    
    dpids = []
    rstr  = []
    
    txtoutF = open(newpdfname.replace("pdf", "txt"), "a")
    txtoutF.write("### "+str(datetime.now())+"\n")
    for stationN in range(1,37):
    #stationN = 18
        chamberName = "CSC_ME_P11_C%02d" % (stationN)
        for layer in range(1,7):
        #layer = 6
            DPID        = ME11info.getDPIDfromName(chamberName, layer, verbouse=True)
            dpids.append([DPID,chamberName+"_"+str(layer)])
            #cms_csc_dcs_4:CAEN/HVME11P/board08/channel001     754667    
            rstr.append(ME11info.queryHVvsLumi(DPID, fill, timestampMin, timestampMax, chamberName+"_"+str(layer), verbouse=True))
            ME11info.canvas.Print(pdfname,"pdf");
            print rstr[-1]+"\n\n\n\n\n"
            txtoutF.write(rstr[-1]+"\n")
    
    txtoutF.close()
    
    Lumi.canvas.Print(pdfname+")","pdf"); # just to close file
    for astr in rstr:
        print astr
    del orac

    os.rename(pdfname, newpdfname) # root does not like complicated names :(

#select  diptime, value from CMS_LHC_BEAM_COND.lhc_beammode where DIPTIME>=to_timestamp('17.10.16 00:00:00','dd.mm.rr HH24:MI:SS') and DIPTIME<=to_timestamp('19.10.16 00:00:00','dd.mm.rr HH24:MI:SS') order by DIPTIME;
