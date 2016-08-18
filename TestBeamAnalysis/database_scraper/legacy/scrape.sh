#!/bin/bash

# gets the ls of the current list of raw files and adds emugif2.cern.ch: to the beginning
#echo "SSH'ing to emugif2; type in password for localuser@emugif2"
echo "SSH'ing to emugif2 to get file list"
./autopass.sh PASSWORD ssh -t localuser@emugif2 "ls -1 /raid/data/current/*.raw" > all_files
sed -i "s/^/emugif2.cern.ch:/" all_files
dos2unix all_files
echo -e "emugif2 file list obtained, written to \e[31mall_files\e[m."

# gets list of measurement numbers and strips unnecessary information
# stops at 1649, which is the last file in /raid/data/current
wget -O mtmp -o /dev/null https://oraweb.cern.ch/pls/cms_emu_fast.pro/gif_log.list_measurements
sed -n "/gif.*num/s/.*num=//p" mtmp | sed -n "s/>//p" | sed "/1648/Q" > measlist
rm mtmp
echo -e "Measurement list obtained, written to \e[31mmeaslist\e[m."

# runs get_logs.sh, which wgets the source code for every measurement
# and gets the line matching "raid", which contains the raw file name
# it all gets put into table, which is then cleaned up by finalize.awk
./internal/get_logs.sh

# make orphan_meas: measurements without a raw file or not marked as TMB or Missing_file (lines in final with $2=="")
echo -e "Finding orphan measurements, written to \e[31morphan_meas\e[m."
awk '{if ($2=="") print $1}' final > orphan_meas

# make orphan_raw: raw files without a measurement (files unique to all_files)
# note: since some files in "final" have stars, referring to multiple files,
# they will appear in orphan_raw, because no measurement matches them exactly
echo -e "Finding orphan raw files, written to \e[31morphan_raw\e[m."
awk '{if ($2!="" && $2!="TMB" && $2!="Missing_file") { $1=""; print $0; } }' final > tmp
sed -i "s/^ //" tmp
comm -13 <(sort tmp) <(sort all_files) > orphan_raw

# make missing: measurements with a non-existent raw file (files unique to tmp)
# note: since some files in "final" have stars, referring to multiple files,
# they are excluded from being considered "missing"
echo -e "Finding missing raw files, written to \e[31mmissing\e[m; check that they exist on /mnt/backup/."
rm -f missing
touch missing
for f in "`comm -23 <(sort tmp) <(sort all_files) | sed "/\*/d"`"; do grep "$f" final >> missing; done
# Test_19_000_160422_225142 is listed twice, so since it doesn't appear twice in the ls, it's "missing".

rm tmp

# make dqm_urls: urls to DQM plots
# creates a file with raw files and chamber (1 or 2), separated by a space
# then processes it with url.awk
# only uses raw files with STEP or Test_* in the name, where * is 11, 16, 19, or 21
echo -e "Making DQM URLs, written to \e[31mdqm_urls\e[m."
awk '/STEP|Test_11|Test_16|Test_19|Test_21/ {if ($2!="" && $2!="TMB" && $2!="Missing_file" && $2 !~ /\*/) print $0}' final > conv
join -o 1.2 2.2 <(sort conv) <(sort meta) > url_raw
awk -f internal/url.awk url_raw > dqm_urls
rm conv url_raw

# make bad_urls: urls that don't exist
echo -e "Finding bad urls, written to \e[31mbad_urls\e[m."
rm -f bad_urls
touch bad_urls
while read url; do if curl --output /dev/null --silent --head --fail $url; then true; else echo $url >> bad_urls; fi; done < dqm_urls

# make daq_runs: runs with raw files that have FastFilterScanSettings 0-4
echo -e "Finding DAQ runs, written to \e[31mdaq_runs\e[m."
join meta final | awk '/raid/ {if ($(NF-1)!="N") print $1}' > daq_runs

echo -e "\e[32mDone!\e[m"
