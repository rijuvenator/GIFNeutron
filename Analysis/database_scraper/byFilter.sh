#!/bin/bash

echo "=== ME11 ==="
for i in `awk '{print $7}' meta_tmb | sort -n | uniq -d | tail -n +2`
do
	echo "=== "$i" ==="
	awk '{if ($1 > 1924 && $2=="1" && $7=="'$i'") print}' meta_tmb
	#awk '{if ($2=="1" && $7=="'$i'") print}' meta_tmb
done
echo "=== ME21 ==="
for i in `awk '{print $7}' meta_tmb | sort -n | uniq -d | tail -n +2`
do
	echo "=== "$i" ==="
	awk '{if ($1 > 2061 && $2=="2" && $7=="'$i'") print}' meta_tmb
	#awk '{if ($2=="2" && $7=="'$i'") print}' meta_tmb
done
