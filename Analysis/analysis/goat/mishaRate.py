rates = open('logs/lumiSlopes.txt')

whens = ['early','total']
ecs = ['','-','+']
#rings = ['11','21','31','41','12','13','22','32','42']
rings = ['11','12','13','21','22','31','32','41','42']
data = {ec+ring:{when:{} for when in whens} for ring in rings for ec in ecs}
ffrac = 0.62
misha = {
		1:{
			'lumi':11.7*10**33,
			'rates':{
				'-11':388.42,
				'-12': 14.25,
				'-13':  4.21,
				'-21':222.65,
				'-22': 10.99,
				'-31':137.93,
				'-32': 14.52,
				'-41':155.75,
				'-42': 41.99,
				'+11':386.80,
				'+12': 14.11,
				'+13':  4.17,
				'+21':223.27,
				'+22': 10.89,
				'+31':142.76,
				'+32': 14.48,
				'+41':153.44,
				'+42': 38.81,
				},
			},
		2:{
			'lumi':17.7*10**30,
			'rates':{
				'-11':0.91,
				'-12':0.11,
				'-13':0.08,
				'-21':0.49,
				'-22':0.11,
				'-31':0.32,
				'-32':0.10,
				'-41':0.34,
				'-42':0.16,
				'+11':0.90,
				'+12':0.11,
				'+13':0.08,
				'+21':0.49,
				'+22':0.09,
				'+31':0.32,
				'+32':0.10,
				'+41':0.34,
				'+42':0.14,
				},
			},
		3:{
			#'lumi':6.88*10**33,
			'lumi':7.2*10**33,
			'rates':{
				'-11':265.96,
				'-12':9.66,
				'-13':2.89,
				'-21':155.48,
				'-22':7.67,
				'-31':95.45,
				'-32':10.09,
				'-41':107.18,
				'-42':29.05,
				'+11':267.12,
				'+12':9.59,
				'+13':2.88,
				'+21':156.59,
				'+22':7.56,
				'+31':99.27,
				'+32':10.05,
				'+41':106.09,
				'+42':26.89,
				},
			},
		4:{
			'lumi':10.9*10**33,
			'rates':{
				'-11':369.65,
				'-12':13.40,
				'-13':3.98,
				'-21':212.81,
				'-22':10.53,
				'-31':131.62,
				'-32':13.90,
				'-41':147.17,
				'-42':40.04,
				'+11':335.86,
				'+12':12.31,
				'+13':3.78,
				'+21':212.48,
				'+22':10.34,
				'+31':135.55,
				'+32':13.73,
				'+41':144.45,
				'+42':36.72,
				},
			},
		}

for line in rates:
	cols = line.strip('\n').split()
	when = cols[1]
	ring = cols[3]
	slope = float(cols[5])
	area = float(cols[6])
	bxtos = float(cols[7])
	data[ring][when]['slope'] = slope*bxtos/area
	print data[ring][when]['slope']*1.e34

for meas in misha.keys():
	print 'Lumi =',misha[meas]['lumi']
	print 'ring      rate     chris  misha ratio'
	for ring in rings:
		for ec in ecs:
			if meas==2:
				rate = 0.998*data[ec+ring]['early']['slope']+0.002*data[ec+ring]['total']['slope']
			else:
				rate = ffrac*data[ec+ring]['total']['slope'] + (1-ffrac)*data[ec+ring]['early']['slope']
			tot = rate*misha[meas]['lumi']
			string = '{ec:>2}{ring}  {rate:6.3e}   {tot:6.2f}'
			misharate = 0
			if ec!='':
				string+= ' {misharate:6.2f} {ratio:5.3f}'
				misharate = misha[meas]['rates'][ec+ring]
				ratio = misharate/tot
			print string.format(**locals())
	print
