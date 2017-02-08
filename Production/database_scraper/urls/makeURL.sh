#!/bin/bash

# make dqm_urls: urls to DQM plots
# creates a file with raw files and chamber (1 or 2), separated by a space
# then processes it with url.awk
# only uses raw files with STEP or Test_* in the name, where * is 11, 16, 19, or 21
echo -e "Making DQM URLs, written to \e[31mdqm_urls\e[m."
awk '/STEP|Test_11|Test_16|Test_19|Test_21/ {if ($0!="TMB" && $0 !~ /\*/) print $NF, $2}' ../meta > url_raw
awk -f url.awk url_raw > dqm_urls
rm url_raw

# make bad_urls: urls that don't exist
echo -e "Finding bad urls, written to \e[31mbad_urls\e[m."
rm -f bad_urls
touch bad_urls
while read url; do if curl --output /dev/null --silent --head --fail $url; then true; else echo $url >> bad_urls; fi; done < dqm_urls
