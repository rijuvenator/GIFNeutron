''' Submission script for running the GIF Analysis code
Historammer and N-Tupler
'''
import sys,os
import commands

if __name__ == '__main__' and 'submit' in sys.argv:
    user = commands.getoutput('echo $USER')
    plotsDir = '/afs/cern.ch/work/'+user[0]+'/'+user+'/GIF/data/'
    dryrun = 'dryrun' in sys.argv
    from Gif.TestBeamAnalysis.TestBeamMeasurements import measurements
    #measurements = [m2040,m2064]
    for TBM in measurements:
        chamber = TBM.CSC
        test = TBM.test
        HV = TBM.HV
        beam = TBM.beam
        uAtt = TBM.uAtt
        dAtt = TBM.dAtt
        meas = TBM.meas
        fn = TBM.fn
        ana_dataset = plotsDir+'ana_%s_%s_%s_%s_%s_%s_%s_TEST.root'%(chamber,test,HV,beam,uAtt,dAtt,meas)
        print chamber, test, HV, beam, uAtt, dAtt, meas
        print fn
        print ana_dataset

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
            print cmd
            os.system(cmd)

    if not dryrun:
        pass
        os.system('rm submit_GifAnalysis.py submit_GifAnalysis.pyc')
