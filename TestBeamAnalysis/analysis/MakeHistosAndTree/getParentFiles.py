import commands,sys


# Fill 5423
runs5423 = [283407,  283413, 283415, 283416] # skip 283414 since no data taken #283408, already done
# Fill 5405
runs5405 = [283040, 283041, 283042, 283043]
# Fill 5443
runs5443 = [283884, 283885]
# Fill 5338
runs5338 = [281638, 281639,  281641] # skip 281640,
# Fill 5386
runs5386 = [282663]
#runs = runs5423 + runs5405 + runs5443 + runs5338 + runs5386
runs = [283408, 281641, 282663]
for run in runs:
	print run
	runFileList = open('runFiles/'+str(run)+'.txt','r')
	for l,line in enumerate(runFileList):
		runFile = line.strip('\n').strip("'").strip(',').strip("'")
		parentFileList = open('parentFiles/parent_'+str(run)+'_'+str(l)+'.txt','w')
		parentFiles = commands.getoutput('das_client.py --limit=1000 --query="parent file=%s" | tail -n +4'%(runFile))
		print >> parentFileList, parentFiles
		parentFileList.close()
