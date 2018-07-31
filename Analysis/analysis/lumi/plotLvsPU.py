import ROOT as R
import numpy as np
import Gif.Analysis.Plotter as Plotter
R.gStyle.SetPadTickX(1)
R.gStyle.SetPadTickY(1)
R.gROOT.SetBatch(True)

fout = R.TFile('lumiVsPileup.root','recreate')
runlumigrid = open('../datafiles/runlumigrid')

colors = {
        0.044051627385:{'line':R.kBlack,'dots':R.kOrange+1},
        0.326879910213:{'line':R.kBlack,'dots':R.kRed},
        0.569023569024:{'line':R.kBlack,'dots':R.kBlue},
        0.592592592593:{'line':R.kBlack,'dots':R.kViolet},
        0.619528619529:{'line':R.kBlack,'dots':R.kGreen+1},
        }

T = 2.5e-8
TDRNAME = '8.73 fb^{-1} (13 TeV)'
ffdict = {
        5331:0.044051627385,
        5338:0.326879910213,
        5339:0.619528619529,
        5340:0.619528619529,
        5345:0.619528619529,
        5351:0.619528619529,
        5352:0.619528619529,
        5355:0.619528619529,
        5391:0.619528619529,
        5393:0.619528619529,
        5394:0.619528619529,
        5395:0.619528619529,
        5401:0.619528619529,
        5405:0.619528619529,
        5406:0.619528619529,
        5416:0.619528619529,
        5418:0.592592592593,
        5421:0.619528619529,
        5423:0.619528619529,
        5424:0.619528619529,
        5427:0.619528619529,
        5433:0.569023569024,
        5437:0.619528619529,
        5439:0.619528619529,
        5441:0.619528619529,
        5442:0.619528619529,
        5443:0.619528619529,
        5446:0.619528619529,
        5448:0.619528619529,
        5450:0.619528619529,
        5451:0.619528619529
        }

hists = {fill:{ 'LumiVsPU':{'hist':R.TH2F(str(fill)+'_LumiVsPU','',100,0,50,2000,0,2E34),
                            'data':{'x':np.array([]),'y':np.array([])},
                            },
                'xs':R.TH1F(str(fill)+'_xs','Min-Bias Cross Section;#sigma_{MB} [mb];N(lumi sections)',1000,68.5,70.3),
                } 
        for fill in ffdict.keys()}

xsHist = R.TH1F('xs','Min-Bias Cross Section;#sigma_{MB} [mb];N(lumi sections)',1000,79.5,80.3)
lumiVsPUhist = R.TH2F('LumiVsPU','',100,0,50,2000,0,2E34)
mbXSscale = 79940. / 69200.

ppVsL = {'L':np.array([]), 'dppdt':np.array([])}
for line in runlumigrid:
    cols = line.strip('\n').split()
    fill = int(cols[0])
    run = int(cols[1])
    ls = int(cols[2])
    lumi = float(cols[3])*1.e33
    pu = float(cols[4]) / mbXSscale
    if fill not in ffdict.keys(): continue

    xsHist.Fill(ffdict[fill]*pu*1e27/(lumi*T))
    lumiVsPUhist.Fill(pu,lumi)

    hists[fill]['LumiVsPU']['hist'].Fill(pu,lumi)
    hists[fill]['LumiVsPU']['data']['x'] = np.append(hists[fill]['LumiVsPU']['data']['x'], pu)
    hists[fill]['LumiVsPU']['data']['y'] = np.append(hists[fill]['LumiVsPU']['data']['y'], lumi)
    hists[fill]['xs'].Fill(ffdict[fill]*pu/(lumi*T)*1e27)
    ppVsL['L'] = np.append(ppVsL['L'], lumi)
    ppVsL['dppdt'] = np.append(ppVsL['dppdt'], ffdict[fill]*pu/T)

fout.cd()

c = R.TCanvas()
canvas = Plotter.Canvas(extra='Preliminary',lumi=TDRNAME)
ppVsLGraph = R.TGraph(len(ppVsL['L']),ppVsL['L'],ppVsL['dppdt'])
ppVsLPlot = Plotter.Plot(ppVsLGraph,option='p')
canvas.addMainPlot(ppVsLPlot)
ppVsLPlot.GetXaxis().SetTitle('inst. lumi. [cm^{-2} s^{-1}]')
ppVsLPlot.GetYaxis().SetTitle('N_{pp}^{CMS}/t')
ppVsLPlot.SetTitle('')
ppVsLPlot.SetMarkerStyle(R.kFullDotLarge)
canvas.Write('dppdt_vs_L')
canvas.moveExponent()
canvas.makeTransparent()
canvas.finishCanvas()
canvas.save('dppdt_vs_L.png')
canvas.deleteCanvas()

graphs = {fill:{} for fill in ffdict.keys()}
for fill in ffdict.keys():
    g = R.TGraph(len(hists[fill]['LumiVsPU']['data']['x']),hists[fill]['LumiVsPU']['data']['x'],hists[fill]['LumiVsPU']['data']['y'])
    graphs[fill]['graph'] = g.Clone()
    g.Write(str(fill)+'_LumiVsPU_graph')

    f = R.TF1(str(fill)+'_ffunc','pol1',0,50)
    #f = R.TF1(str(fill)+'_ffunc','[0]*x',0,50)
    print '-'*10
    print str(fill),'Lumi vs PU'
    g.Fit(f,'R')
    print
    print 'offset',f.GetParameter(0),f.GetParError(0)
    print 'xs',1./(f.GetParameter(1)*ffdict[fill]*T)
    print

    graphs[fill]['fit'] = f

    hists[fill]['LumiVsPU']['hist'].Write()
    hists[fill]['xs'].Write()


canvas = Plotter.Canvas(extra='Preliminary',lumi=TDRNAME)
for f,fill in enumerate(ffdict.keys()):
	graphs[fill]['plot'] = Plotter.Plot(graphs[fill]['graph'],option='p')
	canvas.addMainPlot(graphs[fill]['plot'])
	graphs[fill]['plot'].SetMarkerColor(colors[ffdict[fill]]['dots'])
	graphs[fill]['plot'].SetMarkerStyle(R.kFullDotLarge)
	graphs[fill]['plot'].GetXaxis().SetTitle('pileup')
	graphs[fill]['plot'].GetYaxis().SetTitle('inst. lumi. [cm^{-2} s^{-1}]')
	graphs[fill]['plot'].GetYaxis().SetRangeUser(0,15E33)
	graphs[fill]['plot'].GetXaxis().SetLimits(0,43)
	#graphs[fill]['graph'].SetTitle('L = 5#times10^{32} #frac{cm^{-2}s^{-1}}{pile-up pp-coll} #upoint f_{fill} #upoint pile-up')
	graphs[fill]['graph'].SetTitle('')
	#draw = 'psame' if f>0 else 'ap'
	#graphs[fill]['graph'].Draw(draw)
canvas.moveExponent()
canvas.makeTransparent()

fits = {}
lims = {
        0.619528619529:[0,40.0],
        0.592592592593:[13,39],
        0.569023569024:[23,29],
        0.326879910213:[3,39],
        0.044051627385:[21,30],
        }
for i,ff in enumerate(colors.keys()):
    fits[ff] = R.TF1('f'+str(i),str(ff)+'*5.01E32*x',*lims[ff])
    fits[ff] = R.TF1('f'+str(i),str(ff)+'*x*1e27/(69.2*2.5e-8)',*lims[ff])
    fits[ff].SetLineColor(colors[ff]['dots']+3)
    fits[ff].Draw('same')

tex = R.TLatex()
tex.SetTextSize(0.04)
tex.SetTextFont(42)
tex.DrawLatex(3,13E33,'L = #frac{f_{fill} #upoint pileup}{#sigma_{MB} #upoint 25#times10^{-9}s}, #sigma_{MB} = 69.2 mb')
leg = R.TLegend(0.15,0.45,0.4,0.7)
leg.AddEntry(graphs[5421]['graph'], 'f_{fill} = 0.62','p')
leg.AddEntry(graphs[5418]['graph'], 'f_{fill} = 0.59','p')
leg.AddEntry(graphs[5433]['graph'], 'f_{fill} = 0.57','p')
leg.AddEntry(graphs[5338]['graph'], 'f_{fill} = 0.33','p')
leg.AddEntry(graphs[5331]['graph'], 'f_{fill} = 0.04','p')
leg.SetBorderSize(0)
leg.Draw()
canvas.Write('LumiVsPU_all')
canvas.finishCanvas()
canvas.save('lumi_vs_pu_allfills.png')
canvas.deleteCanvas()

xsHist.Write()
lumiVsPUhist.Write()

