// -*- C++ -*-
//
// Package:    Gif/Gif
// Class:      Gif
// 
/**\class Gif Gif.cc Gif/Gif/plugins/Gif.cc

   Description: [one line class summary]

   Implementation:
   [Notes on implementation]
*/
//
// Original Author:  Alexey Kamenev
//         Created:  Sun, 30 Aug 2015 13:47:42 GMT
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "Geometry/Records/interface/GlobalTrackingGeometryRecord.h"
#include "Geometry/CommonDetUnit/interface/GlobalTrackingGeometry.h"
#include "Geometry/CommonDetUnit/interface/GeomDet.h"



#include <Geometry/CSCGeometry/interface/CSCGeometry.h> 
#include <Geometry/Records/interface/MuonGeometryRecord.h> 
#include <RecoMuon/Records/interface/MuonRecoGeometryRecord.h> 
#include "DataFormats/CSCRecHit/interface/CSCRecHit2D.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "CondFormats/AlignmentRecord/interface/GlobalPositionRcd.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include <DataFormats/GeometrySurface/interface/LocalError.h> 
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include <DataFormats/Provenance/interface/EventID.h> 


#include "DataFormats/CSCDigi/interface/CSCWireDigi.h"
#include "DataFormats/CSCDigi/interface/CSCWireDigiCollection.h"
#include "DataFormats/CSCDigi/interface/CSCStripDigi.h"
#include "DataFormats/CSCDigi/interface/CSCStripDigiCollection.h"
#include "DataFormats/CSCDigi/interface/CSCComparatorDigi.h"
#include "DataFormats/CSCDigi/interface/CSCComparatorDigiCollection.h"
#include "DataFormats/CSCDigi/interface/CSCALCTDigi.h"
#include "DataFormats/CSCDigi/interface/CSCALCTDigiCollection.h"
#include "DataFormats/CSCDigi/interface/CSCCLCTDigi.h"
#include "DataFormats/CSCDigi/interface/CSCCLCTDigiCollection.h"
#include "DataFormats/CSCDigi/interface/CSCCorrelatedLCTDigi.h"
#include "DataFormats/CSCDigi/interface/CSCCorrelatedLCTDigiCollection.h"

 
#include "DataFormats/MuonDetId/interface/CSCDetId.h"
#include <DataFormats/CSCRecHit/interface/CSCRecHit2D.h>
#include <DataFormats/CSCRecHit/interface/CSCSegmentCollection.h>
#include "DataFormats/MuonDetId/interface/RPCDetId.h"

#include "DataFormats/L1GlobalMuonTrigger/interface/L1MuGMTReadoutRecord.h"
#include "DataFormats/L1GlobalMuonTrigger/interface/L1MuGMTReadoutCollection.h"

#include "Geometry/CSCGeometry/interface/CSCGeometry.h"
#include "Geometry/CSCGeometry/interface/CSCChamber.h"
#include "Geometry/CSCGeometry/interface/CSCLayer.h"
#include "Geometry/CSCGeometry/interface/CSCLayerGeometry.h"
#include "Geometry/Records/interface/MuonGeometryRecord.h"

#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "Geometry/CommonDetUnit/interface/GlobalTrackingGeometry.h"
#include "Geometry/Records/interface/GlobalTrackingGeometryRecord.h"

#include "DataFormats/CSCRecHit/interface/CSCRecHit2DCollection.h"
#include "SimDataFormats/TrackingHit/interface/PSimHitContainer.h"

#include "DataFormats/GeometryVector/interface/GlobalPoint.h"
#include "DataFormats/GeometryVector/interface/GlobalVector.h"
#include "DataFormats/GeometryVector/interface/LocalPoint.h"
#include "DataFormats/GeometryVector/interface/LocalVector.h"
#include "DataFormats/CLHEP/interface/AlgebraicObjects.h"
#include "DataFormats/MuonDetId/interface/CSCIndexer.h"

#include "CondFormats/CSCObjects/interface/CSCDBGains.h"
#include "CondFormats/DataRecord/interface/CSCDBGainsRcd.h"
#include "CondFormats/CSCObjects/interface/CSCDBNoiseMatrix.h"
#include "CondFormats/DataRecord/interface/CSCDBNoiseMatrixRcd.h"
#include "CondFormats/CSCObjects/interface/CSCDBCrosstalk.h"
#include "CondFormats/DataRecord/interface/CSCDBCrosstalkRcd.h"
#include "CondFormats/CSCObjects/interface/CSCDBPedestals.h"
#include "CondFormats/DataRecord/interface/CSCDBPedestalsRcd.h"
#include "CondFormats/Alignment/interface/Alignments.h"

#include "DataFormats/MuonReco/interface/MuonFwd.h"
#include "DataFormats/MuonReco/interface/Muon.h"

#include <TGClient.h>
#include <TRootEmbeddedCanvas.h>
#include "TCanvas.h"
#include "TPad.h"
#include "TStyle.h"

#include "TF1.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TH1I.h"
#include "TProfile.h"
#include "TProfile2D.h"
#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TGraph.h"
#include <vector>
#include <cmath>
#include <string>
#include <iostream>
#include <fstream>
// class declaration
//

// If the analyzer does not use TFileService, please remove
// the template argument to the base class so the class inherits
// from  edm::one::EDAnalyzer<> and also remove the line from
// constructor "usesResource("TFileService");"
// This will improve performance in multithreaded jobs.

class Gif : public edm::one::EDAnalyzer<edm::one::SharedResources>  {
public:
  explicit Gif(const edm::ParameterSet&);
  ~Gif();

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


private:
  virtual void beginJob() override;
  virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
  virtual void endJob() override;

  // ----------member data ---------------------------
  edm::InputTag stripDigiTag;
  edm::InputTag wireDigiTag;
  //edm::InputTag compDigiTag;
  edm::InputTag cscRecHitTag;
  edm::InputTag cscSegTag;
  //edm::InputTag saMuonTag;
  //edm::InputTag l1aTag;
  //edm::InputTag alctDigiTag;
  //edm::InputTag clctDigiTag;
  //edm::InputTag corrlctDigiTag;
  //edm::InputTag hltTag;

  std::string theRootFileName,pdf;
  //std::string test;
  //std::string date;
  //std::string cond;

  TFile *fout;	
  TH1D *strip[7]; //occ
  TH1D *wire[7];  //occ
  TH2D *all_wire_time;
  TH2D *str;  //station and ring
  TProfile2D *all_strip_time;

  TH1I *anode_trig;
  TH2I *firedWG;

  //TH1I *ped[6][112];
  TH1I *wtime[7]; //time
  TProfile *stime[7]; //time

  //TProfile2D *gg2d;
  TH2I *coordMM,*coordCH;
  TH1I *gg;
  TH1F* nSeg;
  TH1F* hnRecHitsAll;
  TH1F* hnRecHitsMax;
  //TH1I *hit_ctime;
  //TH1I *hit_atime;

  std::vector<TH2I> dumpW,dumpS;
  TH2I *evW,*evS;

  int lf[8];

  unsigned int fev,lev;
  int evn;	  
	  
	  
};

//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
Gif::Gif(const edm::ParameterSet& iConfig)

{
  //now do what ever initialization is needed
  // usesResource("TFileService");
   
  //now do what ever initialization is needed
  theRootFileName= iConfig.getUntrackedParameter<std::string>("rootFileName");
  //cond= iConfig.getUntrackedParameter<std::string>("cond");
  std::cout<<theRootFileName.c_str()<<"\n";
  pdf=theRootFileName+".pdf";
  //theRootFileName=theRootFileName+".root";
  fout=new TFile(theRootFileName.c_str(),"RECREATE");
  fout->cd();

  //hits=new TH1D("hits","landau 3x3;ADC;N",300,0,1200);
  //strip=new TH1D("strips","Occupancy of strips with signals (>13 ADC);Strip;N",112,0.5,112.5);
  //wire=new TH1D("wire","digi wires;Wire;N",112,0.5,112.5);
  str=new TH2D("str","strips station and ring;Station;Ring",4,0.5,4.5,4,0.5,4.5);
  all_wire_time=new TH2D("awt","Anode times;Wire Group;Time Bin",112,0.5,112.5,16,0.5,16.5);
  all_strip_time=new TProfile2D("ast","Strip average ADCs;Strip;Time Bin",112,0.5,112.5,8,0.5,8.5);


  //gg2d=new TProfile2D("gg2d","2D");
  coordMM=new TH2I("coordMM","RecHit coordinates from all layers;X, cm;Y, cm;",50,-100,100,50,-150,150);
  coordCH=new TH2I("coordCH","RecHit channels from all layers;Strip;Wiregroup;",112,-.5,112.5,112,-.5,112.5);
  gg=new TH1I("gg","Landau distribution of RecHit3x3 cluster charge for all layers;ADC;N",100,0,2000);
  //hit_ctime=new TH1I("hct","RecHit strip time;Time, ns");
  //hit_atime=new TH1I();

  nSeg = new TH1F("nSeg", ";number of segments in event;events", 21, -0.5, 20.5);
  hnRecHitsAll = new TH1F("hnRecHitsAll", ";number of rec hits on all segments;segments", 21, -0.5, 20.5); 
  hnRecHitsMax = new TH1F("hnRecHitsMax", ";max number of rec hits on any segment in event;events", 21, -0.5, 20.5); 

  evW=new TH2I("evW","Wire groups in event;Wire group;Time bin",112,0.5,112.5,16,0.5,16.5);
  evS=new TH2I("evS","Strips in event;Strip;Time bin",112,0.5,112.5,8,0.5,8.5);

  char t1[250],t2[250];
  for(int i=0;i<6;i++)
    {sprintf(t1,"stripsL%d",i+1);
      sprintf(t2,"Occupancy of strips with signals (>13 ADC) for layer %d;Strip;N",i+1);
      strip[i]=new TH1D(t1,t2,112,0.5,112.5);
      sprintf(t1,"wiresL%d",i+1);
      sprintf(t2,"Occupancy of wiregroups for layer %d;Wiregroup;N",i+1);
      wire[i]=new TH1D(t1,t2,112,0.5,112.5);
	
      sprintf(t1,"stimeL%d",i+1);
      sprintf(t2,"Average strip signal (>13 ADC) by time for layer %d (ADC[i]-ADC[0]);Time bin;N",i+1);
      stime[i]=new TProfile(t1,t2,8,0.5,8.5);
      sprintf(t1,"wtimeL%d",i+1);
      sprintf(t2,"Average anode time for layer %d;Time bin;N",i+1);
      wtime[i]=new TH1I(t1,t2,16,0.5,16.5);
    };
  sprintf(t1,"stripsL%d",7);
  sprintf(t2,"Occupancy of strips with signals (>13 ADC) for all layers;Strip;N");
  strip[6]=new TH1D(t1,t2,112,0.5,112.5);
  sprintf(t1,"wiresL%d",7);
  sprintf(t2,"Occupancy of wiregroups for all layers;Wiregroup;N");
  wire[6]=new TH1D(t1,t2,112,0.5,112.5);

  sprintf(t1,"stimeL%d",7);
  sprintf(t2,"Average strip signal (>13 ADC)by time for all layers (ADC[i]-ADC[0]);Time bin;N");
  stime[6]=new TProfile(t1,t2,8,0.5,8.5);
  sprintf(t1,"wtimeL%d",7);
  sprintf(t2,"Average anode time for all layers;Time bin;N");
  wtime[6]=new TH1I(t1,t2,16,0.5,16.5);


  anode_trig=new TH1I("anode_trig","Number of fired anode layers;Layers;N",8,0.5,8.5);
  firedWG=new TH2I("firedWG","Number of fired wiregroups in layer;Wiregroups;Layer",113,-0.5,112.5,6,0.5,6.5);

  cscRecHitTag  = iConfig.getParameter<edm::InputTag>("cscRecHitTag");
  stripDigiTag  = iConfig.getParameter<edm::InputTag>("stripDigiTag");
  wireDigiTag   = iConfig.getParameter<edm::InputTag>("wireDigiTag");
  cscSegTag     = iConfig.getParameter<edm::InputTag>("cscSegTag");

  //template<typename T>
  //edm::EDGetTokenT<CSCRecHit2DCollection> consumes<CSCRecHit2DCollection>(cscRecHitTag)
  fev=2000000000,lev=0;



  for(int i=0;i<8;i++){lf[i]=0;};
  evn=0;   
   

}


Gif::~Gif()
{
 
  // do anything here that needs to be done at desctruction time
  // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
Gif::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  using namespace edm;

  edm::ESHandle<CSCGeometry> cscGeom;
  iSetup.get<MuonGeometryRecord>().get(cscGeom);
  //edm::EventId evId=iEvent.id();
  unsigned int time=iEvent.time().unixTime();
  if(fev>time)fev=time;
  if(lev<time)lev=time;

  lf[6]++;
  //bool intW=false;//,intS=false;
  //char t1[250];


  //========================== SEGMENTS ========================
  edm::Handle<CSCSegmentCollection> cscSegments;
  iEvent.getByLabel(cscSegTag, cscSegments);


  int nSegments = cscSegments->size();
  nSeg->Fill(nSegments);

  int nRecHitsMax = -1;  

  for(CSCSegmentCollection::const_iterator dSiter=cscSegments->begin(); dSiter != cscSegments->end(); dSiter++) {

    //CSCDetId id  = (CSCDetId)(*dSiter).cscDetId();                                                                                                                                                       
    LocalPoint localPos = (*dSiter).localPosition();
    float segX     = localPos.x();
    float segY     = localPos.y();
    int nRecHits = (*dSiter).nRecHits();  
    hnRecHitsAll->Fill(nRecHits);  
    if (nRecHits > nRecHitsMax) {
      nRecHitsMax = nRecHits;
    }

    for (CSCSegmentCollection::const_iterator dSiter2=dSiter+1; dSiter2 != cscSegments->end(); dSiter2++) {
      LocalPoint localPos2 = (*dSiter2).localPosition();
      float segX2     = localPos2.x();
      float segY2     = localPos2.y();
      float dSeg = (segX-segX2)*(segX-segX2)+(segY-segY2)*(segY-segY2);
      dSeg = sqrt(dSeg);
      //     distanceBetweenSegs->Fill(dSeg);
    }

  }

  hnRecHitsMax->Fill(nRecHitsMax);  


  //========================== HITS ========================
  edm::Handle<CSCRecHit2DCollection> recHits;
  iEvent.getByLabel(cscRecHitTag,recHits);


  //std::string s1="";
  //std::string s2="csc2DRecHits";
  //iEvent.getByLabel(s2,s1,recHits);

  CSCRecHit2DCollection::const_iterator dRHIter;
  for (dRHIter = recHits->begin(); dRHIter != recHits->end(); dRHIter++) {
    if((*dRHIter).nStrips()==3){
      CSCDetId id = (CSCDetId)(*dRHIter).cscDetId();
      //std::cout<<id.endcap()<<"  "<<id.station()<<"  "<<id.ring()<<"  "<<id.chamber()<<"\n";
      int rHSumQ = 0;
      for (int i = 0; i < 3; i++){
	for (int j = 0; j < 3; j++){
	  rHSumQ = rHSumQ + (*dRHIter).adcs(i,j);
	};
      };
      //int ind=cscdb.CC(id.endcap(),id.station(),id.ring());
      //	std::cout<<ind<<"  "<<id.endcap()<<"  "<<id.station()<<"  "<<id.ring()<<"  "<<id.chamber()<<"  "<<id.layer()<<"  "<<cscdb.GetHVseg(ind,(*dRHIter).hitWire())<<"  "<<(*dRHIter).hitWire()<<"\n";
      //	h_land[ind][id.chamber()-1][id.layer()-1][cscdb.GetHVseg(ind,(*dRHIter).hitWire())-1]->Fill(rHSumQ);
      gg->Fill(rHSumQ);
	
      LocalPoint rhitlocal = (*dRHIter).localPosition();  
      coordMM->Fill(rhitlocal.x(),rhitlocal.y());
	
      int centerStrip =  (*dRHIter).channels(1);
      if(id.ring()==4&&centerStrip>0)centerStrip+=64;
      //     h_nstr->Fill((*dRHIter).nStrips());
      //    h_ntb->Fill((*dRHIter).nTimeBins());
      int centerWG=(*dRHIter).hitWire();
      // if((*dRHIter).nStrips()==3&&(*dRHIter).nTimeBins()==4)h_hit_ch->Fill(centerStrip,centerWG);
      coordCH->Fill(centerStrip,centerWG);
	
    }//3 strips
  }//all hits


  int lff[6];//,example[6];
  for(int i=0;i<6;i++){lff[i]=0;}
  //========================== WIRES ========================
  edm::Handle<CSCWireDigiCollection> wires;
  iEvent.getByLabel(wireDigiTag,wires);

  for (CSCWireDigiCollection::DigiRangeIterator wi=wires->begin(); wi!=wires->end(); wi++) {
    CSCDetId id = (CSCDetId)(*wi).first;
    //std::cout<<id.layer()<<"    la\n";	
    std::vector<CSCWireDigi>::const_iterator wireIt = (*wi).second.first;
    std::vector<CSCWireDigi>::const_iterator lastWire = (*wi).second.second;
    //int nn=0,pw=0,pt=0;
				
    for( ; wireIt != lastWire; ++wireIt){
      //h_w_T->Fill(wireIt->getWireGroup(),wireIt->getTimeBin());
      wire[id.layer()-1]->Fill(wireIt->getWireGroup());
      wire[6]->Fill(wireIt->getWireGroup());
      std::vector<int>tbins=wireIt->getTimeBinsOn();
      //if(tbins.size()>1)intW=true;
      all_wire_time->Fill(wireIt->getWireGroup(),wireIt->getTimeBin()+1);
      wtime[id.layer()-1]->Fill(wireIt->getTimeBin()+1);
      wtime[6]->Fill(wireIt->getTimeBin()+1);
      lff[id.layer()-1]++;
      //if(lff[id.layer()-1]>40)intW=true;	
    };// all wires
    //if(intW){example[id.layer()-1]=1;  //Plot an example of wire event
    /*
      if(evn<3000){	
      wireIt = (*wi).second.first;
      sprintf(t1,"Wire groups in event %d layer %d;Wire group;Time bin",evn,id.layer());
      evW->Clear();
      evW->SetTitle(t1);
      for( ; wireIt != lastWire; ++wireIt){
      std::vector<int>tbins=wireIt->getTimeBinsOn();
      for(size_t i=0;i<tbins.size();i++)
      {evW->Fill(wireIt->getWireGroup(),tbins.at(i));
      };
      };
      dumpW.push_back(*evW);
      }; //if
    */
  };	//all layers for wires		
  int zero=0;
  for(int i=0;i<6;i++){
    if(lff[i]>0){zero++;};
    //if(lff[i]>40)intW=true;
    firedWG->Fill(lff[i],i+1);
  };
  if(zero>0)lf[zero-1]++;
  if(zero==0)lf[7]++;
  //========================== STRIPS ========================
  edm::Handle<CSCStripDigiCollection> strips;
  iEvent.getByLabel(stripDigiTag,strips);
  for (CSCStripDigiCollection::DigiRangeIterator si=strips->begin(); si!=strips->end(); si++) {
    CSCDetId id = (CSCDetId)(*si).first;
    str->Fill(id.station(),id.ring());
    // 	if(id.endcap()==1&&(id.chamber()==27||id.chamber()==28)) 	{
    std::vector<CSCStripDigi>::const_iterator stripIt = (*si).second.first;
    std::vector<CSCStripDigi>::const_iterator lastStrip = (*si).second.second;
    /*
      if(evn<3000){
      sprintf(t1,"Strips in event %d layer %d;Wire group;Time bin",evn,id.layer());
      evS->Clear();
      evS->SetTitle(t1);
		
      };
    */
	
    for( ; stripIt != lastStrip; ++stripIt) {
      std::vector<int> myADCVals = stripIt->getADCCounts();
      int strn=stripIt->getStrip();
      if(id.ring()==4)strn=strn+64;
      bool was_signal=false;
      for(size_t k=0;k<myADCVals.size();k++)
	{if(myADCVals[k]-myADCVals[0]>13)was_signal=true;
	  //if(myADCVals[k]>=4095)intS=true;
	  // if(evn<3000){evS->SetBinContent(strn,k+1,myADCVals[k]);};
	};
      if(was_signal){
	strip[id.layer()-1]->Fill(strn);
	strip[6]->Fill(strn);
	for(size_t k=0;k<myADCVals.size();k++){
	  all_strip_time->Fill(strn,k+1,myADCVals[k]-myADCVals[0]);
	  stime[id.layer()-1]->Fill(k+1,myADCVals[k]-myADCVals[0]);
	  stime[6]->Fill(k+1,myADCVals[k]-myADCVals[0]);
	};
      };
      /*
	if(was_signal){	 
	h_occ_s[cscdb.CC(id.endcap(),id.station(),id.ring())]->Fill((id.chamber()-1)*6+id.layer(),stripIt->getStrip());
	for(size_t k=0;k<myADCVals.size();k++)
	{h_str_T->Fill(stripIt->getStrip(),k,myADCVals[k]-myADCVals[0]);
			 
	p_str_all[cscdb.CC(id.endcap(),id.station(),id.ring())]->Fill(stripIt->getStrip(),k,myADCVals[k]-myADCVals[0]);
	p_str_1d[cscdb.CC(id.endcap(),id.station(),id.ring())]->Fill(k,myADCVals[k]-myADCVals[0]);
				 
	};
	}
	else{
	h_stat_ped[cscdb.CC(id.endcap(),id.station(),id.ring())]->Fill(myADCVals[0]);
	};
      */
		
    };//all strips
    //if(evn<3000){dumpS.push_back(*evS);}
    // };//chamber
	
  };//strip collection


  evn++;





#ifdef THIS_IS_AN_EVENT_EXAMPLE
  Handle<ExampleData> pIn;
  iEvent.getByLabel("example",pIn);
#endif
   
#ifdef THIS_IS_AN_EVENTSETUP_EXAMPLE
  ESHandle<SetupData> pSetup;
  iSetup.get<SetupRecord>().get(pSetup);
#endif
}


// ------------ method called once each job just before starting event loop  ------------
void 
Gif::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
Gif::endJob() 
{
  gStyle->SetHistFillColor(4);
  gStyle->SetHistFillStyle(1);
  for(int i=0;i<7;i++){wire[i]->Write();}
	
  for(int i=0;i<7;i++){strip[i]->Write();};
  str->Write();
  all_strip_time->Write();
  all_wire_time->Write();


  for(int i=0;i<7;i++){stime[i]->Write();};
  for(int i=0;i<7;i++){wtime[i]->Write();};
  for(int i=0;i<8;i++){anode_trig->SetBinContent(i+1,lf[i]);};
  anode_trig->Write();
  firedWG->Write();
  //gg2d->Write();
  coordMM->Write();
  coordCH->Write();
  gg->Write();
  //hit_ctime->Write();
  //hit_atime->Write();

  nSeg->Write();
  hnRecHitsAll->Write();
  hnRecHitsMax->Write();


  TCanvas *cc=new TCanvas();
  char t1[200],t2[200],t3[200];
  sprintf(t1,"%s[",pdf.c_str());
  sprintf(t2,"%s]",pdf.c_str());
  sprintf(t3,"%s",pdf.c_str());
  cc->Print(t1);

  for(int i=0;i<7;i++){wire[i]->Draw();cc->Print(t3);};
  for(int i=0;i<7;i++){strip[i]->Draw();cc->Print(t3);}
  str->Draw();cc->Print(t3);

  for(int i=0;i<7;i++){stime[i]->Draw();cc->Print(t3);};
  for(int i=0;i<7;i++){wtime[i]->Draw();cc->Print(t3);};

  //hit_ctime->Draw();cc->Print(t3);
  //hit_atime->Draw();cc->Print(t3);
  //gg->Draw();cc->Print(t3);



  firedWG->Draw("COLZ");cc->SetLogz(1);cc->Print(t3);
  cc->SetLogz(0);
  gStyle->SetOptStat(0);
  anode_trig->Draw();cc->Print(t3);
  anode_trig->Draw();cc->SetLogy(1);cc->Print(t3);cc->SetLogy(0);
  all_strip_time->Draw("COLZ");cc->Print(t3);
  all_wire_time->Draw("COLZ");cc->Print(t3);
  coordMM->Print(t3);
  coordCH->Print(t3);
  gg->Print(t3);
  cc->Print(t2);
  /*
    cc->Print("ex.pdf[");
    cc->Divide(2,1);
    std::cout<<dumpW.size()<<"  "<<dumpS.size()<<"\n";
    for(size_t i=0;i<dumpW.size();i++)
    {
    cc->cd(1);
    dumpW.at(i).Draw("COLZ");
    cc->cd(2);
    dumpS.at(i).Draw("COLZ");
    cc->Print("ex.pdf");
    cc->cd(1);gPad->Clear();cc->cd(2);gPad->Clear();
    };
    cc->Print("ex.pdf]");
  */
  std::cout<<"start: "<<fev<<"   stop: "<<lev<<"     length: "<<lev-fev<<"s\n";
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
Gif::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(Gif);
