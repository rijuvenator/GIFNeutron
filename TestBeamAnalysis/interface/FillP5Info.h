#ifndef FILLP5INFO_H
#define FILLP5INFO_H

#include "Gif/TestBeamAnalysis/interface/TreeContainer.h"

class FillP5EventInfo : public FillInfo
{
	public:
		FillP5EventInfo(TreeContainer &tree) : FillInfo(tree)
		{
			book("sT", sT, "F");
			book("nJets0", nJets0, "I");
			book("nJets10", nJets10, "I");
			book("nJets20", nJets20, "I");
			book("Ht0", Ht0, "F");
			book("Ht10", Ht10, "F");
			book("Ht20", Ht20, "F");
			//book("met_pT", met_pT, "F");
			//book("met_phi", met_phi, "F");
		}
		virtual ~FillP5EventInfo() {};
		void fill(float sT_, int nJets0_, int nJets10_, int nJets20_, float Ht0_, float Ht10_, float Ht20_);
		//void fill(float sT_, int nJets0_, int nJets10_, int nJets20_, int Ht0_, int Ht10_, int Ht20_, const reco::PFMET met);
	private:
		float sT;
		int nJets0;
		int nJets10;
		int nJets20;
		float Ht0;
		float Ht10;
		float Ht20;
		//float met_pT;
		//float met_phi;


		virtual void reset()
		{
			sT = -999.;
			nJets0 = -999.;
			nJets10 = -999.;
			nJets20 = -999.;
			Ht0 = -999.;
			Ht10 = -999.;
			Ht20 = -999.;
			//met_pT = -999.;
			//met_phi = -999.;
		}
};

class FillP5MuonInfo : public FillInfo
{
	public:
		FillP5MuonInfo(TreeContainer &tree) : FillInfo(tree)
		{
			book("muon_charge"  , muon_charge  );
			book("muon_pT"      , muon_pT      );
			book("muon_eta"     , muon_eta     );
			book("muon_phi"     , muon_phi     );
			book("muon_pZ"      , muon_pZ      );
			book("muon_chamlist", muon_chamlist);
		}
		virtual ~FillP5MuonInfo() {};
		void fill(const std::vector<reco::Muon> &muons);
		// Important to be public!!!!
		std::vector<std::vector<unsigned short int>> muon_chamlist;

	private:
		std::vector<int>                             muon_charge;
		std::vector<double>                          muon_pT;
		std::vector<double>                          muon_eta;
		std::vector<double>                          muon_phi;
		std::vector<double>                          muon_pZ;

		virtual void reset()
		{
			muon_charge  .clear();
			muon_pT      .clear();
			muon_eta     .clear();
			muon_phi     .clear();
			muon_pZ      .clear();
			muon_chamlist.clear();
		}
};

class FillP5ZInfo : public FillInfo
{
	public:
		FillP5ZInfo(TreeContainer &tree) : FillInfo(tree)
		{
			book("Z_pT"      , Z_pT      , "D");
			book("Z_rapidity", Z_rapidity, "D");
			book("Z_eta"     , Z_eta     , "D");
			book("Z_phi"     , Z_phi     , "D");
			book("Z_pZ"      , Z_pZ      , "D");
			book("Z_mass"    , Z_mass    , "D");
		}
		virtual ~FillP5ZInfo() {};
		void fill(const TLorentzVector &Z);
		//void fill(const std::vector<reco::Muon> &muons);
	private:
		double Z_pT;
		double Z_rapidity;
		double Z_eta;
		double Z_phi;
		double Z_pZ;
		double Z_mass;

		virtual void reset()
		{
			Z_pT       = -999.;
			Z_rapidity = -999.;
			Z_eta      = -999.;
			Z_phi      = -999.;
			Z_pZ       = -999.;
			Z_mass     = -999.;
		}
};

#endif
