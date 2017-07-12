#! /usr/bin/env python
from ROOT import TCanvas
from ROOT import TDatime
from ROOT import TGraph
from ROOT import TGraphErrors
from ROOT import TFile
from ROOT import gROOT
from ROOT import gStyle

from datetime import timedelta, datetime, tzinfo
import getpass
import inspect
from math import sqrt
import time

from KPyLib.basics import kout     # printout
from KPyLib.basics import isfloat  # str to float conversion check
# ---------------------------------------------------------------------------
class LumiDBinfo:
    max_recursive_calls_ = 60 # min  

    def __init__(self, curs):
        self.curs     = curs
        self.graph    = None
        self.canvas   = None
        self.outfname = None
        self.mean  = [-1,-1,0]        
    
    ##\brief - !!!TBD!!! to be done different way!!! just a template
    def getFillTiming(self, fill, verbouse="FALSE"):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]
        if verbouse: kout.printFID(selfName)
        cmd  = """ select DIPTIME from CMS_BEAM_COND.CMS_BRIL_LUMINOSITY where DATAQUALITY=1 and FILL=""" +str(fill)+" order by diptime"
        r1cmd = """ select * from ("""+cmd+""") where rownum=1"""
        if verbouse: kout.printQER(r1cmd)
        self.curs.execute(cmd)
        rows  = self.curs.fetchall()
        if(len(rows)>0):
            if(verbouse): kout.printOUT(rows[0][0])
    
    ##\brief !!!TBD!! if timestampMin is not given try -1 h
    def querryLumiLastValue(self, timestampMax, verbouse=False, counter=0):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]
        if verbouse: kout.printFID(selfName)
        
        val = [None,-1]
        timeMax = datetime.today()     
        try:#here we also check if timestampMax of proper format
            timeMax = datetime.strptime(timestampMax, "%d.%m.%y %H:%M:%S")
        except (ValueError, TypeError):
            kout.printERR(selfName, "error converting time string %s"%timestampMax) 
            return [None,-2]

        timestampMin = datetime.strftime((timeMax - timedelta(minutes=1)), "%d.%m.%y %H:%M:%S")                                    
        cmd  = """ select DIPTIME, INSTLUMI from CMS_BEAM_COND.CMS_BRIL_LUMINOSITY where DATAQUALITY=1"""        
        cmd +=""" and DIPTIME>=to_timestamp('"""+timestampMin+"""','dd.mm.rr HH24:MI:SS')""" 
        cmd +=""" and DIPTIME<=to_timestamp('"""+timestampMax+"""','dd.mm.rr HH24:MI:SS')"""
        cmd +=""" order by DIPTIME desc"""
        cmd = """select * from ("""+cmd+""") where rownum=1"""
        if verbouse: kout.printQER(cmd)
        
        self.curs.execute(cmd)
        rows  = self.curs.fetchall()
        if(len(rows)>0): 
            if verbouse: kout.printOUT("last lumi record for given time range: %s %.3e e34[Hz/cm2]"%(rows[0][0], float(rows[0][1])/10000.0))
            val = [rows[0][1], float(rows[0][1])/10000.0]
        else:
            if(counter<self.max_recursive_calls_):
                counter+=1
                newTimestamp = datetime.strftime((timeMax - timedelta(minutes=1)), "%d.%m.%y %H:%M:%S")
                val = self.querryLumiLastValue(newTimestamp, verbouse, counter)
        if val[0]==None: kout.printERR(selfName, "no lumi records found for %d min before %s"%(self.max_recursive_calls_,timestampMax))                            
        return val
        
        
                
    def querryLumi(self, fill, timestampMin="", timestampMax="", mean=0, plot=False, printout=False, verbouse=False):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]
        
        self.mean  = [-1,-1,0]
        
        if(plot): #check if graph exists
            if(self.graph!=None):
                del self.graph
                del self.canvas
            self.canvas   = TCanvas("Lumi")
            self.graph    = TGraphErrors()    
            fillName = "fill "+str(fill)
            if(timestampMax!="" or timestampMin!=""): fillName+="[%s - %s]"%(timestampMin,timestampMax);
            self.graph.SetTitle(fillName+";time;Lumi x10^{34} [Hz/cm^{2}]")
            self.graph.SetName ("fill_"+str(fill))
            self.outfname = "Lumi_"+fillName
            #rootFile      = TFile(self.outfname+".root")
            
        if verbouse: kout.printFID(selfName)

        cmd  = """ select DIPTIME, INSTLUMI, RUN from CMS_BEAM_COND.CMS_BRIL_LUMINOSITY where DATAQUALITY=1 and FILL=""" +str(fill)        
        if(timestampMin!=""): cmd +=""" and DIPTIME>=to_timestamp('"""+timestampMin+"""','dd.mm.rr HH24:MI:SS')""" 
        if(timestampMax!=""): cmd +=""" and DIPTIME<=to_timestamp('"""+timestampMax+"""','dd.mm.rr HH24:MI:SS')"""
        if(mean==0):          cmd+="""  and INSTLUMI>0.1"""
        cmd +=""" order by DIPTIME"""

        
        self.curs.execute(cmd)
        rows  = self.curs.fetchall()
        
        mvals=[] # for mean calculation
        count = 0   
        if(len(rows)>0): 
            if(printout): kout.printOUT("%10s %30s %20s %10s %20s"% ("POINT#","DIPTIME", "LUMI_TOTINST", "RUN", "time converted"))                
            for data in rows:
                dt= TDatime(str(data[0]))
                t = dt.Convert()
                if(printout): kout.printOUT("%10d %30s %20.3e %10s %20d" % (count, data[0], float(data[1])/10000.0, data[2], t))
                if(mean==1):          mvals.append(float(data[1])/10000.0)
                if(plot):             
                    self.graph.SetPoint(count, t, float(data[1])/10000.0)                
                    #self.canvas.Write()
                    #rootFile.Close()
                    #self.graph.GetXaxis().SetTimeOffset(0,"gmt");  
                count=count+1   
            if(plot):
                self.graph.SetMarkerStyle(20)
                self.graph.Draw("AP");
                self.graph.GetXaxis().SetTimeDisplay(1);
                self.graph.GetXaxis().SetNdivisions(507);
                self.graph.GetXaxis().SetTimeFormat("%H:%M");
                self.canvas.Modified()
                self.canvas.Update()
            if(mean==1):
                themean = 0
                for m in mvals: themean+=m
                themean=themean/len(mvals)
                thesigm2 = 0
                for m in mvals:
                    delta = m-themean
                    thesigm2+=(delta*delta)
                self.mean[0] = themean
                self.mean[1] = sqrt(thesigm2/len(mvals))
                self.mean[2] = len(mvals)
        else: kout.printERR(selfName, "no data found for given fill %d and timing [%s, %s]"%(fill, timestampMin, timestampMax))
        
        if verbouse: 
            kout.printQER(cmd)
            kout.printOUT("number of points : %d"%count)
            if(mean>0 and self.mean[2]>0): 
                kout.printOUT("mean, err(mean), rms [x e34 Hz/cm2], rms/mean: %6.2e %6.2e %6.2e"%
                                      (self.mean[0], self.mean[1]/sqrt(self.mean[2]), self.mean[1]))
# ---------------------------------------------------------------------------
class ME11Info:
    def __init__(self, curs):
        self.curs    = curs
        self.graph   = [None, None]
        self.canvas  = None
    
# ---------------------------------------------------------------------------
    
