import ROOT as R
import subprocess as bash
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.roottools as RT
import threading, logging, sys

def analyzeEvent(event):
	vetolist = [186, 214, 231]
	if event in vetolist: return

	fedm  = R.TFile.Open('$WS/public/GIF/3Mar/ana_neutronMC_{NUMBER}.root'.format(NUMBER=event))
	gt    = fedm.Get('GIFTree/GIFDigiTree')
	fpart = R.TFile.Open('forest/partTree_{NUMBER}.root'.format(NUMBER=event))
	pt    = fpart.Get('partTree')
	for entry in gt:
		E = Primitives.ETree(gt, DecList=['SIMHIT'])
		simhits = [Primitives.SimHit(E, i) for i in range(len(gt.sim_id))]

		if simhits != []:
			log = logging.getLogger('log'+str(event))
			log.setLevel(logging.INFO)
			fh = logging.FileHandler('log_'+str(event)+'.log')
			fh.setFormatter(logging.Formatter('%(message)s'))
			log.addHandler(fh)

			log.info('Event {EVENT}'.format(EVENT=event))
			dic = RT.getTreeDict(scanarg=r'"ID"',num=event)
			for sh in simhits:
				pt.GetEntry(dic[str(sh.trackID)])
				trackID = str(sh.trackID)
				proc = None
				capE = 0.
				tstring = '  '
				while True:
					pt.GetEntry(dic[trackID])
					tstring += str(pt.name) + ' '
					if pt.name == 'neutron':
						proc = str(list(pt.process)[-1])
						tstring += '(' + proc + ')'
						capE = float(list(pt.energy)[-2])
						log.info(tstring)
						break
					if pt.parent == '0':
						tstring += '<= 0'
						log.info(tstring)
						break
					tstring += '<= '
					trackID = str(pt.parent)

				pt.GetEntry(dic[str(sh.trackID)])
				log.info('  {cham:3d} {track:7d} {eloss:8.4f} {ds:7.4f} {pid:10d} {tof:15.4f} {proc:20s} {cape:10.4f}'.format(
					cham  = sh.cham,
					track = sh.trackID,
					eloss = sh.energyLoss*1e6,
					ds    = ((sh.exitPos['x']-sh.entryPos['x'])**2 + (sh.exitPos['y']-sh.entryPos['y'])**2 + (sh.exitPos['z']-sh.entryPos['z'])**2)**0.5,
					pid   = sh.particleID,
					tof   = sh.tof,
					proc  = proc,
					cape  = capE*1e15
				)
				)
			dlog.warning('Finished Event {EVENT}'.format(EVENT=event))


#for i in range(1, 301): analyzeEvent(i)

threads = []
dlog = logging.getLogger('debug')
dlog.addHandler(logging.StreamHandler(sys.stdout))
for i in range(201, 301):
	dlog.warning('Starting thread '+str(i))
	t = threading.Thread(target=analyzeEvent, args=(i,))
	threads.append(t)
	t.start()
