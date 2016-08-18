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
	"RUN_COMMENT"     ,
	"TMB_DUMP_TIME"   ,
	"TMB_DUMP_COMMENT",
	"SPS_CYCLE"
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
	"comment",
	"time"   ,
	"dump"   ,
	"spstime"
	]

cmd = "select "
cmd += ", ".join(cnames)
cmd += " from gif_table"
cmd += " where MEASUR_NUM>1648"
cmd += " order by MEASUR_NUM"

empty = [2480, 2589, 2612, 2733, 2783]
special = [2318, 2319]

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

	hasErred = False
	data = dict(zip(cshort, row))
	meas = str(data['meas'])

	# skip the empty and double-readout special runs entirely
	if int(meas) in empty or int(meas) in special:
		row = curs.fetchone()
		continue

	# find which chamber is on; default to 1 if both on or neither on
	if   data['me11'] == 'on' and (data['me21'] == 'off' or data['me21'] is None):
		cham = '1'
	elif data['me21'] == 'on' and (data['me11'] == 'off' or data['me11'] is None): 
		cham = '2'
	else:
		if not hasErred:
			hasErred = True
			sys.stderr.write("\n")
		sys.stderr.write("%s: Only one chamber is not on: ME11 %s, ME21 %s\n" % (meas, data['me11'], data['me21']))
		cham = '1'

	# find HV for selected chamber; look in dropdown, then except, then text box; default to X if not found
	if data['dhv'+cham+'1'] is not None:
		if 'HV0' in data['dhv'+cham+'1']:
			hv = 'HV0'
	elif data['ehv'+cham+'1'] is not None:
		if 'HV0' in data['ehv'+cham+'1']:
			hv = 'HV0'
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
	
	if data['dump'] is None:
		dump = ''
	else:
		dump = data['dump'].read()

	if 'TMB' in dtyp or 'Counter' in dump:
		mtype = 'TMB'
		# also save the duration (as time, or as 3 x SPS Cycle Time)
		time = str(data['time'])
		if time=='None' and data['spstime'] is not None:
			#if not hasErred:
			#	hasErred = True
			#	sys.stderr.write("\n")
			#sys.stderr.write("%s: No duration; using 3 x SPS Cycle Time instead\n" % meas)
			time = str(3 * data['spstime'])
		elif time=='None':
			if not hasErred:
				hasErred = True
				sys.stderr.write("\n")
			sys.stderr.write("%s: Found TMB dump, but no duration found\n" % meas)
			time = str(0)
		# also save the TMB dump, stripping carriage returns, extra newlines, adding the Counters, and the Duration
		dump = dump.replace('\r','')
		while dump[-2:] == '\n\n':
			dump = dump.strip('\n')
		if 'Counter' not in dump:
			dump = """--------------------------------------------------------
			---              Counters                             --
			--------------------------------------------------------""" + dump
		dump = dump + '\nDuration: ' + time
		tmb = open("tmb/"+meas+".tmb", "w")
		tmb.write(dump)
		tmb.close()
		if 'TMB' not in dtyp:
			if not hasErred:
				hasErred = True
				sys.stderr.write("\n")
			sys.stderr.write("%s: Found TMB dump, but run type is not TMB dump\n" % meas)
	elif data['file'] is not None:
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
		if 'FastFilter' in data['comment'] or 'option' in data['comment']:
			byline = data['comment'].split('\n')
			for line in byline:
				if 'FastFilter' in line or 'option' in line:
					ff = line.split()[-1]
					# make sure it's a number
					try:
						x = int(ff)
					except ValueError:
						if not hasErred:
							hasErred = True
							sys.stderr.write("\n")
						sys.stderr.write('%s: FF not an int\n' % meas)
		elif 'Cameron' in data['comment']:
			ff = 'C'
		elif 'TB1' in data['comment']:
			ff = 'TB1'
		elif 'P5' in data['comment']:
			ff = 'P5'
		else:
			ff = 'N'
	else:
		ff = 'N'
	
	# print: meas cham HV source beam attup attdown ff type/run
	print '%4s %s %4s %s %s %5s %5s %3s %s' % (meas, cham, hv, source, beam, attup, attdown, ff, mtype)
	row = curs.fetchone()
