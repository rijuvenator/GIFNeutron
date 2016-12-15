SCINT = {1:{'HS':(25,72),'WG':(37,43)},110:{'HS':(8,38),'WG':(55,65)}}

# defines a paddle region
def inPad(hs, wg, CHAM):
	if      hs >= SCINT[CHAM]['HS'][0]\
		and hs <= SCINT[CHAM]['HS'][1]\
		and wg >= SCINT[CHAM]['WG'][0]\
		and wg <= SCINT[CHAM]['WG'][1]:
		return True
	else:
		return False

# determines if a segment and an lct match each other
def matchSegLCT(seg, lct, layer=3, thresh=(2, 1)):
	if abs(seg.halfStrip[layer] - lct.keyHalfStrip) <= thresh[0] and abs(seg.wireGroup[layer] - lct.keyWireGroup) <= thresh[1]:
		return True
	else:
		return False
