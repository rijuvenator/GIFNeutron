#include "Gif/TestBeamAnalysis/include/FillGIFInfo.h"
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
      rh_pos_strip		.push_back(hiti->positionWithinStrip());
	  rh_wireGrp		.push_back(GIFHelper::convertTo<size8>(hiti->hitWire(),"rh_wireGrp"));
      rh_n_wiregroups	.push_back(GIFHelper::convertTo<size8>(hiti->nWireGroups(),"rh_n_wiregroups"));
	  rh_n_timebins		.push_back(GIFHelper::convertTo<size8>(hiti->nTimeBins(),"rh_n_timebins"));
	  rh_n_strips		.push_back(GIFHelper::convertTo<size8>(hiti->nStrips(),"rh_n_strips"));

	  // Find the charge associated with this hit
	  int centerID = hiti->nStrips()/2;
	  float rhMax = -999.;
	  for (unsigned int it=0; it<hiti->nTimeBins()-1; it++) {
		  if (hiti->adcs(centerID,it) > rhMax) rhMax = hiti->adcs(centerID,it);
	  }
	  rh_adc_max.push_back(rhMax);
	  float rHSumQ = 0;
	  float sumsides=0.;
	  int adcsize=hiti->nStrips()*hiti->nTimeBins();
	  for ( unsigned int i=0; i< hiti->nStrips(); i++) {
		  for ( unsigned int j=0; j< hiti->nTimeBins()-1; j++) {
			  rHSumQ+=hiti->adcs(i,j); 
			  if (i!=1) sumsides+=hiti->adcs(i,j);
		  }
	  }
	  rh_adc3x3_Qsum.push_back(rHSumQ);
	  // (Ql+Qr)/Qt ratio
      float rHratioQ = sumsides/rHSumQ;
      if (adcsize != 12) rHratioQ = -99;
	  rh_lr_Qratio.push_back(rHratioQ);
	  // RH energy
	  rh_energy.push_back(hiti->energyDepositedInLayer());
	  // RH time
	  rh_time.push_back(hiti->tpeak());

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
	  strip_ADC.push_back(myADCVals);
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
      comp_time  .push_back(GIFHelper::convertTo<size8>((*digiItr).getTimeBin(),"comp_time"));
      comp_timeOn.push_back((*digiItr).getTimeBinsOn());
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
		wire_bx  .push_back(GIFHelper::convertTo<int>((*digiItr).getWireGroupBX(),"wire_bx"));
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

int FillGIFSegmentInfo::segmentQuality(edm::OwnVector<CSCSegment>::const_iterator segment)
{
  int Nchi2 = 0;
  int quality = 0;
  int nhits = segment->recHits().size();
  if ( segment->chi2()/(nhits*2.-4.) > 3. ) Nchi2 = 1;
  if ( segment->chi2()/(nhits*2.-4.) > 9. ) Nchi2 = 2;

  if ( nhits >  4 ) quality = 1 + Nchi2;
  if ( nhits == 4 ) quality = 3 + Nchi2;
  if ( nhits == 3 ) quality = 5 + Nchi2;

  // there's no globalDirection in CSCSegment (there is in MuonTransientTrackingRecHit), so commenting this bit out
  //float dPhiGloDir = fabs ( deltaPhi(segment->globalPosition().phi(), segment->globalDirection().phi()) );

  //if ( dPhiGloDir > .2 ) ++quality;

  // there's no isCSC in CSCSegment (there is in MuonTransientTrackingRecHit), so
  // hard-coding isCSC as true, since all of our segments are CSC segments. At least I assume that's what that means...
  // add a penalty for being ME1A
  if(true && CSCDetId(segment->geographicalId()).ring() == 4) ++quality;
  return quality;
}

void FillGIFSegmentInfo::fill(const CSCGeometry * theCSC,const CSCSegmentCollection& segments, const CSCRecHit2DCollection* recHits){
  reset();

  int nSegs = 0;
  for(CSCSegmentCollection::const_iterator dSiter=segments.begin(); dSiter != segments.end(); dSiter++) {
	// Specifically for segment positon in (strip,wg) units
	// Create the ChamberId
	DetId gid = (*dSiter).geographicalId();

	CSCDetId chamberId(gid.rawId());
	const CSCChamber *segChamber = theCSC->chamber(chamberId);
	const CSCLayer *segLay3 = segChamber->layer(3);
	//const CSCLayer *segLay4 = segChamber->layer(4);
	const CSCLayerGeometry *segLay3Geo = segLay3->geometry();
	//GlobalPoint lay4zero = segLay4->toGlobal(lzero); 
	//LocalPoint lay4zeroIn3 = segLay3->toLocal(lay4zero);
	//float cm2lay = fabs(lay4zeroIn3.z());

	LocalPoint  segLPlayer = segLay3->toLocal(segChamber->toGlobal((*dSiter).localPosition() ));
	LocalVector segLVlayer = segLay3->toLocal(segChamber->toGlobal((*dSiter).localDirection()));
	float scale = -1.0*segLPlayer.z()/segLVlayer.z();
	LocalVector tV = scale*segLVlayer;
	LocalPoint tP = segLPlayer + tV;

	float segStrip = segLay3Geo->strip(tP);
	float segWire  = segLay3Geo->wireGroup(segLay3Geo->nearestWire(tP));
	
	// strip width
	//int strI = floor(segStrip);
	//float cm2strip = fabs( segLay3Geo->xOfStrip(strI,tP.y()) - segLay3Geo->xOfStrip(strI+1,tP.y()) );
	// wire width
	//int wireI = floor(segWire);
	//float cm2wire = fabs( segLay3Geo->yOfWire(wireI,tP.x()) - segLay3Geo->yOfWire(wireI+1,tP.x()) );


	
	// old
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
	segment_pos_strip_x.push_back(segStrip);
	segment_pos_wire_y.push_back(segWire);
    segment_dxdz.push_back(segDir.x()/segDir.z());
    segment_dydz.push_back(segDir.y()/segDir.z());
	//segment_strip_dxdz.push_back( ( segDir.x() / cm2strip ) / ( segDir.z() / cm2lay ) );
	//segment_wire_dydz.push_back( ( segDir.y() / cm2wire ) / ( segDir.z() / cm2lay ) );
    segment_dx.push_back(segDir.x());
    segment_dy.push_back(segDir.y());
    segment_chisq.push_back((*dSiter).chi2());
    segment_dof.push_back((*dSiter).degreesOfFreedom());
    segment_nHits.push_back(GIFHelper::convertTo<size8>(segmentHits.size()  ,"segment_nHits"));
	segment_quality.push_back(segmentQuality(dSiter));
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
