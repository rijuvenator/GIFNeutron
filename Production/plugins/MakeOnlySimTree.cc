// user include files

#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Framework/interface/ESHandle.h"

//#include "Gif/Production/interface/FillGIFInfo.h"
#include "Gif/Production/interface/FillSimInfo.h"

using namespace std;

class MakeSimpleNeutronSimTree : public edm::EDAnalyzer {
    public:
		const CSCGeometry *theCSC;
        explicit MakeSimpleNeutronSimTree(const edm::ParameterSet&);
        ~MakeSimpleNeutronSimTree();

    private:
        virtual void beginJob() {};
        virtual void analyze(const edm::Event&, const edm::EventSetup&);
        virtual void endJob() {};

    private:
		// CSC
        //edm::EDGetTokenT<CSCRecHit2DCollection> rh_token;
        //edm::EDGetTokenT<CSCStripDigiCollection> sd_token;
        //edm::EDGetTokenT<CSCComparatorDigiCollection> cod_token;
        //edm::EDGetTokenT<CSCWireDigiCollection> wd_token;
        //edm::EDGetTokenT<CSCCorrelatedLCTDigiCollection> ld_token;
        //edm::EDGetTokenT<CSCSegmentCollection> seg_token;
        //edm::EDGetTokenT<CSCCLCTDigiCollection> cd_token;
        //edm::EDGetTokenT<CSCALCTDigiCollection> ad_token;
		// Sim
		edm::EDGetTokenT<edm::PSimHitContainer> sim_token;

        TreeContainer tree;
        //FillGIFEventInfo eventInfo;
        //FillGIFRecHitInfo recHitInfo;
        //FillGIFStripInfo recStripInfo;
        //FillGIFCompInfo compInfo;
        //FillGIFWireInfo wireInfo;
        //FillGIFLCTInfo lctInfo;
        //FillGIFSegmentInfo segmentInfo;
        //FillGIFCLCTInfo clctInfo;
        //FillGIFALCTInfo alctInfo;
		// Sim
		FillSimHitInfo simHitInfo;

};

MakeSimpleNeutronSimTree::MakeSimpleNeutronSimTree(const edm::ParameterSet& iConfig) :
    tree("GIFDigiTree","Tree holding CSCDigis"/*,"test.root"*/)
//  , eventInfo(tree)
//  , recHitInfo(tree)
//  , recStripInfo(tree)
//  , compInfo(tree)
//  , wireInfo(tree)
//  , lctInfo(tree)
//  , segmentInfo(tree)
//  , clctInfo(tree)
//  , alctInfo(tree)
  , simHitInfo(tree)
{
	// CSC
    //rh_token = consumes<CSCRecHit2DCollection>( iConfig.getParameter<edm::InputTag>("recHitTag") );
    //sd_token = consumes<CSCStripDigiCollection>( iConfig.getParameter<edm::InputTag>("stripDigiTag") );
    //cod_token = consumes<CSCComparatorDigiCollection>( iConfig.getParameter<edm::InputTag>("compDigiTag") );
    //wd_token = consumes<CSCWireDigiCollection>( iConfig.getParameter<edm::InputTag>("wireDigiTag") );
    //ld_token = consumes<CSCCorrelatedLCTDigiCollection>( iConfig.getParameter<edm::InputTag>("lctDigiTag") );
    //seg_token  = consumes<CSCSegmentCollection>(iConfig.getParameter<edm::InputTag>("segmentTag")) ;
    //cd_token = consumes<CSCCLCTDigiCollection>( iConfig.getParameter<edm::InputTag>("clctDigiTag") );
    //ad_token = consumes<CSCALCTDigiCollection>( iConfig.getParameter<edm::InputTag>("alctDigiTag") );
	// Sim
	sim_token = consumes<edm::PSimHitContainer>( iConfig.getParameter<edm::InputTag>("simHitTag") );
    //edm::Service<TFileService> fs;
}


MakeSimpleNeutronSimTree::~MakeSimpleNeutronSimTree() {tree.write();}


void
MakeSimpleNeutronSimTree::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{

	edm::ESHandle<CSCGeometry> cscGeom;
	iSetup.get<MuonGeometryRecord>().get(cscGeom);
	theCSC = cscGeom.product();
/*
	eventInfo.fill(iEvent);

	edm::Handle<CSCRecHit2DCollection> recHits;
	iEvent.getByToken( rh_token, recHits );
	recHitInfo.fill(theCSC, *recHits);

	edm::Handle<CSCStripDigiCollection> cscStripDigi;
	iEvent.getByToken(sd_token,cscStripDigi);
	recStripInfo.fill(*cscStripDigi);

	// Printout if strip digi container is empty
	//if(cscStripDigi->begin() == cscStripDigi->end())
	//cout << "Error!"<<endl;

	edm::Handle<CSCComparatorDigiCollection> compDigi;
	iEvent.getByToken(cod_token, compDigi);
	compInfo.fill(theCSC, *compDigi);

	edm::Handle<CSCWireDigiCollection> cscWireDigi;
	iEvent.getByToken(wd_token,cscWireDigi);
	wireInfo.fill(theCSC, *cscWireDigi);

	edm::Handle<CSCCorrelatedLCTDigiCollection> cscLCTDigi;
	iEvent.getByToken(ld_token, cscLCTDigi);
	lctInfo.fill(*cscLCTDigi);

	edm::Handle<CSCSegmentCollection> cscSegments;
	iEvent.getByToken(seg_token, cscSegments);
	segmentInfo.fill(theCSC,*cscSegments,&(*recHits));

	edm::Handle<CSCCLCTDigiCollection> cscCLCTDigi;
	iEvent.getByToken(cd_token, cscCLCTDigi);
	clctInfo.fill(*cscCLCTDigi);

	edm::Handle<CSCALCTDigiCollection> cscALCTDigi;
	iEvent.getByToken(ad_token, cscALCTDigi);
	alctInfo.fill(*cscALCTDigi);
*/
	edm::Handle<edm::PSimHitContainer> simHits;
	iEvent.getByToken(sim_token, simHits );
	simHitInfo.fill(theCSC, *simHits);
	

	tree.fill();
}



//define this as a plug-in
DEFINE_FWK_MODULE(MakeOnlySimTree);
