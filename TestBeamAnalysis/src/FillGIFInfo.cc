#include "Gif/TestBeamAnalysis/include/FillGIFInfo.h"
//#include "CSCUCLA/CSCDigiTuples/include/GIFHelper.h"
#include "Gif/TestBeamAnalysis/include/GIFHelper.h"

void FillGIFEventInfo::fill(const edm::Event& iEvent){
  reset();
  Event_EventNumber     = iEvent.id().event();
  Event_RunNumber       = iEvent.id().run();
  Event_LumiSection     = iEvent.eventAuxiliary().luminosityBlock();
  Event_BXCrossing      = iEvent.eventAuxiliary().bunchCrossing();
}


void FillGIFRecHitInfo::fill(const CSCRecHit2DCollection& recHits){
  reset();
  int nRHs = 0;
  for (CSCRecHit2DCollection::const_iterator hiti=recHits.begin(); hiti!=recHits.end(); hiti++)
  {
      nRHs++;
      DetId idd = (hiti)->geographicalId();
      CSCDetId hitID(idd.rawId());
      rh_id          .push_back(GIFHelper::chamberSerial(hitID));
      rh_lay         .push_back(GIFHelper::convertTo<size8>(hitID.layer(),"rh_lay"));
      rh_pos_x       .push_back(hiti->localPosition().x());
      rh_pos_y       .push_back(hiti->localPosition().y());
      rh_strip_1 .push_back(GIFHelper::convertTo<size8>(hiti->channels(0),"rh_strip_1"));
      rh_strip_2 .push_back(GIFHelper::convertTo<size8>(hiti->channels(1),"rh_strip_2"));
      rh_strip_3 .push_back(GIFHelper::convertTo<size8>(hiti->channels(2),"rh_strip_3"));
      rh_pos_strip   .push_back(hiti->positionWithinStrip());
      rh_n_wiregroups.push_back(GIFHelper::convertTo<size8>(hiti->nWireGroups(),"rh_n_wiregroups"));
  }
  nRH = nRHs;
}

void FillGIFStripInfo::fill(const CSCStripDigiCollection& strips){
  reset();
  int nStrips = 0;
  for (CSCStripDigiCollection::DigiRangeIterator dSDiter=strips.begin(); dSDiter!=strips.end(); dSDiter++) {
    CSCDetId id = (CSCDetId)(*dSDiter).first;

    std::vector<CSCStripDigi>::const_iterator stripIter = (*dSDiter).second.first;
    std::vector<CSCStripDigi>::const_iterator lStrip = (*dSDiter).second.second;
    for( ; stripIter != lStrip; ++stripIter) {
      std::vector<int> myADCVals = stripIter->getADCCounts();
      bool thisStripFired = false;
      float thisPedestal = 0.5*(float)(myADCVals[0]+myADCVals[1]);
      float threshold = 13.3 ;
      float diff = 0.;
      for (unsigned int iCount = 0; iCount < myADCVals.size(); iCount++) {
        diff = (float)myADCVals[iCount]-thisPedestal;
        if (diff > threshold) { thisStripFired = true; }
      }
      if(!thisStripFired) continue;

      nStrips++;
      strip_id.push_back(GIFHelper::chamberSerial(id));
      strip_lay.push_back(GIFHelper::convertTo<size8>(id.layer(),"strip_lay"));
      strip_number.push_back(GIFHelper::convertTo<size8>(stripIter->getStrip(),"strip_number"));
    }
  } // end strip loop
  nStrip = nStrips;
}

void FillGIFCompInfo::fill(const CSCComparatorDigiCollection& comps){
  reset();
  for (CSCComparatorDigiCollection::DigiRangeIterator chamber=comps.begin(); chamber!=comps.end(); chamber++)
  {
    CSCDetId id = (*chamber).first;

    const CSCComparatorDigiCollection::Range& range =(*chamber).second;
    for(CSCComparatorDigiCollection::const_iterator digiItr = range.first; digiItr != range.second; ++digiItr)
    {
      comp_id    .push_back(GIFHelper::chamberSerial(id));
      comp_lay   .push_back(GIFHelper::convertTo<size8>(id.layer(),"comp_lay"));
      comp_strip .push_back(GIFHelper::convertTo<size8>((*digiItr).getStrip(),"comp_strip"));
      comp_comp  .push_back(GIFHelper::convertTo<size8>((*digiItr).getComparator(),"comp_comp"));
    }
  }

}

void FillGIFWireInfo::fill(const CSCWireDigiCollection& wires){
  reset();
  // lay is array of layer occupancy indexed by layer
  int lay[6] = {0,0,0,0,0,0};
  int nWGs = 0;
  for (CSCWireDigiCollection::DigiRangeIterator chamber=wires.begin(); chamber!=wires.end(); chamber++)
  {
    CSCDetId id = (*chamber).first;
    int layer = id.layer();
      const CSCWireDigiCollection::Range& range =(*chamber).second;
      for(CSCWireDigiCollection::const_iterator digiItr = range.first; digiItr != range.second; ++digiItr)
      {
        nWGs++;
        // layer = {1,...,6}
        lay[layer-1]++;
        wire_id  .push_back(GIFHelper::chamberSerial(id));
        wire_lay .push_back(GIFHelper::convertTo<size8>(layer,"wire_lay"));
        wire_grp .push_back(GIFHelper::convertTo<size8>((*digiItr).getWireGroup(),"wire_grp"));
        wire_time.push_back(GIFHelper::convertTo<size8>((*digiItr).getTimeBin(),"wire_time"));
      }
  }
  nWG = nWGs;
  // loop on layers in occupancy array
  // if layer has hits, then increment
  // nlays by one
  int nlays = 0;
  for (int i = 0; i < 6; i++)
  {
    if (lay[i]>0) nlays++;
  }
  // nlays is number of fired layers in an event
  wire_nlay = nlays;

}




void FillGIFLCTInfo::fill(const CSCCorrelatedLCTDigiCollection& lcts){
  reset();
  int nLCTs = 0;
  for (CSCCorrelatedLCTDigiCollection::DigiRangeIterator chamber=lcts.begin(); chamber!=lcts.end(); chamber++)
  {
    CSCDetId id = (*chamber).first;
    const CSCCorrelatedLCTDigiCollection::Range& range =(*chamber).second;
    for(CSCCorrelatedLCTDigiCollection::const_iterator digiItr = range.first; digiItr != range.second; ++digiItr)
    {
      nLCTs++;
      lct_id          .push_back(GIFHelper::chamberSerial(id));
      lct_quality     .push_back(GIFHelper::convertTo<size8>(digiItr->getQuality(),"lct_quality"));
      lct_pattern     .push_back(GIFHelper::convertTo<size8>(digiItr->getPattern(),"lct_pattern"));
      lct_bend        .push_back(GIFHelper::convertTo<size8>(digiItr->getBend()   ,"lct_bend"));
      lct_keyWireGroup.push_back(GIFHelper::convertTo<size8>(digiItr->getKeyWG()  ,"lct_keyWireGroup"));
      lct_keyHalfStrip.push_back(GIFHelper::convertTo<size8>(digiItr->getStrip()  ,"lct_keyHalfStrip"));
      }
  }
  nLCT = nLCTs;
}


size16 FillGIFSegmentInfo::findRecHitIdx(const CSCRecHit2D& hit, const CSCRecHit2DCollection* allRecHits){
  int idx = -1;
  int foundIDX = -1;
  for (CSCRecHit2DCollection::const_iterator hiti=allRecHits->begin(); hiti!=allRecHits->end(); hiti++)
  {
    idx++;
    if(!hit.sharesInput(&(*hiti),CSCRecHit2D::all)) continue;
    foundIDX = idx;
    break;
  }
  if(foundIDX < 0) throw std::invalid_argument("FillGIFSegmentInfo::findRecHitIdx -> Could not find rechit");
  return GIFHelper::convertTo<size16,int>(foundIDX,"foundIDX");
}

void FillGIFSegmentInfo::fill(const CSCSegmentCollection& segments, const CSCRecHit2DCollection* recHits){
  reset();

  int nSegs = 0;
  for(CSCSegmentCollection::const_iterator dSiter=segments.begin(); dSiter != segments.end(); dSiter++) {
    CSCDetId id  = (CSCDetId)(*dSiter).cscDetId();
    nSegs++;

    LocalPoint localPos = (*dSiter).localPosition();
    float segX     = localPos.x();
    float segY     = localPos.y();
    LocalVector segDir = (*dSiter).localDirection();
    const auto& segmentHits = dSiter->specificRecHits();

    segment_id   .push_back(GIFHelper::chamberSerial(id));
    segment_pos_x.push_back(segX);
    segment_pos_y.push_back(segY);
    segment_dxdz.push_back(segDir.x()/segDir.z());
    segment_dydz.push_back(segDir.y()/segDir.z());
    segment_dx.push_back(segDir.x());
    segment_dy.push_back(segDir.y());
    segment_chisq.push_back((*dSiter).chi2());
    segment_dof.push_back((*dSiter).degreesOfFreedom());
    segment_nHits.push_back(GIFHelper::convertTo<size8>(segmentHits.size()  ,"segment_nHits"));
    segment_recHitIdx_1 .push_back((recHits && segmentHits.size() > 0) ?findRecHitIdx(segmentHits[0],recHits) : 0);
    segment_recHitIdx_2 .push_back((recHits && segmentHits.size() > 1) ?findRecHitIdx(segmentHits[1],recHits) : 0);
    segment_recHitIdx_3 .push_back((recHits && segmentHits.size() > 2) ?findRecHitIdx(segmentHits[2],recHits) : 0);
    segment_recHitIdx_4 .push_back((recHits && segmentHits.size() > 3) ?findRecHitIdx(segmentHits[3],recHits) : 0);
    segment_recHitIdx_5 .push_back((recHits && segmentHits.size() > 4) ?findRecHitIdx(segmentHits[4],recHits) : 0);
    segment_recHitIdx_6 .push_back((recHits && segmentHits.size() > 5) ?findRecHitIdx(segmentHits[5],recHits) : 0);

  }
  nSegments = nSegs;

}

void FillGIFCLCTInfo::fill(const CSCCLCTDigiCollection& clcts){
  reset();

  int nCLCTs = 0;
  for(CSCCLCTDigiCollection::DigiRangeIterator chamber=clcts.begin(); chamber != clcts.end(); chamber++) {
    CSCDetId id = (*chamber).first;
    const CSCCLCTDigiCollection::Range& range =(*chamber).second;
    for(CSCCLCTDigiCollection::const_iterator digiItr = range.first; digiItr != range.second; ++digiItr)
    {
      nCLCTs++;

      clct_id         .push_back(GIFHelper::chamberSerial(id));
      clct_isvalid    .push_back(GIFHelper::convertTo<size8>(digiItr->isValid()  ,"clct_isvalid"  ));
      clct_quality    .push_back(GIFHelper::convertTo<size8>(digiItr->getQuality()  ,"clct_quality"  ));
      clct_pattern    .push_back(GIFHelper::convertTo<size8>(digiItr->getPattern()  ,"clct_pattern"  ));
      clct_stripType  .push_back(GIFHelper::convertTo<size8>(digiItr->getStripType()  ,"clct_stripType"));
      clct_bend       .push_back(GIFHelper::convertTo<size8>(digiItr->getBend()  ,"clct_bend"     ));
      clct_halfStrip  .push_back(GIFHelper::convertTo<size8>(digiItr->getStrip()  ,"clct_halfStrip"));
      clct_CFEB       .push_back(GIFHelper::convertTo<size8>(digiItr->getCFEB()  ,"clct_CFEB"     ));
      clct_BX         .push_back(GIFHelper::convertTo<size8>(digiItr->getBX()  ,"clct_BX"       ));
      clct_trkNumber  .push_back(GIFHelper::convertTo<size8>(digiItr->getTrknmb()  ,"clct_trkNumber"));
      clct_keyStrip   .push_back(GIFHelper::convertTo<size8>(digiItr->getKeyStrip()  ,"clct_keyStrip" ));
    }
  }
  nCLCT = nCLCTs;
}


void FillGIFALCTInfo::fill(const CSCALCTDigiCollection& alcts){
  reset();

  int nALCTs = 0;
  for(CSCALCTDigiCollection::DigiRangeIterator chamber=alcts.begin(); chamber != alcts.end(); chamber++) {
    CSCDetId id = (*chamber).first;
    const CSCALCTDigiCollection::Range& range =(*chamber).second;
    for(CSCALCTDigiCollection::const_iterator digiItr = range.first; digiItr != range.second; ++digiItr)
    {
      nALCTs++;

      alct_id         .push_back(GIFHelper::chamberSerial(id));
      alct_isvalid    .push_back(GIFHelper::convertTo<size8>(digiItr->isValid()  ,"alct_isvalid"  ));
      alct_quality    .push_back(GIFHelper::convertTo<size8>(digiItr->getQuality()  ,"alct_quality"  ));
      alct_accel      .push_back(GIFHelper::convertTo<size8>(digiItr->getAccelerator()  ,"alct_accel"  ));
      alct_collB      .push_back(GIFHelper::convertTo<size8>(digiItr->getCollisionB()  ,"alct_collB"  ));
      alct_wireGroup  .push_back(GIFHelper::convertTo<size8>(digiItr->getKeyWG()  ,"alct_wireGroup"));
      alct_BX         .push_back(GIFHelper::convertTo<size8>(digiItr->getBX()  ,"alct_BX"       ));
      alct_trkNumber  .push_back(GIFHelper::convertTo<size8>(digiItr->getTrknmb()  ,"alct_trkNumber"));
    }
    nALCT = nALCTs;
  }
}
