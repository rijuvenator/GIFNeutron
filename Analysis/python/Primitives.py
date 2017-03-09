import Gif.Analysis.ChamberHandler as CH

##########
# This file defines the Primitives classes for ease of access and idiomatic analysis code.
# Seriously, life is much better once you have a list of objects that are actual objects.
# Line breaks are meta-computation -- things you can't get directly from the trees.
##########

# Select Branches: 2-5x speedup
def SelectBranches(t, DecList=(), branches=()):
	t.SetBranchStatus('*', 0)
	Branches = [br for br in branches]
	BranchList = [str(br.GetName()) for br in list(t.GetListOfBranches())]
	BranchHead = {
		'COMP'   : 'comp_' ,
		'STRIP'  : 'strip_',
		'WIRE'   : 'wire_' ,
		'RECHIT' : 'rh_'   ,
		'LCT'    : 'lct_'  ,
		'SEGMENT': 'seg_'  ,
		'CLCT'   : 'clct_' ,
		'SIMHIT' : 'sim_'
	}
	for KEY in DecList:
		Branches.extend([br for br in BranchList if BranchHead[KEY] in br])
	for branch in Branches:
		t.SetBranchStatus(branch, 1)

# "EventTree", purely for speed purposes. Making lists from ROOT vectors is slow.
# It should only be done once per event, not once per object! So create this,
# then pass it to the classes (which used to take addressed trees; they now take this)
# DecList is for turning on or off some declarations. No need to declare everything
# if we're not going to use them.
class ETree():
	def __init__(self, t, DecList=('COMP', 'STRIP', 'WIRE', 'RECHIT', 'LCT', 'SEGMENT','CLCT','SIMHIT')):
		if 'COMP' in DecList:
			self.comp_cham      = list(t.comp_id)
			self.comp_layer     = [ord(x)  for x in list(t.comp_lay)   ]
			self.comp_strip     = [ord(x)  for x in list(t.comp_strip) ]
			self.comp_comp      = [ord(x)  for x in list(t.comp_comp)  ]
			self.comp_timeBin   = [ord(x)  for x in list(t.comp_time)  ]
			self.comp_timeBins  = [list(x) for x in list(t.comp_timeOn)]
			# Temporarily not backwards compatible!
			if hasattr(t, 'comp_pos_x'):
				self.comp_pos       = (list(t.comp_pos_x), list(t.comp_pos_y))
				self.comp_globalPos = (list(t.comp_pos_glb_x), list(t.comp_pos_glb_y), list(t.comp_pos_glb_z))
			else:
				self.comp_pos       = [[0. for i in self.comp_cham] for j in range(2)]
				self.comp_globalPos = [[0. for i in self.comp_cham] for j in range(3)]

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
			# Temporarily not backwards compatible!
			if hasattr(t, 'wire_pos_x'):
				self.wire_pos       = (list(t.wire_pos_x), list(t.wire_pos_y))
				self.wire_globalPos = (list(t.wire_pos_glb_x), list(t.wire_pos_glb_y), list(t.wire_pos_glb_z))
			else:
				self.wire_pos       = [[0. for i in self.wire_cham] for j in range(2)]
				self.wire_globalPos = [[0. for i in self.wire_cham] for j in range(3)]

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
			if hasattr(t, 'rh_time'):
				self.rh_stripTime = list(t.rh_time)
				self.rh_wireTime  = [0. for i in self.rh_cham]
			else:
				self.rh_stripTime = list(t.rh_tpeak)
				self.rh_wireTime  = list(t.rh_wireTime)
			if hasattr(t, 'rh_pos_glb_x'):
				self.rh_globalPos = (list(t.rh_pos_glb_x), list(t.rh_pos_glb_y), list(t.rh_pos_glb_z))
			else:
				self.rh_globalPos = [[0. for i in self.rh_cham] for j in range(3)]

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

		if 'SIMHIT' in DecList:
			if hasattr(t, 'sim_id'):
				self.sim_cham         = list(t.sim_id)
				self.sim_particle_id  = list(t.sim_particle_id)
				self.sim_process_type = list(t.sim_process_type)
				self.sim_layer        = [ord(x) for x in list(t.sim_lay)]
				self.sim_pos          = (list(t.sim_pos_x), list(t.sim_pos_y), list(t.sim_pos_z))
				self.sim_tof          = list(t.sim_tof)
				self.sim_energyLoss   = list(t.sim_energyLoss )
				self.sim_entry        = (list(t.sim_entry_x), list(t.sim_entry_y), list(t.sim_entry_z))
				self.sim_exit         = (list(t.sim_exit_x), list(t.sim_exit_y), list(t.sim_exit_z))
				self.sim_stripPos     = list(t.sim_pos_strip)
				self.sim_wirePos      = list(t.sim_pos_wire)
				self.sim_globalPos    = (list(t.sim_pos_glb_x), list(t.sim_pos_glb_y), list(t.sim_pos_glb_z))
				self.sim_entry_pabs   = list(t.sim_entry_pabs)
				self.sim_entry_p      = (list(t.sim_entry_px), list(t.sim_entry_py), list(t.sim_entry_pz))

# The Primitives Classes: take in an ETree and an index, produces an object.
class Comp():
	def __init__(self, E, i):
		self.cham      = E.comp_cham[i]
		self.layer     = E.comp_layer[i]
		self.strip     = E.comp_strip[i]
		self.comp      = E.comp_comp[i]
		self.timeBin   = E.comp_timeBin[i]
		self.timeBins  = E.comp_timeBins[i]
		self.pos       = {'x' : E.comp_pos[0][i], 'y' : E.comp_pos[1][i]}
		self.globalPos = {'x' : E.comp_globalPos[0][i], 'y' : E.comp_globalPos[1][i], 'z' : E.comp_globalPos[2][i]}

		c = CH.Chamber(self.cham)
		self.isStaggered = (not (c.station == 1 and c.ring == 1)) * (self.layer % 2 == 0)

		self.halfStrip = 2*self.strip + self.comp
		self.staggeredHalfStrip = self.halfStrip - self.isStaggered * 1.0

class Strip():
	def __init__(self, E, i):
		self.cham   = E.strip_cham[i]
		self.layer  = E.strip_layer[i]
		self.number = E.strip_number[i]
		self.ADC    = E.strip_ADC[i]

		c = CH.Chamber(self.cham)
		self.isStaggered = (not (c.station == 1 and c.ring == 1)) * (self.layer % 2 == 0)

		self.staggeredNumber = self.number - self.isStaggered * 0.5

class Wire():
	def __init__(self, E, i):
		self.cham      = E.wire_cham[i]
		self.layer     = E.wire_layer[i]
		self.number    = E.wire_number[i]
		self.timeBin   = E.wire_timeBin[i]
		self.pos       = {'x' : E.wire_pos[0][i], 'y' : E.wire_pos[1][i]}
		self.globalPos = {'x' : E.wire_globalPos[0][i], 'y' : E.wire_globalPos[1][i], 'z' : E.wire_globalPos[2][i]}

class RecHit():
	def __init__(self, E, i):
		self.cham      = E.rh_cham[i]
		self.layer     = E.rh_layer[i]
		self.pos       = {'x' : E.rh_pos[0][i], 'y' : E.rh_pos[1][i]}
		self.strips    = [E.rh_strips[0][i], E.rh_strips[1][i], E.rh_strips[2][i]]
		self.posStrip  = E.rh_posStrip[i]
		self.nStrips   = E.rh_nStrips[i]
		self.wireGroup = E.rh_wireGroup[i]
		self.energy    = E.rh_energy[i]
		self.stripTime = E.rh_stripTime[i]
		self.wireTime  = E.rh_wireTime[i]
		self.globalPos = {'x' : E.rh_globalPos[0][i], 'y' : E.rh_globalPos[1][i], 'z' : E.rh_globalPos[2][i]}

		self.halfStrip = (self.strips[0 if self.nStrips == 1 else 1] + self.posStrip) * 2

class SimHit():
	def __init__(self, E, i):
		self.cham        = E.sim_cham[i]
		self.particleID  = E.sim_particle_id[i]
		self.processType = E.sim_process_type[i]
		self.layer       = E.sim_layer[i]
		self.pos         = {'x' : E.sim_pos[0][i], 'y' : E.sim_pos[1][i], 'z' : E.sim_pos[2][i]}
		self.tof         = E.sim_tof[i]
		self.energyLoss  = E.sim_energyLoss[i]
		self.entryPos    = {'x' : E.sim_entry[0][i], 'y' : E.sim_entry[1][i], 'z' : E.sim_entry[2][i]}
		self.exitPos     = {'x' : E.sim_exit[0][i] , 'y' : E.sim_exit[1][i] , 'z' : E.sim_exit[2][i]}
		self.stripPos    = E.sim_stripPos[i]
		self.wirePos     = E.sim_wirePos[i]
		self.globalPos   = {'x' : E.sim_globalPos[0][i], 'y' : E.sim_globalPos[1][i], 'z' : E.sim_globalPos[2][i]}
		self.pabsEntry   = E.sim_entry_pabs[i]
		self.pEntry      = {'x' : E.sim_entry_p[0][i], 'y' : E.sim_entry_p[1][i], 'z' : E.sim_entry_p[2][i]}

class LCT():
	def __init__(self, E, i):
		self.cham         = E.lct_cham[i]
		self.pattern      = E.lct_pattern[i]
		self.keyHalfStrip = E.lct_keyHalfStrip[i]
		self.keyWireGroup = E.lct_keyWireGroup[i]

class Segment():
	def __init__(self, E, i):
		self.cham      = E.seg_cham[i]
		self.nHits     = E.seg_nHits[i]
		self.chisq     = E.seg_chisq[i]
		self.dof       = E.seg_dof[i]
		self.rhID      = [E.seg_rhID1[i], E.seg_rhID2[i], E.seg_rhID3[i], E.seg_rhID4[i], E.seg_rhID5[i], E.seg_rhID6[i]][0:self.nHits]

		self.primSlope          = {layer + 1 : {'x' : slp[0], 'y' : slp[1], 'z' : slp[2] } for layer, slp in enumerate(E.seg_slope_prim[i])}
		self.pos                = {layer + 1 : {'x' : pos[0], 'y' : pos[1], 'z' : pos[2] } for layer, pos in enumerate(E.seg_pos[i])       }
		self.strip              = {layer + 1 : pos[3]                                      for layer, pos in enumerate(E.seg_pos[i])       }
		self.wireGroup          = {layer + 1 : pos[4]                                      for layer, pos in enumerate(E.seg_pos[i])       }

		c = CH.Chamber(self.cham)
		self.isStaggered = (not (c.station == 1 and c.ring == 1))

		self.halfStrip          = {layer : 2 * self.strip[layer]                                             for layer in self.strip.keys()}
		self.staggeredStrip     = {layer : self.strip[layer]     - 0.5 * self.isStaggered * (layer % 2 == 0) for layer in self.strip.keys()}
		self.staggeredHalfStrip = {layer : self.halfStrip[layer] - 1.0 * self.isStaggered * (layer % 2 == 0) for layer in self.strip.keys()}

		self.slope = {'x' : E.seg_slope[i][0], 'y' : E.seg_slope[i][1], 'z' : E.seg_slope[i][2]}

class CLCT():
	def __init__(self, E, i):
		self.cham      = E.clct_cham[i]
		self.quality   = E.clct_quality[i]
		self.halfStrip = E.clct_halfStrip[i]
		self.CFEB      = E.clct_CFEB[i]
		self.keyStrip  = E.clct_keyStrip[i]
		self.pattern   = E.clct_pattern[i]

		self.keyHalfStrip = self.keyStrip if self.cham == 1 else self.CFEB*32 + self.halfStrip
