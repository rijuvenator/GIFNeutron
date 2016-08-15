#!/bin/bash

# get URLHEAD + measurement number; save the line with "raid", or write "TMB" or "Missing_file"
# also save another file with chambers
# run "finalize.awk" which cleans the lines to only include the file name or "TMB" or "Missing_file"
# adds emugif2.cern.ch: before /raid
URLHEAD='https://oraweb.cern.ch/pls/cms_emu_fast.pro/gif_log.form_view?w_run_num='
NUMS="`cat measlist`"
TOT=`wc -l < measlist`
rm -f table
rm -f meta
touch table
touch meta
touch tmp
ct=0
for meas in $NUMS; do
	wget -O ${meas}.log -o tmp ${URLHEAD}${meas}
	extra=$(sed -n "/raid/p" ${meas}.log)
	if [ "$extra" == "" ]; then
		extra=$(grep -A 1 "v_run_type" ${meas}.log | awk '/TMB/ {print "TMB"}')
		if [ "$extra" == "" ]; then
			if [ $((`grep -A 1 "v_run_type" ${meas}.log | wc -c` >= 37)) == "1" ]; then
				extra="Missing_file"
			fi
		elif [ "$extra" == "TMB" ]; then
			sed -n "/v_tmb_dump_comment/,/TEXTAREA/p" ${meas}.log | tail -n +2 | head -n -1 > tmb/${meas}.tmb
			awk 'BEGIN {s="0"; c="0"} /v_tmb_dump_time/ {if ($0 ~ /VALUE/) {s=$0; sub(/^.*VALUE="/,"",s); sub(/".*$/,"",s);}} /v_sps_cycle/ {if ($0 ~ /VALUE/) {c=$0; sub(/^.*VALUE="/,"",c); sub(/".*$/,"",c);}} END {printf "Duration: %-5s, Cycle x3: %-5s\n", s, c*3}' ${meas}.log >> tmb/${meas}.tmb
			sed -i -e "s///g" -e "/^\s*$/d" tmb/${meas}.tmb
		fi
	fi
	echo ${meas} ${extra} >> table

	./internal/write_meta.sh ${meas} meta

	rm ${meas}.log
	ct=$((ct += 1))
	printf "%s measurements of %s total completed.\r" "$ct" "$TOT"
done
echo -e "\nScraping complete, written to 'table'."
rm tmp
awk -f internal/finalize.awk table > final
sed -i "s/raid/emugif2.cern.ch:\/raid/" final
sed -i -e "s///" -e "s/\.$//" meta
echo -e "Cleanup complete, final output written to \e[31mfinal\e[m and \e[31mmeta\e[m."
echo "Removing 'table'..."
rm table

cd tmb
for j in $(for i in *; do if [ -z "`grep Counter $i`" ]; then echo $i; fi; done); do
	cat <(echo -e "--------------------------------------------------------\n---              Counters                             --\n--------------------------------------------------------") $j > tmp
	mv tmp $j
done
cd ..
echo -e "TMB dumps complete, output written to \e[31m./tmb/*.tmb\e[m."
