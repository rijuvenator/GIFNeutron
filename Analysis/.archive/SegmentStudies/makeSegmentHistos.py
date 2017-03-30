''' Purpose of this script is to loop on tree for test beam measurements and make analysis histograms.
useage : python makeSegmentHistos.py 
options : --extra EXTRA (optional)
'''
import ROOT as r
import struct
import os,sys
import Gif.Analysis.Measurements as Meas
#from Gif.Analysis.TestBeamMeasurements import *
import argparse
parser = argparse.ArgumentParser(description='Segment Analysis : make histograms from tree')
parser.add_argument('--extra',dest='extra',help='Extra info about plots',default=None)
parser.add_argument('--CSC',dest='CSC',help='Choose which CSC to make plots for',default=None)
parser.add_argument('--test',dest='test',help='Choose which test to make plots for',default=None)
parser.add_argument('--slope',dest='slope',help='Choose which slope to penalize segments',default='0.07')
args = parser.parse_args()
EXTRA = args.extra
CSC = args.CSC
TEST = args.test
SLOPE = float(args.slope)
sslope = args.slope[2:]
print sslope

if (TEST is not None) and (TEST[:1]=='t'): raise ValueError('do --test TestXX not --test testXX')

# Normalize quality histograms to be relative to N(segment quality = 1)
def ratioToBin(hist,rBin):
    nBins = hist.GetXaxis().GetNbins()
    refBinCont = hist.GetBinContent(rBin)
    for ibin in range(nBins):
        ibin=ibin+1
        ratio = hist.GetBinContent(ibin)/refBinCont
        #print hSegQual.GetBinContent(ibin), refQual, ratio
        hist.SetBinContent(ibin,ratio)

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
hSegSlope = r.TH1F('hSegSlope','Segment Slope;#sqrt{(dx/dz)^{2} + (dy/dz)^{2}};N(segments)',200,0,2)
hSegdSlope = r.TH1F('hSegdSlope','Segment Slope;#sqrt{(#Delta(dx/dz))^{2} + (#Delta(dy/dz))^{2}};N(segments)',100,0,1)
hSegSlopeIN = r.TH1F('hSegSlopeIN','Segment Slope in scintillator paddle region;#sqrt{(dx/dz)^{2} + (dy/dz)^{2}};N(segments)',200,0,2)
hSegdSlopeIN = r.TH1F('hSegdSlopeIN','Segment Slope in scintillator paddle region;#sqrt{(#Delta(dx/dz))^{2} + (#Delta(dy/dz))^{2}};N(segments)',100,0,1)
hSegSlopeOUT = r.TH1F('hSegSlopeOUT','Segment Slope out of scintillator paddle region;#sqrt{(dx/dz)^{2} + (dy/dz)^{2}};N(segments)',200,0,2)
hSegdSlopeOUT = r.TH1F('hSegdSlopeOUT','Segment Slope out of scintillator paddle region;#sqrt{(#Delta(dx/dz))^{2} + (#Delta(dy/dz))^{2}};N(segments)',100,0,1)
# N(segments)
hNSeg = r.TH1F('hNSeg','Number of segments in an event;N(segments);N(events)',15,0,15)
# Segment Quality (all and best segments)
hSegQual = r.TH1F('hSegQual','Segment Quality;quality;N(segments)',10,0,10)
hSegQualNorm = r.TH1F('hSegQualNorm','Segment Quality Normalized to Quality = 1;quality;N(segments)',10,0,10)
hSegQualBest = r.TH1F('hSegQualBest','Best Segment Quality;quality;N(segments)',10,0,10)
hSegQualBestNorm = r.TH1F('hSegQualBestNorm','Best Segment Quality Normalized to Quality = 1;quality;N(segments)',10,0,10)
hSegQualSlope = r.TH1F('hSegQualSlope','Segment Quality with slope penalty;quality;N(segments)',10,0,10)
hSegQualSlopeNorm = r.TH1F('hSegQualSlopeNorm','Segment Quality with slope penalty normalized to Quality = 1;quality;N(segments)',10,0,10)
hSegQualSlopePen = r.TH1F('hSegQualSlopePen','Quality of segments affected by slope penalty;quality;N(segments)',10,0,10)
hSegQualSlopePenFrac = r.TH1F('hSegQualSlopePenFrac','Fraction of segments affected by slope penalty;quality;Fraction of segments',10,0,10)
hSegQualSlopePenNorm = r.TH1F('hSegQualSlopePenNorm','Quality of segments affected by slope penalty;quality;N(segments)',10,0,10)

mList = ['2312','2095','2262','2064','2079','2224','2333']
toDo = [Meas.meas[i] for i in mList]
# Set list of measurements to make histograms for
for tbm in toDo:
    # Set locals
    CSC = tbm.cham
    test = tbm.runtype
    HV = tbm.HV
    beam = 'bOn' if tbm.beam else 'bOff'
    uAtt = 'uOff' if tbm.uAtt=='0' else 'u'+tbm.uAtt
    dAtt = 'dOff' if tbm.dAtt=='0' else 'd'+tbm.dAtt
    measNum = 'm'+tbm.meas
    inFile = 'data/ana_%(CSC)s_%(test)s_%(HV)s_%(beam)s_%(uAtt)s_%(dAtt)s_%(measNum)s.root'%locals()
    outFile = 'histos/ana_segHistos_%(CSC)s_%(test)s_%(HV)s_%(beam)s_%(uAtt)s_%(dAtt)s_%(measNum)s_%(sslope)s.root'%locals()
    print CSC, test, HV, beam, uAtt, dAtt, measNum
    print inFile
    print outFile
    fin = r.TFile(inFile,'read')
    tree = fin.Get('GIFTree').Get('GIFDigiTree')
    fout = r.TFile(outFile,'recreate')

    # Set beam slope parameters
    # Mean of segment slopes in x and y directions
    # - No Source, segment position w/in scintillator paddle
    if tbm.cham == 'ME21':
        bXZslope = -0.04995
        bYZslope = 0.006429
        padYlow = -2.5
        padYhigh = 12.5
        padXlow = -38.5
        padXhigh = -22.5
    else:#ME11
        bXZslope = 0.
        bYZslope = 0.
        padXlow = 0.
        padXhigh = 100.
        padYlow = 0.
        padYhigh = 100.

    # reset per measurement quantities
    events = 0
    eventsSegs = 0
    totalSegs = 0
    nSegIN = 0
    nSegOUT = 0
    nSegSlopePen = 0

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
            # N(segments)/measurement
            totalSegs = totalSegs + 1
            # N(segments)/event
            nSegs = nSegs + 1

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
            # To add : Segment Quality with slope penalty
            segSlope = ((slopeXZ)**2 + (slopeYZ)**2)**(0.5)
            dSegSlope = ((slopeXZ-bXZslope)**2 + (slopeYZ-bYZslope)**2)**(0.5)
            hSegSlope.Fill(segSlope)
            hSegdSlope.Fill(dSegSlope)
            # Inside scintillator paddle area
            if entry.segment_pos_x[seg]>padXlow and \
                entry.segment_pos_x[seg]<padXhigh and \
                entry.segment_pos_y[seg]>padYlow and \
                entry.segment_pos_y[seg]<padYhigh:
                hSegSlopeIN.Fill(segSlope)
                hSegdSlopeIN.Fill(dSegSlope)
                nSegIN = nSegIN + 1
            else: # Outside scintillator paddle area
                hSegSlopeOUT.Fill(segSlope)
                hSegdSlopeOUT.Fill(dSegSlope)
                nSegOUT = nSegOUT + 1

            # Segment Quality (all segments)
            hSegQual.Fill(seg_qual)
            hSegQualNorm.Fill(seg_qual)
            if entry.n_segments>0 and seg_qual == best_seg_qual: 
                N_best_seg_qual = N_best_seg_qual + 1
            # Add a penalty for dSlope>SLOPE
            seg_qual_slope = seg_qual
            if dSegSlope>SLOPE:
                hSegQualSlopePen.Fill(seg_qual)
                hSegQualSlopePenNorm.Fill(seg_qual)
                seg_qual_slope = seg_qual_slope + 1
                nSegSlopePen = nSegSlopePen + 1
            hSegQualSlope.Fill(seg_qual_slope)
            hSegQualSlopeNorm.Fill(seg_qual_slope)

        # Fill Per event histograms

        # N(Segments)
        hNSeg.Fill(nSegs)

        # Segment Quality (best segments)
        if entry.n_segments>0:
            hSegQualBest.SetBinContent(best_seg_qual,N_best_seg_qual)
            hSegQualBestNorm.SetBinContent(best_seg_qual,N_best_seg_qual)
            #print best_seg_qual,N_best_seg_qual

    print events, eventsSegs
    print SLOPE, tbm.dAtt[1:], nSegSlopePen, totalSegs-nSegSlopePen, totalSegs, float(nSegSlopePen)/totalSegs, \
            events, eventsSegs, float(nSegSlopePen)/eventsSegs, float(totalSegs-nSegSlopePen)/eventsSegs
    # Fill/modify per measurement histograms
    for ibin in [4,5,6,7]:
        hSeg3hits.SetBinContent(ibin,hSegNhits.GetBinContent(ibin)/hSegNhits.GetBinContent(4))
        hSeg4hits.SetBinContent(ibin,hSegNhits.GetBinContent(ibin)/hSegNhits.GetBinContent(5))
        hSeg5hits.SetBinContent(ibin,hSegNhits.GetBinContent(ibin)/hSegNhits.GetBinContent(6))
        hSeg6hits.SetBinContent(ibin,hSegNhits.GetBinContent(ibin)/hSegNhits.GetBinContent(7))
    # Normalize quality histograms to be relative to N(segment quality = 1)
    ratioToBin(hSegQualNorm,2)
    ratioToBin(hSegQualSlopeNorm,2)
    ratioToBin(hSegQualBestNorm,2)
    ratioToBin(hSegQualSlopePenNorm,2)

    for ibin in range(1,10):
        ibin = ibin + 1
        affBySlopeInBin = hSegQualSlopePen.GetBinContent(ibin)
        totalInBin = hSegQual.GetBinContent(ibin)
        if totalInBin==0 or affBySlopeInBin==0:
            hSegQualSlopePenFrac.SetBinContent(ibin,0.)
        else:
            frac = affBySlopeInBin/totalInBin
            hSegQualSlopePenFrac.SetBinContent(ibin,frac)

    # Normalize Histograms 
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
    hSegSlope.Scale(1./totalSegs)
    hSegdSlope.Scale(1./totalSegs)
    hSegSlopeIN.Scale(1./totalSegs)
    hSegdSlopeIN.Scale(1./totalSegs)
    hSegSlopeOUT.Scale(1./totalSegs)
    hSegdSlopeOUT.Scale(1./totalSegs)
    hNSeg.Scale(1./eventsSegs)
    hSegQual.Scale(1./totalSegs)
    hSegQualBest.Scale(1./totalSegs)
    hSegQualSlope.Scale(1./totalSegs)
    hSegQualSlopePen.Scale(1./totalSegs)

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
    hSegSlope.Write()
    hSegdSlope.Write()
    hSegSlopeIN.Write()
    hSegdSlopeIN.Write()
    hSegSlopeOUT.Write()
    hSegdSlopeOUT.Write()
    hSegQual.Write()
    hSegQualBest.Write()
    hSegQualSlope.Write()
    hSegQualSlopePen.Write()
    hSegQualSlopePenFrac.Write()
    hSegQualNorm.Write()
    hSegQualBestNorm.Write()
    hSegQualSlopeNorm.Write()
    hSegQualSlopePenNorm.Write()
    hNSeg.Write()

    # Close in/out files
    fout.Close()
    fin.Close()

