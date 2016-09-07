#!/bin/bash

if [ -z "$1" ]
then
	echo "Usage: makeAllFiles.sh SUFFIX"
	exit
fi

SUFFIX=$1

python makeSpectrum.py           $SUFFIX > ../files/energies_${SUFFIX}
python makeDist.py               $SUFFIX > ../files/dists_${SUFFIX}
python makePhotonEnergies.py     $SUFFIX > ../files/photons_${SUFFIX}
python makePosition.py           $SUFFIX > ../files/pos_final_${SUFFIX}

# Still needs some work
#python makeThermalPathLengths.py $SUFFIX > ../files/paths_${SUFFIX}
