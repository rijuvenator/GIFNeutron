##########
# This file defines the Primitives classes for ease of access and idiomatic analysis code.
# Seriously, life is much better once you have a list of objects that are actual objects.
# Line breaks are meta-computation -- things you can't get directly from the trees.
##########

# "EventTree", purely for speed purposes. Making lists from ROOT vectors is slow.
# It should only be done once per event, not once per object! So create this,
# then pass it to the classes (which used to take addressed trees; they now take this)
# DecList is for turning on or off some declarations. No need to declare everything
# if we're not going to use them.
class ETree():
	def __init__(self, t, DecList=('COMP', 'STRIP', 'WIRE', 'RECHIT')):
		if 'COMP' in DecList:
			self.comp_cham    = list(t.comp_id)
			self.comp_layer   = [ord(x) for x in list(t.comp_lay)  ]
			self.comp_strip   = [ord(x) for x in list(t.comp_strip)]
			self.comp_comp    = [ord(x) for x in list(t.comp_comp) ]
			self.comp_timeBin = [ord(x) for x in list(t.comp_time) ]

		if 'STRIP' in DecList:
			self.strip_cham   = list(t.strip_id)
			self.strip_layer  = [ord(x)  for x in list(t.strip_lay)   ]
			self.strip_number = [ord(x)  for x in list(t.strip_number)]
			self.strip_ADC    = [list(x) for x in list(t.strip_ADC)   ]

		if 'WIRE' in DecList:
			self.wire_cham    = list(t.wire_id)
			self.wire_layer   = [ord(x) for x in list(t.wire_lay) ]
			self.wire_number  = [ord(x) for x in list(t.wire_grp) ]
			self.wire_timeBin = [ord(x) for x in list(t.wire_time)]

		if 'RECHIT' in DecList:
			self.rh_cham      = list(t.rh_id)
			self.rh_layer     = [ord(x) for x in list(t.rh_lay)]
			self.rh_pos       = (list(t.rh_pos_x), list(t.rh_pos_y))
			self.rh_strips    = ([ord(x) for x in list(t.rh_strip_1)], [ord(x) for x in list(t.rh_strip_2)], [ord(x) for x in list(t.rh_strip_3)])
			self.rh_posStrip  = list(t.rh_pos_strip)
			self.rh_nStrips   = [ord(x) for x in list(t.rh_n_strips)]
			self.rh_wireGroup = [ord(x) for x in list(t.rh_wireGrp)]
			self.rh_energy    = list(t.rh_energy)

# The Primitives Classes: take in an ETree and an index, produces an object.
class Comp():
	def __init__(self, t, i):
		self.cham    = t.comp_cham[i]
		self.layer   = t.comp_layer[i]
		self.strip   = t.comp_strip[i]
		self.comp    = t.comp_comp[i]
		self.timeBin = t.comp_timeBin[i]

		self.halfStrip = 2*self.strip + self.comp
		self.staggeredHalfStrip = self.halfStrip - 0.5 * (self.layer % 2 == 0)

class Strip():
	def __init__(self, t, i):
		self.cham   = t.strip_cham[i]
		self.layer  = t.strip_layer[i]
		self.number = t.strip_number[i]
		self.ADC    = t.strip_ADC[i]

		self.staggeredNumber = self.number - 0.5 * (self.layer % 2 == 0)

class Wire():
	def __init__(self, t, i):
		self.cham    = t.wire_cham[i]
		self.layer   = t.wire_layer[i]
		self.number  = t.wire_number[i]
		self.timeBin = t.wire_timeBin[i]

class RecHit():
	def __init__(self, t, i):
		self.cham      = t.rh_cham[i]
		self.layer     = t.rh_layer[i]
		self.pos       = (t.rh_pos[0][i], t.rh_pos[1][i])
		self.strips    = (t.rh_strips[0][i], t.rh_strips[1][i], t.rh_strips[2][i])
		self.posStrip  = t.rh_posStrip[i]
		self.nStrips   = t.rh_nStrips[i]
		self.wireGroup = t.rh_wireGroup[i]
		self.energy    = t.rh_energy[i]
