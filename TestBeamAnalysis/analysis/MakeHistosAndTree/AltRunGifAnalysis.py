''' Submission script for running the GIF Analysis code
Historammer and N-Tupler
'''
import sys,os
import commands

if __name__ == '__main__' and 'submit' in sys.argv:
    user = commands.getoutput('echo $USER')
    plotsDir = '/afs/cern.ch/work/'+user[0]+'/'+user+'/GIF/data/'
    dryrun = 'dryrun' in sys.argv
    from Gif.TestBeamAnalysis.Measurements import meas
    measurements = [meas['2040'], meas['2064']]
    for TBM in measurements:
        chamber = 'ME'+TBM.cham+'1'
        fn = TBM.ROOTFile(prefix='/store/user/adasgupt/GIF/')
        # For Chris: # fn = TBM.fn
        ana_dataset = plotsDir+'ana_%s.root'%(TBM.meas)
        print TBM
        print "\033[1mINPUT:\033[m", fn
        print "\033[1mOUTPUT:\033[m", ana_dataset
        print ""

        gif_py = open('GifAnalysis.py').read()
        if not 'noHistos' in sys.argv:
            gif_py += '\ndoHistos(process)\n'
        if not 'noTree' in sys.argv:
            gif_py += '\ndoTree(process)\n'
        gif_py += '''
process.GIFHistos.chamberType = cms.untracked.string('%(chamber)s')
process.source.fileNames  = cms.untracked.vstring('%(fn)s')
process.TFileService.fileName = cms.string('%(ana_dataset)s')
''' % locals()

        open('submit_GifAnalysis.py','wt').write(gif_py)
        if dryrun:
            pass
        else: 
            cmd = 'cmsRun submit_GifAnalysis.py'
            print "\033[1mEXECUTING:\033[m", cmd
            os.system(cmd)

    if not dryrun:
        pass
        os.system('rm submit_GifAnalysis.py submit_GifAnalysis.pyc')
