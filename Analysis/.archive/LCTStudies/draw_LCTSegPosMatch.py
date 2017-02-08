import ROOT
import struct

f = ROOT.TFile('data/ana_ME11_Test27_HV0_bOn_u46_d46_m1977.root','read')
#f = ROOT.TFile('data/ana_ME11_Test40_HV0_bOn_u46000_d46_m2040.root','read')
#f = ROOT.TFile('data/ana_ME11_Test27_HV0_bOn_uOff_dOff_m2250.root','read')
#f = ROOT.TFile('data/ana_ME11_Test40_HV0_bOn_uOff_dOff_m1966.root','read')
tree = f.Get('GIFTree').Get('GIFDigiTree')
makePlot = False
debug = True
ROOT.gStyle.SetOptStat(0)

if makePlot:
    # Segment chi2/dof
    histsChi2pDoF = []
    histsChi2pDoF_cut = []
    # Only Degrees of freedom 2,4,6,8 exist for segments
    # dof = 2*nRecHits - 4
    for i,d in enumerate(range(2,10,2)):
        histsChi2pDoF.append(ROOT.TH1F('hSegChi2p%sDoF'%d,'Segment #chi^{2}/%s dof;#chi^{2}/dof;N'%d,100,0,50))
        histsChi2pDoF[i].SetLineWidth(2)
        histsChi2pDoF[i].SetLineColor(ROOT.kBlue)
        histsChi2pDoF_cut.append(histsChi2pDoF[i].Clone('histsChi2p%sDoF_cut'%d))
        histsChi2pDoF_cut[i].SetLineWidth(2)
        histsChi2pDoF_cut[i].SetLineColor(ROOT.kOrange+1)
    # segment nHits
    hSegNhits = ROOT.TH1F('hSegNhits',';rec hits in segment;N',100,0,50)
    hSegNhits.SetLineWidth(2)
    hSegNhits.SetLineColor(ROOT.kBlue)
    hSegNhits_cut = hSegNhits.Clone('hSegNhits_cut')
    hSegNhits_cut.SetLineWidth(2)
    hSegNhits_cut.SetLineColor(ROOT.kOrange+1)
    leg = ROOT.TLegend(0.45, 0.7, 0.95, 0.90)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)

for n,entry in enumerate(tree):

    # Clear per entry quantities
    lctXpos = []
    alreadyPicked = 999

    # Loop on LCTs
    for lct,lid in enumerate(entry.lct_id):
        # Clear per LCT quantites
        segHits = []
        segXpos = []
        stripDiff = 999.
        minstripDiff = 999.
        #chosenSeg = 999

        # Get strip position of lct
        lctXpos.append((struct.unpack('1b',entry.lct_keyHalfStrip[lct])[0]+1)/2)
        if debug: print 'LCT strip pos ',lctXpos[lct]

        if debug: print 'Number of segments',len(entry.segment_id), entry.segment_id.size()
        # Loop on segments
        for seg,sid in enumerate(entry.segment_id):
            segHits.append(struct.unpack('1b',entry.segment_nHits[seg])[0])
            # Get strip position of layer 3 in segment
            if entry.rh_strip_2.size()==0:
                segXpos.append(struct.unpack('1b',entry.rh_strip_1[entry.segment_recHitIdx_3[seg]])[0])
                if debug: print 'Segment strip pos',segXpos[seg],segHits[seg]
            else:
                segXpos.append(struct.unpack('1b',entry.rh_strip_2[entry.segment_recHitIdx_3[seg]])[0])
                if debug: print 'Segment strip pos',segXpos[seg],segHits[seg]
        
            # Get closest segment to lct that has most hits and hasn't already been picked
            stripDiff = segXpos[seg] - lctXpos[lct]
            if seg == alreadyPicked:
                # If the current seg for the current LCT has already been picked
                # dont pick it and go to next segment
                continue
            else:
                # Set the matched segment if it hasn't already been matched
                if abs(stripDiff) < minstripDiff:
                    # If distance is smallest set chosen segment
                    chosenSeg = seg
                    minstripDiff = abs(stripDiff)
                elif abs(stripDiff) == minstripDiff:
                    # If distance is equal to smallest choose segment based on most hits
                    if segHits[seg] > segHits[chosenSeg]:
                        chosenSeg = seg
                        minstripDiff = abs(stripDiff)
    
        # Make sure there's an LCT and a segment in the entry
        if entry.lct_id.size()>0 and entry.segment_id.size()>0:
            # Print matched LCT and Segment strip positions
            if debug: print 'Chosen segment strip, hits:',segXpos[chosenSeg],segHits[chosenSeg],'Chosen LCT strip:',lctXpos[lct]
        
            # Fill Histograms per LCT matching
            chi2 = entry.segment_chisq[chosenSeg]
            dof = struct.unpack('1b',entry.segment_dof[chosenSeg])[0]
            chosenchi2dof = chi2/dof
            # Fill chosen segment histograms
            if entry.lct_pattern[lct] >= 8:
                # If LCT has a straight pattern
                if makePlot: hSegNhits.Fill(struct.unpack('1b',entry.segment_nHits[chosenSeg])[0])
                for i,d in enumerate(range(2,10,2)):
                    if dof == d:
                        if debug: print 'chi2',chi2,'dof',dof,'iterator',d
                        # Fill histograms for particular dof
                        if makePlot: histsChi2pDoF_cut[i].Fill(chosenchi2dof)
                            
            # Save the segment that was picked for an LCT
            alreadyPicked = chosenSeg
        if debug: print
    if debug: print '----------------'
    if debug: print

    # Fill histograms that don't need LCT matching 
    for seg,sid in enumerate(entry.segment_id):
        chi2 = entry.segment_chisq[seg]
        dof = struct.unpack('1b',entry.segment_dof[seg])[0]
        nHits = struct.unpack('1b',entry.segment_nHits[seg])[0]
        chi2dof = chi2/dof
        if makePlot: hSegNhits_cut.Fill(nHits)
        for i,d in enumerate(range(2,10,2)):
            if dof == d:
                if makePlot: histsChi2pDoF[i].Fill(chi2dof)

if makePlot:
    # Draw/Save chi2/dof histo
    for i,d in enumerate(range(2,10,2)):
        c1 = ROOT.TCanvas()
        histsChi2pDoF[i].Draw('hist')
        leg.AddEntry(histsChi2pDoF[i],'All segments','L')
        histsChi2pDoF_cut[i].Draw('hist same')
        leg.AddEntry(histsChi2pDoF_cut[i],'Segments with matched LCT & Pattern ID >= 8','L')
        leg.Draw()
        c1.SetLogy()
        c1.SaveAs('hSegChi2p%sDoF_ME11_Test27_sourceOn.png'%d)
        #c1.SaveAs('hSegChi2p%sDoF_ME11_Test40_sourceOn.png'%d)
        #c1.SaveAs('hSegChi2p%sDoF_ME11_Test27_sourceOff.png'%d)
        #c1.SaveAs('hSegChi2p%sDoF_ME11_Test40_sourceOff.png'%d)
        c1.Delete()
    c1 = ROOT.TCanvas()
    # Draw/Save nHits histo
    c1.SetLogy(1)
    hSegNhits.Draw('hist')
    #c1.SaveAs('hSegNhits.png')
    leg.AddEntry(hSegNhits,'All segments','L')
    hSegNhits_cut.Draw('hist same')
    leg.AddEntry(hSegNhits_cut,'Segments with matched LCT & Pattern ID >= 8','L')
    leg.Draw()
    c1.SaveAs('hSegNhits_ME11_Test27_sourceOn.png')
    #c1.SaveAs('hSegNhits_ME11_Test40_sourceOn.png')
    #c1.SaveAs('hSegNhits_ME11_Test27_sourceOff.png')
    #c1.SaveAs('hSegNhits_ME11_Test40_sourceOff.png')
