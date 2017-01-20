''' Submission script for running the GIF Analysis code
Historammer and N-Tupler
'''
import sys,os
import commands


if __name__ == '__main__' and 'submit' in sys.argv:
	user = commands.getoutput('echo $USER')
	#plotsDir = '/afs/cern.ch/work/'+user[0]+'/'+user+'/public/GIF/TestBeam5/'
	#plotsDir = '/afs/cern.ch/work/'+user[0]+'/'+user+'/public/GIF/test/'
	cmssw_base = commands.getoutput('echo $CMSSW_BASE')
	plotsDir = cmssw_base+'/src/Gif/TestBeamAnalysis/analysis/MakeHistosAndTree/'
	outPath = plotsDir+'test.root'
	dryrun = 'dryrun' in sys.argv

	gif_py = open('GifAnalysis.py').read()
	# commented out since we only want trees (histos are chamber dependent)
	#if not 'noHistos' in sys.argv:
	#    gif_py += '\ndoHistos(process)\n'
	#if not 'noTree' in sys.argv:
	gif_py += '\ndoTree(process)\n'
	# commented out since we only want trees (histos are chamber dependent)
	#process.GIFHistos.chamberType = cms.untracked.string('%(chamber)s')
	fn = '/store/data/Run2016H/SingleMuon/AOD/PromptReco-v1/000/281/130/00000/3A7ACFF8-7980-E611-A56E-02163E01464B.root'
	fn2 = ''' "/store/data/Run2016H/SingleMuon/RAW/v1/000/281/130/00000/00EF1E2D-E07E-E611-857D-02163E0141A3.root", 
	"/store/data/Run2016H/SingleMuon/RAW/v1/000/281/130/00000/2231EC57-8E7E-E611-BF08-02163E0144AC.root", 
	"/store/data/Run2016H/SingleMuon/RAW/v1/000/281/130/00000/3C41E86E-8D7E-E611-8BD1-02163E0141E6.root",
	"/store/data/Run2016H/SingleMuon/RAW/v1/000/281/130/00000/8CAC4D57-8E7E-E611-9FAA-02163E014101.root",
	"/store/data/Run2016H/SingleMuon/RAW/v1/000/281/130/00000/CC3D86C1-8D7E-E611-98A1-02163E0142C1.root",
	"/store/data/Run2016H/SingleMuon/RAW/v1/000/281/130/00000/E00E6CBF-8D7E-E611-B609-FA163ECDF20C.root",
	"/store/data/Run2016H/SingleMuon/RAW/v1/000/281/130/00000/ECADCF37-8E7E-E611-A093-02163E0142FC.root",
	"/store/data/Run2016H/SingleMuon/RAW/v1/000/281/130/00000/F0996E63-9C7E-E611-9737-02163E014396.root" '''
	gif_py += '''
process.GlobalTag.globaltag = '80X_dataRun2_Prompt_v14'
process.source.fileNames  = cms.untracked.vstring('%(fn)s')
process.source.secondaryFileNames  = cms.untracked.vstring(%(fn2)s)
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
		#os.system('rm submit_GifAnalysis.py submit_GifAnalysis.pyc')
