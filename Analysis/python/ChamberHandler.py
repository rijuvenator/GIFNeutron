# Chamber handling class, constructed from a serial ID.
#
# display() returns a formatted string, replacing {E} {S} {R} {C}
# with the appropriate data. Useful for printing, filenames, etc.
#
class Chamber():
	def __init__(self, serial):
		self.id      = serial
		self.endcap  = 0
		self.station = 0
		self.ring    = 0
		self.chamber = 0
		self.nwires  = 0
		self.nstrips = 0
		self.area    = 0
		self.inverseSerial()
		# Compute area after self.station and
		# self.ring are set!
		self.setArea()
	
	def inverseSerial(self):
		serial = self.id
		if serial > 300:
			self.endcap = -1
			serial = serial - 300
		else:
			self.endcap =  1

		chambers = {\
			(1  ,  36) : (1, 1, 48 , 112),
			(37 ,  72) : (1, 2, 48 , 80 ),
			(73 , 108) : (1, 3, 48 , 64 ),
			(109, 126) : (2, 1, 112, 80 ),
			(127, 162) : (2, 2, 64 , 80 ),
			(163, 180) : (3, 1, 96 , 80 ),
			(181, 216) : (3, 2, 64 , 80 ),
			(217, 234) : (4, 1, 96 , 80 ),
			(235, 270) : (4, 2, 64 , 80 )
		}

		for limits in chambers.keys():
			if serial >= limits[0] and serial <= limits[1]:
				self.station = chambers[limits][0]
				self.ring    = chambers[limits][1]
				self.nwires  = chambers[limits][2]
				self.nstrips = chambers[limits][3]
				self.chamber = serial - (limits[0] - 1)
				break

	def display(self, fstring='ME{S}/{R}'):
		fstring = fstring.replace('{E}','{endcap:1s}'  )
		fstring = fstring.replace('{S}','{station:1d}' )
		fstring = fstring.replace('{R}','{ring:1d}'    )
		fstring = fstring.replace('{C}','{chamber:02d}')
		return fstring.format(endcap=('+' if self.endcap == 1 else '-'), station=self.station, ring=self.ring, chamber=self.chamber)

	def setArea(self):
		# Areas are calculated from this link
		# https://twiki.cern.ch/twiki/pub/CMS/MuonDPGCSC/table_of_csc_properties_150730.pdf
		# Area = 6 * 0.5 * AGV_h * ( AGV_t - AGV_b )
		areas = {
				'11' : 0.,
				'12' : 0.,
				'13' : 0.,
				'21' : 0.,
				'22' : 0.,
				'31' : 0., 
				'32' : 0.,
				'41' : 0.,
				'42' : 0.,
		}
		#   me11    me12    me13    me21    me22    me31    me32    me41    me42 # me11a  me11b 
		h=[152.0, 174.49, 164.16, 189.66, 323.06, 169.70, 323.06, 149.42, 323.06]#  44.5, 107.5,
		b=[19.14,  51.00,  63.40,  54.00,  66.46,  61.40,  66.46,  69.01,  66.46]# 19.14,  27.4,
		t=[ 47.4,  83.74,  92.10, 125.71, 127.15, 125.71, 127.15, 125.65, 127.15]#  27.4,  47.4,
		for r,ring in enumerate(areas.keys()):
			areas[ring] = 6*0.5*h[r]*(t[r]+b[r])

		self.area = areas[self.display('{S}{R}')]


def serialID(E, S, R, C):
	SerialDict = {
		(1, 1): 0,
		(1, 2): 36,
		(1, 3): 72,
		(1, 4): 0,
		(2, 1): 108,
		(2, 2): 126,
		(3, 1): 162,
		(3, 2): 180,
		(4, 1): 216,
		(4, 2): 234
	}
	return C + SerialDict[(S, R)] + (300 * (E == -1 or E == 2))
