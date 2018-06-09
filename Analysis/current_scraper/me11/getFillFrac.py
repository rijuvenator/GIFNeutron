import numpy as np
from helper11 import fills

fillFile = open('../../analysis/datafiles/bunchstructures')

lumis = {
		5451:349.95178,
		5450:106.41861,
		5448:364.63391,
		5446:322.76547,
		5443:400.04984,
		5442:419.04622,
		5441:271.27872,
		5439:398.80341,
		5437:126.82923,
		5433:175.96552,
		5427:223.44873,
		5424:126.59911,
		5423:498.88300,
		5421:434.58981,
		5418:350.80488,
		5416:594.41850,
		5406:217.41214,
		5405:152.59228,
		5401:188.09125,
		5395:23.72786,
		5394:441.68734,
		5393:472.15128,
		5391:22.22395,
		5355:392.59656,
		5352:358.30631,
		5351:393.66094,
		5345:397.88459,
		5340:469.43272,
		5339:442.17359,
		5338:77.46145,
		5331:9.56052,
		}

valTypes = ['current','offset','slope']
valDict = {fill:{valType:{ec:{} for ec in ['p','m']} for valType in valTypes} for fill in lumis.keys()}
for valType in valTypes:
	valFile = open('test_tmp/logs/fill_'+valType+'.log')
	for line in valFile:
		cols = line.strip('\n').split()
		fill = int(cols[0])
		valPlus = float(cols[1])
		valMinus = float(cols[3])
		valDict[fill][valType]['p'] = valPlus
		valDict[fill][valType]['m'] = valMinus

totalLumi = 0.
avgFF = 0.
avgVal = {
		'current':0.,
		'offset':0.,
		'slope':0.,
		}

for fill in fills.keys():
	if fill==5331: continue
	if fill==5339: continue
	if fill==5351: continue
	if fill==5355: continue
	if fill==5391: continue
	if fill==5393: continue
	if fill==5437: continue
	if fill==5446: continue
	totalLumi+=lumis[fill]

for line in fillFile:
	cols = line.strip('\n').split()
	fill = int(cols[0])
	if fill==5331: continue
	if fill==5339: continue
	if fill==5351: continue
	if fill==5355: continue
	if fill==5391: continue
	if fill==5393: continue
	if fill==5437: continue
	if fill==5446: continue
	filled = 0.
	for structs in cols[1:]:
		if structs[0]=='T':
			filled += float(structs[1:])
	avgFF += filled/3564.*lumis[fill]/totalLumi
	for valName in valDict[fill].keys():
			val = 0.5*(valDict[fill][valName]['p']+valDict[fill][valName]['m'])
			avgVal[valName] += lumis[fill]/totalLumi * val
	curr = 0.5*(valDict[fill]['current']['p']+valDict[fill]['current']['m'])
	#avgCurr += lumis[fill]/totalLumi * curr
	print fill, filled, filled/3564., lumis[fill], lumis[fill]/totalLumi, curr

hitrate = 7.2*10**6

def printStuff(valName):
	hitrate = 7.2*10**6
	print valName
	val = avgVal[valName]
	totval = 6.0*val
	chargeperhit = totval/hitrate*10**9 # in fC/hit
	print '{val:5.2f} {totval:5.2f} {hitrate:4.2e} {chargeperhit:.0f}'.format(**locals())
	print

#print 'Avg current',avgCurr, avgCurr*6.0
print 'Avg fill fraction',avgFF
print 'Total Luminosity [1/pb]',totalLumi

for valName in valTypes:
	printStuff(valName)
