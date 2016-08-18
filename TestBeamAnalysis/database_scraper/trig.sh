#!/bin/bash

rm -f trigdata
touch trigdata
for i in tmb/*
do
	meas=${i%%.tmb}
	meas=${meas##*/}
	if [ "`awk '/^'$meas'/ {print $2}' meta`" == "1" ]
	then
		data="$(awk '
		/Duration/ {
		print $2
		}
		/13CLCT|14CLCT|15CLCT|16CLCT|17CLCT|18CLCT|19CLCT|20CLCT|29CLCT|30CLCT|32TMB|55L1A/ {
		print $NF
		}
		' $i)"
		echo $meas $data >> trigdata
	elif [ "`awk '/^'$meas'/ {print $2}' meta`" == "2" ]
	then
		data="$(awk '
		/Duration/ {
		print $2
		}
		/13CLCT|14CLCT|15CLCT|16CLCT|17CLCT|18CLCT|19CLCT|20CLCT|27CLCT|28CLCT|30TMB|53L1A/ {
		print $NF
		}
		' $i)"
		echo $meas $data >> trigdata
	fi
done
awk '
	BEGIN {
			printf "%4s %12s %12s %12s %12s %12s %12s %12s %12s %12s %12s %12s %5s\n", "MEAS", "Total", "CFEB0", "CFEB1", "CFEB2", "CFEB3", "CFEB4", "CFEB5", "CFEB6", "CLCT0", "CLCT1", "ALCT*CLCT", "L1A"
		}
	{
		printf "%4i %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %12.4f %5i\n",  $1, $2/$NF, $3/$NF, $4/$NF, $5/$NF, $6/$NF, $7/$NF, $8/$NF, $9/$NF, $10/$NF, $11/$NF, $12/$NF, $13
	}
	' trigdata > tmp; mv tmp trigdata
