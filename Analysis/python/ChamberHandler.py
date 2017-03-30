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

		chambers = {
			(1  ,  36) : (1, 1, 48 , 112),
			(37 ,  72) : (1, 2, 64 , 80 ),
			(73 , 108) : (1, 3, 32 , 64 ),
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

	def display(self, fstring='ME{S}/{R}/{C}'):
		fstring = fstring.replace('{E}','{endcap:1s}'  )
		fstring = fstring.replace('{S}','{station:1d}' )
		fstring = fstring.replace('{R}','{ring:1d}'    )
		fstring = fstring.replace('{C}','{chamber:02d}')
		return fstring.format(endcap=('+' if self.endcap == 1 else '-'), station=self.station, ring=self.ring, chamber=self.chamber)

	def setArea(self):
		# Areas are calculated from this link
		# https://twiki.cern.ch/twiki/pub/CMS/MuonDPGCSC/table_of_csc_properties_150730.pdf
		# Area = 6 * 0.5 * AGV_h * ( AGV_t + AGV_b )
		areas = {}
		# me11 me12 me13 me21 me22 me31 me32 me41 me42 # me11a me11b 
		h = {'11': 152.0, '12': 174.49, '13': 164.16, '21': 189.66, '22': 323.06, '31': 169.70, '32': 323.06, '41': 149.42, '42': 323.06}#  44.5, 107.5,
		b = {'11': 19.14, '12':  51.00, '13':  63.40, '21':  54.00, '22':  66.46, '31':  61.40, '32':  66.46, '41':  69.01, '42':  66.46}# 19.14,  27.4,
		t = {'11':  47.4, '12':  83.74, '13':  92.10, '21': 125.71, '22': 127.15, '31': 125.71, '32': 127.15, '41': 125.65, '42': 127.15}#  27.4,  47.4,
		for ring in h.keys():
			areas[ring] = 6*0.5*h[ring]*(t[ring]+b[ring])

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
