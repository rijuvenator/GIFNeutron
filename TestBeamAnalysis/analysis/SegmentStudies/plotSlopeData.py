import ROOT as r
import array as array
import numpy as np

def savePlot(canvas,plotName):
    canvas.Print(plotName+'.png','png')
    canvas.Print(plotName+'.pdf','pdf')
    canvas.Print(plotName+'.root','root')

def plotData(data,fewer):
    fileData = open(data, 'r')

    att=[]
    frac=[]
    dataX={}
    dataY1={}
    dataY2={}
    
    c = r.TCanvas('c','c',0,0,800,600)
    mg1 = r.TMultiGraph()
    mg2 = r.TMultiGraph()
    r.gStyle.SetOptStat(0)

    if fewer:
        # Slope values >= 0.65
        slopes = [0.065, 0.0675, 0.070, 0.0725, 0.075,0.0775, 0.080,0.0825, 0.085]
        colors = [r.kMagenta, r.kYellow, r.kSpring, r.kBlack, r.kGray, r.kTeal, r.kAzure, r.kPink, r.kCyan]
    else:
        # All slope values
        slopes = [0.040, 0.045, 0.050, 0.055, 0.060, 0.065, 0.070, 0.075, 0.0775, 0.080, 0.0825, 0.085, 0.090, 0.095, 0.100, 0.105, 0.11, 0.115]
        colors = [r.kGreen+1, r.kBlue, r.kRed, r.kViolet, r.kOrange+1, r.kMagenta, r.kYellow+1, r.kSpring, r.kBlack, r.kGray, r.kTeal, r.kAzure, r.kPink, r.kCyan, r.kOrange, r.kGreen+2, r.kYellow+3, r.kRed-1]

    # Make slope cut keyed lists X and Y
    # X - 1/A
    # Y1 - N(segments not penalized) / events with segments
    # Y2 - N(segments penalized) / events with segments
    # Since there's two 1/A = 0.10 measurements, just pick the first
    # Loop on keys and make a graph for each slope cut and plot them all together in a multi-graph
    #
    # Also, calculate and print out the mean difference from 1 for each slope cut
    # Mean( |frac-1| over all att ) for each slope cut (still skipping second 1/A=0.10 measurement)

    for entry in fileData:
        slopeKey = float(entry.split()[0])
        for slope in slopes: 
            #print slope, slopeKey
            if slope == slopeKey:
                if slope not in dataX: dataX[slope] = []
                if slope not in dataY1: dataY1[slope] = []
                if slope not in dataY2: dataY2[slope] = []
                if entry.split()[1]=='Off': attPoint = 0
                else: attPoint=1./float(entry.split()[1])
                if attPoint in dataX[slope]: continue
                dataX[slope].append(attPoint)
                frac1=float(entry.split()[9])
                dataY1[slope].append(frac1)
                frac2=float(entry.split()[8])
                dataY2[slope].append(frac2)
    
    # Plot and print best fit constant line to each slope cut
    for slope in slopes:
        print '*****'
        tot1 = 0
        tot2 = 0
        for attPt,frac1,frac2 in zip(dataX[slope],dataY1[slope], dataY2[slope]):
            tot1 += abs(frac1)
            tot2 += abs(frac2)
            if attPt == 0.:
                att = 'NS'
            else: att = int(1./attPt)
            print attPt, att, abs(1-frac1), frac2
        print '*'
        print slope, tot1
        print slope, tot2

    # what to plot
    draw = 'pl'
    leg1 = r.TLegend(0.91,0.55, 1.0,0.99)
    leg1.SetLineWidth(0)
    leg2 = r.TLegend(0.91,0.55, 1.0,0.99)
    leg2.SetLineWidth(0)
    for color, slope in reversed(zip(colors,slopes)):
        X = array.array('d',dataX[slope])
        # Segments not penalized / events w segments
        Y1 = array.array('d',dataY1[slope])
        Graph1 = r.TGraph(len(X),X,Y1)
        Graph1.SetLineWidth(2)
        Graph1.SetFillStyle(0)
        Graph1.SetMarkerColor(color)
        Graph1.SetLineColor(color)
        Graph1.SetDrawOption('pl')
        leg1.AddEntry(Graph1,'%s'%slope,'l')
        mg1.Add(Graph1)
        # Segments penalized / events w segments
        Y2 = array.array('d',dataY2[slope])
        Graph2 = r.TGraph(len(X),X,Y2)
        Graph2.SetLineWidth(2)
        Graph2.SetFillStyle(0)
        Graph2.SetMarkerColor(color)
        Graph2.SetLineColor(color)
        Graph2.SetDrawOption('pl')
        leg2.AddEntry(Graph2,'%s'%slope,'l')
        mg2.Add(Graph2)
    
    # Draw Segments not penalized plot
    mg1.Draw('apl')
    mg1.GetXaxis().SetTitle('Source Intensity (1/Att)')
    mg1.GetYaxis().SetTitle('<N(not penalized segments)> / events')
    mg1.SetTitle('Fraction of segments not penalized in events with segments at various cut values')
    mg1.GetXaxis().SetLimits(0,0.1)
    leg1.Draw()
    line = r.TLine(0,1,0.1,1)
    line.SetLineStyle(2)
    line.SetLineWidth(2)
    line.Draw()
    c.SetTickx(1)
    c.SetTicky(1)
    c.Update()
    saveName = 'histos/slopeCutNotPenalized'
    if fewer: saveName += 'Fewer'
    savePlot(c,saveName)

    # Draw segments penalized plot
    mg2.Draw('apl')
    mg2.GetXaxis().SetTitle('Source Intensity (1/Att)')
    mg2.GetYaxis().SetTitle('<N(penalized segments)> / events')
    mg2.SetTitle('Fraction of segments penalized in events with segments at various cut values')
    mg2.GetXaxis().SetLimits(0,0.1)
    leg2.Draw()
    c.SetTickx(1)
    c.SetTicky(1)
    c.Update()
    saveName = 'histos/slopeCutPenalized'
    if fewer: saveName += 'Fewer'
    savePlot(c,saveName)


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(usage='plotSlopeData.py --data DATA --output OUTPUT',description = 'Plots things', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--data',dest='data',default='optimizeSlopeData.txt',help='text file with slope data')
    parser.add_argument('--fewer',dest='fewer',action='store_true',default=False,help='Plot fewer lines')
    args = parser.parse_args()
    
    plotData(args.data,args.fewer)
