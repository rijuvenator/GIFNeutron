'''
Created on 17 Feb 2017

@author: kkuzn
'''
from math import sqrt


import numpy

def getConfidenceIntervals(fitResult,xVals,nStride = 1,confLevel = 0.683):
    x = numpy.array(xVals , dtype = float)
    nPoints = len(xVals)
    err = numpy.array([0. for v in xVals] , dtype = float)
    fitResult.GetConfidenceIntervals(nPoints, nStride, nStride, x, err, confLevel, False)
    return err

##\brief checks if the given parameter is a number, returns True if it is a number
def isfloat(text):
    try:
        int(text)
        return True
    except (ValueError, TypeError): pass
    try:
        float(text)
        return True    
    except (ValueError, TypeError): pass
    return False


def appendToDictOfArr(theDict, theKey, value):
    if not(theKey in theDict):
        theDict[theKey] = []
    else:
        theDict[theKey].append(value)
    return theDict

#[[val1, err1], [val2, err2],...]
#TBD check array size
def weightedMean(theArray, valIndx=0, errIndx=1):
    mean   = 0
    wsum   = 0
    for meas in theArray:
        weight = 1./(meas[errIndx]*meas[errIndx])
        #weight = 1.0
        wsum+=weight
        mean+=(meas[valIndx]*weight)
    mean = mean/wsum
    chi2 = 0
    for meas in theArray:
        chi2+= (meas[valIndx]-mean)*(meas[valIndx]-mean)/(meas[errIndx]*meas[errIndx])
        #weight = 1.0
    chi2/=(len(theArray)-1)
    err  = sqrt(chi2/wsum)
    print mean, err
    return [mean, err]

##\brief arrayData [[datetime1, val1, val2,...],[]...
# checks in range [rangeIndxMin,rangeIndxMax] INCLUSIVE
# array is supposed to be sorted with time
def getMaxDeltaTimeBetweenPoints(arrayData, indx=0, rangeIndxMin=0,rangeIndxMax=0):
    maxINDX = len(arrayData)-1
    if rangeIndxMax==0 or rangeIndxMax>maxINDX: rangeIndxMax = maxINDX
    
    dT=0
    for ii in range (rangeIndxMin+1, rangeIndxMax):
        dt = (arrayData[ii][indx]-arrayData[ii-1][indx]).total_seconds()
        if dt>dT: dT=dt
    return dT
        
##\brief arrayData [[datetime1, val1, val2,...],[]...
# array is supposed to be sorted with time
# TBD - check error on weighted mean
def getMeanOverTimeFromDBarray(arrayData, indx=1):
    if(len(arrayData)==0): return -1, -1
    totalTHV = 0
    totalT   = 0
    seconds = []    
    #print arrayData
    for i in range (0,len(arrayData)-1):
        sec = (arrayData[i+1][0]-arrayData[i][0]).total_seconds()
        seconds.append(sec)
        totalTHV+=arrayData[i][indx]*sec
        totalT  +=sec
        #print arrayData[i], arrayData[i+1], arrayData[i+1][0]-arrayData[i][0], seconds
    if(totalT==0): return -1,-1
    mean = totalTHV/totalT
    totalSigma2T = 0
    for i in range (0,len(arrayData)-1):
        delta = mean - arrayData[i][indx]
        totalSigma2T+=delta*delta*seconds[i]
    err = sqrt(totalSigma2T/totalT)
    return mean, err



class GIFGraphics:
    #lcolours = [401, 866, 629, 418, 617, 802];
    lcolours = [401, 866, 629, 418, 882, 795];
##\brief coloured print out
class kout:
    #HEADER = '\033[95m'
    #OKBLUE = '\033[94m'
    #OKGREEN = '\033[92m'
    #FAIL = '\033[91m'
    #ENDC = '\033[0m'
    #BOLD = '\033[1m'
    #UNDERLINE = '\033[4m'
    @staticmethod
    def printFID(fname, info=""):
        print '\t\033[4m'+'\033[95m'+"%40s"%fname+'\033[0m:'+"%70s"%info
    @staticmethod
    def printQER(querry):
        print "\t\033[32m"+querry+'\033[0m\n'
    @staticmethod
    def printERR(errorSource, errorMessage):
        print '\n\t\033[4m\033[91m'+"%40s"%errorSource+'\033[0m:'+"\033[91m\t"+"%70s"%errorMessage+'\033[0m\n'
    @staticmethod
    def printWAR(warningSource, errorMessage):
        print '\t\033[38;5;198m\033[4m'+"%40s"%warningSource+'\033[0m:'+"\033[38;5;198m\t"+"%70s"%errorMessage+'\033[0m\n'
    @staticmethod
    def printOUT(string):
        print '\t\033[34m'+string+'\033[0m'
        