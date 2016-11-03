#!/usr/bin/env python

import sys
import os
import cx_Oracle

if not os.path.exists("tmb"): os.mkdir("tmb")

class connectDB:
	def __init__(self):
		magic='Read_gif_mnl1%'
		connect= 'cms_emu_fast_r/' + magic + '@cmsr'
		self.orcl = cx_Oracle.connect(connect)
		self.curs = self.orcl.cursor()
	def cursor(self):
		return self.curs

orac = connectDB()
curs = orac.cursor()

cnames = [\
	"MEASUR_NUM"      ,
	"ME11_state"      ,
	"ME21_state"      ,
	"HV_ME11"         ,
	"HV_ME21"         ,
	"HV_SETTING1"     ,
	"HV_SETTING2"     ,
	"HV_ME11_EXCEPT"  ,
	"HV_ME21_EXCEPT"  ,
	"SOURCE_STATE"    ,
	"BEAM_STATE"      ,
	"ATTENUAT_UP"     ,
	"ATTENUAT_DOWN"   ,
	"RUN_TYPE"        ,
	"FILE_NAME"       ,
	"RUN_COMMENT"
	]

cshort = [\
	"meas"   ,
	"me11"   ,
	"me21"   ,
	"hv11"   ,
	"hv21"   ,
	"dhv11"  ,
	"dhv21"  ,
	"ehv11"  ,
	"ehv21"  ,
	"source" ,
	"beam"   ,
	"attup"  ,
	"attdown",
	"type"   ,
	"file"   ,
	"comment"
	]

cmd = "select "
cmd += ", ".join(cnames)
cmd += " from gif_table"
cmd += " where MEASUR_NUM>3218 and MEASUR_NUM<3400"
cmd += " order by MEASUR_NUM"

empty = [3408]
special = []

curs.execute(cmd)

row = curs.fetchone()
while row is not None:

	# reset metadata and hasErred
	meas = 'X'
	cham = 'X'
	hv = 'X'
	source = 'X'
	beam = 'X'
	attup = 'X'
	attdown = 'X'
	ff = 'X'
	mtype = 'X'
	isDual = False

	hasErred = False
	data = dict(zip(cshort, row))
	meas = str(data['meas'])

	# skip the empty and double-readout special runs entirely
	if int(meas) in empty or int(meas) in special:
		row = curs.fetchone()
		continue

	# find which chamber is on; 1 if both on, but set isDual to True; default to 0 if neither on
	if   data['me11'] == 'on' and (data['me21'] == 'off' or data['me21'] is None):
		cham = '1'
	elif data['me21'] == 'on' and (data['me11'] == 'off' or data['me11'] is None): 
		cham = '2'
	elif data['me11'] == 'on' and data['me21'] == 'on':
		isDual = True
		cham = '1'
	else:
		if not hasErred:
			hasErred = True
			sys.stderr.write("\n")
		sys.stderr.write("%s: Neither chamber on: ME11 %s, ME21 %s\n" % (meas, data['me11'], data['me21']))
		cham = '0'

	# find HV for selected chamber; look in dropdown, then except, then text box; default to X if not found
	# use Chamber 1 HV if both are on (assumed to be the same)
	if data['dhv'+cham+'1'] is not None:
		if 'HV0' in data['dhv'+cham+'1']:
			hv = 'HV0'
		elif 'HV1' in data['dhv'+cham+'1']:
			hv = 'HV1'
	elif data['ehv'+cham+'1'] is not None:
		if 'HV0' in data['ehv'+cham+'1']:
			hv = 'HV0'
		elif 'HV1' in data['ehv'+cham+'1']:
			hv = 'HV1'
		# for a handful of cases I don't want to edit -- the text in "except" is not HV0:
		elif data['hv'+cham+'1'] is not None:
			hv = str(data['hv'+cham+'1'])
		else:
			if not hasErred:
				hasErred = True
				sys.stderr.write("\n")
			sys.stderr.write("%s: HV not found\n" % meas)
			hv = 'X'
	elif data['hv'+cham+'1'] is not None:
		hv = str(data['hv'+cham+'1'])
		try:
			x = int(hv)
		except ValueError:
			if not hasErred:
				hasErred = True
				sys.stderr.write("\n")
			sys.stderr.write('%s: HV not an int\n' % meas)
	else:
		if not hasErred:
			hasErred = True
			sys.stderr.write("\n")
		sys.stderr.write("%s: HV not found\n" % meas)
		hv = 'X'

	# find source state; default to X if not found
	if data['source'] == 'on':
		source = '1'
	elif data['source'] == 'off':
		source = '0'
	else:
		if not hasErred:
			hasErred = True
			sys.stderr.write("\n")
		sys.stderr.write('%s: Source not on or off\n' % meas)
		source = 'X'
	
	# find beam state; default to X if not found
	if data['beam'] == 'on':
		beam = '1'
	elif data['beam'] == 'off':
		beam = '0'
	else:
		if not hasErred:
			hasErred = True
			sys.stderr.write("\n")
		sys.stderr.write('%s: Beam not on or off\n' % meas)
		beam = 'X'

	# find upstream attenuation if source on; default to 0 if off, X if not found
	if source == '1' and data['attup'] is not None:
		attup = str(data['attup'])
	elif source == '0':
		attup = '0'
	else:
		if not hasErred:
			hasErred = True
			sys.stderr.write("\n")
		sys.stderr.write('%s: No upstream attenuation\n' % meas)
		attup = 'X'

	# find downstream attenuation if source on; default to 0 if off, X if not found
	if source == '1' and data['attdown'] is not None:
		attdown = str(data['attdown'])
	elif source == '0':
		attdown = '0'
	else:
		if not hasErred:
			hasErred = True
			sys.stderr.write("\n")
		sys.stderr.write('%s: No downstream attenuation\n' % meas)
		attdown = 'X'

	# find run type; if TMB write TMB, else write file name; default to X if not found
	if data['type'] is None:
		dtyp = ''
	else:
		dtyp = data['type']
	
	if data['file'] is not None:
		if 'emugif2' in data['file']:
			mtype = data['file']
			tmp = "".join(mtype.split())
			mtype = tmp
		else:
			if not hasErred:
				hasErred = True
				sys.stderr.write("\n")
			sys.stderr.write("%s: Found invalid filename\n" % meas)
			mtype = 'X'
	else:
		if not hasErred:
			hasErred = True
			sys.stderr.write("\n")
		sys.stderr.write("%s: Neither TMB dump nor file found\n" % meas)
		mtype = 'X'

	# find FastFilterScan setting
	if data['comment'] is not None:
		if 'Beam' in data['comment']:
			byline = data['comment'].split('\n')
			for line in byline:
				if 'Beam_' in line:
					ffraw = [i for i in line.split() if 'Beam_' in i]
					ff = ffraw[0][-1] 
					# make sure it's a number
					try:
						x = int(ff)
					except ValueError:
						if not hasErred:
							hasErred = True
							sys.stderr.write("\n")
						sys.stderr.write('%s: FF not an int\n' % meas)
				elif 'Beam' in line:
					ff = '0'
		else:
			ff = 'N'
	else:
		ff = 'N'
	
	# print: meas cham HV source beam attup attdown ff type/run
	print '%4s %s %4s %s %s %5s %5s %3s %s' % (meas, (cham if not isDual else 'D'), hv, source, beam, attup, attdown, ff, mtype)
	row = curs.fetchone()
