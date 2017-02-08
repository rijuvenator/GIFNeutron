import Gif.Analysis.ChamberHandler as CH

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
	def __init__(self, t, DecList=('COMP', 'STRIP', 'WIRE', 'RECHIT', 'LCT', 'SEGMENT','CLCT')):
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
			self.rh_strips    = [[ord(x) for x in list(t.rh_strip_1)], [ord(x) for x in list(t.rh_strip_2)], [ord(x) for x in list(t.rh_strip_3)]]
			self.rh_posStrip  = list(t.rh_pos_strip)
			self.rh_nStrips   = [ord(x) for x in list(t.rh_n_strips)]
			self.rh_wireGroup = [ord(x) for x in list(t.rh_wireGrp)]
			self.rh_energy    = list(t.rh_energy)
			# Temporarily not backwards compatible!
			if 'rh_time' in [br.GetName() for br in list(t.GetListOfBranches())]:
				self.rh_time      = list(t.rh_time)
			else:
				self.rh_time      = list(t.rh_tpeak)

		if 'LCT' in DecList:
			self.lct_cham         = list(t.lct_id)
			self.lct_pattern      = [ord(x) for x in list(t.lct_pattern)     ]
			self.lct_keyHalfStrip = [ord(x) for x in list(t.lct_keyHalfStrip)]
			self.lct_keyWireGroup = [ord(x) for x in list(t.lct_keyWireGroup)]

		if 'CLCT' in DecList:
			self.clct_cham       = list(t.clct_id)
			self.clct_quality    = [ord(x) for x in list(t.clct_quality)]
			self.clct_halfStrip  = [ord(x) for x in list(t.clct_halfStrip)]
			self.clct_CFEB       = [ord(x) for x in list(t.clct_CFEB)]
			self.clct_keyStrip   = [ord(x) for x in list(t.clct_keyStrip)]
			self.clct_pattern    = [ord(x) for x in list(t.clct_pattern)]

		if 'SEGMENT' in DecList:
			self.seg_cham       = list(t.segment_id)
			self.seg_pos        = [list(x) for x in [list(posByLay) for posByLay in list(t.segment_pos)]]
			self.seg_slope      = [list(x) for x in list(t.segment_slope)]
			self.seg_slope_prim = [list(x) for x in [list(slopeByLay) for slopeByLay in list(t.segment_slope_prim)]]
			self.seg_nHits      = [ord(x)  for x in list(t.segment_nHits)]
			self.seg_rhID1      = list(t.segment_recHitIdx_1)
			self.seg_rhID2      = list(t.segment_recHitIdx_2)
			self.seg_rhID3      = list(t.segment_recHitIdx_3)
			self.seg_rhID4      = list(t.segment_recHitIdx_4)
			self.seg_rhID5      = list(t.segment_recHitIdx_5)
			self.seg_rhID6      = list(t.segment_recHitIdx_6)
			self.seg_chisq      = list(t.segment_chisq)
			self.seg_dof        = [ord(x) for x in list(t.segment_dof)]

# The Primitives Classes: take in an ETree and an index, produces an object.
class Comp():
	def __init__(self, t, i):
		self.cham    = t.comp_cham[i]
		self.layer   = t.comp_layer[i]
		self.strip   = t.comp_strip[i]
		self.comp    = t.comp_comp[i]
		self.timeBin = t.comp_timeBin[i]

		c = CH.Chamber(self.cham)
		self.isStaggered = (not (c.station == 1 and c.ring == 1)) * (self.layer % 2 == 0)

		self.halfStrip = 2*self.strip + self.comp
		self.staggeredHalfStrip = self.halfStrip - self.isStaggered * 1.0

class Strip():
	def __init__(self, t, i):
		self.cham   = t.strip_cham[i]
		self.layer  = t.strip_layer[i]
		self.number = t.strip_number[i]
		self.ADC    = t.strip_ADC[i]

		c = CH.Chamber(self.cham)
		self.isStaggered = (not (c.station == 1 and c.ring == 1)) * (self.layer % 2 == 0)

		self.staggeredNumber = self.number - self.isStaggered * 0.5

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
		self.pos       = {'x' : t.rh_pos[0][i], 'y' : t.rh_pos[1][i]}
		self.strips    = [t.rh_strips[0][i], t.rh_strips[1][i], t.rh_strips[2][i]]
		self.posStrip  = t.rh_posStrip[i]
		self.nStrips   = t.rh_nStrips[i]
		self.wireGroup = t.rh_wireGroup[i]
		self.energy    = t.rh_energy[i]
		self.time      = t.rh_time[i]

		self.halfStrip = (self.strips[0 if self.nStrips == 1 else 1] + self.posStrip) * 2

class LCT():
	def __init__(self, t, i):
		self.cham         = t.lct_cham[i]
		self.pattern      = t.lct_pattern[i]
		self.keyHalfStrip = t.lct_keyHalfStrip[i]
		self.keyWireGroup = t.lct_keyWireGroup[i]

class Segment():
	def __init__(self, t, i):
		self.cham      = t.seg_cham[i]
		self.nHits     = t.seg_nHits[i]
		self.chisq     = t.seg_chisq[i]
		self.dof       = t.seg_dof[i]
		self.rhID      = [t.seg_rhID1[i], t.seg_rhID2[i], t.seg_rhID3[i], t.seg_rhID4[i], t.seg_rhID5[i], t.seg_rhID6[i]][0:self.nHits]

		self.primSlope          = {layer + 1 : {'x' : slp[0], 'y' : slp[1], 'z' : slp[2] } for layer, slp in enumerate(t.seg_slope_prim[i])}
		self.pos                = {layer + 1 : {'x' : pos[0], 'y' : pos[1], 'z' : pos[2] } for layer, pos in enumerate(t.seg_pos[i])       }
		self.strip              = {layer + 1 : pos[3]                                      for layer, pos in enumerate(t.seg_pos[i])       }
		self.wireGroup          = {layer + 1 : pos[4]                                      for layer, pos in enumerate(t.seg_pos[i])       }

		c = CH.Chamber(self.cham)
		self.isStaggered = (not (c.station == 1 and c.ring == 1))

		self.halfStrip          = {layer : 2 * self.strip[layer]                                             for layer in self.strip.keys()}
		self.staggeredStrip     = {layer : self.strip[layer]     - 0.5 * self.isStaggered * (layer % 2 == 0) for layer in self.strip.keys()}
		self.staggeredHalfStrip = {layer : self.halfStrip[layer] - 1.0 * self.isStaggered * (layer % 2 == 0) for layer in self.strip.keys()}

		self.slope = {'x' : t.seg_slope[i][0], 'y' : t.seg_slope[i][1], 'z' : t.seg_slope[i][2]}

class CLCT():
	def __init__(self, t, i):
		self.cham      = t.clct_cham[i]
		self.quality   = t.clct_quality[i]
		self.halfStrip = t.clct_halfStrip[i]
		self.CFEB      = t.clct_CFEB[i]
		self.keyStrip  = t.clct_keyStrip[i]
		self.pattern   = t.clct_pattern[i]

		self.keyHalfStrip = self.keyStrip if self.cham == 1 else self.CFEB*32 + self.halfStrip