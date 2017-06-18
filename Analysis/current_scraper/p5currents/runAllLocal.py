'''
Created on 17 Feb 2017

@author: kkuzn
Edited for batch on LXBatch with RunH2016 fills by cschnaib
'''

import os
from datetime import datetime
import ROOT as R

from connectPVSSdb import connectPVSSdb
import ME11.ME11DBinfo as ME11DBinfo
import Lumi.LumiDBinfo as LumiDBinfo
from fillDict import fills


R.gROOT.SetBatch()

orac = connectPVSSdb()

ME11info = ME11DBinfo.ME11DBInfo(orac.curs)
#ME11info.printDP_NAME2ID("CAEN/HVME11P", False)

Lumi = LumiDBinfo.LumiDBinfo(orac.curs)

for f,fill in enumerate(fills.keys()):

	timestampMin = fills[fill][0]
	timestampMax = fills[fill][1]
	print fill,timestampMin,timestampMax

	Lumi.querryLumi(fill, timestampMin, timestampMax, plot=True, verbouse=False, mean=False, printout=False)
	os.system('mkdir -p test/fill'+str(fill))
	pdfname = 'test/fill'+str(fill)+'/'+'tmp.pdf'
	newpdfname = 'test/fill'+str(fill)+'/'+'f'+str(fill)
	if(len(timestampMax)>0 or len(timestampMin)>0):
		newpdfname+= '_['+timestampMin.replace(' ','_')+'-'+timestampMax.replace(' ','_')+']'
	newpdfname+='.pdf'    
	print 'creating pdf: '+pdfname

	Lumi.canvas.Print('test/fill'+str(fill)+'/'+pdfname+'(','pdf');

	dpids = []
	rstr  = []

	txtoutF = open(newpdfname.replace('pdf', 'txt'), 'a')
	txtoutF.write('### '+str(datetime.now())+'\n')
	for ec in ['P','N']:
		for stationN in range(1,37):
		#stationN = 18
			chamberName = 'CSC_ME_%s11_C%02d' % (ec,stationN)
			for layer in range(1,7):
			#layer = 6
				DPID        = ME11info.getDPIDfromName(chamberName, layer, verbouse=True)
				dpids.append([DPID,chamberName+'_'+str(layer)])
				#cms_csc_dcs_4:CAEN/HVME11P/board08/channel001     754667    
				rstr.append(ME11info.queryHVvsLumi(DPID, fill, timestampMin, timestampMax, chamberName+'_'+str(layer), verbouse=True))
				ME11info.canvas.Print(pdfname,'pdf');
				print rstr[-1]+'\n\n\n\n\n'
				txtoutF.write(rstr[-1]+'\n')

	txtoutF.close()

	Lumi.canvas.Print('test/fill'+str(fill)+'/'+pdfname+')','pdf'); # just to close file
	for astr in rstr:
		print astr
	del orac

	os.rename(pdfname, newpdfname) # root does not like complicated names :(

	#select  diptime, value from CMS_LHC_BEAM_COND.lhc_beammode where DIPTIME>=to_timestamp('17.10.16 00:00:00','dd.mm.rr HH24:MI:SS') and DIPTIME<=to_timestamp('19.10.16 00:00:00','dd.mm.rr HH24:MI:SS') order by DIPTIME;
