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
args = parser.parse_args()
EXTRA = args.extra

# Control Plots to Make per Test Beam Measurement
#
# Chi^2/dof for each dof 2,4,6,8
hSegChi2p2dof = r.TH1F('hSegChi2p2dof','#chi^{2}/dof for 2 dof;#chi^{2}/dof;N(segments)',100,0,50)
hSegChi2p4dof = r.TH1F('hSegChi2p4dof','#chi^{2}/dof for 4 dof;#chi^{2}/dof;N(segments)',100,0,50)
hSegChi2p6dof = r.TH1F('hSegChi2p6dof','#chi^{2}/dof for 6 dof;#chi^{2}/dof;N(segments)',100,0,50)
hSegChi2p8dof = r.TH1F('hSegChi2p8dof','#chi^{2}/dof for 8 dof;#chi^{2}/dof;N(segments)',100,0,50)
hSegChi2pdof = r.TH1F('hSegChi2pdof','#chi^2/dof;#chi^2/dof;N(segments)',100,0,50)
# Chi^2/dof probability
hSegChi2pdofProb = r.TH1F('hSegChi2pdofProb','#chi^2/dof Proability;p;N(segments)',100,0,1)
# N(hits)
hSegNhits = r.TH1F('hSegNhits','Number of hits in a segment;N(hits);N(segments)',7,0,7)
# N(segments) normalized a specific N(hits)
hSeg3hits = r.TH1F('hSeg3hits','Number of segments relative to number of segments with 3 hits;N(hits);ratio',7,0,7)
hSeg4hits = r.TH1F('hSeg4hits','Number of segments relative to number of segments with 4 hits;N(hits);ratio',7,0,7)
hSeg5hits = r.TH1F('hSeg5hits','Number of segments relative to number of segments with 5 hits;N(hits);ratio',7,0,7)
hSeg6hits = r.TH1F('hSeg6hits','Number of segments relative to number of segments with 6 hits;N(hits);ratio',7,0,7)
# Position
hSegXpos = r.TH1F('hSegXpos','Segment X position;pos [cm];N(segments)',100,70,40)
hSegYpos = r.TH1F('hSegYpos','Segment Y position;pos [cm];N(segments)',200,-100,100)
# Slope
hSegXslope = r.TH1F('hSegXslope','Segment dx/dz;segment slope dx/dz;N(segments)',100,-2,2)
hSegYslope = r.TH1F('hSegYslope','Segment dy/dz;segment slope dy/dz;N(segments)',100,-2,2)
# N(segments)
hNSeg = r.TH1F('hNSeg','Number of segments in an event;N(segments);N(events)',50,0,50)
# Segment Quality (all and best segments)
hSegQual = r.TH1F('hSegQual','Segment Quality;quality;N(segments)',20,0,20)
hSegQualBest = r.TH1F('hSegQualBest','Best Segment Quality;quality;N(segments)',20,0,20)
# To add : Segment Quality with slope penalty

measurements = [m1966,m2040,m2312,m2064] # Test40
#measurements = [m2250,m1977,m2306,m2062] # Test27
for tbm in measurements:
    print 'In : ana_%s_%s_%s_%s_%s_%s_%s.root'%(tbm.CSC, tbm.test, tbm.HV, tbm.beam, tbm.uAtt, tbm.dAtt, tbm.meas)
    fin = r.TFile('data/ana_%s_%s_%s_%s_%s_%s_%s.root'%(tbm.CSC, tbm.test, tbm.HV, tbm.beam, tbm.uAtt, tbm.dAtt, tbm.meas),'read')
    tree = fin.Get('GIFTree').Get('GIFDigiTree')
    fout = r.TFile('histos/ana_segHistos_%s_%s_%s_%s_%s_%s_%s.root'%(tbm.CSC, tbm.test, tbm.HV, tbm.beam, tbm.uAtt, tbm.dAtt, tbm.meas),'recreate')
    print 'Out : ana_segHistos_%s_%s_%s_%s_%s_%s_%s.root'%(tbm.CSC, tbm.test, tbm.HV, tbm.beam, tbm.uAtt, tbm.dAtt, tbm.meas)

    # reset per measurement quantities
    events = 0

    for entry in tree:
        # reset per event quantites
        nSegs = 0
        N_best_seg_qual = 0
        #best_seg_qual = min(entry.segment_quality)
        seg_quals = []
        for seg,qual in enumerate(entry.segment_id):
            seg_quals.append(entry.segment_quality[seg])
        if entry.n_segments>0: best_seg_qual = min(seg_quals)
        for seg, sid in enumerate(entry.segment_id):
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
            if dof==2: hSegChi2p2dof.Fill(chi2dof)
            if dof==4: hSegChi2p4dof.Fill(chi2dof)
            if dof==6: hSegChi2p6dof.Fill(chi2dof)
            if dof==8: hSegChi2p8dof.Fill(chi2dof)
            hSegChi2pdof.Fill(chi2dof)
            # Chi^2/dof probability
            #hSegChi2pdofProb.Fill(chi2probab
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
    # Fill/modify per measurement histograms
    for ibin in [4,5,6,7]:
        hSeg3hits.SetBinContent(ibin,hSegNhits.GetBinContent(ibin)/hSegNhits.GetBinContent(4))
        hSeg4hits.SetBinContent(ibin,hSegNhits.GetBinContent(ibin)/hSegNhits.GetBinContent(5))
        hSeg5hits.SetBinContent(ibin,hSegNhits.GetBinContent(ibin)/hSegNhits.GetBinContent(6))
        hSeg6hits.SetBinContent(ibin,hSegNhits.GetBinContent(ibin)/hSegNhits.GetBinContent(7))
    # Normalize quality histograms to be relative to N(segment quality = 1)
    #print hSegQual.GetBinContent(2)
    for ibin in range(hSegQual.GetXaxis().GetNbins()):
        #print hSegQual.GetBinContent(ibin), hSegQual.GetBinContent(2), hSegQual.GetBinContent(ibin)/hSegQual.GetBinContent(2)
        ratio = hSegQual.GetBinContent(ibin)/hSegQual.GetBinContent(2)
        hSegQual.SetBinContent(ibin,ratio)
    # write histos
    hSegChi2p2dof.Write()
    hSegChi2p4dof.Write()
    hSegChi2p6dof.Write()
    hSegChi2p8dof.Write()
    hSegChi2pdof.Write()
    #hSegChi2pdofProb.Write()
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
    fout.Close()
    fin.Close()

