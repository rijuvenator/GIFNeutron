'''
Created on 17 Feb 2017

@author: kkuzn
'''

import inspect

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

from KPyLib.basics import isfloat  # str to float conversion check
from KPyLib.basics import kout  # printout
from KPyLib.basics import getMeanOverTimeFromDBarray  # 
import Lumi.LumiDBinfo as LumiDBinfo
from ME11.ME11mapping import ME11mapping
from KPyLib.basics import getMaxDeltaTimeBetweenPoints


##\brief DB information for ME11
class ME11DBInfo:
    gtitles  =["HVvsT;;HV [V]", "stableHV;;HV [V]","IvsT;;I [uA]", "stableIvsT;;I [uA]", "LvsT;;Lx10^{34} [Hz/cm^{2}]", "stableLvsT;;Lx10^{34} [Hz/cm^{2}]", "stableLAvsT;;Lx10^{34} [Hz/cm^{2}]","IvsL;Lx10^{34} [Hz/cm^{2}];I [uA]", "IvsLA;Lx10^{34} [Hz/cm^{2}];I [uA]"]
    gcolours =[1,        2,         1,      2,           1,        2,            4,           2,       4]
    gmsizes  =[2,       1.5,        2,    1.5,           2,      1.5,           1.5,          2,       2]
    gmstyles =[20,      22,        20,    22,           20,       22,            32,          22,     32]

    max_recursive_calls_ = 720 # h, 30 days  
    lumithresh = 1e-4 # lumi in 1e34 Hz/cm2 where we consider some collisions 
    ##\brief requires DB connection cursor (see connectPVSSdb)
    #@param cx_Oracle.connect("").cursor()
    def __init__(self, curs):
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

    
    ##\brief name is 'CSC_ME_X11_CYY', where X is 'P' or 'N' ('CSC_ME_P11_C01'); layers are 1-6
    #@param  stationName : string like 'CSC_ME_X11_CYY', where X is 'P' or 'N', Y is station number
    #@param  layer       : integer 1-6
    #@param  segment     : always 1 for ME11
    #@param  case        : always 0 for ME11
    #@param verbouse     : boolean, default False
    def getDPIDfromName(self, stationName, layer, segment=1, case=0, verbouse=False):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]
        DPID = -1
        kout.printFID(selfName, stationName+"_L"+str(layer))     
                
        if not(layer in range(1,7) or not(segment==1)): 
            kout.printERR(selfName, "unknown layer number %d or segment number %d,returning -1"%(layer,segment))
            return DPID
                
        side = stationName[7:8]
        fullName = "cms_csc_dcs_4:CAEN/HVME11%s/board%02d/channel%03d" % \
            (side, ME11mapping.CAENchannels_[stationName][layer-1][0], ME11mapping.CAENchannels_[stationName][layer-1][1])
        
        cmd = """ select id from  CMS_CSC_PVSS_COND.DP_NAME2ID where dpname like '%s'""" % fullName
        if verbouse: kout.printQER(cmd)     

        self.curs.execute(cmd)
        rows  = self.curs.fetchall()
        
        if(len(rows)==1):
            DPID = rows[0][0]
        elif(len(rows)==0): 
            kout.printERR(selfName, "no DPID found for stations name %s layer %d, returning -1"%(stationName, layer))
        else:
            kout.printERR(selfName, "several DPID found for station name %s layer %d, returning -1"%(stationName, layer))
                        
        if verbouse: kout.printOUT("%10s, %1d : %30s : %10d" %(stationName, layer, fullName, DPID))
        
        return DPID
    
    
    
    ##\brief !!!TBD!! if timestampMin is not given try -1 h    
    def querryHVLastValue(self, dpid, timestampMax, status=False, verbouse=False, counter=0):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]
        if verbouse: kout.printFID(selfName, "\tstatus = %s, timestampMax = %s, counter = %d"%(str(status), timestampMax, counter))
        
        val = [None,-1]   
        timeMax = datetime.today()     
        try: #here we also check if timestampMax of proper format
            timeMax = datetime.strptime(timestampMax, "%d.%m.%y %H:%M:%S")
        except (ValueError, TypeError):
            kout.printERR(selfName, "error converting time string %s"%timestampMax) 
            return [None,-2]
        #print datetime.strftime((timeMax - timedelta(hours=1)), "%d.%m.%y %H:%M:%S")
        
        timestampMin = datetime.strftime((timeMax - timedelta(hours=1)), "%d.%m.%y %H:%M:%S")
        cmd  = """ select change_date, actual_vmon from CMS_CSC_PVSS_COND.FWCAENCHANNEL where dpid="""+str(dpid)
        cmd +=""" and CHANGE_DATE>=to_timestamp('"""+timestampMin+"""','dd.mm.rr HH24:MI:SS')""" 
        cmd +=""" and CHANGE_DATE<=to_timestamp('"""+timestampMax+"""','dd.mm.rr HH24:MI:SS')"""
        cmd+=""" and actual_vmon is not NULL order by CHANGE_DATE desc"""
        cmd = """select * from ("""+cmd+""") where rownum=1"""
        if status: cmd = cmd.replace("actual_vmon", "ACTUAL_STATUS")
        
        if verbouse: kout.printQER(cmd)
        
        self.curs.execute(cmd)
        rows  = self.curs.fetchall()
        if(len(rows)>0): 
            if verbouse:                 
                if status:
                    kout.printOUT("last HV status for given time range: %s %d"%(rows[0][0], int(rows[0][1])))
                else:
                    kout.printOUT("last HV record for given time range: %s %7.1f V"%(rows[0][0], float(rows[0][1])))                    
            val = [rows[0][0], float(rows[0][1])]
        else:
            if(counter<self.max_recursive_calls_):
                counter+=1
                newTimestamp = datetime.strftime((timeMax - timedelta(hours=1)), "%d.%m.%y %H:%M:%S")
                val = self.querryHVLastValue(dpid, newTimestamp, status, False, counter)
        if (val[0]==None and counter==0): 
            if status:
                kout.printERR(selfName, "no HV status found for %s h before %s"%(self.max_recursive_calls_,timestampMax))
            else:
                kout.printERR(selfName, "no HV records found for %s h before %s"%(self.max_recursive_calls_,timestampMax))        
        return val



    ##\brief!!!TBD!!! check stable condition interval in case of channel trip....        
    def queryHVvsLumi(self, dpid, fill, timestampMin="", timestampMax="", plotTitle="", verbouse=False,offset=True,fitmin=0.0,fitmax=1.5,where='doesnotexist'):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]
        if verbouse : kout.printFID(selfName,"\t dpid=%10d; fill=%6d; time selection:[%s %s]"%(dpid, fill, timestampMin, timestampMax))
        if (len(timestampMin)==0 or len(timestampMax)==0):kout.printERR(selfName, " without given time ranges still don't work... TBD soon")
        rstr = "" # to be returned            

        plot = (plotTitle!="")
        
        Lumi = LumiDBinfo.LumiDBinfo(self.curs)


        timecutStr = ""
        if(len(timestampMax)>0 or len(timestampMin)>0):
            timecutStr = "_["+timestampMin.replace(" ","_")+"-"+timestampMax.replace(" ","_")+"]"
        self.lastQuerryStr = plotTitle+"_f"+str(fill)+timecutStr
        if(plot):
            self.prepareGraphics(self.lastQuerryStr,fill,offset,fitmin,fitmax,where)
        
        if(self.Idata!=None):  del self.Idata
        if(self.HVdata!=None): del self.HVdata
        if(self.stableHVvalues!=None):  del self.stableHVvalues
        if(self.lumiE30IvaluesD!=None): del self.lumiE30IvaluesD 
        if(self.lumiE30IvaluesM!=None): del self.lumiE30IvaluesM 
        self.Idata  = []
        self.HVdata = []
        self.stableHVvalues = []
        self.lumiE30IvaluesD = [] 
        self.lumiE30IvaluesM = [] 

        
        self.HVdata.append(self.querryHVLastValue(dpid, timestampMin, False, verbouse=False)) 
        if(verbouse): kout.printOUT("previous HV = %.1f V at %s"%(self.HVdata[-1][1],self.HVdata[-1][0]))        

        collisions = False
        darkRegions = [False,False]

        self.stableIrecN  = [None,None] #start stop in record numbers of Idata
        checkHV     = False
        
        #!!!TBD!!! more clever check if fill starts 
        lastStatus = -1
        lastLumi   = Lumi.querryLumiLastValue(timestampMin, verbouse=False)[1]
        if(lastLumi>=0):             
            lastStT, lastStatus = self.querryHVLastValue(dpid, timestampMin, True, verbouse=False)
            if(verbouse): kout.printOUT("previous HV status = %s at %s"%(lastStatus, lastStT))
            if(lastStatus==1 and self.HVdata[-1][1]>2100): 
                self.stableIrecN[0]=0
                self.stableHVvalues.append(self.HVdata[-1])
            if(lastLumi>=self.lumithresh): collisions=True
            
        
        cmd  = """ select change_date, actual_vmon, ACTUAL_IMON,  ACTUAL_STATUS from CMS_CSC_PVSS_COND.FWCAENCHANNEL where dpid="""+str(dpid)
        if(timestampMin!=""): cmd +=""" and CHANGE_DATE>=to_timestamp('"""+timestampMin+"""','dd.mm.rr HH24:MI:SS')""" 
        if(timestampMax!=""): cmd +=""" and CHANGE_DATE<=to_timestamp('"""+timestampMax+"""','dd.mm.rr HH24:MI:SS')"""
        cmd+=""" order by CHANGE_DATE, ACTUAL_STATUS"""

        if verbouse:
            kout.printQER(cmd)

        self.curs.execute(cmd)
        rows  = self.curs.fetchall()
         
        count = 0
        if(len(rows)>0):
            if(verbouse): kout.printOUT("%30s %20s %20s %10s"% ("chande_date", "actual_vmon", "actual_imon", "actual_stat"))
            
            printoutstr = []
            iindx       = 0
            ii =-1

            for data in rows:
                ii+=1
                #each column is written individually
                if(verbouse): printoutstr.append("%6d %30s %20s %20s %10s\t" % (count, data[0], data[1], data[2], data[3]))
            
                # treat current record
                if(isfloat(data[2])):                                         
                    #get last lumi record for the current current point
                    lastLumi = Lumi.querryLumiLastValue(data[0].strftime('%d.%m.%y %H:%M:%S'), verbouse=False)
                    if verbouse: printoutstr[ii] +=" %10.3e"%(lastLumi[1])

                    self.Idata.append([data[0], data[2], self.HVdata[-1][1], -1,-1, lastLumi[1]])

                    tmpstr = " --- "
                    if (lastLumi[1]>self.lumithresh):
                        if (darkRegions[0] and self.lumiE30IvaluesD)>0:
                            if(len(self.lumiE30IvaluesD)>0): 
                                prevID = self.lumiE30IvaluesD[-1][1]
                                self.lumiE30IvaluesD.append([data[0], prevID]) #add last point, important for very stable dark currents
                        collisions = True
                        darkRegions[0] = False
                        if(verbouse and self.stableIrecN[0]!=None and self.stableIrecN[1]==None): tmpstr=" *** "
                    else:
                        if (self.stableIrecN[0]!=None and self.stableIrecN[1]==None): # nominal HV 
                            if not(collisions):
                                self.lumiE30IvaluesD.append([data[0],data[2]])
                                darkRegions[0] = True
                                if(verbouse): tmpstr = " DDD "
                            else:
                                self.lumiE30IvaluesM.append([data[0],data[2]])
                                darkRegions[1] = True                                
                                if(verbouse): tmpstr = " MMM "
                    if verbouse: printoutstr[-1]+=tmpstr
                    
                    if(count>0): # we treat lumi for the previous current point! Current is stable for certain lumi range, then current changes and stays for the next lumi range
                        #calculate average lumi for the previous current point                        
                        Lumi.querryLumi(fill, timestampMin=self.Idata[count-1][0].strftime('%d.%m.%y %H:%M:%S'), timestampMax=data[0].strftime('%d.%m.%y %H:%M:%S'), mean=1, plot=False, verbouse=False)
                        #get last lumi value for Armando's style plot
                        if(Lumi.mean[2]!=0): 
                            self.Idata[count-1][3]=Lumi.mean[0]
                            self.Idata[count-1][4]=Lumi.mean[1]/sqrt(Lumi.mean[2])
                            if verbouse: printoutstr[iindx]+="%10.3e   %10.3e"%(self.Idata[count-1][3], self.Idata[count-1][4])

                    count=count+1
                    iindx=ii
                    
                elif(isfloat(data[1])): # HV record
                    self.HVdata.append([data[0], data[1]])
                    if(checkHV and data[1]>2100):
                        self.stableIrecN[0] = count # next current point
                        if not(collisions): self.stableHVvalues=[]                        
                        if count>0 and abs( (self.HVdata[-1][0]-self.Idata[count-1][0]).total_seconds() ) < 0.01 :  
                            self.stableIrecN[0] = count-1 # previous current record if was almost simultaneous
                            if self.Idata[count-1][5]<self.lumithresh:
                                self.lumiE30IvaluesD.append([self.Idata[count-1][0],self.Idata[count-1][1]])
                                darkRegions[0] = True
                                if verbouse: printoutstr[iindx] =printoutstr[iindx].replace("---","DDD")
                        #print "stableN[0]", self.stableIrecN[0], self.stableIrecN[1]
                        checkHV = False
                    if(self.stableIrecN[0]!=None and self.stableIrecN[1]==None):
                        #print ":", len(self.stableHVvalues)
                        self.stableHVvalues.append([data[0], data[1]])
                    
                elif(isfloat(data[3])): # status record (the order: first status, then HV)
                    newStat = int(data[3])
                    #print lastStatus, newStat, collisions
                    if(lastStatus==1 or newStat==1):
                        if newStat==1: checkHV = True
                        if(lastStatus==1 and collisions and self.stableIrecN[0]!=None): # we were in a stable conditions
                            self.stableIrecN[1] = count-1 # last record of stable current
                            darkRegions[1] = False   # end of Malter current regions
                            if(len(self.stableHVvalues)>0):
                                lastHV=self.stableHVvalues[-1][1]
                                self.stableHVvalues.append([data[0],lastHV])
                            if(len(self.lumiE30IvaluesM)==0): # stable currents "malter" currents (dark current after irradiation)
                                self.lumiE30IvaluesM.append([self.Idata[count-1][0],self.Idata[count-1][1]])
                                self.lumiE30IvaluesM.append([data[0],self.Idata[count-1][1]])
                                if verbouse: printoutstr[iindx] =printoutstr[iindx].replace("***","MMM")
                        elif (lastStatus==1 and not(collisions)):
                            #print "HERE"
                            self.stableHVvalues = []
                            self.lumiE30IvaluesD = []
                            self.stableIrecN[0]=None
                            if verbouse: printoutstr[ii]+="\n Cleaning dark currents!\n"
                    lastStatus = newStat

            # after the loop over data     
            
            # just for nice graphs
            if(isfloat(rows[-1][2])): # last record was current
                lastHV = self.HVdata[-1][1]
                self.HVdata.append([rows[-1][0],lastHV]) # last HV value corresponds to the time of last current point 
                if(self.stableIrecN[1]==None):           # if all last current points are at stable HV
                    self.stableHVvalues.append(self.HVdata[-1]) # do the same for stableHV
                    self.stableIrecN[1] = count-1
            
            #just for nice graphs        
            self.HVdata[0][0]=datetime.strptime(timestampMin, "%d.%m.%y %H:%M:%S")

            if(self.stableIrecN[1]==None): self.stableIrecN[1] = len(self.Idata)-1

            if verbouse:
                for adatastr in printoutstr:
                    kout.printOUT(adatastr)
            
            if verbouse: kout.printOUT("StableConditions: %s"%str(self.stableIrecN))
            #for ll in self.stableHVvalues:
            #    print ll
            print "dark currents:"
            for ll in self.lumiE30IvaluesD:
                print ll            
            #print "malter currents:"
            #for ll in self.lumiE30IvaluesM:
            #    print ll            

            if plot: 
                self.createGraphics(verbouse)
                rstr = self.generateReportGraphics(plotTitle)
        else:
            kout.printERR(selfName, "no data found")
        
        
        return rstr
# ---------------------------------------------------------------------------
    ##\brief prepares canvas, defines root objects         
    def generateReportGraphics(self, plotTitle):
        rstr = " %17s %6d "%(plotTitle, (self.time-datetime.now()).microseconds/1000)       
        stHV, stHVerr = getMeanOverTimeFromDBarray(self.stableHVvalues)
        stID, stIDerr = getMeanOverTimeFromDBarray(self.lumiE30IvaluesD)
        stIM, stIMerr = getMeanOverTimeFromDBarray(self.lumiE30IvaluesM)
        rstr+=" %8.1f %5.1f %6.2f %5.2f "%(stHV, stHVerr, stID, stIDerr)
        if(stHV>0):
            for i in range (0,2):
                if(self.ffunc[i]!=None): 
                    rstr+=" %   8.1f %6d "%(self.ffunc[i].GetChisquare(), self.ffunc[i].GetNDF())
                    for ii in range (0,int(self.ffunc[i].GetNpar())):
                        rstr+=" %7.3f %7.3f "%(self.ffunc[i].GetParameter(ii),self.ffunc[i].GetParError(ii))
            #if self.Iminmax[0]>=0: rstr+="%7.1f %7.1f"%(self.Iminmax[0],self.Iminmax[1])
            rstr+=" %5d %7.1f "%(-1, self.maxDeviationOverFit(False, verbouse=True))
            rstr+=" %6.2f %5.2f "%(stIM, stIMerr)
            rstr+=" %8d %6d "%(getMaxDeltaTimeBetweenPoints(self.Idata, 0, self.stableIrecN[0], self.stableIrecN[1]), self.stableIrecN[1]-self.stableIrecN[0]+1) 
        return rstr
               
# ---------------------------------------------------------------------------
    ##\brief prepares canvas, defines root objects         
    def createGraphics(self, verbouse=False, fitmin=0.0,fitmax=1.5):
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
            self.graph[7].SetPointError(ii, IvsL[ii][1], 0.1)
        for ii in range (0, len(IvsLA)) :
            self.graph[8].SetPoint     (ii, IvsLA[ii][0], IvsLA[ii][1]) # alternative Lumi
            self.graph[8].SetPointError(ii, 0,            0.1)
    
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
                self.graph[ii].GetXaxis().SetLimits(0.0,1.5)
                self.graph[ii].Draw(opt);
                self.graph[ii].Fit(self.ffunc[ii-7],'R')
                #self.graph[ii].Fit(self.ffunc[ii-7],'R','',fitmin,fitmax)
                self.canvas.GetPad(2).Modified()
                self.canvas.GetPad(2).Update()
                stats =  self.graph[ii].FindObject('stats')
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
             
        print self.outFRoot
        for gr in self.graph: gr.Write()            
        self.outFRoot.Close()
        del self.outFRoot
        self.outFRoot = None
# ---------------------------------------------------------------------------
    ##\brief prepares canvas, defines root objects         
    def prepareGraphics(self, plotTitle,fill,offset,fitmin=0.0,fitmax=1.5,where='doesnotexist'):
        if (self.outFRoot!=None): del self.outFRoot
        self.outFRoot = TFile(where+'/fill'+str(fill)+'/'+plotTitle+".root", "RECREATE")
		#self.outFRoot = TFile('results_noOffset/fill'+str(fill)+'/'+plotTitle+".root", "RECREATE")
        
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
                self.ffunc[i] = TF1(ftitle[i], "[0]+x*[1]", fitmin,fitmax)
                self.ffunc[i].SetLineColor(self.gcolours[i+7])
            else:
                self.ffunc[i] = TF1(ftitle[i], "x*[0]", fitmin,fitmax)
                self.ffunc[i].SetLineColor(self.gcolours[i+7])

    ##\brief type A not implemented yet
    def maxDeviationOverFit(self, typeA=False, verbouse=False):
        maxDev = 0
        if verbouse: kout.printOUT("calculating deviation per each point of Idata: #, Idata, fitfunc")
        for ii in range (self.stableIrecN[0], self.stableIrecN[1]):
            if(self.Idata[ii][4]<=0.01 and self.Idata[ii][3]>0):
                ff  = self.ffunc[0].Eval(self.Idata[ii][3])
                dev = self.Idata[ii][1]-ff
                if verbouse: kout.printOUT("%5d %8.2f %8.2f %8.2f"%(ii, self.Idata[ii][1], ff, dev))
                if dev>maxDev : maxDev = dev
        return maxDev   
