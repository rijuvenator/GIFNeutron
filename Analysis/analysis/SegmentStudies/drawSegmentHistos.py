''' Combines and styles histograms across multiple measurements
usage : python drawSegmentHistos.py
options : ?
'''

import os,sys
import ROOT as r
import Gif.Analysis.Measurements as Meas
from Gif.Analysis.roottools import *
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


# Set list of measurements to use for each comparison plot
to_use = {
    # Nominal set of plots
    #'ME11_Test27_HV0' : [segHisto(m) for m in ['2250','1977']],
    #'ME11_Test40_HV0' : [segHisto(m) for m in ['1966','2040']],
    #'ME21_Test27_HV0' : [segHisto(m) for m in ['2306','2062']],
    'ME21_Test40_HV0_riju'      : [segHisto(m) for m in ['2095','2064','2079','2312']],
    'ME21_Test40_HV0'           : [segHisto(m) for m in ['2095','2262','2064','2079','2224','2333','2312']],
    'ME21_Test40_HV0_u100_d10'  : [segHisto(m) for m in ['2312','2095']],
    'ME21_Test40_HV0_u46_d10'   : [segHisto(m) for m in ['2312','2262']],
    'ME21_Test40_HV0_u46_d15'   : [segHisto(m) for m in ['2312','2064']],
    'ME21_Test40_HV0_u69_d46'   : [segHisto(m) for m in ['2312','2079']],
    'ME21_Test40_HV0_u46_d100'  : [segHisto(m) for m in ['2312','2224']],
    'ME21_Test40_HV0_u69_d1000' : [segHisto(m) for m in ['2312','2333']],
}

# List of comparison plots (m2312, no source, is left implicit)
to_plot = [
    #'ME11_Test27_HV0',
    #'ME11_Test40_HV0',
    #'ME21_Test27_HV0',
    'ME21_Test40_HV0_riju',
    'ME21_Test40_HV0',
    'ME21_Test40_HV0_u100_d10',
    'ME21_Test40_HV0_u46_d10',
    'ME21_Test40_HV0_u46_d15',
    'ME21_Test40_HV0_u69_d46',
    'ME21_Test40_HV0_u46_d100',
    'ME21_Test40_HV0_u69_d1000',
]

# Loop over measurement/slope comparison plots to make
for comp in to_plot:
    outFile = ROOT.TFile('histos/segAnalysis_'+comp+'.root','recreate')
    # Loop over histograms to compare
    for hName in hists:
        # Set save name
        outname = 'plots/' + comp + '_' + hName
        
        # Set canvas options
        c = ROOT.TCanvas()
        c.SetTopMargin(0.10)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptTitle(0)
        
        # Set legend
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
        
        histMax = 0.
        for i, entry in enumerate(to_use[comp]):
            # Get measurement specific plot attributes
            hist = entry.histos[hName]
            color = colors[entry.m.dAtt]
            Ytitle,Xtitle = histAxesTitles[hName]

            # Set X,Y axes styles
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
            if i==0:
                yAxis = hist.GetYaxis()
                hist.SetStats(0)
            hist.SetTitle('')
            yAxis.SetTitle(Ytitle)
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

            # Set plot title
            HeaderLabel = ROOT.TPaveLabel(0.2, 0.92, 0.8, 0.98,entry.title,"NDC")
            # HeaderLabel.SetTextAlign(32)
            HeaderLabel.SetTextFont(42)
            HeaderLabel.SetTextSize(0.8)
            HeaderLabel.SetBorderSize(0)
            HeaderLabel.SetFillColor(0)
            HeaderLabel.SetFillStyle(0)

            # Set hist line styles
            hist.SetLineColor(color)
            hist.SetLineWidth(2)
            hist.SetLineStyle(styles[entry.m.meas])
            
            # Draw histograms and title
            leg.AddEntry(hist,entry.legEntry,'L')
            draw = 'HIST' if i==0 else 'HIST SAME'
            hist.Draw(draw)
            HeaderLabel.Draw()
            print "Wrote plot: ", outname

        # Draw legend and save plot
        leg.Draw()
        outFile.cd()
        for saveas in ['.pdf','.png']:
            c.SaveAs(outname+saveas)
        c.Write(hName)
    outFile.Close()


