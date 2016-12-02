##########
# This file defines the Primitives classes for ease of access and idiomatic analysis code.
# Seriously, life is much better once you have a list of objects that are actual objects.
# Line breaks are meta-computation -- things you can't get directly from the trees.
##########

class Comp():
	def __init__(self, t, i):
		self.cham    = list(t.comp_id)[i]
		self.layer   = ord(list(t.comp_lay)[i])
		self.strip   = ord(list(t.comp_strip)[i])
		self.comp    = ord(list(t.comp_comp)[i])
		self.timeBin = ord(list(t.comp_time)[i])

		self.halfStrip = 2*self.strip + self.comp
		self.staggeredHalfStrip = self.halfStrip - 0.5 * (self.layer % 2 == 0)

class Strip():
	def __init__(self, t, i):
		self.cham   = list(t.strip_id)[i]
		self.layer  = ord(list(t.strip_lay)[i])
		self.number = ord(list(t.strip_number)[i])
		self.ADC    = list(list(t.strip_ADC)[i])

		self.staggeredNumber = self.number - 0.5 * (self.layer % 2 == 0)

class Wire():
	def __init__(self, t, i):
		self.cham    = list(t.wire_id)[i]
		self.layer   = ord(list(t.wire_lay)[i])
		self.number  = ord(list(t.wire_grp)[i])
		self.timeBin = ord(list(t.wire_time)[i])

class RecHit():
	def __init__(self, t, i):
		self.cham      = list(t.rh_id)[i]
		self.layer     = ord(list(t.rh_lay)[i])
		self.pos       = (list(t.rh_pos_x)[i], list(t.rh_pos_y)[i])
		self.strips    = (ord(list(t.rh_strip_1)[i]), ord(list(t.rh_strip_2)[i]), ord(list(t.rh_strip_3)[i]))
		self.posStrip  = list(t.rh_pos_strip)[i]
		self.nStrips   = ord(list(t.rh_n_strips)[i])
		self.wireGroup = ord(list(t.rh_wireGrp)[i])
		self.energy    = list(t.rh_energy)[i]
