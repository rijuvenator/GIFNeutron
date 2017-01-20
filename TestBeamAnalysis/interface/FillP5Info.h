#ifndef FILLP5INFO_H
#define FILLP5INFO_H

#include "Gif/TestBeamAnalysis/interface/TreeContainer.h"

class FillP5EventInfo : public FillInfo
{
	public:
		FillP5EventInfo(TreeContainer &tree) : FillInfo(tree)
		{
			book("sT", sT, "F");
			book("nJets", nJets, "I");
		}
		virtual ~FillP5EventInfo() {};
		void fill(float sT_, int nJets_);
	private:
		float sT;
		int nJets;

		virtual void reset()
		{
			sT = -999.;
			nJets = -999.;
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
			book("Z_pT"      , Z_pT      , "F");
			book("Z_rapidity", Z_rapidity, "F");
			book("Z_eta"     , Z_eta     , "F");
			book("Z_phi"     , Z_phi     , "F");
			book("Z_pZ"      , Z_pZ      , "F");
			book("Z_mass"    , Z_mass    , "F");
		}
		virtual ~FillP5ZInfo() {};
		void fill(const std::vector<reco::Muon> &muons);
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
