#!/bin/bash

FILE="meta"
let CUTOFF=2719

for m in $(awk '/\*/ {print $1}' $FILE)
#for m in 2720 2729 2730 2731 2732
do
	if (($m > $CUTOFF))
	then
		BACKUP=""
	else
		BACKUP="/mnt/backup"
	fi

	fb=$(awk '/^'$m'/ {sub(/emugif2.*current\//,"",$NF); print $NF}' $FILE)
	ct=$(./autopass.sh \\\$localuser\\\$ ssh localuser@emugif2.cern.ch "ls $BACKUP/raid/data/current/$fb | wc -l" | sed -e "/spawn\|Connection\|Password/d")
	echo $m $ct
done
