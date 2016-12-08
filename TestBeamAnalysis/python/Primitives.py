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
	def __init__(self, t, DecList=('COMP', 'STRIP', 'WIRE', 'RECHIT', 'LCT', 'SEGMENT')):
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

		if 'LCT' in DecList:
			self.lct_cham         = list(t.lct_id)
			self.lct_pattern      = [ord(x) for x in list(t.lct_pattern)     ]
			self.lct_keyHalfStrip = [ord(x) for x in list(t.lct_keyHalfStrip)]
			self.lct_keyWireGroup = [ord(x) for x in list(t.lct_keyWireGroup)]

		if 'SEGMENT' in DecList:
			self.seg_cham      = list(t.segment_id)
			self.seg_pos_x     = list(t.segment_pos_x)
			self.seg_pos_y     = list(t.segment_pos_y)
			self.seg_dxdz      = list(t.segment_dxdz)
			self.seg_dydz      = list(t.segment_dydz)
			self.seg_dx        = list(t.segment_dx)
			self.seg_dy        = list(t.segment_dy)
			self.seg_strip     = list(t.segment_pos_strip_x)
			self.seg_wireGroup = list(t.segment_pos_wire_y)
			self.seg_nHits     = [ord(x) for x in list(t.segment_nHits)]
			self.seg_rhID1     = list(t.segment_recHitIdx_1)
			self.seg_rhID2     = list(t.segment_recHitIdx_2)
			self.seg_rhID3     = list(t.segment_recHitIdx_3)
			self.seg_rhID4     = list(t.segment_recHitIdx_4)
			self.seg_rhID5     = list(t.segment_recHitIdx_5)
			self.seg_rhID6     = list(t.segment_recHitIdx_6)

# The Primitives Classes: take in an ETree and an index, produces an object.
class Comp():
	def __init__(self, t, i):
		self.cham    = t.comp_cham[i]
		self.layer   = t.comp_layer[i]
		self.strip   = t.comp_strip[i]
		self.comp    = t.comp_comp[i]
		self.timeBin = t.comp_timeBin[i]

		self.halfStrip = 2*self.strip + self.comp
		self.staggeredHalfStrip = self.halfStrip - (self.cham == 110) * (0.5 * (self.layer % 2 == 0))

class Strip():
	def __init__(self, t, i):
		self.cham   = t.strip_cham[i]
		self.layer  = t.strip_layer[i]
		self.number = t.strip_number[i]
		self.ADC    = t.strip_ADC[i]

		self.staggeredNumber = self.number - (self.cham == 110) * (0.5 * (self.layer % 2 == 0))

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

class LCT():
	def __init__(self, t, i):
		self.cham         = t.lct_cham[i]
		self.pattern      = t.lct_pattern[i]
		self.keyHalfStrip = t.lct_keyHalfStrip[i]
		self.keyWireGroup = t.lct_keyWireGroup[i]

class Segment():
	def __init__(self, t, i):
		self.cham      = t.seg_cham[i]
		self.pos_x     = t.seg_pos_x[i]
		self.pos_y     = t.seg_pos_y[i]
		self.dxdz      = t.seg_dxdz[i]
		self.dydz      = t.seg_dydz[i]
		self.dx        = t.seg_dx[i]
		self.dy        = t.seg_dy[i]
		self.strip     = t.seg_strip[i]
		self.wireGroup = t.seg_wireGroup[i]
		self.nHits     = t.seg_nHits[i]
		self.rhID1     = t.seg_rhID1[i]
		self.rhID2     = t.seg_rhID2[i]
		self.rhID3     = t.seg_rhID3[i]
		self.rhID4     = t.seg_rhID4[i]
		self.rhID5     = t.seg_rhID5[i]
		self.rhID6     = t.seg_rhID6[i]

		self.halfStrip = 2 * self.strip
