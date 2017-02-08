import ROOT as r
import struct
import os,sys
from Gif.NeutronSim.TestBeamMeasurements import *

r.gROOT.SetBatch(True)

import argparse
parser = argparse.ArgumentParser(description='Segment Analysis : make event lists')
parser.add_argument('--eventList',dest='eventList',help='Event list to draw',default=None)
parser.add_argument('--meas',dest='meas',help='Measurement number to draw from',default=None)
parser.add_argument('--extra',dest='extra',help='Extra info about event displays (e.g. noSegments, twoMuons)',default=None)
parser.add_argument('--plot',dest='plot',action='store_true',default=False,help='Flag to make histograms')
parser.add_argument('--stats',dest='stats',action='store_true',default=False,help='Flag to print statistics')
args = parser.parse_args()

# Flags
PLOT = args.plot
STATS = args.stats
if args.eventList:
    LIST = args.eventList
    EVTLIST = True
else: EVTLIST = False
MEAS = args.meas
EXTRA = args.extra

# Set input/output root files and call TBM class
TBM = eval(MEAS)
print 'ana_%s_%s_%s_%s_%s_%s_%s.root'%(TBM.CSC, TBM.test, TBM.HV, TBM.beam, TBM.uAtt, TBM.dAtt, TBM.meas)
f = r.TFile('data/ana_%s_%s_%s_%s_%s_%s_%s.root'%(TBM.CSC, TBM.test, TBM.HV, TBM.beam, TBM.uAtt, TBM.dAtt, TBM.meas),'read')
fout = r.TFile('histos/noSegmentHists_%s_%s_%s_%s_%s_%s_%s.root'%(TBM.CSC, TBM.test, TBM.HV, TBM.beam, TBM.uAtt, TBM.dAtt, TBM.meas),'recreate')

tree = f.Get('GIFTree').Get('GIFDigiTree')

if PLOT:
    hNSeg = r.TH1F('hNSeg',':number of segments:events',40,0,40)
    hNoSegNLCTs = r.TH1F('hNoSegNLCTs','Events with no segments;number of LCTs;events',11,-1,10)
    hNoSegNALCTs = r.TH1F('hNoSegNALCTs','Events with no segments;number of ALCTs;events',11,-1,10)
    hNoSegNCLCTs = r.TH1F('hNoSegNCLCTs','Events with no segments;number of CLCTs;events',11,-1,10)
    hNoSegNComps = r.TH1F('hNoSegNComps','Events with no segments;number of comparators;events',51,-1,50)
    hNoSegNWGs = r.TH1F('hNoSegNWGs','Events with no segments;number of wire groups;events',101,-1,100)
    hNoSegNStrips = r.TH1F('hNoSegNStrips','Events with no segments;number of strips;events',51,-1,50)

NnoSeg = 0
events = 0
NnoSegNoLCT = 0
NnoSegNoALCT = 0
NnoSegNoCLCT = 0
NnoSegNoComp= 0
NnoSegNoWG= 0
NnoSegNoStrips = 0
NnoSegYesLCT = 0
NnoSegYesALCT = 0
NnoSegYesCLCT = 0
NnoSegYesComp= 0
NnoSegYesWG= 0
NnoSegYesStrips = 0
NnoSegYesEverything= 0
nCAT1 = 0
nCAT2 = 0
nCAT3 = 0
nCAT4 = 0
nCAT5 = 0
nCAT6 = 0
nCAT7 = 0
if EVTLIST: eventListFile = open('%s.txt'%LIST,'w')
for entry in tree:
    events = events + 1
    #for seg, sid in enumerate(entry.segment_id):
    if PLOT: hNSeg.Fill(entry.n_segments)
    if entry.n_segments==0:
        if EVTLIST: eventListFile.write(str(entry.Event_EventNumber)+'\n')
        NnoSeg = NnoSeg + 1
        # LCT
        if entry.n_lcts == 0: NnoSegNoLCT = NnoSegNoLCT + 1
        else: NnoSegYesLCT = NnoSegYesLCT + 1
        if PLOT: hNoSegNLCTs.Fill(entry.n_lcts)
        # Comparators
        if entry.comp_id.size() == 0: NnoSegNoComp = NnoSegNoComp + 1
        else: NnoSegYesComp = NnoSegYesComp + 1
        if PLOT: hNoSegNComps.Fill(entry.comp_id.size())
        # ALCT
        if entry.n_alcts == 0: NnoSegNoALCT = NnoSegNoALCT + 1
        else: NnoSegYesALCT = NnoSegYesALCT + 1
        if PLOT: hNoSegNALCTs.Fill(entry.n_alcts)
        # CLCT
        if entry.n_clcts == 0: NnoSegNoCLCT = NnoSegNoCLCT + 1
        else: NnoSegYesCLCT = NnoSegYesCLCT + 1
        if PLOT: hNoSegNCLCTs.Fill(entry.n_clcts)
        # Wire Groups
        if entry.n_wires == 0: NnoSegNoWG = NnoSegNoWG + 1
        else: NnoSegYesWG = NnoSegYesWG + 1
        if PLOT: hNoSegNWGs.Fill(entry.n_wires)
        # Strips
        if entry.n_strips == 0: NnoSegNoStrips = NnoSegNoStrips + 1
        else: NnoSegYesStrips = NnoSegYesStrips + 1
        if PLOT: hNoSegNStrips.Fill(entry.n_strips)
        # yes everything
        if entry.n_strips>0 and entry.n_wires>0 and entry.n_clcts>0 and entry.n_alcts and \
            entry.comp_id.size()>0 and entry.n_lcts>0:
            NnoSegYesEverything = NnoSegYesEverything + 1

        # CAT1 : Only Anode information
        if entry.n_strips==0 and entry.comp_id.size()==0 and entry.n_wires>0:
            nCAT1 = nCAT1 + 1
        # CAT2 : Only Trigger information
        elif entry.n_strips==0 and entry.comp_id.size()>0 and entry.n_wires>0:
            nCAT2 = nCAT2 + 1
        # CAT3 : No Comparator information
        elif entry.n_strips>0 and entry.comp_id.size()==0 and entry.n_wires>0:
            nCAT3 = nCAT3 + 1
        # CAT4 : No Trigger information
        elif entry.n_strips>0 and entry.comp_id.size()==0 and entry.n_wires==0:
            nCAT4 = nCAT4 + 1
        # CAT5 : All information
        elif entry.n_strips>0 and entry.comp_id.size()>0 and entry.n_wires>0:
            nCAT5 = nCAT5 + 1
        # CAT6 : No Wire Information
        elif entry.n_strips>0 and entry.comp_id.size()>0 and entry.n_wires==0:
            nCAT6 = nCAT6 + 1
        # CAT7 : Only Comparator information
        elif entry.n_strips==0 and entry.comp_id.size()>0 and entry.n_wires==0:
            nCAT7 = nCAT7 + 1
        else:
            print '------'
            print 'nSegments',entry.n_segments
            print 'nWires',entry.n_wires
            print 'nComps',entry.comp_id.size()
            print 'nStrips',entry.n_strips
            print 'nLCTs',entry.n_lcts
            print 'nCLCTs',entry.n_clcts
            print 'nALCTs',entry.n_alcts

print '------'
if EVTLIST: eventListFile.close()
if PLOT:
    c = r.TCanvas()
    for hist in [hNSeg, hNoSegNLCTs, hNoSegNALCTs, hNoSegNCLCTs, hNoSegNComps, hNoSegNWGs, hNoSegNStrips]:
        hist.Draw('hist')
        for ftype in ['.png','.pdf']:
            c.SaveAs('histos/'+hist.GetName()+ftype)
        c.Write(hist.GetName())
    fout.Write()
    fout.Close()

if STATS:
    print 'number of events with no segments', NnoSeg
    print 'number of events with no segments and no LCTs', NnoSegNoLCT, 'yes LCTs', NnoSegYesLCT
    print 'number of events with no segments and no ALCTs', NnoSegNoALCT, 'yes ALCTs', NnoSegYesALCT
    print 'number of events with no segments and no CLCTs', NnoSegNoCLCT, 'yes CLCTs', NnoSegYesCLCT
    print 'number of events with no segments and no Comparators', NnoSegNoComp, 'yes Comparators', NnoSegYesComp
    print 'number of events with no segments and no Wire Groups', NnoSegNoWG, 'yes Wire Groups', NnoSegYesWG
    print 'number of events with no segments and no Strips', NnoSegNoStrips, 'yes Strips', NnoSegYesStrips
    print 'number of events with no segments yes everything', NnoSegYesEverything
    print 'number of events', events
    print 'eff', float(NnoSeg)/events
    nCAT = nCAT1 + nCAT2 + nCAT3 + nCAT4 + nCAT5 + nCAT6 + nCAT7
    print 'CAT1',nCAT1,'%',float(nCAT1)/nCAT
    print 'CAT2',nCAT2,'%',float(nCAT2)/nCAT
    print 'CAT3',nCAT3,'%',float(nCAT3)/nCAT
    print 'CAT4',nCAT4,'%',float(nCAT4)/nCAT
    print 'CAT5',nCAT5,'%',float(nCAT5)/nCAT
    print 'CAT6',nCAT6,'%',float(nCAT6)/nCAT
    print 'CAT7',nCAT7,'%',float(nCAT7)/nCAT
    print 'nCAT',nCAT
