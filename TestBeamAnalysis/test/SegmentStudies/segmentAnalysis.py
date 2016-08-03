import ROOT as r
import struct
import os

f = r.TFile('data/ana_ME21_Test40_HV0_bOn_u46_d15_m2064.root','read')

tree = f.Get('GIFTree').Get('GIFDigiTree')

hNSeg = r.TH1F('hNSeg',':number of segments:events',40,0,40)

NnoSeg = 0
events = 0
for entry in tree:
    nSeg = 0
    events = events + 1
    for seg, sid in enumerate(entry.segment_id):
        nSeg = nSeg + 1
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
    hNSeg.Fill(nSeg)
    if nSeg==0:
        NnoSeg = NnoSeg + 1
        print entry.Event_EventNumber
    
c = r.TCanvas()
hNSeg.Draw('hist')
c.SaveAs('hNSeg.png')
#print 'number of events with no segments', NnoSeg
#print 'number of events', events
#print 'eff', float(NnoSeg)/events
