#include "Gif/NeutronSim/interface/FillSimInfo.h"

void FillSimHitInfo::fill(const CSCGeometry * theCSC, const edm::PSimHitContainer& simHits)
{
	reset();

	for (edm::PSimHitContainer::const_iterator hiti=simHits.begin(); hiti!=simHits.end(); hiti++)
	{
		CSCDetId simID = hiti->detUnitId();
		sim_id.push_back(GIFHelper::chamberSerial(simID));
		sim_particle_id.push_back(hiti->particleType());
		sim_lay.push_back(GIFHelper::convertTo<size8>(simID.layer(),"sim_lay"));
		sim_pos_x.push_back(hiti->localPosition().x());
		sim_pos_y.push_back(hiti->localPosition().y());
		sim_tof.push_back(hiti->timeOfFlight());
		sim_energyLoss.push_back(hiti->energyLoss());
		sim_entry_x.push_back(hiti->entryPoint().x());
		sim_entry_y.push_back(hiti->entryPoint().y());
		sim_exit_x.push_back(hiti->exitPoint().x());
		sim_exit_y.push_back(hiti->exitPoint().y());

		CSCDetId chamberId(simID);
		const CSCChamber *simChamber = theCSC->chamber(chamberId);
		const CSCLayer *simLay = simChamber->layer(simID.layer());
		const CSCLayerGeometry *simLayGeo = simLay->geometry();
		LocalPoint simLP = simLay->toLocal(simChamber->toGlobal(hiti->localPosition()));
		float simStrip = simLayGeo->strip(simLP);
		float simWire = simLayGeo->wireGroup(simLayGeo->nearestWire(simLP));
		float simWireF = simWire + (simLayGeo->nearestWire(simLP) - simLayGeo->middleWireOfGroup(simWire))/(simLayGeo->numberOfWiresPerGroup(simWire)) + 0.5;
		sim_pos_strip.push_back(simStrip);
		sim_pos_wire.push_back(simWireF);
	}
}

