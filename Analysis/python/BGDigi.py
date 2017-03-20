import itertools
import ROOT as R
import Gif.Analysis.ChamberHandler as CH
import Gif.Analysis.Primitives as Primitives

def getBGCompCandList(lcts, comps):
	''' Find and return opposite-half background comparators

		Input  : Full lists of lcts and comparators
		Return : Lists of isolated lcts and candidate background comparators

		The function finds lcts that are isolated (meaning in a corner 1/16th of a
		chamber and looks for comparator hits in the opposite half of the chamber 
		(ME1/1 handled specially). No cut on comparator time is made at this step.
	'''
	bgComps = []
	bgLCTs  = []

	#twolcts = list(set([i for i in E.lct_cham if E.lct_cham.count(i)>1]))
	lctchams = [lct.cham for lct in lcts]
	twolcts = list(set([cham for cham in lctchams if lctchams.count(cham)>1]))
	for lct in lcts:
		if lct.cham in twolcts: continue
		cham = CH.Chamber(lct.cham)
		nHS = cham.nstrips*2
		nWG = cham.nwires
		if cham.station==1 and cham.ring==1:
			# ME1/1a and ME1/1b are separated by a cut in the strips.
			# Since wires are tilted use the a/b divider as a crude radial cut
			# on LCT position instead of wires.
			# ME1/1b : strips  1 to  64 (top)    | hs   0 to 127 (top)
			# ME1/1a : strips 65 to 112 (bottom) | hs 128 to 224 (bottom)
			# (remember strips are numbered from 1 while hs are numbered from 0!)
			#
			# For ME1/1 the +/- endcaps are 'flipped' wrt each other
			# (+:bl) is (-:br) and vice versa
			# (+:tl) is (-:tr) and vice versa
			# Does not actually matter for what we are doing but important to keep in mind!
			#
			# -> LCTAreas are defined for ME+1/1
			# ME+1/1b - tl : (  0, 31) , tr : ( 95,127) (hs are numbered R to L - top)
			# ME+1/1a - bl : (200,224) , br : (128,152) (hs are numbered L to R - bottom)
			#
			# For opposite area, the set of opposite half halfstrips are disjoint for LCT 
			# tr and bl areas
			#
			# -> OppAreas are defined for ME+1/1
			#             (top) + (bottom)
			# bl,tl : (64, 127) + (128, 171)
			# tr,br : ( 0,  63) + (172, 223)
			LCTAreas = \
			{
				'bl' : {'wg0' : 0. , 'wg1' : nWG , 'hs0' : 200. , 'hs1' : 223},
				'tl' : {'wg0' : 0. , 'wg1' : nWG , 'hs0' : 0.   , 'hs1' : 31 },
				'tr' : {'wg0' : 0. , 'wg1' : nWG , 'hs0' : 96   , 'hs1' : 127},
				'br' : {'wg0' : 0. , 'wg1' : nWG , 'hs0' : 128  , 'hs1' : 151},
			}
			OppAreas = \
			{
				'bl' : {'hs0' : 64 , 'hs1' : 127 , 'hs2' : 128 , 'hs3' : 171},
				'tl' : {'hs0' : 64 , 'hs1' : 127 , 'hs2' : 128 , 'hs3' : 171},
				'tr' : {'hs0' :  0 , 'hs1' :  63 , 'hs2' : 172 , 'hs3' : 223},
				'br' : {'hs0' :  0 , 'hs1' :  63 , 'hs2' : 172 , 'hs3' : 223},
			}
		else:
			LCTAreas = \
			{
				'bl' : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : 0.          , 'hs1' : nHS*0.25},
				'tl' : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : 0.          , 'hs1' : nHS*0.25},
				'tr' : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
				'br' : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
			}
			OppAreas = \
			{
				'bl' : {'hs0' : (1-0.50)*nHS, 'hs1' : nHS     },
				'tl' : {'hs0' : (1-0.50)*nHS, 'hs1' : nHS     },
				'tr' : {'hs0' : 0.          , 'hs1' : nHS*0.50},
				'br' : {'hs0' : 0.          , 'hs1' : nHS*0.50},
			}
		# Loop on all areas (we've already forced there to be only one LCT in this chamber)
		for key in LCTAreas.keys():
			# If LCT in a corner
			if  lct.keyWireGroup >= LCTAreas[key]['wg0'] and lct.keyWireGroup <= LCTAreas[key]['wg1']\
			and lct.keyHalfStrip >= LCTAreas[key]['hs0'] and lct.keyHalfStrip <= LCTAreas[key]['hs1']:
				bgLCTs.append(lct)
				for comp in comps:
					if comp.cham != lct.cham: continue
					# For comparators in opposite half of LCT
					OPPAREA = False
					if cham.station==1 and cham.ring==1:
						if ((comp.staggeredHalfStrip >= OppAreas[key]['hs0'] and comp.staggeredHalfStrip <= OppAreas[key]['hs1'])\
								or \
							(comp.staggeredHalfStrip >= OppAreas[key]['hs2'] and comp.staggeredHalfStrip <= OppAreas[key]['hs3'])):
							OPPAREA = True
					else:
						if comp.staggeredHalfStrip >= OppAreas[key]['hs0'] and comp.staggeredHalfStrip <= OppAreas[key]['hs1']:
							OPPAREA = True
					if OPPAREA:
						bgComps.append(comp)

	return bgLCTs, bgComps


def getBGWireCandList(lcts, wires):
	''' Find and return opposite-half background wire group hits

		Input  : Full lists of lcts and wire group hits
		Return : List of tuples of LCT and which opposite half wire group
				 histogram to fill.
				 List of opposite half wiregroup hits

		The function finds lcts that are isolated (meaning in a corner 1/16th of a
		chamber and looks for wire group hits in the opposite half of the chamber 
		(ME1/1 handled specially). No cut on wire group time is made at this step.
	'''
	bgWires = []
	bgLCTs  = []

	#twolcts = list(set([i for i in E.lct_cham if E.lct_cham.count(i)>1]))
	lctchams = [lct.cham for lct in lcts]
	twolcts = list(set([cham for cham in lctchams if lctchams.count(cham)>1]))
	for lct in lcts:
		if lct.cham in twolcts: continue
		nWire = 0
		cham = CH.Chamber(lct.cham)
		nHS = cham.nstrips*2
		nWG = cham.nwires
		if cham.station==1 and cham.ring==1:
			# ME1/1 has wires tilted at 29 degrees wrt local +x axis
			# Instead of requiring that the LCT is in a "corner", for 
			# ME1/1 we use "bottom" and "top" parts to look for an LCT
			# "Bottom" is defined as  1 <= kwg <= 12 (bl,br)
			# "Top"    is defined as 37 <= kwg <= 48 (tl,tr)
			# (Only defined differently because in ME1/1 we don't 
			#  make any requirement on the HS of the LCT)
			LCTAreas = \
			{
				'bl' : {'wg0' :  1. , 'wg1' : 12. , 'hs0' : 0. , 'hs1' : nHS},
				'tl' : {'wg0' : 37. , 'wg1' : 48. , 'hs0' : 0. , 'hs1' : nHS},
				'tr' : {'wg0' : 37. , 'wg1' : 48. , 'hs0' : 0. , 'hs1' : nHS},
				'br' : {'wg0' :  1. , 'wg1' : 12. , 'hs0' : 0. , 'hs1' : nHS},
			}
			# ME1/1 opposite areas are the other "half"
			# keys correspond to LCT location
			# "Bottom" LCTs -> Look for wgs in 25 <= wg <= 48 (0,3)
			#    "Top" LCTs -> Look for wgs in  1 <= wg <= 24 (1,2)
			# (Same for all other chambers but defined explicitly for ME1/1)
			OppAreas = \
			{
				'bl' : {'wg0' :  25 , 'wg1' : 48 },
				'tl' : {'wg0' :   1 , 'wg1' : 24 },
				'tr' : {'wg0' :   1 , 'wg1' : 24 },
				'br' : {'wg0' :  25 , 'wg1' : 48 },
			}
		else:
			LCTAreas = \
			{
				'bl' : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : 0.          , 'hs1' : nHS*0.25},
				'tl' : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : 0.          , 'hs1' : nHS*0.25},
				'tr' : {'wg0' : (1-0.25)*nWG, 'wg1' : nWG     , 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
				'br' : {'wg0' : 0.          , 'wg1' : nWG*0.25, 'hs0' : (1-0.25)*nHS, 'hs1' : nHS     },
			}
			OppAreas = \
			{
				'bl' : {'wg0' : (1-0.50)*nWG, 'wg1' : nWG     },
				'tl' : {'wg0' : 0.          , 'wg1' : nWG*0.50},
				'tr' : {'wg0' : 0.          , 'wg1' : nWG*0.50},
				'br' : {'wg0' : (1-0.50)*nWG, 'wg1' : nWG     },
			}
		for key in LCTAreas.keys():
			if  lct.keyWireGroup >= LCTAreas[key]['wg0'] and lct.keyWireGroup <= LCTAreas[key]['wg1']\
			and lct.keyHalfStrip >= LCTAreas[key]['hs0'] and lct.keyHalfStrip <= LCTAreas[key]['hs1']:
				for wire in wires:
					if wire.cham != lct.cham: continue
					if wire.number >= OppAreas[key]['wg0'] and wire.number <= OppAreas[key]['wg1']:
						if key[0]=='b': # Fill upper bg wire group list
							bgLCTs.append((lct,'u'))
							bgWires.append(wire)
						if key[0]=='t': # Fill lower bg wire group list
							bgLCTs.append((lct,'l'))
							bgWires.append(wire)
	
	return bgLCTs,bgWires

def removeDigiRoads(digis):
	''' Find background digi tracks with a road method
		
		Input  : List of background digis (chamber lists are obtained from the digis 
				 instead of from a list of LCTs, so that it can be applied to MC)
		Output : List of chambers with a background track found with a road method
				 (optional output is the list of background digis with 
				 track-candidate digis removed)

		The function finds tracks of digis with the road-method. Default 
		requirements on the road is a width parameter of +/- 3 digis and a length
		4 layers.
	
	'''
	minRoadLength = 4 # minimum 4 layers in a road
	roadWidth     = 3 # size away from central road hs

	# Allows road finder to operate on a generic "digi": either a Wire or a Comp
	# Also, handle an empty digi list, since there is an explicit index
	try:
		location = 'number' if type(digis[0]) == Primitives.Wire else 'staggeredHalfStrip'
	except IndexError:
		return []

	# return value
	roadchams = []
	# lambda returning chamber ID for use in the groupby and sort
	chamID = lambda digi: digi.cham
	# lambda returning number of layers in road (to be compared to minRoadLength)
	roadLength = lambda road: len(set([digi.layer for digi in road]))

	# groupby gives a tuple (cham, generator of digis); the sort function is chamID
	for cham, digisGen in itertools.groupby(sorted(digis, key=chamID), key=chamID):
		digisCham = list(digisGen)
		# Explicitly filling the BGDigiList dictionary is better here
		BGDigiList = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[]}
		for digi in digisCham:
			BGDigiList[digi.layer].append(digi)

		roads = []
		# Loop through outer layers
		for beginLayer, endLayer in [(1,6),(1,5),(2,6),(1,4),(2,5),(3,6)]:
			# Calculate hs difference between comparators in outer layer and inner layer
			layerDiff = endLayer - beginLayer
			for beginDigi in BGDigiList[beginLayer]:
				for endDigi in BGDigiList[endLayer]:
					# Make road and count comparators
					road = []
					locDiff = getattr(endDigi,location) - getattr(beginDigi,location)
					road.append(beginDigi)
					for interLayer in range(beginLayer+1, endLayer):
						interLoc = (float(locDiff)/layerDiff)*(interLayer-beginLayer) + getattr(beginDigi,location)
						for d in BGDigiList[layer]:
							if getattr(d,location) >= interLoc-roadWidth and getattr(d,location) <= interLoc+roadWidth:
								road.append(d)
					road.append(endDigi)

					if roadLength(road) < minRoadLength: continue
					roads.append(road)

		if roads != []:
			roadchams.append(cham)

	return roadchams

# Old code
		# Remove comparators from background comp list if they're in a road
		#roads.sort(key=sortFunc,reverse=True)
		#for road in roads:
		#   allCompsInBkg = True
		#   for comp in road:
		#	   if comp not in BGCompList[comp.layer]:
		#		   allCompsInBkg = False
		#		   break
		#   if allCompsInBkg:
		#	   for comp in road:
		#		   #print idx, comp.cham, comp.layer, comp.staggeredHalfStrip, comp.timeBin
		#		   BGCompList[comp.layer].remove(comp)
		#		   comps.remove(comp)


