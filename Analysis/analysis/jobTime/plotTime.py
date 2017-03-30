'''
Script to plot job timing information

- Requires timing data to be stored in 
  data/<mcType>/<timeDataFile>

- Gather data by running getTimes.sh in a CRAB results 
  directory with the job_out.*.*.txt files from the 
  command:
  $ crab getlog --short --jobids 1-X crab/crab_name

- May need to do some extra cleaning by hand
  - CrabUserCpuTime and ExeTime will have trailing 
  commas on every line
  - All other files will have a leading line or two 
  to delete
'''
import ROOT as R
import Gif.Analysis.Plotter as Plotter
R.gROOT.SetBatch(True)

# Types of MC to plot
mcTypes = ['HP_ThermalON','HP_ThermalOFF','XS_ThermalON','XS_ThermalOFF']

# Types of times to plot
timeTypes = ['MinEventTimeSummary','MaxEventTimeSummary','AvgEventTimeSummary',
		'TotalJobTimeSummary','TotalLoopTimeSummary','TotalLoopCPUTimeSummary',
		'TotalJobCPUTimeSummary','CrabUserCpuTime','ExeTime',
		'EventThroughput']

# Set dictionary containing data locations and histograms
fileDict = {mcType:{} for mcType in mcTypes}
for mcType in fileDict.keys():
	fileDict[mcType] = {
		'MinEventTimeSummary'     :{
			'data':'data/'+mcType+'/MinEventTimeSummary',
			'hist':R.TH1F(mcType+'_MinEventTimeSummary',''    ,100,0,20000),
		},
		'MaxEventTimeSummary'     :{
			'data':'data/'+mcType+'/MaxEventTimeSummary',
			'hist':R.TH1F(mcType+'_MaxEventTimeSummary',''    ,100,0,20000),
		},
		'AvgEventTimeSummary'     :{
			'data':'data/'+mcType+'/AvgEventTimeSummary',
			'hist':R.TH1F(mcType+'_AvgEventTimeSummary',''    ,100,0,3000),
		},
		'TotalJobTimeSummary'     :{
			'data':'data/'+mcType+'/TotalJobTimeSummary',
			'hist':R.TH1F(mcType+'_TotalJobTimeSummary',''    ,100,0,100000),
		},
		'TotalLoopTimeSummary'    :{
			'data':'data/'+mcType+'/TotalLoopTimeSummary',
			'hist':R.TH1F(mcType+'_TotalLoopTimeSummary',''   ,100,0,100000),
		},
		'TotalJobCPUTimeSummary'  :{
			'data':'data/'+mcType+'/TotalJobCPUTimeSummary',
			'hist':R.TH1F(mcType+'_TotalJobCPUTimeSummary','' ,100,0,100000),
		},
		'TotalLoopCPUTimeSummary' :{
			'data':'data/'+mcType+'/TotalLoopCPUTimeSummary',
			'hist':R.TH1F(mcType+'_TotalLoopCPUTimeSummary','',100,0,100000),
		},
		'CrabUserCpuTime'         :{
			'data':'data/'+mcType+'/CrabUserCpuTime',
			'hist':R.TH1F(mcType+'_CrabUserCpuTime',''        ,100,0,100000),
		},
		'ExeTime'                 :{
			'data':'data/'+mcType+'/ExeTime',
			'hist':R.TH1F(mcType+'_ExeTime',''                ,100,0,100000),
		},
		'EventThroughput'        :{
			'data':'data/'+mcType+'/EventThroughput',
			'hist':R.TH1F(mcType+'_EventThroughput',''       ,100,0,0.025),
		},
	}

# Set color and legend titles for each MC type
mcDict = {mcType:{} for mcType in mcTypes}
mcDict['XS_ThermalOFF']['color'] = R.kBlue
mcDict['XS_ThermalOFF']['title'] = 'XS Thermal OFF'
mcDict['XS_ThermalON']['color'] = R.kGreen
mcDict['XS_ThermalON']['title'] = 'XS Thermal ON'
mcDict['HP_ThermalOFF']['color'] = R.kRed
mcDict['HP_ThermalOFF']['title'] = 'HP Thermal OFF'
mcDict['HP_ThermalON']['color'] = R.kOrange+1
mcDict['HP_ThermalON']['title'] = 'HP Thermal ON'
print fileDict


# Fill histograms
for mcType in fileDict.keys():
	print mcType
	for timeType in fileDict[mcType].keys():
		timeFile = open(fileDict[mcType][timeType]['data'])
		for line in timeFile:
			time = line.strip('\n')
			fileDict[mcType][timeType]['hist'].Fill(float(time))


# Draw plots
for timeType in timeTypes:
	plots = []
	# Make Plot class
	canvas = Plotter.Canvas(lumi=timeType)
	canvas.makeLegend(pos='tr')
	canvas.legend.moveLegend(X=-0.2)
	for mcType in mcTypes:
		hist = fileDict[mcType][timeType]['hist']
		hist.SetLineColor(mcDict[mcType]['color'])
		# Normalize to unit area, so that jobs with unequal numbers of jobs
		# can be compared
		hist.Scale(1./hist.Integral())
		plot = Plotter.Plot(hist,legName=mcDict[mcType]['title'],option='hist',legType='l')
		plots.append(plot)
		canvas.addMainPlot(plot)
		plot.SetLineColor(mcDict[mcType]['color'])
		canvas.addLegendEntry(plot)

	# Make Canvas class and draw plot classes
	# and make Legend class and add plot legend entries
	maximum = max(plots[0].GetMaximum(), plots[1].GetMaximum(), plots[2].GetMaximum(), plots[3].GetMaximum())
	canvas.firstPlot.SetMaximum(maximum*1.05)


	# Finish up
	canvas.makeTransparent()
	canvas.finishCanvas('BOB')
	canvas.save('pdfs/'+timeType+'.pdf')
	canvas.deleteCanvas()


