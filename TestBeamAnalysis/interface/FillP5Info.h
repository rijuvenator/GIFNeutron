#ifndef FILLP5INFO_H
#define FILLP5INFO_H

#include "Gif/TestBeamAnalysis/interface/TreeContainer.h"

class FillP5Info
{
	public:
		FillP5Info(TreeContainer &tree) :
			fTree(&tree)
		{
			reset();
		}
		virtual ~FillP5Info() {};
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
		TreeContainer *fTree;
};

class FillP5EventInfo : public FillP5Info
{
	public:
		FillP5EventInfo(TreeContainer &tree) : FillP5Info(tree)
		{
			book("sT", sT, "F");
		}
		virtual ~FillP5EventInfo() {};
		void fill(float sT_);
	private:
		float sT;

		virtual void reset()
		{
			sT = -999.;
		}
};

class FillP5MuonInfo : public FillP5Info
{
	public:
		FillP5MuonInfo(TreeContainer &tree) : FillP5Info(tree)
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
	private:
		std::vector<int>                             muon_charge;
		std::vector<double>                          muon_pT;
		std::vector<double>                          muon_eta;
		std::vector<double>                          muon_phi;
		std::vector<double>                          muon_pZ;
		std::vector<std::vector<unsigned short int>> muon_chamlist;

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

class FillP5ZInfo : public FillP5Info
{
	public:
		FillP5ZInfo(TreeContainer &tree) : FillP5Info(tree)
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
