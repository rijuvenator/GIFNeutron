import ROOT as R
import numpy as np

R.gROOT.SetBatch(True)
R.gStyle.SetOptStat("emr")
R.gStyle.SetTitleBorderSize(0)
R.gStyle.SetPadTickX(1)
R.gStyle.SetPadTickY(1)
R.gStyle.SetTitleW(0.99)
R.gStyle.SetTitleH(0.05)
R.gStyle.SetTitleFont(42,'')
R.gStyle.SetTitleFont(42,'XYZ')
R.gStyle.SetTitleFontSize(0.04)
R.gStyle.SetTitleFontSize(0.04)
R.gStyle.SetLabelFont(42, 'XYZ')
R.gStyle.SetLabelSize(0.04, 'XYZ')


fileDict = {
		'MinEventTimeSummary':{
			'title':'Minimum Event Time',
			'bins':100,
			'min':0,
			'max':11000,
			},
		'MaxEventTimeSummary':{
			'title':'Maximum Event Time',
			'bins':100,
			'min':0,
			'max':11000,
			},
		'AvgEventTimeSummary':{
			'title':'Average Event Time',
			'bins':100,
			'min':0,
			'max':3000,
			},
		'TotalJobTimeSummary':{
			'title':'Time Summary Total Job',
			'bins':100,
			'min':0,
			'max':80000,
			},
		'TotalLoopTimeSummary':{
			'title':'Time Summary Total Loop',
			'bins':100,
			'min':0,
			'max':80000,
			},
		'TotalJobCPUSummary':{
			'title':'CPU Summary Total Job',
			'bins':100,
			'min':0,
			'max':80000,
			},
		'TotalLoopCPUSummary':{
			'title':'CPU Summary Total Loop',
			'bins':100,
			'min':0,
			'max':80000,
			},
		'CrabUserCpuTime':{
			'title':'CRAB User CPU Time',
			'bins':100,
			'min':0,
			'max':80000,
			},
		'ExeTime':{
			'title':'CRAB ExeTime',
			'bins':100,
			'min':0,
			'max':80000,
			},
}

for timeFileName in fileDict.keys():
	print timeFileName
	timeFile = open('data/'+timeFileName)

	timeHist = R.TH1F('h'+timeFileName,'',fileDict[timeFileName]['bins'],fileDict[timeFileName]['min'],fileDict[timeFileName]['max'])

	for l,line in enumerate(timeFile):
		time = line.strip('\n')
		timeHist.Fill(float(time))

	c = R.TCanvas()
	timeHist.Draw()
	R.gPad.Update()
	timeHist.SetTitle(fileDict[timeFileName]['title'])
	timeHist.GetXaxis().SetTitle('time [s]')
	timeHist.GetYaxis().SetTitle('Counts')
	timeHist.SetFillColor(R.kOrange)
	timeHist.SetLineWidth(0)
	stats = timeHist.FindObject('stats')
	stats.SetX1NDC(0.6)
	stats.SetX2NDC(0.8)
	stats.SetY1NDC(0.6)
	stats.SetY2NDC(0.8)
	stats.SetBorderSize(0)
	c.SaveAs('pdfs/'+timeFileName+'.pdf')
