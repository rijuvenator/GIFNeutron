# For finding most common particle ID in cluster
from collections import Counter
from math import atan

# SimHit Cluster Class
class simHitCluster():
	def __init__(self, groupOfSimHits):
		self.groupOfSimHits = groupOfSimHits
		self.matchedComps = []
		self.matchedWires = []
		self._strips = self._getStrips()
		self._wires = self._getWires()
		self._energy = self._getEnergy()
		self._mult = self._getMult()
		self._layer = self._getLayer()
		self._idlist = [simhit.particleID for simhit in self.groupOfSimHits]
		self._ID = self._getID()
		self._extraIDs = self._getExtraIDs()
	
	def __repr__(self):
		string =  '''
				Number of SimHits in Cluster    : %s
				Energy of Cluster               : %s GeV
				local pos (x,y,layer)           : %s
				local pos (strip,wire,layer)    : %s
				global pos (x,y,z)              : %s
				global pos (r,phi,z)            : %s
				size (strip,wire)               : (%s,%s)
				size (x,y)                      : (%s,%s)
				Particles IDs Multiplicity      : %s
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
				self._getWidth(units='strip'),self._getWidth(units='wire'),
				self._getWidth(units='x'),self._getWidth(units='y'),
				Counter(self._idlist).most_common()
				)


	# public
	def wires(self):
		return self._wires
	def strips(self):
		return self._strips
	def energy(self):
		return self._energy
	def mult(self):
		return self._mult
	def width(self,units='strip'):
		return self._getWidth(self,units)
	def ID(self):
		return self._ID
	def nID(self):
		return len(list(set(self._idlist)))
	def extraIDlist(self):
		return self._extraIDs
	def layer(self):
		return self._layer
	def pos(self,coordinates='local',units='prim'):
		return self._getPos(self,coordinates,units)
	def matchWire(self,wire):
		wirePos = wire.number
		if  wirePos >= self._wires[0]-1 and \
			wirePos <= self._wires[-1]+1:
			return True
		else:
			return False
	def matchComp(self,comp):
		compPos = comp.halfStrip/2.
		if  compPos >= self._strips[0]-0.5 and \
			compPos <= self._strips[-1]+1.5:
			return True
		else:
			return False
			
	# private
	def _getWires(self):
		wires = []
		for simhit in self.groupOfSimHits:
			wires.append(simhit.wirePos)
		return wires
	def _getStrips(self):
		strips = []
		for simhit in self.groupOfSimHits:
			strips.append(int(simhit.stripPos))
		return strips
	def _getEnergy(self):
		energy = 0
		for simhit in self.groupOfSimHits:
			energy += simhit.energyLoss
		return energy
	def _getMult(self):
		return len(self.groupOfSimHits)
	def _getLayer(self):
		layerlist = []
		for simhit in self.groupOfSimHits:
			layerlist.append(simhit.layer)
		if len(list(set(layerlist)))>1:
			pass
			#print 'Multiple layers of simhits in cluster'
			#print layerlist
			#exit()
		else:
			return list(set(layerlist))[0]
	def _getID(self):
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
	def _getExtraIDs(self):
		count = Counter([abs(idx) for idx in self._idlist])
		if count.most_common()[0][0]==11:
			if count[11]==count[13]:
				return list(set([abs(idx) for idx in self._idlist])).remove(13)
			else:
				return [extra[0] for extra in count.most_common()[1:]]
		else:
			return [extra[0] for extra in count.most_common()[1:]]
	def _getWidth(self,units):
		if len(self.groupOfSimHits)==1: return 0
		if units=='strip':
			return abs(self.groupOfSimHits[0].stripPos - self.groupOfSimHits[-1].stripPos)
		elif units=='x':
			return abs(self.groupOfSimHits[0].pos['x'] - self.groupOfSimHits[-1].pos['x'])
		elif units=='wire':
			return abs(self.groupOfSimHits[0].wirePos - self.groupOfSimHits[-1].wirePos)
		elif units=='y':
			return abs(self.groupOfSimHits[0].pos['y'] - self.groupOfSimHits[-1].pos['y'])
		else:
			print 'Not a correct unit in simHitCluster.width(\'unit\')!'
			exit()
	def _getPos(self,coordinates,units):
		if coordinates=='local':
			if units=='prim':
				strip = sum(self._strips)/len(self._strips)
				wire = sum(self._wires)/len(self._wires)
				return [strip,wire,self._layer]
			elif units=='xyz':
				xlist = [sh.pos['x'] for sh in self.groupOfSimHits]
				x = sum(xlist)/len(xlist)
				ylist = [sh.pos['y'] for sh in self.groupOfSimHits]
				y = sum(ylist)/len(ylist)
				return [x,y,self._layer]
			else:
				print 'Units must be \'prim\' or \'xyz\' for local coordinates'
				exit()
		elif coordinates=='global':
			if units=='xyz':
				xlist = [sh.globalPos['x'] for sh in self.groupOfSimHits]
				x = sum(xlist)/len(xlist)
				ylist = [sh.globalPos['y'] for sh in self.groupOfSimHits]
				y = sum(ylist)/len(ylist)
				return [x,y,self._layer]
			elif units=='rphiz':
				rlist = [(sh.globalPos['x']**2 + sh.globalPos['y']**2)**0.5 for sh in self.groupOfSimHits]
				r = sum(rlist)/len(rlist)
				philist = [atan(sh.globalPos['y']/sh.globalPos['x']) for sh in self.groupOfSimHits]
				phi = sum(philist)/len(philist)
				z = self.groupOfSimHits[0].globalPos['z']
				return [r,phi,z]
			else:
				print 'Units must be \'xyz\' or \'rphiz\' for global coordinates'
				exit()
		else:
			print 'Coordinates must local or global'
			exit()



def findSimHitClusters(simhits,cham):

	simhitClusters = {layer:[] for layer in [1,2,3,4,5,6]}
	simhitLayers = {layer:[] for layer in [1,2,3,4,5,6]}
	for layer in [1,2,3,4,5,6]:
		for simhit in simhits:
			# Make dict of simhits by layer
			if simhit.cham!=cham: continue
			if simhit.layer!=layer: continue
			simhitLayers[layer].append(simhit)
		# Skip layer if no simhits
		if len(simhitLayers[layer])==0: continue
		# Sort dict by strip position
		simhitLayers[layer] = sorted(simhitLayers[layer], key=lambda simhit: simhit.stripPos)
		# Make strip difference list (initialized to two so that the first
		# simhit gets a blank cluster
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
