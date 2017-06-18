'''
Created on 2 Mar 2017

@author: kkuzn
'''
from ROOT import TFile
from ROOT import TCanvas
from ROOT import TGraphErrors
from ROOT import TH2F
from ROOT import TH1F
from ROOT import gStyle

from KPyLib.basics import appendToDictOfArr, weightedMean
from KPyLib.basics import kout  # printout

import sys
import os

if __name__ == '__main__':
    #fname    =  "../plotsME11Pall/f5423_[17.10.16_19:30:00-18.10.16_18:00:00].txt"
    #fname    =  "../plotsME11Pall/f5416_[14.10.16_18:00:00-15.10.16_20:00:00].txt"
    #fname    =  "../plotsME11Pall/f5394_[10.10.16_13:00:00-11.10.16_08:00:00].txt"
    #fname    =  "../plotsME11Pall/f5355_[02.10.16_13:00:00-03.10.16_07:00:00].txt"
    fname    =  "../plotsME11Pall/f5451_[26.10.16_08:50:00-26.10.16_23:00:00].txt"
    fnameOUT  = fname.replace(".txt", "_REPORT.pdf")
    fnameROOT = fname.replace(".txt", "_REPORT.root")
    fnameTXT  = fname.replace(".txt", "_REPORT.txt")
    
    outFRoot = TFile(fnameROOT, "RECREATE")
    
    f = open(fname,"r")
    lines = f.readlines()    
    f.close()

    #gStyle.SetOptStat(0); 
    
    start = 0
    for ii in range(0, len(lines)):
        if "###" in lines[ii] : start = ii+1 

    
    graphs = []
    canvas = []
    gMax   = 12
    gtitles = ["time","HVst","ID","p0","p0A", "IM", "p1", "p1A", "chi2ndf", "chi2ndfA","Imax", "dTmax"]
    #position in the text file
    columns = [1,      2,      4,  8,   14,    20,   10,    16,     6,         12,      19,      22]
    gcolours =[1,      1,      1,  2,   4,      6,   2,     4,      2,         4,        1,      1]
    gmstyles =[20,    20,     20,  20,  20,    20,   20,    20,     20,        20,       20,     20]
    cMax = 5
    ctitles = [{"time":[[0]]},     {"HV":[[1]]},         {"I0":[[2,3,4,5],[10]]}, {"IvsL":[[6,7],[8,9]]}, {"dTmax":[[11]]}]
    cranges = [[[0,5000]],         [[2700,3000]],        [[-2,2],    [0,5]],        [[0,5],[0,100]],         [[0,50000]]]
    maxCH = 36
    haxtc  = TH2F("haxtc","time per channel;chID;t [ms]",maxCH*10,0.95,maxCH+0.95, 500, cranges[0][0][0], cranges[0][0][1])
    haxtc1 = TH1F("haxtc1","",maxCH*10,0.95,maxCH+0.95)
    
    haxhv   = TH2F("haxhv","stable HV vaues;chID;HV [V]",maxCH*10,0.95,maxCH+0.95, 6000, cranges[1][0][0], cranges[1][0][1])
    haxhv1  = TH1F("haxhv1","",maxCH*10,0.95,maxCH+0.95)
    haxi0   = TH2F("haxi0","current (L<10^{30} Hz/cm^{2});chID;I [uA]",maxCH*10,0.95,maxCH+0.95, 100, cranges[2][0][0], cranges[2][0][1])
    haxi01  = TH1F("haxi01","",maxCH*10,0.95,maxCH+0.95)
    haxid   = TH2F("haxid","maximal current deviation from fit;chID;dI [uA]",maxCH*10,0.95,maxCH+0.95, 100, cranges[2][1][0], cranges[2][1][1])
    haxid1  = TH1F("haxid1","",maxCH*10,0.95,maxCH+0.95)
    haxi1   = TH2F("haxi1","I vs L coefficient;chID;p1 [uA / 10^{34} Hz/cm^{2}]",maxCH*10,0.95,maxCH+0.95, 100, cranges[3][0][0], cranges[3][0][1])
    haxi11  = TH1F("haxi11","",maxCH*10,0.95,maxCH+0.95)
    haxchi  = TH2F("haxchi","#Chi^{2}/ndf;chID;#Chi^{2}/ndf",maxCH*10,0.95,maxCH+0.95, 100, cranges[3][1][0], cranges[3][1][1])
    haxchi1 = TH1F("haxchi1","",maxCH*10,0.95,maxCH+0.95)
    haxdt   = TH2F("haxdt","maximal dT per I rec;chID;dt [s]",maxCH*10,0.95,maxCH+0.95, 100, cranges[4][0][0], cranges[4][0][1])
    haxdt1  = TH1F("haxdt1","",maxCH*10,0.95,maxCH+0.95)

    hcleaned  = TH1F("hcleaned",";par1 [I/10^{34} A/Hz/cm^{3}]",400,0,4)
    hcleaned.SetLineColor(2)
    hcleaned.Sumw2()
    hcleaned1  = TH1F("hcleaned1",";par1 [I/10^{34} A/Hz/cm^{3}]",400,0,4)
    hcleaned1.SetLineColor(4)
    hcleaned1.Sumw2()
    hexcluded  = TH1F("excluded","",maxCH*10,0.95,maxCH+0.95)
    
    VictorsList = ["CSC_ME_N11_C02_6","CSC_ME_N11_C04_3","CSC_ME_N11_C05_2","CSC_ME_N11_C07_1",
                   "CSC_ME_N11_C09_1","CSC_ME_N11_C09_2","CSC_ME_N11_C25_4","CSC_ME_N11_C25_6",
                   "CSC_ME_P11_C01_5","CSC_ME_N11_C33_3"]

    chistos = [{"time":[[haxtc, haxtc1]]}, {"HV":[[haxhv, haxhv1]]}, {"I0":[[haxi0,haxi01],[haxid,haxid1]]}, 
               {"IvsL":[[haxi1, haxi11],[haxchi, haxchi1]]}, {"dTmax":[[haxdt, haxdt1]]}] 
               
    for ckind in range(0, len(chistos)):
        #print chistos[ckind].values()[0]
        for csubkind in range(0, len(chistos[ckind].values()[0])):
            maxx = cranges[ckind][csubkind][1]
            h1 = chistos[ckind].values()[0][csubkind][1]
            h1.SetFillColor(1)
            h1.SetFillStyle(0)
            h1.SetStats(False);
            for i in range(0,maxCH):
                for l in range(1,7):
                    binn = i*10+l+1
                    #print binn, h1.GetBinCenter(binn)
                    h1.SetBinContent(binn, float(maxx))
                for l in range(7,10):
                    binn = i*10+l+1
                    #print binn, h1.GetBinCenter(binn)
                    h1.SetBinContent(binn, -10)
            h1 = chistos[ckind].values()[0][csubkind][0]
            h1.SetStats(False);
    #SAMESBARSAME
    #ctitles = [{"I0":[[2,3,4,5],[10]]}]
    
        
    for gkind in range (0, gMax):
        graphs.append(TGraphErrors())
        graphs[-1].SetTitle(gtitles[gkind])
        graphs[-1].SetLineColor(gcolours[gkind])
        graphs[-1].SetLineWidth(2)
        graphs[-1].SetMarkerColor(gcolours[gkind])
        graphs[-1].SetMarkerStyle(gmstyles[gkind])
        graphs[-1].SetFillColor(gcolours[gkind])  
        graphs[-1].SetFillStyle(3001)

#    for ii in range(start, len(lines)):
    excludeList   = {}
    par1cleanRed  = []
    par1cleanBlue = []  
    # threshold values:
    rchi2   = 15 # chi2/ndf read plot
    maxDevI = 1  # defiation from fit for red plot
    maxIM   = 1  # malter current
    
    #for ii in range(start, start+12):
    for ii in range(start, start+maxCH*6):
        excluded = False
        if(len(lines[ii])<=1): 
            kout.printERR(fname, "MISSING CHANNEL?!\n\n")
            chamber0 = int(ii-start)/6
            layer0   = (ii-start) - chamber0*6
            excludeList = appendToDictOfArr(theDict=excludeList, theKey="CSC_ME_11_C%02d_%1d"%(chamber0+1, layer0+1), value="missing")
            hexcluded.Fill(chamber0+1+float(layer0+1)/10)
            continue # no dpid??? ME11P: CSC_ME_P11_C33_3            
        strgs = lines[ii].split()
        
        #print strgs[0], int(strgs[0][-4:-2]), int(strgs[0][-1]), int(strgs[0][-4:-2])+float(strgs[0][-1])/10, "\t", float(strgs[1]),float(strgs[2]),"\t", len(strgs) 
        x =  int(strgs[0][-4:-2])+float(strgs[0][-1])/10
        print "station=>%s: %2s %2d %2d"%(strgs[0], strgs[0][7:-8], int(strgs[0][-4:-2]), int((strgs[0][-1])))
        
        if(strgs[0] in VictorsList):
            excludeList = appendToDictOfArr(theDict=excludeList, theKey=strgs[0], value="knownMalter")
            kout.printERR(fname, "\tNO HV data, added to the excluded list")
            excluded = True
        if (len(strgs)>=6): # time and stable HV
            for gi in range(0, 2):
                N=graphs[gi].GetN()                    
                val = float(strgs[columns[gi]])
                if(val>-1): graphs[gi].SetPoint(N, x, val)
                #print "\t", N, "\t", float(strgs[columns[gi]]),"\t",
                if(gi==1 and val>-1): 
                    graphs[gi].SetPointError(N, 0.05, float(strgs[columns[gi]+1]))
                    print "\tHV=%6.1f"%float(strgs[columns[gi]]),
        else:
            excludeList = appendToDictOfArr(theDict=excludeList, theKey=strgs[0], value="noRec")
            kout.printERR(fname, "\tNO HV data, added to the excluded list")
            excluded = True
        print ""
        
        if (len(strgs)==24): # full record
            #for gi in range(2, 6):
            for gi in range(2, gMax):
                N=graphs[gi].GetN()
                print "\t", N, "\t", float(strgs[columns[gi]]),"\t",
                if(gi in (8,9)): # chi2/ndf (ndf is always>0)
                    ndf = float(strgs[columns[gi]+1])
                    if(ndf>0):
                        val = float(strgs[columns[gi]])/ndf
                    else:
                        val = 0
                        excludeList = appendToDictOfArr(theDict=excludeList, theKey=strgs[0], value="no fit?")
                        kout.printERR(fname, "\tndf=0, added to the excluded list")
                        excluded = True 
                        
                    graphs[gi].SetPoint(N, x, val)
                    if(gi==8): #chi2/ndf "red"
                        if(val>rchi2):
                            excludeList = appendToDictOfArr(theDict=excludeList, theKey=strgs[0], value="rchi2>%d"%rchi2)
                            kout.printERR(fname, "\tchi2/ndf=%4.1f > %d, added to the excluded list"%(val,rchi2))
                            excluded = True 
                else: # fit parameters and malter current
                    val = float(strgs[columns[gi]])
                    graphs[gi].SetPoint(N, x, val)
                    if(gi in (2,3,4,5,6,7)):
                        err = float(strgs[columns[gi]+1])
                        if(err==0):    # dark and malter currents only - only one measurement
                            err = 0.1
                        elif(err==-1): # dark and malter currents only - no measurements at all, value is also -1
                            err = 0
                        graphs[gi].SetPointError(N, 0.05, err)
                        print float(strgs[columns[gi]+1]),
                        if(gi==5): # malter current
                            if(val>maxIM):
                                excludeList = appendToDictOfArr(theDict=excludeList, theKey=strgs[0], value="IM>%d"%maxIM)
                                kout.printERR(fname, "\tIM=%4.1f > %3.1f [uA], added to the excluded list"%(val,maxIM)) 
                                excluded = True
                    elif (gi==10): #IMax (maximal deviation)                
                        graphs[gi].SetPointError(N, 0.05, 0.1)
                        if(val>maxDevI):
                            excludeList = appendToDictOfArr(theDict=excludeList, theKey=strgs[0], value="dImax>%d"%maxDevI)
                            kout.printERR(fname, "\tdImax=%4.1f > %3.1f [uA], added to the excluded list"%(val,maxDevI)) 
                            excluded = True
                        
            print ""
        else:
            excludeList = appendToDictOfArr(theDict=excludeList, theKey=strgs[0], value="noIRec")
            print "\tNO I data, added to the excluded list"
            excluded = True
        
        if not(excluded):
            gi=6 #p1 (red)
            p1val = float(strgs[columns[gi]])
            p1err = float(strgs[columns[gi]+1])
            #chi2ndf = float(strgs[columns[8]])/float(strgs[columns[8]+1])
            hcleaned.Fill(p1val)
            #hcleaned.Fill(p1val, 1.0/(p1err*p1err))
            par1cleanRed.append([p1val, p1err])
            
            gi=7 #p1A (blue)
            p1val = float(strgs[columns[gi]])
            p1err = float(strgs[columns[gi]+1])
            #chi2ndf = float(strgs[columns[9]])/float(strgs[columns[9]+1])
            hcleaned1.Fill(p1val)
            #hcleaned1.Fill(p1val, 1.0/(p1err*p1err))
            par1cleanBlue.append([p1val, p1err])            
        else:
            hexcluded.Fill(x)
            
    # and loop over file
    
    for ckind in range (0, len(ctitles)):
        key   = ctitles[ckind].keys()[0]
        npads = len(ctitles[ckind][key])
        print "creating canvas ", key 
        h = 600*npads
        canvas.append(TCanvas(ctitles[ckind].keys()[0],ctitles[ckind].keys()[0], 1200, h))
        canvas[-1].Divide(1,npads)
        for pn in range(0,npads):
            canvas[-1].cd(pn+1)
            canvas[-1].GetPad(pn+1).SetGridx()
            canvas[-1].GetPad(pn+1).SetGridy()
            
            print "\t", ctitles[ckind][key][pn], ctitles[ckind][key][pn][0] 
            gi = ctitles[ckind][key][pn][0]
            print chistos[ckind][key]
            print chistos[ckind][key][pn]
            chistos[ckind][key][pn][0].Draw()
            #chistos[ckind][key][pn][1].Draw("SAMESBARSAME")
            #chistos[ckind][key][pn][1].Draw("SAMES")                
            for indx in range(0,len(ctitles[ckind][key][pn])):
                gi = ctitles[ckind][key][pn][indx]
                graphs[gi].Draw("2Psames")  
                graphs[gi].Write()
        if(ckind==0):
            canvas[-1].Print("tmpreport.pdf"+"(","pdf");
        else:
            canvas[-1].Print("tmpreport.pdf","pdf");    
    
    # add last canvas with the average value
    #gStyle.SetOptStat(1); 
    canvas.append(TCanvas("cfinal","averaged", 1200, 1200))
    canvas[-1].Divide(1,2)
    upperPad = canvas[-1].GetPad(1)
    upperPad.Divide(2,1)
    upperPad.cd(1)
    hcleaned.SetStats(True);
    hcleaned.Draw()
    hcleaned.Write()
    upperPad.cd(2)
    hcleaned1.Draw()
    hcleaned1.Write()
    canvas[-1].cd(2)
    #gStyle.SetOptStat(0);
    hexcluded.SetStats(False); 
    hexcluded.Draw()
    hexcluded.Write()
    canvas[-1].Print("tmpreport.pdf"+")","pdf");
    
    #write report
    txtoutF = open(fnameTXT, "w")
    txtoutF.write("excluded channels\n")
    chList = sorted(excludeList.keys())
    for ch in chList:
        txtoutF.write(ch)
        for reason in excludeList[ch]:
            txtoutF.write(" "+reason)
        txtoutF.write("\n")
    aveRed  = weightedMean(theArray=par1cleanRed,  valIndx=0, errIndx=1) 
    aveBlue = weightedMean(theArray=par1cleanBlue, valIndx=0, errIndx=1) 
    txtoutF.write("average  red: %6.3f +/- %6.3f\n"%(aveRed[0], aveRed[1]))
    txtoutF.write("average blue: %6.3f +/- %6.3f\n"%(aveBlue[0],aveBlue[1]))
    txtoutF.close()
    os.rename("tmpreport.pdf", fnameOUT) # root does not like complicated names :(
        