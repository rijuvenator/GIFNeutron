# For finding most common particle ID in cluster
from collections import Counter
from math import atan2

# SimHit Cluster Class
class simHitCluster():
	def __init__(self, groupOfSimHits):
		# public
		self.matchedComps = []
		self.matchedWires = []
		# private
		self._groupOfSimHits = groupOfSimHits
		self._strips = self._setStrips()
		self._wires = self._setWires()
		self._energy = self._setEnergy()
		self._mult = self._setMult()
		self._layer = self._setLayer()
		self._idlist = [simhit.particleID for simhit in self._groupOfSimHits]
		self._ID = self._setID()
		self._extraIDs = self._setExtraIDs()
		self._deltaZ = self._setDeltaZ()
	
	# print cluster
	def __repr__(self):
		string =  '''
				Number of SimHits in Cluster    : %s
				Energy of Cluster               : %s GeV
				local pos (x,y,layer)           : %s
				local pos (strip,wire,layer)    : %s
				global pos (x,y,z)              : %s
				global pos (r,phi,z)            : %s
				size (strip,wire)               : (%s,%s)
				strips                          : %s
				wires                           : %s
				size (x,y)                      : (%s,%s)
				Particles IDs Multiplicity      : %s
				Delta Z of SimHits in Cluster   : %s
				'''
		string = string.lstrip('\n')
		string = string.replace('\t','')
		return string % (\
				self._mult,
				self._energy,
				self._getPos(coordinates='local',units='xyz'),
				self._getPos(coordinates='local',units='prim'),
				self._getPos(coordinates='global',units='xyz'),
				self._getPos(coordinates='global',units='rphiz'),
				self._setWidth(units='strip'),self._setWidth(units='wire'),
				list(set(self._strips)), list(set(self._wires)),
				self._setWidth(units='x'),self._setWidth(units='y'),
				Counter(self._idlist).most_common(),
				self._deltaZ
				)

	# Public members
	@property
	def simhits(self):
		'''Return list of clustered simhits'''
		return self._groupOfSimHits
	@property
	def wires(self):
		'''Returns list of occupied wire groups'''
		return self._wires
	@property
	def strips(self):
		'''Returns list of occupied strips'''
		return self._strips
	@property
	def energy(self):
		'''Returns sum of simhit cluster energy [GeV]'''
		return self._energy
	@property
	def mult(self):
		'''Returns number of simhits in cluster'''
		return self._mult
	@property
	def ID(self):
		'''Returns most common particle ID in cluster'''
		return self._ID
	@property
	def nID(self):
		'''Returns number of unique particle IDs in cluster'''
		return len(list(set(self._idlist)))
	@property
	def extraIDlist(self):
		'''Returns list of extra particle IDs in cluster'''
		return self._extraIDs
	@property
	def layer(self):
		'''Returns layer of cluster'''
		return self._layer
	@property
	def deltaZ(self):
		'''Returns list of entry-exit z positions'''
		return self._deltaZ

	# Public methods
	def width(self,units='strip'):
		'''Returns width/height of cluster in strip/wire units or cm'''
		return self._setWidth(units)
	def pos(self,coordinates='local',units='prim'):
		'''Returns list [x/strip/r,y/wire/phi,layer/z]'''
		return self._getPos(coordinates,units)
	def matchWire(self,wire):
		'''Returns True if wire group is within cluster, False otherwise'''
		wirePos = wire.number
		if  wirePos >= self._wires[0]-1 and \
			wirePos <= self._wires[-1]+1:
			return True
		else:
			return False
	def matchComp(self,comp):
		'''Returns True if comparator is within cluster, False otherwise'''
		compPos = comp.halfStrip/2.
		if  compPos >= self._strips[0]-0.5 and \
			compPos <= self._strips[-1]+1.5:
			return True
		else:
			return False
			
	# Private set methods
	def _setWires(self):
		'''Set list of wire groups in cluster'''
		wires = []
		for simhit in self._groupOfSimHits:
			wires.append(simhit.wirePos)
		return wires
	def _setStrips(self):
		'''Set list of strips in cluster'''
		strips = []
		for simhit in self._groupOfSimHits:
			strips.append(int(simhit.stripPos))
		return strips
	def _setEnergy(self):
		'''Set energy of cluser'''
		energy = 0
		for simhit in self._groupOfSimHits:
			energy += simhit.energyLoss
		return energy
	def _setMult(self):
		'''Set multiplicity of simhits in cluster'''
		return len(self._groupOfSimHits)
	def _setLayer(self):
		'''Set layer of cluster'''
		layerlist = []
		for simhit in self._groupOfSimHits:
			layerlist.append(simhit.layer)
		if len(list(set(layerlist)))>1:
			pass
			#print 'Multiple layers of simhits in cluster'
			#print layerlist
			#exit()
		else:
			return list(set(layerlist))[0]
	def _setID(self):
		'''Set particle ID of cluster as particle ID mode'''
		abslist = [abs(e) for e in self._idlist]
		if len(list(set(abslist)))>1:
			#print 'Multiple particle types in cluster'
			#print abslist
			count = Counter(abslist)
			if count.most_common()[0][0]==11:
				if count[11]==count[13]:
					return 13
				else:
					return count.most_common()[0][0]
			else:
				return count.most_common()[0][0]
		else:
			return list(set(abslist))[0]
	def _setExtraIDs(self):
		'''Set list of extra particle IDs in cluster'''
		count = Counter([abs(idx) for idx in self._idlist])
		if count.most_common()[0][0]==11:
			if count[11]==count[13]:
				return list(set([abs(idx) for idx in self._idlist])).remove(13)
			else:
				return [extra[0] for extra in count.most_common()[1:]]
		else:
			return [extra[0] for extra in count.most_common()[1:]]
	def _setWidth(self,units):
		'''Set witdth of cluster in given units'''
		if len(self._groupOfSimHits)==1: return 0
		if units=='strip':
			return abs(self._groupOfSimHits[0].stripPos - self._groupOfSimHits[-1].stripPos)
		elif units=='x':
			return abs(self._groupOfSimHits[0].pos['x'] - self._groupOfSimHits[-1].pos['x'])
		elif units=='wire':
			return abs(self._groupOfSimHits[0].wirePos - self._groupOfSimHits[-1].wirePos)
		elif units=='y':
			return abs(self._groupOfSimHits[0].pos['y'] - self._groupOfSimHits[-1].pos['y'])
		else:
			print 'Not a correct unit in simHitCluster.width(\'unit\')!'
			exit()
	def _setDeltaZ(self):
		'''Set list of entry-exit z positions of simhits in cluster'''
		return [sh.entryPos['z']-sh.exitPos['z'] for sh in self._groupOfSimHits]
	
	# Private get methods
	def _getPos(self,coordinates,units):
		'''Get position list [x/strip/r,y/wire/phi,layer/z]'''
		if coordinates=='local':
			if units=='prim':
				strip = sum(self._strips)/len(self._strips)
				wire = sum(self._wires)/len(self._wires)
				return [strip,wire,self._layer]
			elif units=='xyz':
				xlist = [sh.pos['x'] for sh in self._groupOfSimHits]
				x = sum(xlist)/len(xlist)
				ylist = [sh.pos['y'] for sh in self._groupOfSimHits]
				y = sum(ylist)/len(ylist)
				return [x,y,self._layer]
			else:
				print 'Units must be \'prim\' or \'xyz\' for local coordinates'
				exit()
		elif coordinates=='global':
			if units=='xyz':
				xlist = [sh.globalPos['x'] for sh in self._groupOfSimHits]
				x = sum(xlist)/len(xlist)
				ylist = [sh.globalPos['y'] for sh in self._groupOfSimHits]
				y = sum(ylist)/len(ylist)
				return [x,y,self._layer]
			elif units=='rphiz':
				'''
				r = sqrt(x**2 + y**2), distance from beamline
				phi = angle w.r.t. +x axis
				z = distance from IP
				'''
				rlist = [(sh.globalPos['x']**2 + sh.globalPos['y']**2)**0.5 for sh in self._groupOfSimHits]
				r = sum(rlist)/len(rlist)
				# atan2(y,x) is aware of x,y signs and can correctly determine the x,y quadrant
				philist = [atan2(sh.globalPos['y'],sh.globalPos['x']) for sh in self._groupOfSimHits]
				phi = sum(philist)/len(philist)
				z = self._groupOfSimHits[0].globalPos['z']
				return [r,phi,z]
			else:
				print 'Units must be \'xyz\' or \'rphiz\' for global coordinates'
				exit()
		else:
			print 'Coordinates must local or global'
			exit()



def findSimHitClusters(simhits,cham,removeDeltaZ=False):
	'''Input a list of simhits in an event and a chamber ID
	Return clusters of simhits in a dictionary for each layer'''
	simhitClusters = {layer:[] for layer in [1,2,3,4,5,6]}
	simhitLayers = {layer:[] for layer in [1,2,3,4,5,6]}
	for layer in [1,2,3,4,5,6]:
		for simhit in simhits:
			if simhit.cham!=cham: continue
			if simhit.layer!=layer: continue
			# Make dict of simhits by layer
			if removeDeltaZ:
				# Skip simhit if delta Z is too small
				if abs(simhit.entryPos['z']-simhit.exitPos['z']) < 0.1:
					continue
				else:
					simhitLayers[layer].append(simhit)
			else:
				simhitLayers[layer].append(simhit)
		# Skip layer if no simhits
		if len(simhitLayers[layer])==0: continue
		# Sort simhits in ascending strip position
		simhitLayers[layer] = sorted(simhitLayers[layer], key=lambda simhit: simhit.stripPos)
		# Make strip difference list (initialized to two so that the first simhit starts a new group)
		diffList = [2] + [int(simhitLayers[layer][idx].stripPos) - int(simhitLayers[layer][idx-1].stripPos) for idx in range(1,len(simhitLayers[layer]))]
		# Group simhits by contiguous strip numbers
		groupOfSimHits = []
		for idx,diff in enumerate(diffList):
			if diff >= 2 and idx!=0:
				cluster = simHitCluster(groupOfSimHits)
				simhitClusters[layer].append(cluster)
				groupOfSimHits = []
			groupOfSimHits.append(simhitLayers[layer][idx])
		# Make the last cluster
		cluster = simHitCluster(groupOfSimHits)
		simhitClusters[layer].append(cluster)
	return simhitClusters
