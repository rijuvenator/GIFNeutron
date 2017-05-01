import ROOT as R
import subprocess as bash
import Gif.Analysis.Primitives as Primitives
import Gif.Analysis.roottools as RT
import threading, logging, sys

def norm(x, y, z):
	return (x**2 + y**2 + z**2)**0.5

def analyzeEvent(event):
	vetolist = [35, 159]
	if event in vetolist: return

	fedm  = R.TFile.Open('$WS/public/Neutron/simtrees/ana_simTree_{NUMBER}.root'.format(NUMBER=event))
	gt    = fedm.Get('GIFTree/GIFDigiTree')
	fpart = R.TFile.Open('forest/partTree_{NUMBER}.root'.format(NUMBER=event))
	pt    = fpart.Get('partTree')

	dic = RT.getTreeDict(scanarg=r'"ID"',num=event)

	for entry in gt:
		E = Primitives.ETree(gt, DecList=['SIMHIT'])
		simhits = [Primitives.SimHit(E, i) for i in range(len(gt.sim_id))]

		if simhits != []:
			#dlog.warning('Starting Event '+str(event))

			log = logging.getLogger('log'+str(event))
			log.setLevel(logging.INFO)
			fh = logging.FileHandler('log_'+str(event)+'.log')
			fh.setFormatter(logging.Formatter('%(message)s'))
			log.addHandler(fh)

			log.info('Event {EVENT}'.format(EVENT=event))
			for sh in simhits:
				# provenance
				pt.GetEntry(dic[str(sh.trackID)])
				trackID = str(sh.trackID)
				proc = None
				lastE = 0.
				neutronDaughterPosition = (0., 0., 0.)
				tstring = '  '
				while True:
					NDP = (list(pt.x)[0], list(pt.y)[0], list(pt.z)[0])
					pt.GetEntry(dic[trackID])
					tstring += str(pt.name) + ' '
					if pt.name == 'neutron':
						proc = str(list(pt.process)[-1])
						tstring += '(' + proc + ')'
						if proc == 'neutronInelastic':
							x, y, z = list(pt.x), list(pt.y), list(pt.z)
							for i in range(len(x)-1, -1, -1):
								if norm(x[i]-NDP[0], y[i]-NDP[1], z[i]-NDP[2]) < 0.0000000001:
									lastE = list(pt.energy)[i-1]
									break
						elif proc == 'nCapture':
							dlog.warning('{EVENT}: nCapture found'.format(EVENT=event))
							x, y, z = list(pt.x), list(pt.y), list(pt.z)
							if norm(x[-1]-NDP[0], y[-1]-NDP[1], z[-1]-NDP[2]) > 0.0000000001:
								dlog.warning('\033[31m{EVENT}: nCapture did not create the SimHit?\033[m'.format(EVENT=event))
								for i in range(len(x)-1, -1, -1):
									if norm(x[i]-NDP[0], y[i]-NDP[1], z[i]-NDP[2]) < 0.0000000001:
										lastE = list(pt.energy)[i-1]
										dlog.warning('\033[31m{EVENT}: {MSG}\033[m'.format(EVENT=event, MSG=str(list(pt.process)[i-1:i+2])))
										break
							else:
								lastE = float(list(pt.energy)[-2])
						log.info(tstring)
						break
					if pt.parent == '0':
						tstring += '<= 0'
						log.info(tstring)
						break
					tstring += '<= '
					trackID = str(pt.parent)

				# printout
				pt.GetEntry(dic[str(sh.trackID)])
				log.info('  {cham:3d} {track:7d} {eloss:8.4f} {pid:10d} {tof:15.4f} {proc:20s} {laste:10.4f}'.format(
					cham  = sh.cham,
					track = sh.trackID,
					eloss = sh.energyLoss*1e6,
					pid   = sh.particleID,
					tof   = sh.tof,
					proc  = proc,
					laste = lastE*1e15
				)
				)
			#dlog.warning('Finished Event {EVENT}'.format(EVENT=event))

#for i in range(1, 301): analyzeEvent(i)

threads = []
dlog = logging.getLogger('debug')
dlog.addHandler(logging.StreamHandler(sys.stdout))

i = 1
while True:
	if threading.activeCount() < 10:
		t = threading.Thread(target=analyzeEvent, args=(i,))
		threads.append(t)
		t.start()
		i += 1
	if i == 301:
		break
