'''
Created on 6 Mar 2017

@author: kkuzn
'''
import inspect
from math import sqrt

from datetime import timedelta, datetime

from ME11.MEDBinfo import MEDBInfo

#from KPyLib.basics import isfloat  # str to float conversion check
from KPyLib.basics import kout  # printout
#from KPyLib.basics import getMeanOverTimeFromDBarray  # 
from KPyLib.basics import isfloat  # str to float conversion check

class MEXXDBinfo(MEDBInfo):
    '''
    classdocs
    '''


    ##\brief name is 'CSC_ME_X11_CYY' of 'CSC_ME_X##_CYY' where X is 'P' or 'N' ('CSC_ME_P11_C01'); layers are 1-6
    #     ME11: everything (I, HV, status) in one table with the same dpid, ME## use four different tables (use case for that)
    #     cms_csc_dcs_3:CSC_ME_P21_C07_HV_V12_IMON     103416
    #     cms_csc_dcs_3:CSC_ME_P21_C07_HV_V12_VCOR     873189
    #     cms_csc_dcs_3:CSC_ME_P21_C07_HV_V12_VMON     103415
    #     cms_csc_dcs_3:CSC_ME_P21_C07_HV_V12_VSET     873186
    #@param  stationName : string like 'CSC_ME_X11_CYY', where X is 'P' or 'N', Y is station number
    #@param  layer       : integer 1-6
    #@param  segment     : HV segment
    #@param  case        : always 0 for ME11
    #@param verbouse     : boolean, default False
    def getDPIDfromName(self, stationName, layer, segment, case, verbouse=False):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]
        DPID = []
        kout.printFID(selfName, stationName+"_S"+str(segment)+"_L"+str(layer))     

        valCases = {1:"VMON", 2:"IMON", 3:"VSET", 4:"VCOR" }
        dcsCases = {'M':2, 'P':3}
        #!!!TBD!!! - check segnemt vs chambertype        
        side = stationName[7:8]
        if not(layer in range(1,7)) or not(case in valCases): 
            kout.printERR(selfName, "unknown layer number %d or segment number %d or value '%s', returning -1"%(layer,segment, case))
            return DPID
                
        HVchannel = (segment-1)*6+layer
        fullName = "cms_csc_dcs_%d:%s_HV_V%02d_%s" %(dcsCases[side], stationName, HVchannel, valCases[case])        
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
                        
        if verbouse: kout.printOUT("%10s, %1d, %1d (%4s) : %30s : %10d" %(stationName, segment, layer, valCases[case], fullName, DPID))
        
        return DPID


    
    def querryHVSETTIMGrecords(self,dpidHV, dpidCorr, timestampMin="", verbouse=False):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]
        if verbouse: kout.printFID(selfName, "dpidHV=%d, dpidCorr=%d, timestampMin = %s"%(dpidHV, dpidCorr, timestampMin))
        
        val    = 3600.0
        corr   = 0.0
        update = None

        #cmd = """ select change_date, value, dpe_status, dpe_position, updateid from  CMS_CSC_PVSS_COND.CSC_HV_SETTINGS_DATA where dpid=%d""" % dpidHV
        cmd = """ select change_date, value from  CMS_CSC_PVSS_COND.CSC_HV_SETTINGS_DATA where dpid=%d""" % dpidHV
        cmd +=""" and CHANGE_DATE<to_timestamp('"""+timestampMin+"""','dd.mm.rr HH24:MI:SS')""" 
        cmd +=""" order by CHANGE_DATE desc"""
        cmd = """select * from ("""+cmd+""") where rownum=1"""

        if verbouse: kout.printQER(cmd)     

        self.curs.execute(cmd)
        rows   = self.curs.fetchall()          
        if(len(rows)==0):
            if verbouse: kout.printERR(selfName, "no HV setting found for dpidHV=%d, timestampMin = %s, will return 3600 V"%(dpidHV, timestampMin))            
            return val, corr, update
        else:
            val    = float(rows[0][1])
            update = rows[0][0] 
            if verbouse: kout.printOUT("last HV settings for given time range: %s %6.1f"%(rows[0][0], float(rows[0][1])))
        cmd = """ select change_date, value from  CMS_CSC_PVSS_COND.CSC_HV_SETTINGS_DATA where dpid=%d""" % dpidCorr
        cmd +=""" and CHANGE_DATE<to_timestamp('"""+timestampMin+"""','dd.mm.rr HH24:MI:SS')""" 
        cmd +=""" order by CHANGE_DATE desc"""
        cmd = """select * from ("""+cmd+""") where rownum=1"""

        if verbouse: kout.printQER(cmd)     

        self.curs.execute(cmd)
        rows   = self.curs.fetchall()
        if(len(rows)==0):
            if verbouse: kout.printERR(selfName, "no HV corrections found for dpidHV=%d, timestampMin = %s, will return 0 V"%(dpidCorr, timestampMin))            
            return val, corr, update
        else:
            corr    = float(rows[0][1])
            update = rows[0][0] #!!!TBD!!! return the most recent date 
            if verbouse: kout.printOUT("last HV corrections for given time range: %s %6.1f"%(rows[0][0], float(rows[0][1])))
        return val, corr, update
    
    
    
        
    def querryHVrecords(self,dpid,timestampMin="", timestampMax="", setHV=3600, verbouse=False):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]
        
        if(self.HVdata!=None): del self.HVdata
        if(self.stableHVvalues!=None):  del self.stableHVvalues
        self.HVdata = []
        self.stableHVvalues = []

        self.querryHVLastValue(dpid, timestampMin, False, verbouse=verbouse)
        self.HVdata.append(self.querryHVLastValue(dpid, timestampMin, False, verbouse=verbouse)) 
        if(verbouse): kout.printOUT("previous HV = %.1f V at %s"%(self.HVdata[-1][1],self.HVdata[-1][0]))        

        if verbouse: kout.printFID(selfName, "dpid=%d, timestampMin = %s, timestampMax = %s, setHV = %6.1f V"%(dpid, timestampMin, timestampMax, setHV))
        cmd = """ select change_date, value, dpe_status, dpe_position, updateid from  CMS_CSC_PVSS_COND.CSC_HV_V_DATA where dpid=%d""" % dpid
        cmd +=""" and CHANGE_DATE>=to_timestamp('"""+timestampMin+"""','dd.mm.rr HH24:MI:SS')""" 
        cmd +=""" and CHANGE_DATE<=to_timestamp('"""+timestampMax+"""','dd.mm.rr HH24:MI:SS')"""
        cmd +=""" order by CHANGE_DATE"""

        if verbouse: kout.printQER(cmd)     

        self.curs.execute(cmd)
        rows  = self.curs.fetchall()
        stableFlag = False
        lowerFlag  = False
        for data in rows:
            self.HVdata.append([data[0], data[1]])
            if abs(data[1]-setHV)<self.MaxHVdevitation:
                if(lowerFlag): 
                    self.stableHVvalues=[]
                    lowerFlag = False
                stableFlag = True
                self.stableHVvalues.append(self.HVdata[-1])
            elif (stableFlag and data[1]<setHV-self.MaxHVdevitation):
                self.stableHVvalues.append([data[0]-timedelta(seconds=1), self.stableHVvalues[-1][1]])
                lowerFlag = True
        if verbouse:
            kout.printOUT("HV values:")
            for HV in self.HVdata:
                kout.printOUT("\t%s %8.2f"%(str(HV[0]), HV[1]))
            kout.printOUT("stable HV values:")
            for HV in self.stableHVvalues:
                kout.printOUT("\t%s %8.2f"%(str(HV[0]), HV[1]))




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
        cmd  = """ select change_date, value from CMS_CSC_PVSS_COND.CSC_HV_V_DATA where dpid="""+str(dpid)
        cmd +=""" and CHANGE_DATE>=to_timestamp('"""+timestampMin+"""','dd.mm.rr HH24:MI:SS')""" 
        cmd +=""" and CHANGE_DATE<=to_timestamp('"""+timestampMax+"""','dd.mm.rr HH24:MI:SS')"""
        cmd+=""" and value is not NULL order by CHANGE_DATE desc"""
        cmd = """select * from ("""+cmd+""") where rownum=1"""
        if status: cmd = cmd.replace("value", "dpe_status") #!!!TBD!! check what id dpe_status????
        
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
                val = self.querryHVLastValue(dpid, newTimestamp, status, True, counter)
        if (val[0]==None and counter==0): 
            if status:
                kout.printERR(selfName, "no HV status found for %s h before %s"%(self.max_recursive_calls_,timestampMax))
            else:
                kout.printERR(selfName, "no HV records found for %s h before %s"%(self.max_recursive_calls_,timestampMax))        
        return val



                
    def queryIvsLumi(self, chamberName, segment, layer, fill, timestampMin="", timestampMax="", plotTitle="", verbouse=False,offset=False):
        selfName = self.__class__.__name__+"."+inspect.stack()[0][3]
        if verbouse : kout.printFID(selfName,"\t chamberName=%10s; segment=%2d; layer=%2d; fill=%6d; time selection:[%s %s]"%
                                    (chamberName, segment, layer, fill, timestampMin, timestampMax))
        if (len(timestampMin)==0 or len(timestampMax)==0):kout.printERR(selfName, " without given time ranges still don't work... TBD soon")

        plot = (plotTitle!="")
        
        timecutStr = ""
        if(len(timestampMax)>0 or len(timestampMin)>0):
            timecutStr = "_["+timestampMin.replace(" ","_")+"-"+timestampMax.replace(" ","_")+"]"
        self.lastQuerryStr = plotTitle+"_f"+str(fill)+timecutStr
        if(plot):
            self.prepareGraphics(self.lastQuerryStr,offset)

        if(self.Idata!=None):           del self.Idata
        if(self.lumiE30IvaluesD!=None): del self.lumiE30IvaluesD 
        if(self.lumiE30IvaluesM!=None): del self.lumiE30IvaluesM 
        self.Idata  = []
        self.lumiE30IvaluesD = [] 
        self.lumiE30IvaluesM = [] 
        
        rstr = "" # to be returned            
        
        # HV part       
        DPIDval        = self.getDPIDfromName(chamberName, layer, segment, case=3, verbouse=verbouse)
        DPIDcorr       = self.getDPIDfromName(chamberName, layer, segment, case=4, verbouse=verbouse)
        HVsettings     = self.querryHVSETTIMGrecords(DPIDval, DPIDcorr, timestampMin, verbouse=verbouse)
        #print "====>", HVsettings[0], HVsettings[1], HVsettings[0]+HVsettings[1], HVsettings[2]

        self.stableHV = HVsettings[0]+HVsettings[1]
        if(verbouse):
            kout.printFID(selfName, "stable HV value = %6.1f"%self.stableHV)
        dpidHV        = self.getDPIDfromName(chamberName, layer, segment, case=1, verbouse=verbouse)
                
        self.querryHVrecords(dpidHV, timestampMin, timestampMax, self.stableHV, verbouse=verbouse)
        if len(self.stableHVvalues)==0: # no stable HV is found
            return plotTitle
        
        
        collisions = False
        darkRegions = [False,False]

        self.stableIrecN  = [None,None] #start stop in record numbers of Idata
        checkHV     = False
        
        #!!!TBD!!! more clever check if fill starts 
        lastStatus = -1
        lastLumi   = self.Lumi.querryLumiLastValue(timestampMin, verbouse=False)[1]
        
        if(lastLumi>0):             #!!!TBD!!! to be optimised here (this call is done twice...)
            lastStT, lastStatus = self.querryHVLastValue(dpidHV, timestampMin, True, verbouse=verbouse)
            if(verbouse): kout.printOUT("previous HV status = %s at %s"%(lastStatus, lastStT))
            if(lastStatus==1 and self.HVdata[-1][1]>self.stableHV-self.MaxHVdevitation): 
                self.stableIrecN[0]=0
                self.stableHVvalues.append(self.HVdata[-1])
            if(lastLumi>=self.lumithresh): collisions=True
            


        dpidI        = self.getDPIDfromName(chamberName, layer, segment, case=2, verbouse=verbouse)
        #here the query will be done for stable HV only!
        timestampMin = datetime.strftime(self.stableHVvalues[0][0],  "%d.%m.%y %H:%M:%S")
        timestampMax = datetime.strftime(self.stableHVvalues[-1][0], "%d.%m.%y %H:%M:%S")
        
        cmd  = """ select change_date, value from CMS_CSC_PVSS_COND.CSC_HV_I_DATA where dpid="""+str(dpidI)
        if(timestampMin!=""): cmd +=""" and CHANGE_DATE>=to_timestamp('"""+timestampMin+"""','dd.mm.rr HH24:MI:SS')""" 
        if(timestampMax!=""): cmd +=""" and CHANGE_DATE<=to_timestamp('"""+timestampMax+"""','dd.mm.rr HH24:MI:SS')"""
        cmd+=""" order by CHANGE_DATE"""

        if verbouse:
            kout.printQER(cmd)

        self.curs.execute(cmd)
        rows  = self.curs.fetchall()
         
        count = 0

        if(len(rows)>0):
            if(verbouse): kout.printOUT("%30s %20s %20s"% ("chande_date", "actual_vmon", "actual_imon"))
            
            printoutstr = []
            iindx       = 0
            ii =-1

            for data in rows:
                ii+=1
                
                # treat current record
                if(isfloat(data[1])):                                         
                    if(verbouse): printoutstr.append("%6d %30s %6.1f %10.3f\t" % (count, data[0], self.stableHV, float(data[1])/1000.))

                    #get last lumi record for the current current point
                    lastLumi = self.Lumi.querryLumiLastValue(data[0].strftime('%d.%m.%y %H:%M:%S'), verbouse=False)
                    if verbouse: printoutstr[ii] +=" %10.3e"%(lastLumi[1])

                    #self.Idata.append([data[0], data[1], self.HVdata[-1][1], -1,-1, lastLumi[1]])
                    self.Idata.append([data[0], float(data[1])/1000., self.stableHV, -1,-1, lastLumi[1]])
                    tmpstr = " --- "
                    if (lastLumi[1]>self.lumithresh):
                        if (darkRegions[0] and self.lumiE30IvaluesD)>0:
                            if(len(self.lumiE30IvaluesD)>0): 
                                prevID = self.lumiE30IvaluesD[-1][1]
                                self.lumiE30IvaluesD.append([data[0], prevID]) #add last point, important for very stable dark currents
                        collisions = True
                        darkRegions[0] = False
                        if(verbouse): tmpstr=" *** "
                    else:
                        if not(collisions):
                            self.lumiE30IvaluesD.append([data[0],data[1]])
                            darkRegions[0] = True
                            if(verbouse): tmpstr = " DDD "
                        else:
                            self.lumiE30IvaluesM.append([data[0],data[1]])
                            darkRegions[1] = True                                
                            if(verbouse): tmpstr = " MMM "
                    if verbouse: printoutstr[-1]+=tmpstr
                    
                    if(count>0): # we treat lumi for the previous current point! Current is stable for certain lumi range, then current changes and stays for the next lumi range
                        #calculate average lumi for the previous current point                        
                        self.Lumi.querryLumi(fill, timestampMin=self.Idata[count-1][0].strftime('%d.%m.%y %H:%M:%S'), timestampMax=data[0].strftime('%d.%m.%y %H:%M:%S'), mean=1, plot=False, verbouse=False)
                        #get last lumi value for Armando's style plot
                        if(self.Lumi.mean[2]!=0): 
                            self.Idata[count-1][3]=self.Lumi.mean[0]
                            self.Idata[count-1][4]=self.Lumi.mean[1]/sqrt(self.Lumi.mean[2])
                            if verbouse: printoutstr[iindx]+="%10.3e   %10.3e"%(self.Idata[count-1][3], self.Idata[count-1][4])

                    count=count+1
                    iindx=ii
                    
            # after the loop over data     
            if verbouse:
                for adatastr in printoutstr:
                    kout.printOUT(adatastr)
            
            self.stableIrecN[0] = 0
            self.stableIrecN[1] = count -1
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
