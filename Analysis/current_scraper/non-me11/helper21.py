''' Helper functions for plotSlopes.py, runAllBatch.py
'''
import logging,os

fills = {
		###5331:['25.09.16 05:00:00','25.09.16 13:00:00'],
		5338:['26.09.16 06:00:00','26.09.16 14:00:00'],
		#5339:['26.09.16 14:00:00','27.09.16 09:30:00'], # all slopes are zero
		5340:['27.09.16 09:00:00','28.09.16 06:30:00'],
		5345:['28.09.16 11:00:00','29.09.16 03:30:00'],
		#5351:['30.09.16 02:30:00','30.09.16 21:00:00'], # all slopes are zero
		5352:['30.09.16 20:30:00','01.10.16 12:30:00'],
		#5355:['02.10.16 13:00:00','03.10.16 07:00:00'],
		###5391:['09.10.16 07:30:00','09.10.16 11:30:00'],
		###5393:['09.10.16 10:00:00','10.10.16 08:00:00'],
		5394:['10.10.16 13:00:00','11.10.16 09:00:00'],
		5395:['11.10.16 08:00:00','11.10.16 13:00:00'],
		5401:['12.10.16 00:00:00','12.10.16 09:30:00'],
		5405:['12.10.16 20:00:00','13.10.16 04:00:00'],
		5406:['13.10.16 04:00:00','13.10.16 14:00:00'],
		5416:['14.10.16 18:00:00','15.10.16 20:00:00'],
		5418:['15.10.16 21:00:00','16.10.16 11:00:00'],
		5421:['16.10.16 19:00:00','17.10.16 12:00:00'],
		5423:['17.10.16 19:30:00','18.10.16 17:30:00'],
		5424:['18.10.16 17:30:00','19.10.16 00:00:00'],
		5427:['19.10.16 03:00:00','19.10.16 12:00:00'],
		5433:['19.10.16 22:00:00','20.10.16 09:00:00'],
		#5437:['21.10.16 00:00:00','21.10.16 11:00:00'], # all slopes are zero
		5439:['21.10.16 18:00:00','22.10.16 14:00:00'],
		5441:['22.10.16 15:00:00','23.10.16 03:00:00'],
		5442:['23.10.16 01:30:00','23.10.16 21:30:00'],
		5443:['23.10.16 21:30:00','24.10.16 15:30:00'],
		##5446:['23.10.16 16:30:00','25.10.16 06:00:00'],
		5448:['25.10.16 05:30:00','25.10.16 21:00:00'],
		5450:['26.10.16 00:00:00','26.10.16 08:00:00'],
		5451:['26.10.16 08:50:00','26.10.16 23:00:00'],
		}

# Setup logging
def setup_logger(logger_name,log_file,level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)

# Setup conv dictionary
def make_conv(offset=False):
	if offset:
		where = 'results_offset'
		save = 'plots/results/'
	else:
		where = 'results'
		save = 'plots/results_offset/'
	# Make dict of conversions
	conv = {fill:{ec:{cham:{seg:{layer:{} for layer in range(1,7)} for seg in range(1,4)} for cham in range(1,19)} for ec in ['P','M']} for fill in fills.keys()}
	# Loop on data files and fill dictionary
	for idx,fill in enumerate(fills.keys()):
		newpdfname = where+'/fill'+str(fill)+'/'+'f'+str(fill)
		timestampMin = fills[fill][0]
		timestampMax = fills[fill][1]
		if(len(timestampMax)>0 or len(timestampMin)>0):
			newpdfname+= '_'+timestampMin.replace(' ','_')#+'-'+timestampMax.replace(' ','_')
			newpdfname=newpdfname[:len(newpdfname)-3]+'-'+timestampMax.replace(' ','_')
			newpdfname=newpdfname[:len(newpdfname)-3].replace(':','h')
		newpdfname+='.txt'
		#print 'creating pdf: '+newpdfname
		dFile = newpdfname
		if not os.path.isfile(dFile): continue

		#dFile = 'results/fill'+str(fill)+'/f'+str(fill)+'_['+start+'-'+end+'].txt' # old ME11
		#dFile = 'results_noOffset/fill'+str(fill)+'/f'+str(fill)+'_'+start+'-'+end+'.txt'
		#dFile = 'results/fill5451/f5451_26.10.16_08h50-26.10.16_23h00.txt'
		data = open(dFile,'r')
		#print dFile
		for jdx,columns in enumerate(data):
			# Skip the header line
			if jdx==0: continue
			# Skip empty lines
			if columns=='\n': continue
			col = columns.strip('\n').split()
			# Skip channels which are problematic
			if col[0]=='CSC_ME_P21_C06_2_2': continue # 2 points a crappy fit makes
			if col[0]=='CSC_ME_P21_C13_1_3': continue # 2 points a crappy fit makes
			# Skip lines w/o data
			if col[0] == '###': continue
			if len(col)<8: 
				#print fill,col[0],len(col)
				continue

			# channel = CSC_ME_P21_C01_1_1 
			channel = col[0].split('_')
			ec = channel[2][0]
			ring = channel[2][1:3]
			cham = int(channel[3][1:])
			segment = int(channel[4])
			layer = int(channel[5])
			HV = float(col[2])
			print fill, ec, cham, layer, HV, col[8], col[9], col[15]
			if offset:
				conv[fill][ec][cham][segment][layer] = {
						'offset':float(col[8]),
						'offset_err':float(col[9]),
						'slope':float(col[10]),
						'err'  :float(col[11]),
						'HV':HV,
						'devI':float(col[19]),
						}
			else:
				conv[fill][ec][cham][segment][layer] = {
						'slope':float(col[8]),
						'err'  :float(col[9]),
						'HV':HV,
						'devI':float(col[15]),
						}
	return conv
