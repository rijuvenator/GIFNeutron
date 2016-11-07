#!/bin/bash

measlist="$(awk '{print $1}' meta)"

cd tmb
for meas in $measlist
do
	datestr=$(awk '/^'$meas'.*STEP_40/ {sub(/emugif2.*STEP_40_000_/,"",$NF); sub(/_UTC\.raw/,"",$NF); print $NF}' ../meta)
	if [ -z "$datestr" ]
	then
		continue
	fi
	../autopass.sh PASSWORD "scp localuser@emugif2.cern.ch:/mnt/backup/raid/data/current/TMBCounters_GIF++_Test40_${datestr}_UTC.txt "${meas}.tmb
done
cd ..
