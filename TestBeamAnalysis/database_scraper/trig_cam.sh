#!/bin/bash

rm -f trigdata_cam
touch trigdata_cam
path='/afs/cern.ch/user/a/adasgupt/GIF/CMSSW_7_5_1/src/Gif/TestBeamAnalysis/database_scraper/tmb/'
for i in {2613..2678}
do
	meas="$i"
	data="$(awk '
	/14CLCT|15CLCT|16CLCT|17CLCT/ {
	print $NF
	}
	' ${path}${i}.tmb)"
	echo $meas $data >> trigdata_cam
done
awk '
	BEGIN {
			printf "%4s %7s %7s %7s %7s\n", "MEAS", "CFEB0", "CFEB1", "CFEB2", "CFEB3"
		}
	{
		printf "%4i %7s %7s %7s %7s\n",  $1, $2, $3, $4, $5
	}
	' trigdata_cam > tmp; mv tmp trigdata_cam
