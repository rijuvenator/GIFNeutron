#!/bin/bash

#python EventDisplay.py  --list elist --meas 3284 --cham 1
#python EventDisplay.py  --list elist --meas 3284 --cham 2
#python EventDisplay.py  --list elist --meas 3384 --cham 1
#python EventDisplay.py  --list elist --meas 3384 --cham 2
#python RecHitDisplay.py --list elist --meas 3284 --cham 1
#python RecHitDisplay.py --list elist --meas 3284 --cham 2
#python RecHitDisplay.py --list elist --meas 3384 --cham 1
#python RecHitDisplay.py --list elist --meas 3384 --cham 2

python EventDisplay.py  --meas 3241 --list cfeb_elist_1 --cham 1
python EventDisplay.py  --meas 3241 --list cfeb_elist_2 --cham 2
python RecHitDisplay.py --meas 3241 --list cfeb_elist_1 --cham 1
python RecHitDisplay.py --meas 3241 --list cfeb_elist_2 --cham 2
