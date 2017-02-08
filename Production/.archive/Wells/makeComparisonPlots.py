#!/usr/bin/env python
from optparse import OptionParser
import os
import re
import sys

parser = OptionParser()

parser.add_option("-i", "--input", dest="input",
                      help="input configuration file")

(arguments, args) = parser.parse_args()

from ROOT import gROOT, gStyle, TCanvas, TFile, TH1F, TLegend, TMath, TPaveLabel    


if arguments.input:
    sys.path.append(os.getcwd())
    exec("from " + re.sub (r".py$", r"", arguments.input) + " import *")
else:
    print "Please specify input file with -i option."
    sys.exit(0)

sys.path.append(os.environ['CMSSW_BASE'] + "/src/AnalysisScripts/") 
import CMS_lumi_CSC, tdrstyle

tdrstyle.setTDRStyle()

gROOT.SetBatch()
gStyle.SetOptStat(0)  
gStyle.SetPalette(1) 

fout = TFile(outputDir + "output.root", "RECREATE")  

# Make a single plot 
for plot in plots:
    c = TCanvas() 
    # c.SetRightMargin(0.15)
    c.SetTopMargin(0.10)
    gStyle.SetOptStat(0)  
    
    f1 = TFile(plot["file1"])  
    f2 = TFile(plot["file2"]) 
    h1 = f1.Get("GIFAnalysis").Get(plot["name"])
    h2 = f2.Get("GIFAnalysis").Get(plot["name"])
    h1.GetXaxis().SetNdivisions(5)  
    h1.GetYaxis().SetNdivisions(5)  
    h1.GetXaxis().SetTitleSize(0.05)
    h1.GetYaxis().SetTitleSize(0.05)
    h1.GetZaxis().SetTitleSize(0.05)
    h1.GetXaxis().SetLabelSize(0.05)
    h1.GetYaxis().SetLabelSize(0.05)
    h1.GetZaxis().SetLabelSize(0.05)
    h1.GetXaxis().SetTitleOffset(1.0) 
    h1.GetYaxis().SetTitleOffset(1.6) 

    HeaderLabel = TPaveLabel(0.2, 0.92, 0.8, 0.98,title,"NDC")
    # HeaderLabel.SetTextAlign(32)
    HeaderLabel.SetTextFont(42)
    HeaderLabel.SetTextSize(0.8) 
    HeaderLabel.SetBorderSize(0)
    HeaderLabel.SetFillColor(0)
    HeaderLabel.SetFillStyle(0)

    if h1.Class().InheritsFrom("TH2"):
        is2D = True
    else:
        is2D = False  

    if is2D:
        c.SetRightMargin(0.15)  
        c.SetLogz(True)  
        HeaderLabel.SetTextSize(0.7) 

        h1.Draw("colz")
        HeaderLabel.SetLabel(title + ": " + plot["label1"])  
        HeaderLabel.Draw()  
        outname = outputDir + plot["name"] + "_1.pdf"  
        c.SaveAs(outname)
        fout.cd()
        c.Write()
        print "Wrote plot: ", outname

        h1.Draw("axis")  # draw axis only
        h2.GetZaxis().SetTitleSize(0.05)
        h2.GetZaxis().SetLabelSize(0.05)
        h2.Draw("same, colz")
        HeaderLabel.SetLabel(title + ": " + plot["label2"])  
        HeaderLabel.Draw()  
        outname = outputDir + plot["name"] + "_2.pdf"  
        c.SaveAs(outname)
        fout.cd()
        c.Write()
        print "Wrote plot: ", outname

    else: 
        h1.SetLineColor(plot["color1"])  
        h2.SetLineColor(plot["color2"])  
        h1.SetMaximum(1.1*TMath.Max(h1.GetMaximum(), h2.GetMaximum())) 
        h1.SetMinimum(0) 
        # print "Title is ", h1.GetTitle()  
        h1.SetTitle(title + h1.GetTitle()) 
        h1.SetLineWidth(2) 
        h2.SetLineWidth(2) 
        h1.Draw("hist")
        h2.Draw("hist same")

        leg = TLegend(0.45, 0.7, 0.95, 0.90)
        leg.AddEntry(h1, plot["label1"], "l")
        leg.AddEntry(h2, plot["label2"], "l")
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)  
        leg.SetTextFont(42)  
        leg.Draw("l")

        HeaderLabel.Draw()  
        outname = outputDir + plot["name"] + ".pdf"  
        c.SaveAs(outname)
        fout.cd()
        c.Write()
        print "Wrote plot: ", outname

fout.Close()  





