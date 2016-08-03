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
    alctTime = []
    alreadyPicked = 999

    # Loop on ALCTs
    for alct,aid in enumerate(entry.alct_id):
        

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
