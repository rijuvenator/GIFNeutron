''' Combines and styles histograms across multiple measurements
usage : python drawSegmentHistos.py
options : ?
'''

import os,sys
import ROOT as r
from Gif.TestBeamAnalysis.TestBeamMeasurements import *
from inputHists import *

r.gROOT.SetBatch(True)
r.gStyle.SetPadTickX(1)
r.gStyle.SetPadTickY(1)
r.gStyle.SetGridStyle(3)
r.gErrorIgnoreLevel = 1001

to_plot = [
    #'ME11_Test27_HV0',
    'ME11_Test40_HV0',
    #'ME21_Test27_HV0',
    'ME21_Test40_HV0',
]

measurements = [m1966,m2040,m2312,m2064]
measList = [segHisto(m) for m in measurements]
for segHisto in measList:
    exec '%s = segHisto' % segHisto.m.meas

to_use = {
    #'ME11_Test27_HV0' : (m2250,m1977),
    'ME11_Test40_HV0' : (m1966,m2040),
    #'ME21_Test27_HV0' : (m2306,m2062),
    'ME21_Test40_HV0' : (m2312,m2064),
}


for comp in to_plot:
    outFile = ROOT.TFile('histos/segAnalysis_'+comp+'.root','recreate')
    for hName in hists:
        c = ROOT.TCanvas()
        c.SetTopMargin(0.10)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptTitle(0)
        leg = ROOT.TLegend(0.45, 0.7, 0.95, 0.90)
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)
        leg.SetTextFont(42)
        draw = ''
        histMax = 0.
        for i, entry in enumerate(to_use[comp]):
            hist = entry.histos[hName]
            color, legEntry, title = styles[entry.m.meas]
            #hist.GetXaxis().SetNdivisions(5)
            #hist.GetYaxis().SetNdivisions(5)
            hist.GetXaxis().SetTitleSize(0.05)
            hist.GetYaxis().SetTitleSize(0.05)
            hist.GetZaxis().SetTitleSize(0.05)
            hist.GetXaxis().SetLabelSize(0.05)
            hist.GetYaxis().SetLabelSize(0.05)
            hist.GetZaxis().SetLabelSize(0.05)
            hist.GetXaxis().SetTitleOffset(1.0)
            hist.GetYaxis().SetTitleOffset(1.6)

            HeaderLabel = ROOT.TPaveLabel(0.2, 0.92, 0.8, 0.98,title,"NDC")
            # HeaderLabel.SetTextAlign(32)
            HeaderLabel.SetTextFont(42)
            HeaderLabel.SetTextSize(0.8)
            HeaderLabel.SetBorderSize(0)
            HeaderLabel.SetFillColor(0)
            HeaderLabel.SetFillStyle(0)
            if i==0:
                yAxis = hist.GetYaxis()
                hist.SetStats(0)
            ROOT.gStyle.SetOptTitle(0)
            hist.SetLineColor(color)
            #hist.SetTitle(title + hist.GetTitle()) 
            hist.SetLineWidth(2)
            outname = 'histos/' + comp + '_' + hName
            print "Wrote plot: ", outname
            leg.AddEntry(hist,legEntry,'L')
            thisMax = hist.GetMaximum()
            if thisMax > histMax:
                histMax = thisMax
                #hist.GetYaxis().SetRangeUser(0,1.1*histMax)
                yAxis.SetRangeUser(0,1.1*histMax)
            draw += 'HIST'
            hist.Draw(draw)
            HeaderLabel.Draw()
            draw += ' SAME'
        leg.Draw()
        outFile.cd()
        for saveas in ['.pdf','.png']:
            c.SaveAs(outname+saveas)
        c.Write(hName)
    outFile.Close()


