#!/bin/bash

# Takes in a single event (in this case E1, in Riju's workspace)
# Outputs a file containing the header and the first line
# and also the last two lines, if it's a captured neutron

# Use this to get rid of messages -- it deletes all lines %MSG, inclusive
# sed -i '/^\%MSG/,/^\%MSG/d' E1

# pickle.py takes in the output file from this and saves a dictionary
# examine.py opens the pickled dictionary and does some analysis
# energies is just the energies of the captured neutrons

# Before additional complexity!
# save 3 lines after Particles and 1 line before nCaptures
# two steps, out of order, otherwise we'll get lots of junk
# will restore the order using the line numbers later
#grep -n -A3 "Particle = " E1 > P
#grep -n -B1 "nCapture" E1 >> P

# save lines before and after Particle
grep -n -C3 "Particle = " E1 > P

# get rid of stars, headers, and grep separators
sed -i -e "/\*\*/d" -e "/-Step#/d" -e "/^--/d" P

# as it turns out, the only colons *are* the line numbers
# but since sed sucks and doesn't have capture groups, we need to be careful
# it seems that dash space is unique, so
# we can replace dash space with a space
# and then we can just replace all colons with spaces
sed -i -e "s/- / /" -e "s/:/ /" P

# now for the magic... sort numerically by first column
sort -n -k 1 P > P2
mv P2 P

# now get rid of the line numbers
awk '{$1=""; print}' P > P2
mv P2 P
# gtfo leading spaces, ALL commas, and "G4Track Information" nonsense
sed -i -e "s/^ //" -e "s/,//g" -e "s/\* G4Track Information: //" P
