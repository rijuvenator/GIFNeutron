'''
Script for running gifDisplays.py
'''

import os,sys
import argparse
import ROOT as R
import Gif.TestBeamAnalysis.DualMeasurements as Meas
import commands
parser = argparse.ArgumentParser(description='Draw event displays of GIF++ data')
parser.add_argument('--tag',dest='tag',help='Tagged directory name for output plots',default=None)
parser.add_argument('--eventList',dest='eventList',help='Event list to draw',default=None)
parser.add_argument('--meas',dest='meas',help='Measurement number to draw from',default=None)
parser.add_argument('--cham',dest='cham',help='Chamber to draw event from',default=None)
parser.add_argument('--dryrun',dest='dryrun',action='store_true',help='Flag for dry-running',default=False)
parser.add_argument('--extra',dest='extra',help='Extra info about event displays (e.g. noSegments, twoMuons)',default=None)
parser.add_argument('--outdir',dest='outdir',help='Output directory name',default=None)
args = parser.parse_args()
if (args.eventList is None) or (args.meas is None) or (args.cham is None):
    raise ValueError('Need to specify event list and measurement number and chamber type.\
                      Ex: --eventList list.txt --meas XXXX --cham 21')
'''
if args.tag:
	TAG = args.tag + ('/' if args.tag[-1]!='/' else '')
else:
	TAG = 'TEST/'
'''
LIST = args.eventList
MEAS = args.meas
CHAM = 'ME'+args.cham
DRYRUN = args.dryrun
EXTRA = args.extra
'''
if args.outdir:
	OUTDIR = args.outdir + ('/' if args.outdir[-1]!='/' else '')
else:
	user = commands.getoutput('echo $USER')
	OUTDIR = '/afs/cern.ch/work/'+user[0]+'/'+user+'/GIF/eventDisplay/'
'''
OUTDIR = ''
TAG = 'test'

# Set list input and output root/png file paths
listFile = LIST
if not os.path.isfile(listFile):
    raise ValueError('%s is not a valid file' % listFile)
displaysDir = OUTDIR+TAG
if not os.path.isdir(displaysDir):
    raise ValueError('%s is not a tagged directory' % displaysDir)

TBM = Meas.meas[MEAS]
fn = TBM.ROOTFile(prefix='/store/user/cschnaib/GIF/')
'''
# Get Measurement information
from Gif.TestBeamAnalysis.TestBeamMeasurements import *
TBM = eval(MEAS)
'''
chamber = CHAM
test = 'test40'
HV = TBM.HV
beam = TBM.beam
uAtt = TBM.uAtt
dAtt = TBM.dAtt
#meas = TBM.meas
#fn = TBM.fn
if EXTRA:
    displayRootFile =  'displays_%s_%s_%s_%s.root'%(chamber,test,MEAS,EXTRA)
else:
    displayRootFile =  'displays_%s_%s_%s.root'%(chamber,test,MEAS)
print chamber, test, HV, beam, uAtt, dAtt, MEAS
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

