''' Purpose of this script is to loop on tree for test beam measurements and make analysis histograms.
useage : python makeSegmentHistos.py 
options : --extra EXTRA (optional)
'''
import ROOT as r
import struct
import os,sys
from Gif.TestBeamAnalysis.TestBeamMeasurements import *
import argparse
parser = argparse.ArgumentParser(description='Segment Analysis : make histograms from tree')
parser.add_argument('--extra',dest='extra',help='Extra info about plots',default=None)
parser.add_argument('--CSC',dest='CSC',help='Choose which CSC to make plots for',default=None)
parser.add_argument('--test',dest='test',help='Choose which test to make plots for',default=None)
args = parser.parse_args()
EXTRA = args.extra
CSC = args.CSC
TEST = args.test
if (TEST is not None) and (TEST[:1]=='t'): raise ValueError('do --test TestXX not --test testXX')

# Control Plots to Make per Test Beam Measurement
#
# Chi^2/dof for each dof 2,4,6,8
hSegChi2p2dof = r.TH1F('hSegChi2p2dof','#chi^{2}/dof for 2 dof;#chi^{2}/dof;N(segments)',100,0,50)
hSegChi2p4dof = r.TH1F('hSegChi2p4dof','#chi^{2}/dof for 4 dof;#chi^{2}/dof;N(segments)',80,0,20)
hSegChi2p6dof = r.TH1F('hSegChi2p6dof','#chi^{2}/dof for 6 dof;#chi^{2}/dof;N(segments)',80,0,20)
hSegChi2p8dof = r.TH1F('hSegChi2p8dof','#chi^{2}/dof for 8 dof;#chi^{2}/dof;N(segments)',80,0,20)
hSegChi2pdof = r.TH1F('hSegChi2pdof','#chi^2/dof;#chi^2/dof;N(segments)',100,0,25)
# Chi^2/dof probability
hSegChi2pdofProb = r.TH1F('hSegChi2pdofProb','#chi^2/dof Proability;probability;N(segments)',100,0,1)
# N(hits)
hSegNhits = r.TH1F('hSegNhits','Number of hits in a segment;N(hits);N(segments)',7,0,7)
# N(segments) normalized a specific N(hits)
hSeg3hits = r.TH1F('hSeg3hits','Number of segments relative to number of segments with 3 hits;N(hits);ratio',7,0,7)
hSeg4hits = r.TH1F('hSeg4hits','Number of segments relative to number of segments with 4 hits;N(hits);ratio',7,0,7)
hSeg5hits = r.TH1F('hSeg5hits','Number of segments relative to number of segments with 5 hits;N(hits);ratio',7,0,7)
hSeg6hits = r.TH1F('hSeg6hits','Number of segments relative to number of segments with 6 hits;N(hits);ratio',7,0,7)
# Position
hSegXpos = r.TH1F('hSegXpos','Segment X position;pos [cm];N(segments)',100,-70,40)
hSegYpos = r.TH1F('hSegYpos','Segment Y position;pos [cm];N(segments)',100,-100,100)
# Slope
hSegXslope = r.TH1F('hSegXslope','Segment dx/dz;segment slope dx/dz;N(segments)',100,-2,2)
hSegYslope = r.TH1F('hSegYslope','Segment dy/dz;segment slope dy/dz;N(segments)',100,-2,2)
# N(segments)
hNSeg = r.TH1F('hNSeg','Number of segments in an event;N(segments);N(events)',15,0,15)
# Segment Quality (all and best segments)
hSegQual = r.TH1F('hSegQual','Segment Quality;quality;N(segments)',10,0,10)
hSegQualBest = r.TH1F('hSegQualBest','Best Segment Quality;quality;N(segments)',10,0,10)
# To add : Segment Quality with slope penalty

#measurements = [m1966,m2040,m2312,m2064] 
#measurements = [m2250,m1977,m2306,m2062] # Test27
toDo = []
# Set list of measurements to make histograms for
for TBM in measurements:
    #print TBM.CSC, TBM.test
    if CSC and TEST:
        if TBM.CSC == CSC and TBM.test == TEST:
            toDo.append(TBM)
    else: toDo.append(TBM)
for tbm in toDo:
    print 'In : ana_%s_%s_%s_%s_%s_%s_%s.root'%(tbm.CSC, tbm.test, tbm.HV, tbm.beam, tbm.uAtt, tbm.dAtt, tbm.meas)
    fin = r.TFile('data/ana_%s_%s_%s_%s_%s_%s_%s.root'%(tbm.CSC, tbm.test, tbm.HV, tbm.beam, tbm.uAtt, tbm.dAtt, tbm.meas),'read')
    tree = fin.Get('GIFTree').Get('GIFDigiTree')
    fout = r.TFile('histos/ana_segHistos_%s_%s_%s_%s_%s_%s_%s.root'%(tbm.CSC, tbm.test, tbm.HV, tbm.beam, tbm.uAtt, tbm.dAtt, tbm.meas),'recreate')
    print 'Out : ana_segHistos_%s_%s_%s_%s_%s_%s_%s.root'%(tbm.CSC, tbm.test, tbm.HV, tbm.beam, tbm.uAtt, tbm.dAtt, tbm.meas)

    # reset per measurement quantities
    events = 0
    eventsSegs = 0
    totalSegs = 0

    n2dof = 0
    n4dof = 0
    n6dof = 0
    n8dof = 0
    for entry in tree:
        events = events + 1
        # reset per event quantites
        nSegs = 0
        N_best_seg_qual = 0
        #best_seg_qual = min(entry.segment_quality)
        seg_quals = []
        for seg,qual in enumerate(entry.segment_id):
            seg_quals.append(entry.segment_quality[seg])
        if entry.n_segments>0: 
            best_seg_qual = min(seg_quals)
            eventsSegs = eventsSegs + 1
        for seg, sid in enumerate(entry.segment_id):
            totalSegs = totalSegs + 1
            # Get segment quantities
            chi2 = entry.segment_chisq[seg]
            dof = struct.unpack('1b',entry.segment_dof[seg])[0]
            nHits = struct.unpack('1b',entry.segment_nHits[seg])[0]
            chi2dof = chi2/dof
            posX = entry.segment_pos_x[seg]
            posY = entry.segment_pos_y[seg]
            slopeXZ = entry.segment_dxdz[seg]
            slopeYZ = entry.segment_dydz[seg]
            seg_qual = entry.segment_quality[seg]

            # Fill histograms
            # Chi^2/dof for each dof 2,4,6,8,all
            if dof==2: 
                hSegChi2p2dof.Fill(chi2dof)
                n2dof = n2dof + 1
            if dof==4: 
                hSegChi2p4dof.Fill(chi2dof)
                n4dof = n4dof + 1
            if dof==6: 
                hSegChi2p6dof.Fill(chi2dof)
                n6dof = n6dof + 1
            if dof==8: 
                hSegChi2p8dof.Fill(chi2dof)
                n8dof = n8dof + 1
            hSegChi2pdof.Fill(chi2dof)
            # Chi^2/dof probability
            prob = r.TMath.Prob(chi2,dof)
            #print prob
            hSegChi2pdofProb.Fill(prob)
            # N(hits)
            hSegNhits.Fill(nHits)
            # Position
            hSegXpos.Fill(posX)
            hSegYpos.Fill(posY)
            # Slope
            hSegXslope.Fill(slopeXZ)
            hSegYslope.Fill(slopeYZ)
            # N(segments)
            nSegs = nSegs + 1
            # Segment Quality (all segments)
            hSegQual.Fill(seg_qual)
            if entry.n_segments>0 and seg_qual == best_seg_qual: 
                N_best_seg_qual = N_best_seg_qual + 1
            # To add : Segment Quality with slope penalty
        # Fill Per event histograms
        # N(Segments)
        hNSeg.Fill(nSegs)
        # Segment Quality (best segments)
        if entry.n_segments>0:
            hSegQualBest.SetBinContent(best_seg_qual,N_best_seg_qual)
            #print best_seg_qual,N_best_seg_qual
    print events, tree.GetEntries()
    # Fill/modify per measurement histograms
    for ibin in [4,5,6,7]:
        hSeg3hits.SetBinContent(ibin,hSegNhits.GetBinContent(ibin)/hSegNhits.GetBinContent(4))
        hSeg4hits.SetBinContent(ibin,hSegNhits.GetBinContent(ibin)/hSegNhits.GetBinContent(5))
        hSeg5hits.SetBinContent(ibin,hSegNhits.GetBinContent(ibin)/hSegNhits.GetBinContent(6))
        hSeg6hits.SetBinContent(ibin,hSegNhits.GetBinContent(ibin)/hSegNhits.GetBinContent(7))
    # Normalize quality histograms to be relative to N(segment quality = 1)
    nBins = hSegQual.GetXaxis().GetNbins()
    refQual = hSegQual.GetBinContent(2)
    for ibin in range(nBins):
        ibin=ibin+1
        ratio = hSegQual.GetBinContent(ibin)/refQual
        #print hSegQual.GetBinContent(ibin), refQual, ratio
        hSegQual.SetBinContent(ibin,ratio)
    # write histos
    # 1/totalSegs normalizes to total number of segments
    # 1/events normalizes to total number of events
    # 1/eventsSegs normalizes to total number of events with segmens
    hSegChi2p2dof.Scale(1./n2dof)
    hSegChi2p4dof.Scale(1./n4dof)
    hSegChi2p6dof.Scale(1./n6dof)
    hSegChi2p8dof.Scale(1./n8dof)
    hSegChi2pdof.Scale(1./totalSegs)
    hSegChi2pdofProb.Scale(1./totalSegs)
    hSegNhits.Scale(1./eventsSegs)
    hSegXpos.Scale(1./totalSegs)
    hSegYpos.Scale(1./totalSegs)
    hSegXslope.Scale(1./totalSegs)
    hSegYslope.Scale(1./totalSegs)
    hNSeg.Scale(1./eventsSegs)
    # Write Histograms
    hSegChi2p2dof.Write()
    hSegChi2p4dof.Write()
    hSegChi2p6dof.Write()
    hSegChi2p8dof.Write()
    hSegChi2pdof.Write()
    hSegChi2pdofProb.Write()
    hSegNhits.Write()
    hSeg3hits.Write()
    hSeg4hits.Write()
    hSeg5hits.Write()
    hSeg6hits.Write()
    hSegXpos.Write()
    hSegYpos.Write()
    hSegXslope.Write()
    hSegYslope.Write()
    hSegQual.Write()
    hSegQualBest.Write()
    hNSeg.Write()
    # Close in/out files
    fout.Close()
    fin.Close()

