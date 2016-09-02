class Particle():
	def __init__(self, dlist):
		self.ID           = dlist[0]
		self.name         = dlist[1]
		self.parent       = dlist[2]
		self.dist         = dlist[3]
		self.process      = dlist[4]
		self.daughters    = dlist[5]
		self.pos_init     = dlist[6]
		self.energy_init  = dlist[7]
		self.pos_final    = dlist[8]
		self.energy_final = dlist[9]

