#!/bin/bash
mkdir -p root

# Thermal OFF does not have 11 comparator digi fix yet
#python BGDigi_MC.py -hp -tof -geo 2015Geo
#python BGDigi_MC.py -xs -tof -geo 2015Geo

# Thermal ON has 11 comparator digi fix
python BGDigi_MC.py -hp -therm -tof -geo 2015Geo -in 11Fix -out BASE_PP
python BGDigi_MC.py -xs -therm -tof -geo 2015Geo -in 11Fix -out BASE_PP

# 2016 Geometries
#python BGDigi_MC.py -xs -tof -geo 2016Geo -out BASE_PP
#python BGDigi_MC.py -xs -tof -geo 2016CavernGeo -out BASE_PP
