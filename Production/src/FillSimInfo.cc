#include "Gif/Production/interface/FillSimInfo.h"

void FillSimHitInfo::fill(const CSCGeometry * theCSC, const edm::PSimHitContainer& simHits)
{
	reset();

	for (edm::PSimHitContainer::const_iterator hiti=simHits.begin(); hiti!=simHits.end(); hiti++)
	{
		CSCDetId simID = hiti->detUnitId();
		sim_id.push_back(GIFHelper::chamberSerial(simID));
		sim_particle_id.push_back(hiti->particleType());
		sim_process_type.push_back(hiti->processType());
		sim_lay.push_back(GIFHelper::convertTo<size8>(simID.layer(),"sim_lay"));
		sim_pos_x.push_back(hiti->localPosition().x());
		sim_pos_y.push_back(hiti->localPosition().y());
		sim_pos_z.push_back(hiti->localPosition().z());
		sim_tof.push_back(hiti->timeOfFlight());
		sim_energyLoss.push_back(hiti->energyLoss());
		sim_entry_x.push_back(hiti->entryPoint().x());
		sim_entry_y.push_back(hiti->entryPoint().y());
		sim_entry_z.push_back(hiti->entryPoint().z());
		sim_exit_x.push_back(hiti->exitPoint().x());
		sim_exit_y.push_back(hiti->exitPoint().y());
		sim_exit_z.push_back(hiti->exitPoint().z());
		sim_entry_pabs.push_back(hiti->pabs());
		sim_entry_px.push_back(hiti->momentumAtEntry().x());
		sim_entry_py.push_back(hiti->momentumAtEntry().y());
		sim_entry_pz.push_back(hiti->momentumAtEntry().z());
		sim_track_id.push_back(hiti->trackId());

		CSCDetId chamberId(simID);
		const CSCChamber *simChamber = theCSC->chamber(chamberId);
		const CSCLayer *simLay = simChamber->layer(simID.layer());
		const CSCLayerGeometry *simLayGeo = simLay->geometry();
		GlobalPoint simGlobalPoint = simChamber->toGlobal(hiti->localPosition());
		sim_pos_glb_x.push_back(simGlobalPoint.x());
		sim_pos_glb_y.push_back(simGlobalPoint.y());
		sim_pos_glb_z.push_back(simGlobalPoint.z());
		LocalPoint simLP = simLay->toLocal(simGlobalPoint);
		float simStrip = simLayGeo->strip(simLP);
		float simWire = simLayGeo->wireGroup(simLayGeo->nearestWire(simLP));
		float simWireF = simWire + (simLayGeo->nearestWire(simLP) - simLayGeo->middleWireOfGroup(simWire))/(simLayGeo->numberOfWiresPerGroup(simWire)) + 0.5;
		sim_pos_strip.push_back(simStrip);
		sim_pos_wire.push_back(simWireF);
	}
}

