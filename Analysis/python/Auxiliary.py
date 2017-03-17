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
def matchSegLCT(seg, lct, layer=3, thresh=(2, 1), old=True):
	if old:
		if abs(seg.halfStrip[layer] - lct.keyHalfStrip) <= thresh[0] and abs(seg.wireGroup[layer] - lct.keyWireGroup) <= thresh[1]:
			return True
		else:
			return False
	else:
		id_ = lct.pattern
		khs = lct.keyHalfStrip
		pat = {
			2  : {6:[khs-5, khs-4, khs-3], 5:[khs-4, khs-3, khs-2], 4:[khs-2, khs-1, khs], 3:[khs], 2:[khs+1, khs+2], 1:[khs+3, khs+4, khs+5]},
			3  : {1:[khs-5, khs-4, khs-3], 2:[khs-2, khs-1], 3:[khs], 4:[khs, khs+1, khs+2], 5:[khs+2, khs+3, khs+4], 6:[khs+3, khs+4, khs+5]},
			4  : {6:[khs-4, khs-3, khs-2], 5:[khs-4, khs-3, khs-2], 4:[khs-2, khs-1], 3:[khs], 2:[khs+1, khs+2], 1:[khs+2, khs+3, khs+4]},
			5  : {1:[khs-4, khs-3, khs-2], 2:[khs-2, khs-1], 3:[khs], 4:[khs+1, khs+2], 5:[khs+2, khs+3, khs+4], 6:[khs+2, khs+3, khs+4]},
			6  : {6:[khs-3, khs-2, khs-1], 5:[khs-2, khs-1], 4:[khs-1, khs], 3:[khs], 2:[khs, khs+1], 1:[khs+1, khs+2, khs+3]},
			7  : {1:[khs-3, khs-2, khs-1], 2:[khs-1, khs], 3:[khs], 4:[khs, khs+1], 5:[khs+1, khs+2], 6:[khs+1, khs+2, khs+3]},
			8  : {6:[khs-2, khs-1, khs], 5:[khs-2, khs-1, khs], 4:[khs-1, khs], 3:[khs], 2:[khs, khs+1], 1:[khs, khs+1, khs+2]},
			9  : {1:[khs-2, khs-1, khs], 2:[khs-1, khs], 3:[khs], 4:[khs, khs+1], 5:[khs, khs+1, khs+2], 6:[khs, khs+1, khs+2]},
			10 : {6:[khs-1, khs, khs+1], 5:[khs-1, khs, khs+1], 4:[khs], 3:[khs], 2:[khs], 1:[khs-1, khs, khs+1]}
		}

		layerHalfStripCount = 0
		for lay in range(1, 7):
			layerHalfStripCount += min(abs(seg.halfStrip[1] - x) for x in pat[id_][lay]) <= thresh[0]

		if layerHalfStripCount >= 3 and abs(seg.wireGroup[3] - lct.keyWireGroup) <= thresh[1]:
			return True
		else:
			return False

# determine if a comparator is within an LCT pattern
def inLCTPattern(lct,comp):
	id_ = lct.pattern
	# lct khs is 0 indexed, comp hs is 1 indexed
	khs = lct.keyHalfStrip+2

	#if comp.cham!=lct.cham: return False

	if id_ == 2:
		pat = {6:[khs-5, khs-4, khs-3], 5:[khs-4, khs-3, khs-2], 4:[khs-2, khs-1, khs], 3:[khs], 2:[khs+1, khs+2], 1:[khs+3, khs+4, khs+5]}
	elif id_ == 3:
		pat = {1:[khs-5, khs-4, khs-3], 2:[khs-2, khs-1], 3:[khs], 4:[khs, khs+1, khs+2], 5:[khs+2, khs+3, khs+4], 6:[khs+3, khs+4, khs+5]}
	elif id_ == 4:
		pat = {6:[khs-4, khs-3, khs-2], 5:[khs-4, khs-3, khs-2], 4:[khs-2, khs-1], 3:[khs], 2:[khs+1, khs+2], 1:[khs+2, khs+3, khs+4]}
	elif id_ == 5:
		pat = {1:[khs-4, khs-3, khs-2], 2:[khs-2, khs-1], 3:[khs], 4:[khs+1, khs+2], 5:[khs+2, khs+3, khs+4], 6:[khs+2, khs+3, khs+4]}
	elif id_ == 6:
		pat = {6:[khs-3, khs-2, khs-1], 5:[khs-2, khs-1], 4:[khs-1, khs], 3:[khs], 2:[khs, khs+1], 1:[khs+1, khs+2, khs+3]}
	elif id_ == 7:
		pat = {1:[khs-3, khs-2, khs-1], 2:[khs-1, khs], 3:[khs], 4:[khs, khs+1], 5:[khs+1, khs+2], 6:[khs+1, khs+2, khs+3]}
	elif id_ == 8:
		pat = {6:[khs-2, khs-1, khs], 5:[khs-2, khs-1, khs], 4:[khs-1, khs], 3:[khs], 2:[khs, khs+1], 1:[khs, khs+1, khs+2]}
	elif id_ == 9:
		pat = {1:[khs-2, khs-1, khs], 2:[khs-1, khs], 3:[khs], 4:[khs, khs+1], 5:[khs, khs+1, khs+2], 6:[khs, khs+1, khs+2]}
	elif id_ == 10:
		pat = {6:[khs-1, khs, khs+1], 5:[khs-1, khs, khs+1], 4:[khs], 3:[khs], 2:[khs], 1:[khs-1, khs, khs+1]}

	#print comp.layer, comp.halfStrip, pat[comp.layer], comp.cham
	if comp.staggeredHalfStrip in pat[comp.layer]:
		return True
	else:
		return False

# given an LCT and a list of Segments, find the "best" segment
def bestSeg(lct, segs):
	cham = lct.cham
	mostHits = 0
	found = False
	for seg in segs:
		if seg.cham != cham: continue
		if not matchSegLCT(seg, lct, thresh=(2., 2.,)): continue
		found = True
		if seg.nHits > mostHits:
			mostHits = seg.nHits
			matchedSegs = [seg]
		elif seg.nHits == mostHits:
			matchedSegs.append(seg)
	closestSeg = float('inf')
	if found:
		for mseg in matchedSegs:
			if abs(lct.keyHalfStrip-mseg.halfStrip[3]) < closestSeg:
				closestSeg = abs(lct.keyHalfStrip-mseg.halfStrip[3])
				seg = mseg
		return found, seg
	else:
		return found, None
