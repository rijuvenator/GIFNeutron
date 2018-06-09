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

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-f','--fill',dest='fill',default=5451,type=int, 
		help='Which fill to get currents for')
parser.add_argument('-min','--min',dest='minTime',default='26.10.16 08:50:00',
		help='Start time of fill')
parser.add_argument('-max','--max',dest='maxTime',default='26.10.16 23:00:00',
		help='End time of fill')
parser.add_argument('-o','--offset',dest='OFFSET',action='store_true',default=False)
parser.add_argument('-fmin','--fitmin',dest='FITMIN',default=0.0,
		        help='Change fit minimum in I vs. L')
parser.add_argument('-fmax','--fitmax',dest='FITMAX',default=1.5,
		        help='Change fit maximum in I vs. L')
parser.add_argument('-where','--where',dest='WHERE',default='doesnotexist',
		help='Where to save results')

args = parser.parse_args()
fill = args.fill
timestampMin = args.minTime
timestampMax = args.maxTime
fitmin = args.FITMIN
fitmax = args.FITMAX
offset = args.OFFSET
if args.WHERE=='doesnotexist':
	print 'Specify where to save in runAllBatch.py!'
	exit()
else:
	where = args.WHERE

print timestampMin
print timestampMax

R.gROOT.SetBatch()

orac = connectPVSSdb()

ME11info = ME11DBinfo.ME11DBInfo(orac.curs)
#ME11info.printDP_NAME2ID("CAEN/HVME11P", False)

Lumi = LumiDBinfo.LumiDBinfo(orac.curs)
Lumi.querryLumi(fill, timestampMin, timestampMax, plot=True, verbouse=False, mean=False, printout=False)
pdfname = where+'/fill'+str(fill)+'/'+'tmp.pdf'
newpdfname = where+'/fill'+str(fill)+'/'+'f'+str(fill)
if(len(timestampMax)>0 or len(timestampMin)>0):
	newpdfname+= '_['+timestampMin.replace(' ','_')+'-'+timestampMax.replace(' ','_')+']'
newpdfname+='.pdf'    
print 'creating pdf: '+pdfname

Lumi.canvas.Print(where+'/fill'+str(fill)+'/'+pdfname+'(','pdf');

dpids = []
rstr  = []

txtoutF = open(newpdfname.replace('pdf', 'txt'), 'a')
txtoutF.write('### '+str(datetime.now())+'\n')
for endcap in ['P','N']:
	for stationN in range(1,37):
		chamberName = 'CSC_ME_%s11_C%02d' % (endcap,stationN)
		for layer in range(1,7):
			DPID        = ME11info.getDPIDfromName(chamberName, layer, verbouse=True)
			dpids.append([DPID,chamberName+'_'+str(layer)])
			#cms_csc_dcs_4:CAEN/HVME11P/board08/channel001     754667    
			rstr.append(ME11info.queryHVvsLumi(DPID, fill, timestampMin, timestampMax, chamberName+'_'+str(layer), verbouse=True,offset=offset,fitmin=float(fitmin),fitmax=float(fitmax),where=where))
			ME11info.canvas.Print(pdfname,'pdf');
			print rstr[-1]+'\n\n\n\n\n'
			txtoutF.write(rstr[-1]+'\n')

txtoutF.close()

Lumi.canvas.Print(pdfname,'pdf'); # just to close file
#Lumi.canvas.Print(where+'/fill'+str(fill)+'/'+pdfname+')','pdf'); # just to close file
for astr in rstr:
	print astr
del orac

os.rename(pdfname, newpdfname) # root does not like complicated names :(

#select  diptime, value from CMS_LHC_BEAM_COND.lhc_beammode where DIPTIME>=to_timestamp('17.10.16 00:00:00','dd.mm.rr HH24:MI:SS') and DIPTIME<=to_timestamp('19.10.16 00:00:00','dd.mm.rr HH24:MI:SS') order by DIPTIME;
