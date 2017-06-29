#!/bin/bash
mkdir -p plots/ForDPNote

# Data only: occ,lumi,phi,int
# with and without fit
python thefinalcountdown.py -n BASE -hn AREA_TIME -a -t -tdr -f -log -ec -dir ForDPNote

# Data only: occ,lumi,phi,int
python thefinalcountdown.py -n BASE_PP -hn AREA_TIME_PP -a -t -pu -tdr -log -ec -dir ForDPNote

# Data + MC: occ,phi,int
# Thermal ON; HP, XS
python thefinalcountdown_TEST.py -n BASE_PP -hn AREA_TIME_PP -a -t -pu -tdr -mc all -geo 2015Geo -ec
