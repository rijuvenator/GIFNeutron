#!/bin/bash

rm -f trigdata
touch trigdata
# the sub below used to say $2 from when the only commas were attached to the field
for i in /afs/cern.ch/user/a/adasgupt/GIF/meas/tmb/*
do
	meas=${i%%.tmb}
	meas=${meas##*/}
	if [ "`awk '/^'$meas'/ {print $2}' meta`" == "1" ]
	then
		data="$(awk '
		/Duration/ {
		sub(/,/,"",$0)
		if ($2=="0")
			print $5
		else
			print $2
		}
		/13CLCT|14CLCT|15CLCT|16CLCT|17CLCT|18CLCT|19CLCT|20CLCT|29CLCT|30CLCT|32TMB/ {
		print $NF
		}
		' $i)"
		echo $meas $data >> trigdata
	elif [ "`awk '/^'$meas'/ {print $2}' meta`" == "2" ]
	then
		data="$(awk '
		/Duration/ {
		sub(/,/,"",$0)
		if ($2=="0")
			print $5
		else
			print $2
		}
		/13CLCT|14CLCT|15CLCT|16CLCT|17CLCT|18CLCT|19CLCT|20CLCT|27CLCT|28CLCT|30TMB/ {
		print $NF
		}
		' $i)"
		echo $meas $data >> trigdata
	fi
done
awk '
	BEGIN {
			printf "%4s %12s %12s %12s %12s %12s %12s %12s %12s %12s %12s %12s\n", "MEAS", "Total", "CFEB0", "CFEB1", "CFEB2", "CFEB3", "CFEB4", "CFEB5", "CFEB6", "CLCT0", "CLCT1", "ALCT*CLCT"
		}
	{
		printf "%4i %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f\n",  $1, $2/$NF, $3/$NF, $4/$NF, $5/$NF, $6/$NF, $7/$NF, $8/$NF, $9/$NF, $10/$NF, $11/$NF, $12/$NF
	}
	' trigdata > tmp; mv tmp trigdata
