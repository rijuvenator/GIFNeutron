#ifndef TREECONTAINER_H
#define TREECONTAINER_H

#include <algorithm>

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/CSCRecHit/interface/CSCRecHit2DCollection.h"
#include "DataFormats/CSCDigi/interface/CSCStripDigiCollection.h"
#include "DataFormats/CSCDigi/interface/CSCWireDigiCollection.h"
#include "DataFormats/CSCDigi/interface/CSCComparatorDigiCollection.h"
#include "DataFormats/CSCDigi/interface/CSCCorrelatedLCTDigiCollection.h"
#include "DataFormats/CSCRecHit/interface/CSCSegmentCollection.h"
#include "DataFormats/CSCDigi/interface/CSCCLCTDigiCollection.h"
#include "DataFormats/CSCDigi/interface/CSCALCTDigiCollection.h"
#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/MuonReco/interface/MuonIsolation.h"
#include "DataFormats/MuonReco/interface/MuonSelectors.h"
#include "DataFormats/MuonReco/interface/MuonFwd.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidateFwd.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/JetReco/interface/Jet.h"
#include "DataFormats/JetReco/interface/PFJet.h"
#include "DataFormats/JetReco/interface/PFJetCollection.h"
#include "JetMETCorrections/JetCorrector/interface/JetCorrector.h"
#include "DataFormats/METReco/interface/MET.h"
#include "DataFormats/METReco/interface/PFMET.h"
#include "DataFormats/METReco/interface/METCollection.h"
#include "DataFormats/METReco/interface/PFMETCollection.h"
#include "DataFormats/EgammaCandidates/interface/Photon.h"
#include "DataFormats/EgammaCandidates/interface/PhotonFwd.h"
#include "DataFormats/EgammaCandidates/interface/Electron.h"
#include "DataFormats/EgammaCandidates/interface/GsfElectron.h"
#include "DataFormats/EgammaCandidates/interface/GsfElectronFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/RecoCandidate/interface/RecoCandidate.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "Geometry/CSCGeometry/interface/CSCGeometry.h"
#include "Geometry/Records/interface/MuonGeometryRecord.h"

#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TLorentzVector.h"

#include "DataFormats/Math/interface/deltaPhi.h"
#include "DataFormats/Math/interface/deltaR.h"

#include "Gif/TestBeamAnalysis/interface/GIFHelper.h"

typedef	unsigned char		 size8 ; // 8 bit 0->255
typedef	unsigned short int	 size16; //16 bit 0->65536
typedef	unsigned int		 size  ; //32 bit 0->4294967296

class TreeContainer
{
	public:
		TreeContainer(TString treeName, TString treeTitle/*, TString fileName*/){
			edm::Service<TFileService> fs;
			//file = fs->make<TFile>(fileName, "RECREATE");
			tree = fs->make<TTree>(treeName,treeTitle);
		}
		void write() {
			//file->cd();
			tree->Write();
			//file->Close();
			//delete file;
		}
		void fill() {tree->Fill();}
		//TFile * file;
		TTree * tree;
};

class FillInfo
{
	public:
		FillInfo(TreeContainer &tree) :
			fTree(&tree)
		{
			reset();
		}
		virtual ~FillInfo() {};
		bool isInChamlist(unsigned short int id, std::vector<std::vector<unsigned short int>> &chamlist);
	protected:
		virtual void reset() {};
		template<class T>
		void book(const char *name, T &var, const char *type) // Book variable
		{
			fTree->tree->Branch(name, &var, TString(name).Append("/").Append(type).Data());
		}

		template <class T>
		void book(const char *name, std::vector<T> &varv) // Book vector
		{
			fTree->tree->Branch(name, &varv);
		}
		TreeContainer * fTree;
};

#endif
