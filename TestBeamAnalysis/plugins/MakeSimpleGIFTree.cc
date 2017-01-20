// user include files

#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Framework/interface/ESHandle.h"

#include "Gif/TestBeamAnalysis/interface/FillGIFInfo.h"
#include "Gif/TestBeamAnalysis/interface/FillP5Info.h"

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
		// Physics
		edm::EDGetTokenT<reco::VertexCollection> vtx_token;
		edm::EDGetTokenT<reco::MuonCollection> mu_token;
		edm::EDGetTokenT<reco::GsfElectron> el_token;
		edm::EDGetTokenT<reco::Photon> ph_token;
		edm::EDGetTokenT<reco::PFMET> met_token;
		edm::EDGetTokenT<reco::PFJet> jet_token;
		// CSC
        edm::EDGetTokenT<CSCRecHit2DCollection> rh_token;
        edm::EDGetTokenT<CSCStripDigiCollection> sd_token;
        edm::EDGetTokenT<CSCComparatorDigiCollection> cod_token;
        edm::EDGetTokenT<CSCWireDigiCollection> wd_token;
        edm::EDGetTokenT<CSCCorrelatedLCTDigiCollection> ld_token;
        edm::EDGetTokenT<CSCSegmentCollection> seg_token;
        edm::EDGetTokenT<CSCCLCTDigiCollection> cd_token;
        edm::EDGetTokenT<CSCALCTDigiCollection> ad_token;

        TreeContainer tree;
        FillGIFEventInfo eventInfo;
        FillGIFRecHitInfo recHitInfo;
        FillGIFStripInfo recStripInfo;
        FillGIFCompInfo compInfo;
        FillGIFWireInfo wireInfo;
        FillGIFLCTInfo lctInfo;
        FillGIFSegmentInfo segmentInfo;
        FillGIFCLCTInfo clctInfo;
        FillGIFALCTInfo alctInfo;
		FillP5Info p5Info;
		FillP5MuonInfo muonInfo;
		FillP5ZInfo zInfo;

};

MakeSimpleGIFTree::MakeSimpleGIFTree(const edm::ParameterSet& iConfig) :
    tree("GIFDigiTree","Tree holding CSCDigis")
  , eventInfo(tree)
  , recHitInfo(tree)
  , recStripInfo(tree)
  , compInfo(tree)
  , wireInfo(tree)
  , lctInfo(tree)
  , segmentInfo(tree)
  , clctInfo(tree)
  , alctInfo(tree)
  , p5Info(tree)
  , muonInfo(tree)
  , zInfo(tree)
{
	// Physics
	vtx_token = consumes<reco::VertexCollection>( iConfig.getParameter<edm::InputTag>("vertices") );
	mu_token = consumes<reco::MuonCollection>( iConfig.getParameter<edm::InputTag>("muonCollection") );
	el_token = consumes<reco::GsfElectron>( iConfig.getParameter<edm::InputTag>("electronCollection") );
	ph_token = consumes<reco::Photon>( iConfig.getParameter<edm::InputTag>("photonCollection") );
	met_token = consumes<reco::PFMET>( iConfig.getParameter<edm::InputTag>("metCollection") );
	jet_token = consumes<reco::PFJet>( iConfig.getParajeter<edm::InputTag>("jetCollection") );
	// CSC
    rh_token = consumes<CSCRecHit2DCollection>( iConfig.getParameter<edm::InputTag>("recHitTag") );
    sd_token = consumes<CSCStripDigiCollection>( iConfig.getParameter<edm::InputTag>("stripDigiTag") );
    cod_token = consumes<CSCComparatorDigiCollection>( iConfig.getParameter<edm::InputTag>("compDigiTag") );
    wd_token = consumes<CSCWireDigiCollection>( iConfig.getParameter<edm::InputTag>("wireDigiTag") );
    ld_token = consumes<CSCCorrelatedLCTDigiCollection>( iConfig.getParameter<edm::InputTag>("lctDigiTag") );
    seg_token  = consumes<CSCSegmentCollection>(iConfig.getParameter<edm::InputTag>("segmentTag")) ;
    cd_token = consumes<CSCCLCTDigiCollection>( iConfig.getParameter<edm::InputTag>("clctDigiTag") );
    ad_token = consumes<CSCALCTDigiCollection>( iConfig.getParameter<edm::InputTag>("alctDigiTag") );
    //edm::Service<TFileService> fs;
}


MakeSimpleGIFTree::~MakeSimpleGIFTree() {tree.write();}


void
MakeSimpleGIFTree::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
	// Check if a primary vertex exists
	edm::Handle<reco::VertexCollection> vertices;
	iEvent.getByToken(vtx_token, vertices);
	if (vertices->empty()) return;
	const reco::Vertex &PV = vertices->front();
	
	// Get Met
	edm::Handle<reco::PFMET> mets;
	iEvent.getByToken(met_token, mets);
	const reco::MET &met = mets->front();
	
	// Get Electrons
	edm::Handle<reco::GsfElectron> electrons;
	iEvent.getByToken(el_token, electrons);

	// Get Photons
	edm::Handle<reco::Photon> photons;
	iEvent.getByToken(ph_token, photons);

	// Get Jets
	edm::Handle<reco::PFJets> jets;
	iEvent.getByToken(jet_token, jets);

	int nJets = 0;
	for (auto &jet : *jets) {
		if (j.pt() < 30) continue;
		nJets++;
	}
	
	// Get Muons
	edm::Handle<reco::MuonCollection> muons;
	iEvent.getByToken(mu_token, muons);

	// Find Good Muons
	int itmu1 = 0;
	int itmu2 = 0;
	const reco::Muon cMuon1;
	const reco::Muon cMuon2;
	bool found = false;
	
	// Hopefully it's safe to assume that the muons in the MuonCollection are sorted by pT...
	// otherwise this algo doesn't choose the two highest pT opposite sign dimuons passing the selection
	for (auto &muon1 : *muons) {
		itmu1++;
		// Muon1 cuts
		if ( !(muon1.pt > 30) ) continue;
		if ( !muon::isHighPtMuon(muon1, PV) ) continue;
		if ( !(muon1.isolationR03().sumPt()/muon1.innerTrack().pt() < 0.1) ) continue;

		for (auto &muon2 : *muons) {
			itmu2++;
			// Avoid double counting?
			if (!(itmu1>itmu2)) continue;
			// Muon2 cuts
			if ( !(muon1.pt > 30) ) continue;
			if ( !muon::isHighPtMuon(muon2, PV) ) continue;
			if ( !(muon2.isolationR03().sumPt()/muon2.innerTrack().pt() < 0.1) ) continue;

			// Dimuon cuts; opposite sign, mass window
			if ( !(muon1.charge()*muon2.charge()<0) )  continue;
			if ( !( (muon1.p4()+muon2.p4()).mass() > 60 && (muon1.p4()+muon2.p4()).mass() < 120 ) ) continue;
			// Need at least one muon in a CSC
			if ( !(fabs(muon1.eta()) > 0.9||fabs(muon2.eta()) > 0.9) ) continue;

			// Choose these muons
			cMuon1 = muon1;
			cMuon2 = muon2;
			found = true;
			break;
		}
		if (found) break;
	}

	// Skip event if no dimuon is found with selection criteria
	if (!found) return;

	std::vector<reco::Muon> chosenMuons = {cMuon1,cMuon2};
	muonInfo.fill(chosenMuons);
	ZInfo.fill(chosenMuons);

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
}



//define this as a plug-in
DEFINE_FWK_MODULE(MakeSimpleGIFTree);
