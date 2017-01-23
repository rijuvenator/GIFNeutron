import commands,sys


# Fill 5423
#runs = [283407,  283413, 283415, 283416] # skip 283414 since no data taken #283408, already done
# Fill 5405
#runs = [283040, 283041, 283042, 283043]
# Fill 5443
#runs = [283884, 283885]
# Fill 5338
#runs = [281638, 281639,  281641] # skip 281640,
# Fill 5386
runs = [282663]
for run in runs:
	runFile = open('runFiles/'+str(run)+'.txt','r')
	parentFile = open('parentFiles/parent_'+str(run)+'.txt','w')

	for line in runFile:
		l = line.strip('\n')
		parent = commands.getoutput('das_client.py --limit=1000 --query="parent file=%s" | tail -n +4'%(l))
		print >> parentFile, parent
	parentFile.close()


