''' Submission script for running the GIF Analysis code
Historammer and N-Tupler
'''
import sys,os
import commands

if __name__ == '__main__' and 'submit' in sys.argv:
    user = commands.getoutput('echo $USER')
    plotsDir = '/afs/cern.ch/work/'+user[0]+'/'+user+'/GIF/data/'
    dryrun = 'dryrun' in sys.argv
    import Gif.TestBeamAnalysis.Measurements as Meas
    #measurements = [Meas.meas[m] for m in ['2312','2095','2262','2064','2079','2224','2333']]
    #measList = [3084,3086,3088,3090,3092,3094,3095,3097,3099,3101,3103,3105,3107,3109,3111,3113,3115,3117,3119,3121,3123,3125,3127,3129,3131,3133]
    measList = [3092, 3103, 3113, 3123, 2758, 3094, 3080, 2970, 2843, 2756]
    measurements = [Meas.meas[str(m)] for m in measList]
    for TBM in measurements:
        chamber = TBM.cham
        test = TBM.runtype
        HV = TBM.HV
        beam = 'bOn' if TBM.beam else 'bOff'
        uAtt = 'uOff' if TBM.uAtt=='0' else 'u'+TBM.uAtt
        dAtt = 'dOff' if TBM.dAtt=='0' else 'd'+TBM.dAtt
        measNum = 'm'+TBM.meas
        fn = TBM.ROOTFile(prefix='/store/user/adasgupt/GIF/')
        #fn = TBM.fn
        # For Chris: # fn = TBM.fn
        ana_dataset = 'ana_%s.root'%(TBM.meas)
        #ana_dataset = 'ana_%(chamber)s_%(test)s_%(HV)s_%(beam)s_%(uAtt)s_%(dAtt)s_%(measNum)s.root'%locals()
        outPath = plotsDir+ana_dataset
        print TBM
        print "\033[1mINPUT:\033[m", fn
        print "\033[1mOUTPUT:\033[m", outPath
        print ""

        gif_py = open('GifAnalysis.py').read()
        if not 'noHistos' in sys.argv:
            gif_py += '\ndoHistos(process)\n'
        if not 'noTree' in sys.argv:
            gif_py += '\ndoTree(process)\n'
        gif_py += '''
process.GIFHistos.chamberType = cms.untracked.string('%(chamber)s')
process.source.fileNames  = cms.untracked.vstring('%(fn)s')
process.TFileService.fileName = cms.string('%(outPath)s')
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
