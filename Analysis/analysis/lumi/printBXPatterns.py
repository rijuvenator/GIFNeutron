#!/usr/bin/python

# Original Script: https://github.com/CMS-LUMI-POG/Normtags/blob/master/compareBXPatterns.py

import sys
import subprocess as bash

# This script compares the pattern of filled bunches in HF and PLT to see if either has shifted
# from the expected pattern. By default, it will run over all 2016 fills, so you probably want
# to direct the output to a file. You can also run over a subset of fills by specifying them
# on the command line.

# Luminometers to compare. The first one in this list will determine the reference pattern
# and the others will be compared to it.
#luminometerOrder = ['hfoc', 'pltzero']
luminometerOrder = ['hfoc']

# Any BX with a luminosity greater than bxThresh times the luminosity of the peak BX will
# be considered filled. 0.1 is good for most purposes but for early fills you may need
# to use a higher threshold for HF. For HI fills 0.2 seems to work a little better.
bxThresh = 0.1

# Default fill list: all 2016 fills (starting with 4925, the start of stable operations for PLT)
fills = ['5331','5338','5339','5340','5345','5351','5352','5355','5391','5393','5394','5395','5401','5405','5406','5416','5418','5421','5423','5424','5427','5433','5437','5439','5441','5442','5443','5446','5448','5450','5451']

# If an individual fill (or fills) is/are specified on the command line, use those instead
if (len(sys.argv) > 1):
    fills = sys.argv[1:]

for fill in fills:
    filledBXTemplate = []
    firstAvgLumi = 0

    for luminometer in luminometerOrder:
        #print "Getting bunch data for "+luminometer+" fill "+fill+" ...please wait..."
        dataFile = "bxdata_"+fill+"_"+luminometer+".csv"
        
        #print 'brilcalc lumi --xing -b "STABLE BEAMS" -u hz/ub -f '+fill+' --type '+luminometer+' --xingTr '+str(bxThresh)+' -o '+dataFile
        # call the command, but catch the stupid newline that prints out of brilcalc
        x = bash.check_output('brilcalc lumi --xing -b "STABLE BEAMS" -u hz/ub -f '+fill+' --type '+luminometer+' --xingTr '+str(bxThresh)+' -o '+dataFile,
            shell=True)

        #print "Checking bunch data for "+luminometer+"..."
        
        infile = open(dataFile, 'r')
        for line in infile:
            fields = line.split(',')
            if (fields[0][0] == '#'):
                continue # skip headers
            
            # Next, split up the individual BX data. Use the slice
            # to drop the initial and final brackets.
            filledBX = []
            if (fields[9][0:2] == '[]'):
                bxFields = []
            else:
                bxFields = fields[9][1:-1].split(' ')
            avgLumi = 0
            # Find the filled BXes and the luminosity in them.
            for i in range(0, len(bxFields), 3):
                filledBX.append(int(bxFields[i]))
                avgLumi += float(bxFields[i+1])
            
            if len(filledBX) > 0:
                avgLumi /= len(filledBX)
                
            # If this is the first LS we've examined, store this as the reference BX pattern.
                
            if (len(filledBXTemplate) == 0):
                filledBXTemplate = list(filledBX)
                shiftedTemplate = list(filledBXTemplate)
                firstAvgLumi = avgLumi
                #print "Found "+str(len(filledBX))+" filled bunch crossings."
                # Print out the full bunch pattern. This is really only useful when debugging fills
                # with small numbers of filled bunches, not so useful for 2200 bunch fills. Hence
                # the reason it's off by default.
                #if 0:
                if 1:
                    #print "Bunch pattern:",
                    print fill,
                    lastBunch = -9 # number of last filled bunches
                    trainCount = 0 # number of bunches in current train
                    for i in filledBX:
                        if (i != lastBunch+1):
                            # Isolated/leading bunch
                            # Print out end of previous train, if we were in one
                            if (trainCount > 0):
                                print "T"+str(trainCount),
                            print str(i),
                            trainCount = 1
                        else:
                            # Train bunch
                            trainCount += 1
                        lastBunch = i
                    # Don't forget to finish the train we were working on at the end
                    if (trainCount > 0):
                        print "T"+str(trainCount),
                    print

#            # Otherwise, see if this matches the reference BX pattern.
#            else:
#                if (filledBXTemplate != filledBX):
#                    # Maybe the fill dropped a little before the STABLE BEAMS
#                    # flag cleared, or we're in a miniscan. Check the average lumi
#                    # to see if it decreased a lot. If so, a mismatch is pretty
#                    # harmless.
#                    if (avgLumi < firstAvgLumi*0.1):
#                        print "Probably harmless mismatch in "+luminometer+ " (much lower lumi) in run:fill "+fields[0]+" ls "+fields[1]
#                    else:
#                        # Try to narrow down the cause a bit. Is it that the number of bunches has changed,
#                        # or is there a shift present?
#                        if (len(filledBXTemplate) != len(filledBX)):
#                            print "Mismatch in numBX "+luminometer+" run:fill "+fields[0]+" ls "+fields[1]+": expected "+str(len(filledBXTemplate))+" got "+str(len(filledBX))
#                        else:
#                            # The number of bunches found is the same, but the individual bunches don't match up.
#                            # Probably there is a shift. Let's see if we can find it.
#                            # If this matches the shift from the last time, then we don't need to do any work!
#                            # Only check the shift if it doesn't.
#                            if (shiftedTemplate != filledBX):
#                                foundShift = 0
#                                shiftedTemplate = list(filledBXTemplate)
#                                for i in range(1, 3564):
#                                    for j in range(0, len(shiftedTemplate)):
#                                        shiftedTemplate[j] += 1
#                                        if (shiftedTemplate[j] > 3564):
#                                            shiftedTemplate[j] -= 3564
#
#                                    shiftedTemplate.sort()
#                                    if (filledBX == shiftedTemplate):
#                                        foundShift = i
#                                        break
#
#                            # Now print out the shift if we found it.
#                            if (foundShift == 0):
#                                # We can't recover the proper bunch pattern just by shifting it. Something more complex is going on...
#                                print "Non-simple shift in "+luminometer+ " run:fill "+fields[0]+" ls "+fields[1]
#                            else:
#                                print luminometer+ " appears to be shifted by "+str(foundShift)+" in run:fill "+fields[0]+" ls "+fields[1]

        # Finished processing this file
        infile.close()
        # Clean up the raw data file.
        bash.call('rm '+dataFile, shell=True)
