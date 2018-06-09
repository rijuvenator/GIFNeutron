'''
Created on 17 Feb 2017

@author: kkuzn
Edited for batch on LXBatch with RunH2016 fills by cschnaib
'''

import os
from datetime import datetime
import ROOT as R

from connectPVSSdb import connectPVSSdb
import ME11.MEXXDBinfo as MEXXDBinfo
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
OFFSET = args.OFFSET
fitmin = float(args.FITMIN)
fitmax = float(args.FITMAX)
where = args.WHERE

print timestampMin
print timestampMax
print 'offset',OFFSET
print fitmin,fitmax

R.gROOT.SetBatch()

orac = connectPVSSdb()

MEXXinfo = MEXXDBinfo.MEXXDBinfo(orac.curs)

info = {
		'21':{
			'chambers':18,
			'segments':3,
			},
		}

Lumi = LumiDBinfo.LumiDBinfo(orac.curs)
Lumi.querryLumi(fill, timestampMin, timestampMax, plot=True, verbouse=False, mean=False, printout=False)
pdfname = where+'/fill'+str(fill)+'/'+'tmp.pdf'
newpdfname = where+'/fill'+str(fill)+'/'+'f'+str(fill)
if(len(timestampMax)>0 or len(timestampMin)>0):
	newpdfname+= '_'+timestampMin.replace(' ','_')#+'-'+timestampMax.replace(' ','_')
	newpdfname=newpdfname[:len(newpdfname)-3]+'-'+timestampMax.replace(' ','_')
	newpdfname=newpdfname[:len(newpdfname)-3].replace(':','h')
newpdfname+='.pdf'
print 'creating pdf: '+newpdfname

Lumi.canvas.Print(where+'/fill'+str(fill)+'/'+pdfname+'(','pdf');

dpids = []
rstr  = []

txtoutF = open(newpdfname.replace('pdf', 'txt'), 'a')
txtoutF.write('### '+str(datetime.now())+'\n')
for ring in info.keys():
	for endcap in ['P','M']:
		for c,chamber in enumerate(range(1,info[ring]['chambers']+1)):
			for segment in range(1,info[ring]['segments']+1):
				chamberName = 'CSC_ME_{endcap}{ring}_C{chamber:02}' .format(**locals())#endcap,ring,chamber)
				for layer in range(1,7):
					rstr = MEXXinfo.queryIvsLumi(chamberName, segment, layer, fill, timestampMin, timestampMax, 
                                      plotTitle='fill'+str(fill)+'/'+chamberName+"_"+str(segment)+"_"+str(layer), verbouse=True,offset=OFFSET,
									  fitmin=fitmin,fitmax=fitmax,where=where)
					MEXXinfo.canvas.Print(pdfname,'pdf');
					print rstr
					#print rstr[-1]+'\n\n\n\n\n'
					#txtoutF.write(rstr[-1]+'\n')
					txtoutF.write(rstr+'\n')

txtoutF.close()

Lumi.canvas.Print(where+'/fill'+str(fill)+'/'+pdfname+')','pdf'); # just to close file
#for astr in rstr:
#	print astr
del orac

os.rename(pdfname, newpdfname) # root does not like complicated names :(

