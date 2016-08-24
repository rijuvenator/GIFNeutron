''' Combines and styles histograms across multiple measurements
usage : python drawSegmentHistos.py
options : ?
'''

import os,sys
import ROOT as r
from Gif.TestBeamAnalysis.TestBeamMeasurements import *
from Gif.TestBeamAnalysis.roottools import *
from inputHists import *
import argparse
parser = argparse.ArgumentParser(description='Segment Analysis : make histograms from tree')
parser.add_argument('--extra',dest='extra',help='Extra info about plots',default=None)
parser.add_argument('--CSC',dest='CSC',help='Choose which CSC to make plots for',default=None)
parser.add_argument('--test',dest='test',help='Choose which test to make plots for',default=None)
args = parser.parse_args()
EXTRA = args.extra
CSC = args.CSC
TEST = args.test

r.gROOT.SetBatch(True)
r.gStyle.SetPadTickX(1)
r.gStyle.SetPadTickY(1)
r.gStyle.SetGridStyle(3)
r.gErrorIgnoreLevel = 1001

# Make segHisto classes
measList = [segHisto(m) for m in measurements if m.CSC==CSC and m.test==TEST]
print measList
for segHisto in measList:
    exec '%s = segHisto' % segHisto.m.meas

# Set list of measurements to use for each comparison plot
to_use = {
    #'ME11_Test27_HV0' : (m2250,m1977),
    #'ME11_Test40_HV0' : (m1966,m2040),
    #'ME21_Test27_HV0' : (m2306,m2062),
    'ME21_Test40_HV0' : (m2312,m2095,m2262,m2064,m2079,m2224,m2333),
    'ME21_Test40_HV0_u100_d10' : (m2312,m2095),
    'ME21_Test40_HV0_u46_d10' : (m2312,m2262),
    'ME21_Test40_HV0_u46_d15' : (m2312,m2064),
    'ME21_Test40_HV0_u69_d46' : (m2312,m2079),
    'ME21_Test40_HV0_u46_d100' : (m2312,m2224),
    'ME21_Test40_HV0_u69_d1000' : (m2312,m2333),
}

# List of comparison plots
to_plot = [
    #'ME11_Test27_HV0',
    #'ME11_Test40_HV0',
    #'ME21_Test27_HV0',
    'ME21_Test40_HV0',
    'ME21_Test40_HV0_u100_d10',
    'ME21_Test40_HV0_u46_d10',
    'ME21_Test40_HV0_u46_d15',
    'ME21_Test40_HV0_u69_d46',
    'ME21_Test40_HV0_u46_d100',
    'ME21_Test40_HV0_u69_d1000',
]


for comp in to_plot:
    outFile = ROOT.TFile('histos/segAnalysis_'+comp+'.root','recreate')
    for hName in hists:
        c = ROOT.TCanvas()
        c.SetTopMargin(0.10)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptTitle(0)
        if hName == 'hSeg3hits' or \
           hName == 'hSeg4hits' or \
           hName == 'hSeg5hits' or \
           hName == 'hSeg6hits' or \
           hName == 'hSegQual' or \
           hName == 'hSegQualBest' or \
           hName == 'hSegQualSlope' or \
           hName == 'hSegQualSlopePen' or \
           hName == 'hSegQualNorm' or \
           hName == 'hSegQualBestNorm' or \
           hName == 'hSegQualSlopePenNorm' or \
           hName == 'hSegQualSlopeNorm':
            leg = ROOT.TLegend(0.15, 0.6, 0.39, 0.85)
        elif hName == 'hSegQualSlopePenFrac':
            leg = ROOT.TLegend(0.50,0.20,0.74,0.45)
        else:
            leg = ROOT.TLegend(0.65, 0.6, 0.89, 0.85)
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)
        leg.SetTextFont(42)
        draw = ''
        histMax = 0.
        for i, entry in enumerate(to_use[comp]):
            if i==0: draw = 'HIST'
            else: draw = 'HIST SAME'

            hist = entry.histos[hName]
            color = colors[entry.m.dAtt]
            Ytitle,Xtitle = histAxesTitles[hName]

            #hist.GetXaxis().SetNdivisions(5)
            #hist.GetYaxis().SetNdivisions(5)
            hist.GetYaxis().SetTitle(Ytitle)
            hist.GetXaxis().SetTitle(Xtitle)
            hist.GetXaxis().SetTitleSize(0.04)
            hist.GetYaxis().SetTitleSize(0.04)
            hist.GetZaxis().SetTitleSize(0.04)
            hist.GetXaxis().SetLabelSize(0.03)
            hist.GetYaxis().SetLabelSize(0.035)
            hist.GetZaxis().SetLabelSize(0.035)
            hist.GetXaxis().SetTitleOffset(1.0)
            #hist.GetYaxis().SetTitleOffset(1.6)

            HeaderLabel = ROOT.TPaveLabel(0.2, 0.92, 0.8, 0.98,entry.title,"NDC")
            # HeaderLabel.SetTextAlign(32)
            HeaderLabel.SetTextFont(42)
            HeaderLabel.SetTextSize(0.8)
            HeaderLabel.SetBorderSize(0)
            HeaderLabel.SetFillColor(0)
            HeaderLabel.SetFillStyle(0)

            if i==0:
                yAxis = hist.GetYaxis()
                hist.SetStats(0)
            hist.SetTitle('')
            yAxis.SetTitle(Ytitle)
            hist.SetLineColor(color)
            hist.SetLineWidth(2)
            hist.SetLineStyle(styles[entry.m.meas])
            outname = 'histos/' + comp + '_' + hName
            print "Wrote plot: ", outname
            leg.AddEntry(hist,entry.legEntry,'L')
            if hName == 'hSeg3hits' or \
               hName == 'hSeg4hits' or \
               hName == 'hSeg5hits' or \
               hName == 'hSeg6hits' or \
               hName == 'hSegQualSlopePenNorm':
                thisMax = hist.GetMaximum()
                if thisMax > histMax:
                    histMax = thisMax
                    yAxis.SetRangeUser(0,1.1*histMax)
            else:
                low,high = yLimits[hName]
                yAxis.SetRangeUser(low,high)
            hist.Draw(draw)
            HeaderLabel.Draw()
        # Plot options
        leg.Draw()
        outFile.cd()
        for saveas in ['.pdf','.png']:
            c.SaveAs(outname+saveas)
        c.Write(hName)
    outFile.Close()


