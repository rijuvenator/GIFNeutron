import ROOT as r
import struct
import os,sys
from Gif.TestBeamAnalysis.TestBeamMeasurements import *
import argparse
parser = argparse.ArgumentParser(description='Segment Analysis : make event lists')
parser.add_argument('--eventList',dest='eventList',help='Event list to draw',default=None)
parser.add_argument('--meas',dest='meas',help='Measurement number to draw from',default=None)
parser.add_argument('--extra',dest='extra',help='Extra info about event displays (e.g. noSegments, twoMuons)',default=None)
args = parser.parse_args()
if (args.eventList is None) or (args.meas is None):
    raise ValueError('Need to specify event list and measurement number.\
                      Ex: --eventList list.txt --meas mXXXX')
LIST = args.eventList
MEAS = args.meas
EXTRA = args.extra

TBM = eval(MEAS)
print 'ana_%s_%s_%s_%s_%s_%s_%s.root'%(TBM.CSC, TBM.test, TBM.HV, TBM.beam, TBM.uAtt, TBM.dAtt, TBM.meas)
#f = r.TFile('data/ana_ME21_Test40_HV0_bOn_u46_d15_m2064.root','read')
#f = r.TFile('data/ana_ME21_Test27_HV0_bOn_u46_d15_m2062.root','read')
f = r.TFile('data/ana_%s_%s_%s_%s_%s_%s_%s.root'%(TBM.CSC, TBM.test, TBM.HV, TBM.beam, TBM.uAtt, TBM.dAtt, TBM.meas),'read')

tree = f.Get('GIFTree').Get('GIFDigiTree')

#hNSeg = r.TH1F('hNSeg',':number of segments:events',40,0,40)
#hNoSeg_nLCTs = r.TH1F('hNoSeg_nLCTs','Events with no segments;number of LCTs;events',11,-1,10)
#hNoSeg_nALCTs = r.TH1F('hNoSeg_nALCTs','Events with no segments;number of ALCTs;events',11,-1,10)
#hNoSeg_nCLCTs = r.TH1F('hNoSeg_nCLCTs','Events with no segments;number of CLCTs;events',11,-1,10)

NnoSeg = 0
events = 0
eventListFile = open('%s.txt'%LIST,'w')
for entry in tree:
    events = events + 1
    for seg, sid in enumerate(entry.segment_id):
        chi2 = entry.segment_chisq[seg]
        dof = struct.unpack('1b',entry.segment_dof[seg])[0]
        nHits = struct.unpack('1b',entry.segment_nHits[seg])[0]
        chi2dof = chi2/dof
        posX = entry.segment_pos_x[seg]
        posY = entry.segment_pos_y[seg]
        if chi2dof < 9.5 and nHits > 4 and \
            posX > -39 and posX < -24 and \
            posY > -3 and posY < 12:
            pass
    #hNSeg.Fill(entry.n_segments)
    if entry.n_segments==0:
        eventListFile.write(str(entry.Event_EventNumber)+'\n')
        NnoSeg = NnoSeg + 1
        #hNoSeg_nLCTs.Fill(entry.n_lcts)
        #hNoSeg_nALCTs.Fill(entry.n_alcts)
        #hNoSeg_nCLCTs.Fill(entry.n_clcts)
eventListFile.close()
    
#c = r.TCanvas()
#hNSeg.Draw('hist')
#c.SaveAs('hNSegtest27.png')
#hNoSeg_nLCTs.Draw('hist')
#c.SaveAs('hNoSeg_nLCTstest27.png')
#hNoSeg_nALCTs.Draw('hist')
#c.SaveAs('hNoSeg_nALCTstest27.png')
#hNoSeg_nCLCTs.Draw('hist')
#c.SaveAs('hNoSeg_nCLCTstest27.png')
print 'number of events with no segments', NnoSeg
print 'number of events', events
print 'eff', float(NnoSeg)/events
