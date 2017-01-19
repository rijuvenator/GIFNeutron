// user include files

#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Framework/interface/ESHandle.h"



#include "Gif/TestBeamAnalysis/include/FillGIFInfo.h"



using namespace std;

class MakeSimpleGIFTree : public edm::EDAnalyzer {
    public:
		const CSCGeometry *theCSC;
        explicit MakeSimpleGIFTree(const edm::ParameterSet&);
        ~MakeSimpleGIFTree();


    private:
        virtual void beginJob() {};
        virtual void analyze(const edm::Event&, const edm::EventSetup&);
        virtual void endJob() {};


    private:
        edm::EDGetTokenT<CSCRecHit2DCollection> rh_token;
        edm::EDGetTokenT<CSCStripDigiCollection> sd_token;
        edm::EDGetTokenT<CSCComparatorDigiCollection> cod_token;
        edm::EDGetTokenT<CSCWireDigiCollection> wd_token;
        edm::EDGetTokenT<CSCCorrelatedLCTDigiCollection> ld_token;
        edm::EDGetTokenT<CSCSegmentCollection> seg_token;
        edm::EDGetTokenT<CSCCLCTDigiCollection> cd_token;
        edm::EDGetTokenT<CSCALCTDigiCollection> ad_token;
		edm::EDGetTokenT<reco::MuonCollection> mu_token;


        GifTreeContainer tree;
        FillGIFEventInfo eventInfo;
        FillGIFRecHitInfo recHitInfo;
        FillGIFStripInfo recStripInfo;
        FillGIFCompInfo compInfo;
        FillGIFWireInfo wireInfo;
        FillGIFLCTInfo lctInfo;
        FillGIFSegmentInfo segmentInfo;
        FillGIFCLCTInfo clctInfo;
        FillGIFALCTInfo alctInfo;

};


MakeSimpleGIFTree::MakeSimpleGIFTree(const edm::ParameterSet& iConfig) :
    tree(/*iConfig.getUntrackedParameter<std::string>("NtupleFileName"),*/"GIFDigiTree","Tree holding CSCDigis")
//Turn on branch filling
  , eventInfo(tree)
  , recHitInfo(tree)
  , recStripInfo(tree)
  , compInfo(tree)
  , wireInfo(tree)
  , lctInfo(tree)
  , segmentInfo(tree)
  , clctInfo(tree)
  , alctInfo(tree)
{
      rh_token = consumes<CSCRecHit2DCollection>( iConfig.getParameter<edm::InputTag>("recHitTag") );
      sd_token = consumes<CSCStripDigiCollection>( iConfig.getParameter<edm::InputTag>("stripDigiTag") );
      cod_token = consumes<CSCComparatorDigiCollection>( iConfig.getParameter<edm::InputTag>("compDigiTag") );
      wd_token = consumes<CSCWireDigiCollection>( iConfig.getParameter<edm::InputTag>("wireDigiTag") );
      ld_token = consumes<CSCCorrelatedLCTDigiCollection>( iConfig.getParameter<edm::InputTag>("lctDigiTag") );
      seg_token  = consumes<CSCSegmentCollection>(iConfig.getParameter<edm::InputTag>("segmentTag")) ;
      cd_token = consumes<CSCCLCTDigiCollection>( iConfig.getParameter<edm::InputTag>("clctDigiTag") );
      ad_token = consumes<CSCALCTDigiCollection>( iConfig.getParameter<edm::InputTag>("alctDigiTag") );
	  mu_token = consumes<reco::MuonCollection>( iConfig.getParameter<edm::InputTag>("muonCollection") );
      //edm::Service<TFileService> fs;
}


MakeSimpleGIFTree::~MakeSimpleGIFTree() {tree.write();}


void
MakeSimpleGIFTree::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
	//
	// Get Muon Stuff
	edm::Handle<reco::MuonCollection> muons;
	iEvent.getByToken(mu_token, muons);
	// Find Good Muons
	for (auto &muon : *muons) {
		std::cout << "Muon pT " << muon.pt() << std::endl;
	}
	// Make Z candidate
	// Cut on cuts
	//
	// Loop on selected muons
	// get matched chamber lists

	/*
	eventInfo.fill(iEvent);

	edm::Handle<CSCRecHit2DCollection> recHits;
	iEvent.getByToken( rh_token, recHits );
	recHitInfo.fill(*recHits);

	edm::Handle<CSCStripDigiCollection> cscStripDigi;
	iEvent.getByToken(sd_token,cscStripDigi);
	recStripInfo.fill(*cscStripDigi);

	//if(cscStripDigi->begin() == cscStripDigi->end())
	//cout << "Error!"<<endl;

	edm::Handle<CSCComparatorDigiCollection> compDigi;
	iEvent.getByToken(cod_token, compDigi);
	compInfo.fill(*compDigi);

	edm::Handle<CSCWireDigiCollection> cscWireDigi;
	iEvent.getByToken(wd_token,cscWireDigi);
	wireInfo.fill(*cscWireDigi);

	edm::Handle<CSCCorrelatedLCTDigiCollection> cscLCTDigi;
	iEvent.getByToken(ld_token, cscLCTDigi);
	lctInfo.fill(*cscLCTDigi);

	edm::ESHandle<CSCGeometry> cscGeom;
	iSetup.get<MuonGeometryRecord>().get(cscGeom);
	theCSC = cscGeom.product();
	edm::Handle<CSCSegmentCollection> cscSegments;
	iEvent.getByToken(seg_token, cscSegments);
	segmentInfo.fill(theCSC,*cscSegments,&(*recHits));

	edm::Handle<CSCCLCTDigiCollection> cscCLCTDigi;
	iEvent.getByToken(cd_token, cscCLCTDigi);
	clctInfo.fill(*cscCLCTDigi);

	edm::Handle<CSCALCTDigiCollection> cscALCTDigi;
	iEvent.getByToken(ad_token, cscALCTDigi);
	alctInfo.fill(*cscALCTDigi);


	tree.fill();
	*/
}



//define this as a plug-in
DEFINE_FWK_MODULE(MakeSimpleGIFTree);
