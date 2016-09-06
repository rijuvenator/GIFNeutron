#!/bin/bash

python makePhotonEnergies.py     > ../files/photon
#python makeThermalPathLengths.py > ../files/paths
python makePosition.py           > ../files/pos_final
