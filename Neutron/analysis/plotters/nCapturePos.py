import ROOT as R
import Gif.TestBeamAnalysis.Plotter as Plotter
import numpy as np
import array as array

# makes a plot of the captured neutron energy spectrum
# note that the x axis is log scale, and the bins are equally spaced on a log scale

f = open('../files/pos_final')
x = array.array('f',[])
y = array.array('f',[])
z = array.array('f',[])
r = array.array('f',[])
hxyz = R.TH3F('hxyz','',100,-1000,1000,100,-1300,1300,100,-1000,1000)
for line in f:
    l = line.strip('\n').split()
    if np.fabs(float(l[2])) > 1200: continue
    if np.fabs(float(l[0])) > 800: continue
    if np.fabs(float(l[1])) > 800: continue
    x.append(float(l[0]))
    y.append(float(l[1]))
    z.append(float(l[2]))
    r.append( ( (float(l[0]))**2 + (float(l[1]))**2 )**(0.5) )
    hxyz.Fill(float(l[0]),float(l[2]),float(l[1]))
nNeutrons = len(x)

hxy = R.TGraph(nNeutrons,x,y)
hxyplot = Plotter.Plot(hxy, 'Position', 'f', 'ap')
canvasxy = Plotter.Canvas('Neutron Capture Position', False, 0., 'Internal', 950, 600)
canvasxy.makeLegend()
canvasxy.addMainPlot(hxyplot,True,False)
# cosmetics
hxy.GetYaxis().SetTitle('y position [cm]')
hxy.GetXaxis().SetTitle('x position [cm]')
hxy.GetYaxis().SetTitleOffset(hxy.GetYaxis().GetTitleOffset()*1.2)
hxy.GetXaxis().SetTitleOffset(hxy.GetXaxis().GetTitleOffset()*1.2)
hxy.SetMaximum(800)
hxy.SetMinimum(-800)
hxy.GetXaxis().SetLimits(-800,800)
hxyplot.scaleTitles(0.8)
hxyplot.scaleLabels(0.8)
canvasxy.finishCanvas()
canvasxy.c.SaveAs('../pdfs/hxy.pdf')

hxz = R.TGraph(nNeutrons,z,x)
hxzplot = Plotter.Plot(hxz, 'Position', 'f', 'ap')
canvasxz = Plotter.Canvas('Neutron Capture Position', False, 0., 'Internal', 950, 600)
canvasxz.makeLegend()
canvasxz.addMainPlot(hxzplot,True,False)
# cosmetics
hxz.GetYaxis().SetTitle('x position [cm]')
hxz.GetXaxis().SetTitle('z position [cm]')
hxz.GetYaxis().SetTitleOffset(hxz.GetYaxis().GetTitleOffset()*1.2)
hxz.GetXaxis().SetTitleOffset(hxz.GetXaxis().GetTitleOffset()*1.2)
hxz.SetMaximum(800)
hxz.SetMinimum(-800)
hxz.GetXaxis().SetLimits(-1200,1200)
hxzplot.scaleTitles(0.8)
hxzplot.scaleLabels(0.8)
canvasxz.finishCanvas()
canvasxz.c.SaveAs('../pdfs/hxz.pdf')

hyz = R.TGraph(nNeutrons,z,y)
hyzplot = Plotter.Plot(hyz, 'Position', 'f', 'ap')
canvasyz = Plotter.Canvas('Captured Neutrons', False, 0., 'Internal', 950, 600)
canvasyz.makeLegend()
canvasyz.addMainPlot(hyzplot,True,False)
# cosmetics
hyz.GetYaxis().SetTitle('y position [cm]')
hyz.GetXaxis().SetTitle('z position [cm]')
hyz.GetYaxis().SetTitleOffset(hyz.GetYaxis().GetTitleOffset()*1.2)
hyz.GetXaxis().SetTitleOffset(hyz.GetXaxis().GetTitleOffset()*1.2)
hyz.SetMaximum(800)
hyz.SetMinimum(-800)
hyz.GetXaxis().SetLimits(-1200,1200)
hyzplot.scaleTitles(0.8)
hyzplot.scaleLabels(0.8)
canvasyz.finishCanvas()
canvasyz.c.SaveAs('../pdfs/hyz.pdf')

hrz = R.TGraph(nNeutrons,z,r)
hrzplot = Plotter.Plot(hrz, 'Position', 'f', 'ap')
canvasrz = Plotter.Canvas('Neutron Capture Position', False, 0., 'Internal', 950, 600)
canvasrz.makeLegend()
canvasrz.addMainPlot(hrzplot,True,False)
# cosmetics
hrz.GetYaxis().SetTitle('r position [cm]')
hrz.GetXaxis().SetTitle('z position [cm]')
hrz.GetYaxis().SetTitleOffset(hrz.GetYaxis().GetTitleOffset()*1.2)
hrz.GetXaxis().SetTitleOffset(hrz.GetXaxis().GetTitleOffset()*1.2)
hrz.SetMinimum(0)
hrz.SetMaximum(800)
hrz.GetXaxis().SetLimits(-1200,1200)
hrzplot.scaleTitles(0.8)
hrzplot.scaleLabels(0.8)
canvasrz.finishCanvas()
canvasrz.c.SaveAs('../pdfs/hrz.pdf')

cxyz = R.TCanvas()
hxyz.Draw('scat')
cxyz.SaveAs('../pdfs/hxyz.pdf')
cxyz.SaveAs('../pdfs/hxyz.root')
