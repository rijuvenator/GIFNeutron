'''
Created on 17 Feb 2017

@author: kkuzn
'''
import ME11.MEXXDBinfo as MEXXDBinfo
import Lumi.LumiDBinfo as LumiDBinfo
from connectPVSSdb import connectPVSSdb

from ROOT import gROOT

import os
from datetime import datetime

if __name__ == '__main__':
    
    #gROOT.SetBatch()
    
    orac    = connectPVSSdb()
    
    MEXXinfo = MEXXDBinfo.MEXXDBinfo(orac.curs)
    #ME11info.printDP_NAME2ID("CAEN/HVME11P", False)
    
#    fill = 5423
#    timestampMin='17.10.16 19:30:00'
#    #timestampMax='18.10.16 01:30:00'
#    timestampMax='18.10.16 18:00:00'
#    fill = 5401
#    timestampMin='12.10.16 00:00:00'
#   timestampMax='12.10.16 08:00:00'

#5433:['19.10.16 22:00:00','20.10.16 09:00:00'],
    fill = 5433
    timestampMin='19.10.16 22:00:00'
    timestampMax='20.10.16 09:00:00'

    Lumi = LumiDBinfo.LumiDBinfo(orac.curs)
    Lumi.querryLumi(fill, timestampMin, timestampMax, plot=True, verbouse=False, mean=False, printout=False)
    #Lumi.getFillTiming(fill, verbouse=True)
    #exit()
    
    pdfname = "tmp.pdf"
    newpdfname = "f"+str(fill)
    if(len(timestampMax)>0 or len(timestampMin)>0):
        newpdfname+= "_"+timestampMin.replace(" ","_")#+"-"+timestampMax.replace(" ","_")
        newpdfname=newpdfname[:len(newpdfname)-3]+"-"+timestampMax.replace(" ","_")
        newpdfname=newpdfname[:len(newpdfname)-3].replace(":","h")
    newpdfname+=".pdf"    
    print "creating pdf: "+newpdfname
    
    Lumi.canvas.Print(pdfname+"(","pdf");
    
    dpids = []
    rstr  = []
    
    txtoutF = open(newpdfname.replace("pdf", "txt"), "a")
    txtoutF.write("### "+str(datetime.now())+"\n")
    for stationN in range(1,3):
    #stationN = 18
        chamberName = "CSC_ME_M21_C%02d" % (stationN)
        for segment in range(1,2):
            for layer in range(1,3):
            #layer = 6
                print "\n\n\n"
                rstr = MEXXinfo.queryIvsLumi(chamberName, segment, layer, fill, timestampMin, timestampMax, 
                                      plotTitle=chamberName+"_"+str(segment)+"_"+str(layer), verbouse=True)
                MEXXinfo.canvas.Print(pdfname,"pdf");
                print rstr
                #print rstr[-1]+"\n\n\n\n\n"
                #txtoutF.write(rstr[-1]+"\n")
                txtoutF.write(rstr+"\n")    
    txtoutF.close()
    
    Lumi.canvas.Print(pdfname+")","pdf"); # just to close file
    #for astr in rstr:
    #    print astr
    #MEXXinfo.printDP_NAME2ID("M21_C07", verbouse=False)
    del orac

    os.rename(pdfname, newpdfname) # root does not like complicated names :(

