#include "Gif/TestBeamAnalysis/interface/FillP5Info.h"

void FillP5EventInfo::fill(float sT_, int nJets_)
{
	reset();
	sT = sT_;
	nJets = nJets_;
}

void FillP5MuonInfo::fill(const std::vector<reco::Muon> &muons)
{
	reset();

	for (auto &muon : muons)
	{
		muon_charge.push_back(muon.charge());
		muon_pT    .push_back(muon.pt());
		muon_eta   .push_back(muon.eta());
		muon_phi   .push_back(muon.phi());
		muon_pZ    .push_back(muon.pz() );

		std::vector<unsigned short int> chambers;
		for (auto &match : muon.matches())
		{
			if (match.detector() != MuonSubdetId::CSC) continue;
			CSCDetId cscId(match.id);
			unsigned short int id = GIFHelper::chamberSerial(cscId);
			chambers.push_back(id);
		}
		muon_chamlist.push_back(chambers);
		chambers.clear();
	}
}

void FillP5ZInfo::fill(const std::vector<reco::Muon> &muons)
{
	reset();
	ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double>> Z = muons[0].p4() + muons[1].p4();
	Z_pT       = Z.pt()  ;
	Z_rapidity = Z.y()   ;
	Z_eta      = Z.eta() ;
	Z_phi      = Z.phi() ;
	Z_pZ       = Z.pz()  ;
	Z_mass     = Z.mass();
}

