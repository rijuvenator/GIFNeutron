#include "Gif/Production/interface/FillP5Info.h"

//void FillP5EventInfo::fill(float sT_, int nJets0_, int nJets10_, int nJets20_, int Ht0_, int Ht10_, int Ht20_, const reco::PFMET met)
void FillP5EventInfo::fill(float sT_, int nJets0_, int nJets10_, int nJets20_, float Ht0_, float Ht10_, float Ht20_)
{
	reset();
	sT = sT_;
	nJets0 = nJets0_;
	nJets10 = nJets10_;
	nJets20 = nJets20_;
	Ht0 = Ht0_;
	Ht10 = Ht10_;
	Ht20 = Ht20_;
	//met_pT = met.pt();
	//met_phi = met.phi();
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

//void FillP5ZInfo::fill(const std::vector<reco::Muon> &muons)
void FillP5ZInfo::fill(const TLorentzVector &Z)
{
	reset();
	//ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double>> Z = muons[0].p4() + muons[1].p4();
	Z_pT       = Z.Pt()  ;
	Z_rapidity = Z.Rapidity()   ;
	Z_eta      = Z.Eta() ;
	Z_phi      = Z.Phi() ;
	Z_pZ       = Z.Pz()  ;
	Z_mass     = Z.M();
}

