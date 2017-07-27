#!/bin/bash
mkdir -p plots/ForDPNote
mkdir -p logs

# Data only: occ,lumi,phi,int
# with and without fit
python thefinalcountdown.py -r -n BASE -hn AREA_TIME -a -t -tdr -f -log -ec
python thefinalcountdown.py -r -n BASE_ROAD -hn AREA_TIME_ROAD -a -t -tdr -f -log -ec -road

# Data only: occ,lumi,phi,int
python thefinalcountdown.py -r -n BASE_PP -hn AREA_TIME_PP -a -t -pu -tdr -log -ec
python thefinalcountdown.py -r -n BASE_ROAD_PP -hn AREA_TIME_ROAD_PP -a -t -pu -tdr -log -ec -road

# Data + MC: occ,phi,int
# Thermal ON; HP, XS
#python thefinalcountdown_TEST.py -n BASE_PP -hn AREA_TIME_PP -a -t -pu -tdr -mc all -geo 2015Geo -ec
