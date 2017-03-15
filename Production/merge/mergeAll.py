import os as os

where = '/afs/cern.ch/user/c/cschnaib/eos/cms/store/user/cschnaib/Neutron/MinBiasNeutronHP/MinBiasNeutronHP_ThermalON/170228_114855/0003'
j=68
fileList = open('files3')
newFile = open('list_%s.txt'%j,'w')
for i,f in enumerate(fileList):
	fileName = f.strip('\n')
	newFile.write('file:'+where+'/'+fileName+'\n')
	if (i+1)%40==0:
		if i==0:
			continue
		else:
			newFile.close()
			j = j+1
			newFile = open('list_%s.txt'%j,'w')
j = j+1
newFile.close()
fileList.close()
