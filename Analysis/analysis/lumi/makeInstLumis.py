##### GET INSTANTANEOUS LUMINOSITIES FROM JSON #####

# --- First, run these commands, replacing DATA.json with some .json
#
# export PATH=$HOME/.local/bin:/afs/cern.ch/cms/lumi/brilconda-1.1.7/bin:$PATH (bash)
# brilcalc lumi --normtag /afs/cern.ch/user/l/lumipro/public/normtag_file/normtag_DATACERT.json -i DATA.json --byls -u 1e33/cm2s > BrilRawOutput
# grep "STABLE BEAMS" BrilRawOutput > tmp; mv tmp BrilRawOutput

# --- Now this produces a formatted output. Pipe to datafiles/
f = open('BrilRawOutput')
for line in f:
	cols = line.split()
	run = int(cols[1].split(':')[0])
	fill = int(cols[1].split(':')[1])
	ls = int(cols[3].split(':')[0])
	ilumi = float(cols[13])
	pu = float(cols[17])
	print '{:4d} {:6d} {:5d} {:6.3f} {:4.1f}'.format(fill, run, ls, ilumi, pu)
