'''
Script for running gifDisplays.py
'''

import os,sys
import argparse
parser = argparse.ArgumentParser(description='Draw event displays of GIF++ data')
parser.add_argument('--tag',dest='tag',help='Tagged directory name for output plots',default=None)
parser.add_argument('--eventList',dest='eventList',help='Event list to draw',default=None)
parser.add_argument('--meas',dest='meas',help='Measurement number to draw from',default=None)
parser.add_argument('--dryrun',dest='dryrun',action='store_true',help='Flag for dry-running',default=False)
parser.add_argument('--extra',dest='extra',help='Extra info about event displays (e.g. noSegments, twoMuons)',default=None)
args = parser.parse_args()
if (args.eventList is None) or (args.meas is None):
    raise ValueError('Need to specify event list and measurement number.\
                      Ex: --eventList list.txt --meas mXXXX')
LIST = args.eventList
MEAS = args.meas
if args.tag: TAG = args.tag
else: TAG = 'TEST'
DRYRUN = args.dryrun
EXTRA = args.extra

# Set list input and output root/png file paths
listDir = '/afs/cern.ch/user/c/cschnaib/Work/CMSSW_7_5_1/src/Gif/TestBeamAnalysis/test/GIFDisplay/'
listFile = listDir+LIST
displaysDir = '/afs/cern.ch/work/c/cschnaib/GIF/eventDisplay/'+TAG+'/'
if not os.path.isdir(displaysDir):
    raise ValueError('%s is not a tagged directory' % displaysDir)

# Get Measurement information
from Gif.TestBeamAnalysis.TestBeamMeasurements import *
TBM = eval(MEAS)
chamber = TBM.CSC
test = TBM.test
HV = TBM.HV
beam = TBM.beam
uAtt = TBM.uAtt
dAtt = TBM.dAtt
meas = TBM.meas
fn = TBM.fn
if EXTRA:
    displayRootFile =  'displays_%s_%s_%s_%s.root'%(chamber,test,meas,EXTRA)
else:
    displayRootFile =  'displays_%s_%s_%s.root'%(chamber,test,meas)
print chamber, test, HV, beam, uAtt, dAtt, meas
print fn
print displaysDir+displayRootFile
print listFile

# Set and submit executable
gifDisplays_py = open('gifDisplays.py').read()
gifDisplays_py += '''
process.source.fileNames  = cms.untracked.vstring('%(fn)s')
process.GifDisplay.rootFileName = cms.untracked.string('%(displaysDir)s'+'%(displayRootFile)s')
process.GifDisplay.chamberType = cms.untracked.string('%(chamber)s')
process.GifDisplay.eventDisplayDir = cms.untracked.string('%(displaysDir)s')
process.GifDisplay.eventListFile = cms.untracked.string('%(listFile)s')
''' % locals()

open('submit_gif_displays.py','wt').write(gifDisplays_py)
if DRYRUN:
    print 'Dry-running: exit.'
    #sys.exit()
else: 
    cmd = 'cmsRun submit_gif_displays.py'
    print cmd
    os.system(cmd)
os.system('rm submit_gif_displays.py')# submit_gif_displays.pyc')

