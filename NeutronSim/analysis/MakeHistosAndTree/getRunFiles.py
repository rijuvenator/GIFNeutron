import commands

# Fill 5423
#runs = [283407, 283408, 283413, 283415, 283416] # skip 283414 since no data taken
# Fill 5405
#runs = [283040, 283041, 283042, 283043]
# Fill 5443
#runs = [283884, 283885]
# Fill 5338
runs = [281638, 281639, 281640, 281641]
# Fill 5386
#runs = [282663]
for run in runs:
	runFile = open('runFiles/'+str(run)+'.txt','w')
	out = commands.getoutput('das_client.py --limit=1000 --query="file run=%s dataset=/SingleMuon/Run2016H-PromptReco-v2/AOD" | tail -n +4'%(run))
	print >> runFile, out
