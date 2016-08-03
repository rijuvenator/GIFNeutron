import os,sys
import random as rd

def makeRandEvtList(inputfile,outputfile,numList):
    '''
    - Function to make a list of randomly selected events from an existing list
    - Inputs: inputfile = name of input text file with event list
              outputfile = name of output text file with random event list
              numList = number of events to randomly select from inputfile
    - Output: List of sorted randomly selected events
    '''

    if not os.path.exists(args.inputfile):
        print 'Input file does not exist'
        sys.exit()
    else:
        evtListFile = open(args.inputfile,'r')
        evtList = evtListFile.readlines()
        lenList = len(evtList)
        randList = open(args.outputfile,'w')

    if numList > int(lenList):
        print 'Number of events to draw cannot be larger than the length of the event list'
        print numList, int(lenList)
        sys.exit()

    alreadyPicked = []
    randEvent = -1
    for n in range(int(args.numList)):
        randLine = rd.randrange(1,lenList+1)
        if randLine not in alreadyPicked:
            alreadyPicked.append(randEvent)
            randEvent = evtList[randLine]
            print randEvent
            #randList.write(str(randEvent)+'\n')
            randList.write(str(randEvent))
        else:
            continue
    randList.close()

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(usage="drawRandomEvents.py [options] -i INPUTFILE -o OUTPUTFile -n NUMEVENTSTOSELECT",description="Generate small event list with events randomly selected from larger event list",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i","--ifile", dest="inputfile",default="evtList.txt", help='input event list')
    parser.add_argument("-o","--ofile", dest="outputfile",default="evtList_10.txt", help='output event list')
    parser.add_argument("-n","--numList", dest="numList",default="10", help='Number of events to draw displays')
    args = parser.parse_args()

    makeRandEvtList(args.inputfile, args.outputfile, int(args.numList))
