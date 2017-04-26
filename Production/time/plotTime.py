import ROOT as R
import numpy as np

mcTypes = ['HP_ThermalON','HP_ThermalOFF','XS_ThermalON']#,'XS_ThermalOFF]

timeTypes = ['MinEventTimeSummary','MaxEventTimeSummary','AvgEventTimeSummary',
		'TotalJobTimeSummary','TotalLoopTimeSummary','TotalLoopCPUTimeSummary',
		'TotalJobCPUTimeSummary','CrabUserCpuTime','ExeTime',
		'EventThoroughput']

fileDict = {mcType:{} for mcType in mcTypes}
for mcType in fileDict.keys():
	fileDict[mcType] = {
		'MinEventTimeSummary'     :{
			'data':'data/'+mcType+'/MinEventTimeSummary',
			'hist':R.TH1F(mcType+'_MinEventTimeSummary',''    ,100,0,20000),
		}
		'MaxEventTimeSummary'     :{
			'data':'data/'+mcType+'/MaxEventTimeSummary',
			'hist':R.TH1F(mcType+'_MaxEventTimeSummary',''    ,100,0,20000),
		}
		'AvgEventTimeSummary'     :{
			'data':'data/'+mcType+'/AvgEventTimeSummary',
			'hist':R.TH1F(mcType+'_AvgEventTimeSummary',''    ,100,0,1000),
		}
		'TotalJobTimeSummary'     :{
			'data':'data/'+mcType+'/TotalJobTimeSummary',
			'hist':R.TH1F(mcType+'_TotalJobTimeSummary',''    ,100,0,100000),
		}
		'TotalLoopTimeSummary'    :{
			'data':'data/'+mcType+'/TotalLoopTimeSummary',
			'hist':R.TH1F(mcType+'_TotalLoopTimeSummary',''   ,100,0,100000),
		}
		'TotalJobCPUTimeSummary'  :{
			'data':'data/'+mcType+'/TotalJobCPUTimeSummary',
			'hist':R.TH1F(mcType+'_TotalJobCPUTimeSummary','' ,100,0,100000),
		}
		'TotalLoopCPUTimeSummary' :{
			'data':'data/'+mcType+'/TotalLoopCPUTimeSummary',
			'hist':R.TH1F(mcType+'_TotalLoopCPUTimeSummary','',100,0,100000),
		}
		'CrabUserCpuTime'         :{
			'data':'data/'+mcType+'/CrabUserCpuTime',
			'hist':R.TH1F(mcType+'_CrabUserCpuTime',''        ,100,0,100000),
		}
		'ExeTime'                 :{
			'data':'data/'+mcType+'/ExeTime',
			'hist':R.TH1F(mcType+'_ExeTime',''                ,100,0,100000),
		}
		'EventThoroughput'        :{
			'data':'data/'+mcType+'/EventThoroughput',
			'hist':R.TH1F(mcType+'_EventThoroughput','',      ,100,0,1),
		}
	}

for mcType in fileDict.keys():
	for timeType in fileDict[mcType].keys():
		for l,line in fileDict[mcType][timeType]['data']:
			time = float(line.strip('\n'))
			fileDict[mcType][timeType]['hist'].Fill(time)


for timeType in timeTypes:
	hist1 = fileDict['XS_ThermalON'][timeType]['hist']
	hist1.SetLineColor(R.kGreen)
	plot1 = Plotter.Plot(hist1,legName='XS Thermal ON',option='hist')

	#hist2 = fileDict['XS_ThermalOFF'][timeType]['hist']
	#hist2.SetLineColor(R.kBlue)
	#plot2 = Plotter.Plot(hist2,legName='XS Thermal OFF',,option='hist')

	hist3 = fileDict['HP_ThermalON'][timeType]['hist']
	hist3.SetLineColor(R.kOrange+1)
	plot3 = Plotter.Plot(hist3,legName='HP Thermal ON',,option='hist')

	hist4 = fileDict['HP_ThermalOFF'][timeType]['hist']
	hist4.SetLineColor(R.kRed)
	plot4 = Plotter.Plot(hist4,legName='HP Thermal OFF',,option='hist')

	canvas = Plotter.Canvas(lumi=TimeType)
	canvas.addMainPlot(plot1)
	canvas.addMainPlot(plot2)
	canvas.addMainPlot(plot3)
	canvas.addMainPlot(plot4)

	canvas.makeLegend(pos='tr')
	canvas.addLegendEntry(plot1)
	canvas.addLegendEntry(plot2)
	canvas.addLegendEntry(plot3)
	canvas.addLegendEntry(plot4)

	canvas.makeTransparent()
	canvas.finishCanvas('BOB')
	canvas.save('pdfs/'+timeType+'.pdf')
	canvas.deleteCanvas()


