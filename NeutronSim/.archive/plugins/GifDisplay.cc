//# -*- C++ -*-
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
#include "TH1F.h"
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

//#include "Gif.h"
#include "display.h"
// class declaration
//

// If the analyzer does not use TFileService, please remove
// the template argument to the base class so the class inherits
// from  edm::one::EDAnalyzer<> and also remove the line from
// constructor "usesResource("TFileService");"
// This will improve performance in multithreaded jobs.

class GifDisplay : public edm::one::EDAnalyzer<edm::one::SharedResources>  {
   public:
      explicit GifDisplay(const edm::ParameterSet&);
      ~GifDisplay();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() override;
      virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
      virtual void endJob() override;
	  int getChamberSerial( CSCDetId id ) {
		  int st = id.station();
		  int ri = id.ring();
		  int ch = id.chamber();
		  int ec = id.endcap();
		  int kSerial = ch;
		  if (st == 1 && ri == 1) kSerial = ch;
		  if (st == 1 && ri == 2) kSerial = ch + 36;
		  if (st == 1 && ri == 3) kSerial = ch + 72;
		  if (st == 1 && ri == 4) kSerial = ch;
		  if (st == 2 && ri == 1) kSerial = ch + 108;
		  if (st == 2 && ri == 2) kSerial = ch + 126;
		  if (st == 3 && ri == 1) kSerial = ch + 162;
		  if (st == 3 && ri == 2) kSerial = ch + 180;
		  if (st == 4 && ri == 1) kSerial = ch + 216;
		  if (st == 4 && ri == 2) kSerial = ch + 234;  // one day...
		  if (ec == 2) kSerial = kSerial + 300;
		  return kSerial;
	  }


	  // ----------member data ---------------------------
	  edm::InputTag stripDigiTag;
	  edm::InputTag wireDigiTag;
	  edm::InputTag comparatorDigiTag;
	  //edm::InputTag compDigiTag;
	  edm::InputTag cscRecHitTag;
	  //edm::InputTag cscSegTag;
	  //edm::InputTag saMuonTag;
	  //edm::InputTag l1aTag;
	  edm::InputTag alctDigiTag;
	  edm::InputTag clctDigiTag;
	  edm::InputTag corrlctDigiTag;
	  //edm::InputTag hltTag;
	  
	  //std::string theRootFileName,pdf;
	  std::string eventDisplayDir;
	  std::vector<int> eventList;
	  std::string eventlistFile;
	  
	  std::string chamberType;
	  int thisChamber=0;

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
GifDisplay::GifDisplay(const edm::ParameterSet& iConfig)

{
   
//now do what ever initialization is needed
//theRootFileName= iConfig.getUntrackedParameter<std::string>("rootFileName");
/*std::cout<<theRootFileName.c_str()<<"\n";
pdf=theRootFileName+".pdf";
fout=new TFile(theRootFileName.c_str(),"RECREATE");
fout->cd();
*/
//cscRecHitTag  = iConfig.getParameter<edm::InputTag>("cscRecHitTag");
stripDigiTag  = iConfig.getParameter<edm::InputTag>("stripDigiTag");
wireDigiTag  = iConfig.getParameter<edm::InputTag>("wireDigiTag");
comparatorDigiTag = iConfig.getParameter<edm::InputTag>("comparatorDigiTag");
//alctDigiTag = iConfig.getParameter<edm::InputTag>("alctDigiTag");
//clctDigiTag = iConfig.getParameter<edm::InputTag>("clctDigiTag");
//corrlctDigiTag = iConfig.getParameter<edm::InputTag>("corrlctDigiTag");
eventDisplayDir = iConfig.getUntrackedParameter<std::string>("eventDisplayDir");//,"/afs/cern.ch/work/c/cschnaib/GIF/tmpDisplay");
eventlistFile = iConfig.getUntrackedParameter<std::string>("eventListFile");
chamberType = iConfig.getUntrackedParameter<std::string>("chamberType", "21");
}





GifDisplay::~GifDisplay()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
GifDisplay::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   using namespace std;

edm::ESHandle<CSCGeometry> cscGeom;
iSetup.get<MuonGeometryRecord>().get(cscGeom);
//edm::EventId evId=iEvent.id();
//unsigned int time=iEvent.time().unixTime();

double Run,Event;
Run = iEvent.id().run();
Event = iEvent.id().event();

vector<CSCDetID> chamberList;
chamberList.clear();
vector<WIRE>   wire_container;
vector<STRIP>  strip_container;
vector<COMPARATOR> com_container;

//==========================Get event list for display================
ifstream file(eventlistFile);
while (file)
 {
     string line;
     getline(file, line);
     istringstream is(line);
     while (is) {

           int data;
           is >> data;
           eventList.push_back(data);

           }

  }

CSCDetID chamberID;

if (chamberType == "ME11"){

   chamberID.Endcap = 1;
   chamberID.Station = 1;
   chamberID.Ring = 1;
   chamberID.Chamber = 1;
   thisChamber = 1;


   }else if(chamberType == "ME21"){

           chamberID.Endcap = 1;
           chamberID.Station = 2;
           chamberID.Ring = 1;
           chamberID.Chamber = 2;
		   thisChamber = 110;

           }
//========================== WIRES ========================
edm::Handle<CSCWireDigiCollection> wires;
iEvent.getByLabel(wireDigiTag,wires);

for (CSCWireDigiCollection::DigiRangeIterator wi=wires->begin(); wi!=wires->end(); wi++) {
    CSCDetId id = (CSCDetId)(*wi).first;
    std::vector<CSCWireDigi>::const_iterator wireIt = (*wi).second.first;
    std::vector<CSCWireDigi>::const_iterator lastWire = (*wi).second.second;

    if (thisChamber!=getChamberSerial(id)) continue;

    CSCDetID tmpID;
    WIRE tmpWIRE;

    tmpID.Endcap = id.endcap();
    tmpID.Ring = id.ring()==4 ? 1 : id.ring();
    tmpID.Station = id.station();
    tmpID.Chamber = id.chamber();
    tmpID.Layer = id.layer();


    for( ; wireIt != lastWire; ++wireIt){

       Wire tmpWG;

       tmpWG.WireGroup = wireIt->getWireGroup();
       tmpWG.TimeBin = wireIt->getTimeBin();
       tmpWG.NumberTimeBin = int((wireIt->getTimeBinsOn()).size());

       tmpWIRE.second.push_back(tmpWG);

       }// all wires
  
    tmpWIRE.first = tmpID;
    wire_container.push_back(tmpWIRE); 
}	//all layers for wires		



//========================== STRIPS ========================

edm::Handle<CSCStripDigiCollection> strips;
iEvent.getByLabel(stripDigiTag,strips);

for (CSCStripDigiCollection::DigiRangeIterator si=strips->begin(); si!=strips->end(); si++) {
    CSCDetId id = (CSCDetId)(*si).first;
    std::vector<CSCStripDigi>::const_iterator stripIt = (*si).second.first;
    std::vector<CSCStripDigi>::const_iterator lastStrip = (*si).second.second;

    if (thisChamber!=getChamberSerial(id)) continue;

    CSCDetID tmpID;
    STRIP tmpSTRIP;

    tmpID.Endcap = id.endcap();
    tmpID.Ring = id.ring()==4 ? 1 : id.ring();//if me11a, set its ring=1
    tmpID.Station = id.station();
    tmpID.Chamber = id.chamber();
    tmpID.Layer = id.layer();

    for( ; stripIt != lastStrip; ++stripIt) {

       Strips tmpSP;

       tmpSP.Strip = stripIt->getStrip();
       if (id.ring() == 4) tmpSP.Strip+=32;//for now ME11A only shift 2cfeb, BECAUSE GIF ME11A ONLY HAS dcfeb 1,5,7

       std::vector<int> myADCVals = stripIt->getADCCounts();
       int adcTotal, maxADC, adcMaxTime;
       double ped = 0.5*(myADCVals[0]+myADCVals[1]);   

       adcTotal = 0; maxADC = 0; adcMaxTime = 0;
      
       for (int i = 2; i < int(myADCVals.size()); i++){

           double tmpADC = myADCVals[i]-ped;
           adcTotal+=tmpADC;

           if (tmpADC > maxADC && tmpADC > 13.3){

              maxADC = tmpADC;
              adcMaxTime = i;
 
              }

           }//loop over all 6 time bins for each strip, from 2 to 7

       tmpSP.ADCTotal = adcTotal;
       tmpSP.MaxADC = maxADC;
       tmpSP.ADCMaxTime = adcMaxTime;

       tmpSTRIP.second.push_back(tmpSP);
    }   

    tmpSTRIP.first = tmpID;
    strip_container.push_back(tmpSTRIP);

}//strip collection

//==========COMPARATOR=========================


edm::Handle<CSCComparatorDigiCollection> comparators;
iEvent.getByLabel(comparatorDigiTag,comparators);


for (CSCComparatorDigiCollection::DigiRangeIterator com=comparators->begin(); com!=comparators->end(); com++) {

    CSCDetId id = (CSCDetId)(*com).first;
    std::vector<CSCComparatorDigi>::const_iterator comparatorIt = (*com).second.first;
    std::vector<CSCComparatorDigi>::const_iterator lastComparator = (*com).second.second;

    if (thisChamber!=getChamberSerial(id)) continue;

    CSCDetID tmpID;
    
    COMPARATOR tmpCOMPARATOR;

    tmpID.Endcap = id.endcap();
    tmpID.Ring = id.ring()==4 ? 1 : id.ring();
    tmpID.Station = id.station();
    tmpID.Chamber = id.chamber();
    tmpID.Layer = id.layer();

    for( ; comparatorIt != lastComparator; ++comparatorIt) {

       Comparator tmpCOM;   

       tmpCOM.Strip = comparatorIt->getStrip();
       if (id.ring() == 4) tmpCOM.Strip+=32; //gif for now, same reason as strip
       tmpCOM.TimeBin = comparatorIt->getTimeBin();
       tmpCOM.ComparatorNumber = comparatorIt->getComparator();
       if (id.ring() == 4) tmpCOM.ComparatorNumber+=64;

       tmpCOMPARATOR.second.push_back(tmpCOM);

       }


    tmpCOMPARATOR.first = tmpID;
    com_container.push_back(tmpCOMPARATOR);

}//comparator collection


//make event display
vector<CSCDetID> usedChamber;

//if (Event < 500){//find(eventList.begin(), eventList.end(), Event) != eventList.end()){
if (find(eventList.begin(), eventList.end(), Event) != eventList.end()){

   WireStripDisplay(eventDisplayDir, chamberID, wire_container, strip_container, com_container, usedChamber, Run, Event);

   }






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
GifDisplay::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
GifDisplay::endJob() 
{

}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
GifDisplay::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}


//define this as a plug-in
DEFINE_FWK_MODULE(GifDisplay);
