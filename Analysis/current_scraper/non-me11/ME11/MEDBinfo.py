'''
Created on 17 Feb 2017

@author: kkuzn
'''

import inspect
import sys

import abc

from datetime import datetime, timedelta
from math import sqrt
from ROOT import TCanvas
from ROOT import TDatime
from ROOT import TGraph
from ROOT import TGraphErrors
from ROOT import TFile
from ROOT import TF1
from ROOT import gROOT
from ROOT import gStyle
from ROOT import TPaveStats

from KPyLib.basics import kout  # printout
from KPyLib.basics import getMeanOverTimeFromDBarray  # 
from KPyLib.basics import getMaxDeltaTimeBetweenPoints

import Lumi.LumiDBinfo as LumiDBinfo

##\brief DB information for ME11
class MEDBInfo:
    __metaclass__ = abc.ABCMeta
    gtitles  =["HVvsT;;HV [V]", "stableHV;;HV [V]","IvsT;;I [uA]", "stableIvsT;;I [uA]", "LvsT;;Lx10^{34} [Hz/cm^{2}]", "stableLvsT;;Lx10^{34} [Hz/cm^{2}]", "stableLAvsT;;Lx10^{34} [Hz/cm^{2}]","IvsL;Lx10^{34} [Hz/cm^{2}];I [uA]", "IvsLA;Lx10^{34} [Hz/cm^{2}];I [uA]"]
    gcolours =[1,        2,         1,      2,           1,        2,            4,           2,       4]
    gmsizes  =[2,       1.5,        2,    1.5,           2,      1.5,           1.5,          2,       2]
    gmstyles =[20,      22,        20,    22,           20,       22,            32,          22,     32]

    max_recursive_calls_ = 720 # h, 30 days  
    lumithresh = 1e-4 # lumi in 1e34 Hz/cm2 where we consider some collisions
    MaxHVdevitation = 10 # V maximal allowed deviation for stable HV values 
    IerrME11 = 0.1
    IerrMEXX = 0.001
    ##\brief requires DB connection cursor (see connectPVSSdb)
    #@param cx_Oracle.connect("").cursor()
    def __init__(self, curs):
        print "\n\nAbstract class constructor (MEDBInfo)\n\n"
        self.curs    = curs
        self.lastQuerryStr = ""
        self.graph   = [None, None, None, None, None, None, None, None, None]
        self.ffunc   = [None, None]
        self.canvas  = None
        self.outFRoot = None
        
        #self.Idata = [[time, I, HV, <lumi>, err(<lumi>), lumi],[...],...]
        self.Idata  = None
        self.HVdata = None
        self.stableHVvalues   = None
        self.stableIrecN  = [None,None] #start stop in record numbers of Idata        
        
        
        #!!!TBD!!! - better definition (HV ON at squeese)
        # self.lumiE30IvaluesD[[lumi,I],[...],...]
        self.lumiE30IvaluesD = None
        
        #!!!TBD!!! - not implemented yet ("do nothing" at beam dump??!)
        self.lumiE30IvaluesM = None

        #current min and max during Lumi
        self.Iminmax = [10000000, -1]
        
        #time query start
        self.time = datetime.now()
        
        self.Lumi = LumiDBinfo.LumiDBinfo(self.curs) 
        
        self.IERR = self.IerrMEXX
    ##\brief prints out the content of CMS_CSC_PVSS_COND.DP_NAME2ID with a given selection
    #@param selection : string for dpname selection, default "" - no selection
    #@param verbouse  : boolean, default False
    def printDP_NAME2ID(self,selection="", verbouse=False):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]
        if verbouse: kout.printFID(selfName, "selection=%s"%selection)
        cmd = """ select dpname, id from CMS_CSC_PVSS_COND.DP_NAME2ID """
        if selection!="":
            cmd+=""" where dpname like '%""" +str(selection)+"""%' """
        cmd+=" order by dpname"
        self.curs.execute(cmd)
        rows  = self.curs.fetchall()
         
        if(len(rows)>0):
            kout.printOUT("%40s %10s" % ("dpname", "id"))
            for data in rows: kout.printOUT("%40s %10s" % (data[0], data[1]))
        else:
            kout.printERR(selfName, "no data found!")

        if verbouse: kout.printQER(cmd)

    ##\brief name is 'CSC_ME_X11_CYY' of 'CSC_ME_X##_CYY' where X is 'P' or 'N' ('CSC_ME_P11_C01'); layers are 1-6
    #     ME11: everything (I, HV, status) in one table with the same dpid, ME## use four different tables (use case for that)
    #     cms_csc_dcs_3:CSC_ME_P21_C07_HV_V12_IMON     103416
    #     cms_csc_dcs_3:CSC_ME_P21_C07_HV_V12_VCOR     873189
    #     cms_csc_dcs_3:CSC_ME_P21_C07_HV_V12_VMON     103415
    #     cms_csc_dcs_3:CSC_ME_P21_C07_HV_V12_VSET     873186
    #@param  stationName : string like 'CSC_ME_X11_CYY', where X is 'P' or 'N', Y is station number
    #@param  layer       : integer 1-6
    #@param  segment     : always 1 for ME11
    #@param  case        : always 0 for ME11
    #@param verbouse     : boolean, default False
    @abc.abstractmethod        
    def getDPIDfromName(self, stationName, layer, segment=1, case=0, verbouse=False):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]
        DPID = -1
        kout.printFID(selfName, stationName+"_L"+str(layer))     
                
        if not(layer in range(1,7)): 
            kout.printERR(selfName, "unknown layer number %d, returning -1"%layer)
            return DPID
        return DPID
    
        
    ##\brief     
    @abc.abstractmethod
    def querryHVLastValue(self, dpid, timestampMax, status=False, verbouse=False, counter=0):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]
        if verbouse: kout.printFID(selfName, "\tstatus = %s, timestampMax = %s, counter = %d"%(str(status), timestampMax, counter))
        
        val = [None,-1]   
        return val



    ##\brief!!!TBD!!! check stable condition interval in case of channel trip....        
    @abc.abstractmethod
    def queryIvsLumi(self, chamberName, segment, layer, fill, timestampMin="", timestampMax="", plotTitle="", verbouse=False):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]
        if verbouse : kout.printFID(selfName,"\t chamberName=%10s; segment=%2d; layer=%2d; fill=%6d; time selection:[%s %s]"%
                                    (chamberName, segment, layer, fill, timestampMin, timestampMax))        
        if (len(timestampMin)==0 or len(timestampMax)==0):kout.printERR(selfName, " without given time ranges still don't work... TBD soon")
        rstr = "" # to be returned            
        return rstr
# ---------------------------------------------------------------------------
    ##\brief prepares canvas, defines root objects         
    def generateReportGraphics(self, plotTitle):
        channelName = plotTitle.split('/')[2]
        rstr = "%17s %6d"%(channelName, (self.time-datetime.now()).microseconds/1000)       
        stHV, stHVerr = getMeanOverTimeFromDBarray(self.stableHVvalues)
        stID, stIDerr = getMeanOverTimeFromDBarray(self.lumiE30IvaluesD)
        stIM, stIMerr = getMeanOverTimeFromDBarray(self.lumiE30IvaluesM)
        rstr+=" %8.1f %5.1f %6.2f %5.2f"%(stHV, stHVerr, stID, stIDerr)
        if(stHV>0):
            for i in range (0,2):
                if(self.ffunc[i]!=None): 
                    rstr+=" %   8.1f %6d"%(self.ffunc[i].GetChisquare(), self.ffunc[i].GetNDF())
                    for ii in range (0,int(self.ffunc[i].GetNpar())):
                        rstr+=" %7.3f %7.3f"%(self.ffunc[i].GetParameter(ii),self.ffunc[i].GetParError(ii))
#             #if self.Iminmax[0]>=0: rstr+="%7.1f %7.1f"%(self.Iminmax[0],self.Iminmax[1])
            rstr+=" %5d %7.1f"%(-1, self.maxDeviationOverFit(False))
            rstr+=" %6.2f %5.2f"%(stIM, stIMerr)
            rstr+=" %8d %6d"%(getMaxDeltaTimeBetweenPoints(self.Idata, 0, self.stableIrecN[0], self.stableIrecN[1]), self.stableIrecN[1]-self.stableIrecN[0]+1) 
        return rstr
               
# ---------------------------------------------------------------------------
    ##\brief prepares canvas, defines root objects         
    def createGraphics(self, verbouse=False):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]

        #gtitles=["HVvsT", "stableHV","IvsT", "stableIvsT", "LvsT", "stableLvsT", "stableLAvsT","IvsL", "IvsLA"]
        #self.Idata = [[time, I, HV, <lumi>, err(<lumi>), lumi],[],...
        
        # HV graph [0]
        for ii in range(0,len(self.HVdata)):
            dt= TDatime(str(self.HVdata[ii][0]))
            t = dt.Convert()
            self.graph[0].SetPoint(ii, t, self.HVdata[ii][1])
        
        # stable HV graph [1]
        nomHV, nomHVerr = getMeanOverTimeFromDBarray(self.stableHVvalues)
        for ii in range(0,len(self.stableHVvalues)):
            dt= TDatime(str(self.stableHVvalues[ii][0]))
            t = dt.Convert()
            self.graph[1].SetPoint(ii, t, nomHV)
            self.graph[1].SetPointError(ii, 0, nomHVerr)
        
        # current [2], stable current [3], lumi[4], stable lumi[5]  stable lumuA[6]
        lcount        = 0
        lcountStable  = 0
        lcountStableA = 0
        IvsL  = []
        IvsLA = []
        self.Iminmax = [10000000, -1]
        for ii in range(0,len(self.Idata)):
            dt= TDatime(str(self.Idata[ii][0]))
            t = dt.Convert()
            stable = (ii>=self.stableIrecN[0] and ii<=self.stableIrecN[1])
            self.graph[2].SetPoint     (ii, t, self.Idata[ii][1]) # current
            if(self.Idata[ii][3]>=0):
                self.graph[4].SetPoint     (lcount, t, self.Idata[ii][3]) # lumi
                self.graph[4].SetPointError(lcount, 0, self.Idata[ii][4])
                lcount+=1
    
                # remove points with undefined lumi (last points and out of fill)
                # remove unstable HV points
                # !!!TBD!!! also HV in proper range can be checked, not done yet
                if( stable  and self.Idata[ii][4]<=0.01):
                    self.graph[3].SetPoint     (lcountStable, t, self.Idata[ii][1]) # current
                    self.graph[5].SetPoint     (lcountStable, t, self.Idata[ii][3]) # <lumi>
                    self.graph[5].SetPointError(lcountStable, 0, self.Idata[ii][4])
                    IvsL.append([self.Idata[ii][3], self.Idata[ii][4], self.Idata[ii][1]])                            
                    lcountStable+=1                            
            if( stable  and self.Idata[ii][5]>=0):
                self.graph[6].SetPoint(lcountStableA, t, self.Idata[ii][5]) 
                IvsLA.append([self.Idata[ii][5], self.Idata[ii][1]])
                lcountStableA+=1                           
                if self.Idata[ii][1]<self.Iminmax[0]: self.Iminmax[0] = self.Idata[ii][1]
                if self.Idata[ii][1]>self.Iminmax[1]: self.Iminmax[1] = self.Idata[ii][1]
                
        IvsL.sort(key=lambda x: x[0])
        IvsLA.sort(key=lambda x: x[0])
        for ii in range (0, len(IvsL)) :
            self.graph[7].SetPoint     (ii, IvsL[ii][0], IvsL[ii][2]) # <lumi>
            self.graph[7].SetPointError(ii, IvsL[ii][1], self.IERR)
        for ii in range (0, len(IvsLA)) :
            self.graph[8].SetPoint     (ii, IvsLA[ii][0], IvsLA[ii][1]) # alternative Lumi
            self.graph[8].SetPointError(ii, 0,            self.IERR)
    
        padN = 1
        for ii in (0,1,2,3,4,5,6,8,7):
            if(verbouse): kout.printFID(selfName, "printing %s for pad %d (%d points)"%(self.gtitles[ii],padN, self.graph[ii].GetN()))                    
            self.graph[ii].SetMarkerStyle(self.gmstyles[ii])
            self.graph[ii].SetMarkerColor(self.gcolours[ii])
            self.graph[ii].SetMarkerSize(self.gmsizes[ii])
            self.graph[ii].SetLineWidth(2)
            self.graph[ii].SetLineColor(self.gcolours[ii])
            
            opt = "AP"
            if ii==0: 
                opt = "APL"
            elif ii==1: 
                opt = "3Psames"
                self.graph[ii].SetFillColor(self.gcolours[ii])
                self.graph[ii].SetFillStyle(30)
            elif (ii==3 or ii==5 or ii==6 or ii==7):
                opt = "Psames"
            if(ii<7):
                self.canvas.GetPad(1).GetPad(padN).cd()
                self.graph[ii].Draw(opt);   
                self.graph[ii].GetXaxis().SetTimeDisplay(1);
                self.graph[ii].GetXaxis().SetNdivisions(507);
                self.graph[ii].GetXaxis().SetTimeFormat("%H:%M");
            else:
                #update HV and Lumi plots
                if ii==7:
                    minT = self.graph[2].GetXaxis().GetXmin()
                    maxT = self.graph[2].GetXaxis().GetXmax()
                    #for ig in (0, 4): self.graph[ig].GetXaxis().SetRangeUser(min,max)
                    for ig in (0, 4): self.graph[ig].GetXaxis().SetLimits(minT,maxT)
                    for ip in (1, 3):
                        self.canvas.GetPad(1).GetPad(ip).Modified()
                        self.canvas.GetPad(1).GetPad(ip).Update()
                    
                self.canvas.GetPad(2).cd()                        
                self.graph[ii].Draw(opt);
                self.graph[ii].Fit(self.ffunc[ii-7])
                self.canvas.GetPad(2).Modified()
                self.canvas.GetPad(2).Update()
                stats =  self.graph[ii].FindObject("stats")
                stats.__class__ = TPaveStats
                if stats!=None:
                    stats.SetLineColor(self.gcolours[ii])
                    stats.SetLineWidth(2)
                    stats.SetY1NDC(.15)       
                    stats.SetY2NDC(.25)       
                    stats.SetX1NDC(0.3+0.3*(ii-7))       
                    stats.SetX2NDC(0.59+0.3*(ii-7))       
                if(ii==8):
                    self.graph[ii].GetXaxis().SetLabelSize(0.04);        
                    self.graph[ii].GetYaxis().SetLabelSize(0.04);        
                    self.graph[ii].GetXaxis().SetTitleSize(0.06);
                    self.graph[ii].GetYaxis().SetTitleSize(0.06);
                    self.graph[ii].GetXaxis().SetTitleOffset(0.75);
                    self.graph[ii].GetYaxis().SetTitleOffset(0.75);
    
                self.canvas.GetPad(2).Modified()
                self.canvas.GetPad(2).Update()
    
    #                     if(ii==0 or ii==2):
    #                         #self.graph[ii].GetXaxis().SetRangeUser(TDatime(str(self.Idata[0][0])).Convert(),TDatime(str(self.Idata[-1][0])).Convert())
            if(ii==1 or ii==3 or ii==6):
                padN+=1
    
            self.canvas.Modified()
            self.canvas.Update()
             
        #print self.outFRoot
        for gr in self.graph: gr.Write()            
        self.outFRoot.Close()
        del self.outFRoot
        self.outFRoot = None
# ---------------------------------------------------------------------------
    ##\brief prepares canvas, defines root objects         
    def prepareGraphics(self, plotTitle,offset):
        if (self.outFRoot!=None): del self.outFRoot
        self.outFRoot = TFile(plotTitle+".root", "RECREATE")
        
        gStyle.SetOptFit(1);             # show fit pars
        gStyle.SetOptTitle(1);           # show graph titles
        gStyle.SetTitleFontSize(0.1);    # graph title size        
        gStyle.SetTitleOffset(.8)
        
        gStyle.SetLabelSize(0.08,  "XY");
        gStyle.SetLabelOffset(0.01,  "XY");        
        gStyle.SetTitleSize(0.08,  "XY");
        gStyle.SetTitleOffset(0.6, "XY");
        
        gStyle.SetNdivisions(505, "XY");       # Ndivs for axis
        gStyle.SetPadLeftMargin(0.1);    # pad left marging
        gStyle.SetPadRightMargin(0.02);
        gStyle.SetPadTopMargin(0.2);    # pad top marging
        gStyle.SetPadBottomMargin(0.1); # pad bottom marging

        if (self.canvas!=None):   del self.canvas
        for g in self.graph: del g
        self.graph   = [None, None, None, None, None, None, None, None, None]
        for f in self.ffunc: del f
        self.ffunc = [None, None]
        
        self.canvas = TCanvas(plotTitle, plotTitle, 2000,1000)
        self.canvas.Divide(2,1,0.01, 0.01)
        self.canvas.GetPad(2).SetTopMargin(0.1)
        self.canvas.GetPad(2).SetBottomMargin(0.1)
        self.canvas.GetPad(1).Divide(1,3, 0.01)
        for i in range (0,9):
            self.graph[i]=TGraphErrors()                     
            self.graph[i].SetTitle(plotTitle+"_"+self.gtitles[i])
            self.graph[i].SetName (plotTitle+"_"+self.gtitles[i])
        ftitle = ['ff','ffA']
        for i in range (0,2):
            if offset:
                self.ffunc[i] = TF1(ftitle[i], "[0]+x*[1]", 0, 1.5);
            else:
                self.ffunc[i] = TF1(ftitle[i], "x*[0]", 0, 1.5);
            self.ffunc[i].SetLineColor(self.gcolours[i+7])

    ##\brief type A not implemented yet
    def maxDeviationOverFit(self, typeA=False):
        maxDev = 0
        for ii in range (self.stableIrecN[0], self.stableIrecN[1]):
            if(self.Idata[ii][4]<=0.01 and self.Idata[ii][3]>0):
                dev = self.Idata[ii][1]-self.ffunc[0].Eval(self.Idata[ii][3])
                #print ii, self.Idata[ii][1], self.ffunc[0].Eval(self.Idata[ii][3])
                if dev>maxDev : maxDev = dev
        return maxDev   
