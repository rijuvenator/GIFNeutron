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
		self.inverseSerial()
	
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
