#ifndef FILLGIFINFO_H
#define FILLGIFINFO_H

#include "Gif/TestBeamAnalysis/interface/TreeContainer.h"

class FillGIFEventInfo : public FillInfo
{
	public:
		FillGIFEventInfo(TreeContainer& tree) :FillInfo(tree)
		{
			book("Event_EventNumber",Event_EventNumber,"I");
			book("Event_RunNumber"  ,Event_RunNumber  ,"I");
			book("Event_LumiSection",Event_LumiSection,"I");
			book("Event_BXCrossing" ,Event_BXCrossing ,"I");
		}
		virtual ~FillGIFEventInfo() {};

	private:
		unsigned int Event_EventNumber;
		int Event_RunNumber  ;
		int Event_LumiSection;
		int Event_BXCrossing ;

		virtual void reset()
		{
			Event_EventNumber  = 0;
			Event_RunNumber    = -1;
			Event_LumiSection  = -1;
			Event_BXCrossing   = -1;
		}

	public:
		void fill(const edm::Event& iEvent);
};


class FillGIFRecHitInfo : public FillInfo
{
	public:

		FillGIFRecHitInfo(TreeContainer& tree) :FillInfo(tree)
		{
			book("rh_id"           ,rh_id           );
			book("rh_lay"          ,rh_lay          );
			book("rh_pos_x"        ,rh_pos_x        );
			book("rh_pos_y"        ,rh_pos_y        );
			book("rh_pos_err_xx"   ,rh_pos_err_xx   );
			book("rh_pos_err_xy"   ,rh_pos_err_xy   );
			book("rh_pos_err_yy"   ,rh_pos_err_yy   );
			book("rh_strip_1"      ,rh_strip_1      );
			book("rh_strip_2"      ,rh_strip_2      );
			book("rh_strip_3"      ,rh_strip_3      );
			book("rh_pos_strip"    ,rh_pos_strip    );
			book("rh_pos_strip_err",rh_pos_strip_err);
			book("rh_n_wiregroups" ,rh_n_wiregroups );
			book("rh_energy"       ,rh_energy       );
			book("rh_wireGrp"      ,rh_wireGrp      );
			book("rh_n_timebins"   ,rh_n_timebins   );
			book("rh_n_strips"     ,rh_n_strips     );
			book("rh_adc3x3_Qsum"  ,rh_adc3x3_Qsum  );
			book("rh_lr_Qratio"    ,rh_lr_Qratio    );
			book("rh_tpeak"        ,rh_tpeak        );
			book("rh_wireTime"     ,rh_wireTime     );
			book("rh_adc_max"      ,rh_adc_max      );
		}
		virtual ~FillGIFRecHitInfo() {};

	private:
		std::vector<size16> rh_id ;
		std::vector<size8>  rh_lay ;
		std::vector<float>  rh_pos_x ;
		std::vector<float>  rh_pos_y ;
		std::vector<float>  rh_pos_err_xx;
		std::vector<float>  rh_pos_err_xy;
		std::vector<float>  rh_pos_err_yy;
		std::vector<size8>  rh_strip_1;
		std::vector<size8>  rh_strip_2;
		std::vector<size8>  rh_strip_3;
		std::vector<float>  rh_pos_strip ;
		std::vector<float>  rh_pos_strip_err ;
		std::vector<size8>  rh_n_wiregroups;
		std::vector<float>  rh_energy;
		std::vector<size8>  rh_wireGrp;
		std::vector<size8>  rh_n_timebins;
		std::vector<size8>  rh_n_strips;
		std::vector<float>  rh_adc3x3_Qsum;
		std::vector<float>  rh_lr_Qratio;
		std::vector<float>  rh_tpeak;
		std::vector<float>  rh_wireTime;
		std::vector<int>    rh_adc_max;

		virtual void reset()
		{
			rh_id            .clear();
			rh_lay           .clear();
			rh_pos_x         .clear();
			rh_pos_y         .clear();
			rh_pos_err_xx    .clear();
			rh_pos_err_xy    .clear();
			rh_pos_err_yy    .clear();
			rh_strip_1       .clear();
			rh_strip_2       .clear();
			rh_strip_3       .clear();
			rh_pos_strip     .clear();
			rh_pos_strip_err .clear();
			rh_n_wiregroups  .clear();
			rh_energy        .clear();
			rh_wireGrp       .clear();
			rh_n_timebins    .clear();
			rh_n_strips      .clear();
			rh_adc3x3_Qsum   .clear();
			rh_lr_Qratio     .clear();
			rh_tpeak         .clear();
			rh_wireTime      .clear();
			rh_adc_max       .clear();
		}

	public:
		void fill(const CSCRecHit2DCollection& recHits, std::vector<std::vector<unsigned short int>> &chamlist);
};

class FillGIFStripInfo : public FillInfo
{
	public:

		FillGIFStripInfo(TreeContainer& tree) :FillInfo(tree)
		{
			book("strip_id"    ,strip_id    );
			book("strip_lay"   ,strip_lay   );
			book("strip_number",strip_number);
			book("strip_ADC"   ,strip_ADC   );
		}
		virtual ~FillGIFStripInfo() {};

	private:
		std::vector<size16>           strip_id;
		std::vector<size8>            strip_lay;
		std::vector<size8>            strip_number;
		std::vector<std::vector<int>> strip_ADC;

		virtual void reset()
		{
			strip_id    .clear();
			strip_lay   .clear();
			strip_number.clear();
			strip_ADC   .clear();
		}

	public:
		void fill(const CSCStripDigiCollection& strips, std::vector<std::vector<unsigned short int>> &chamlist);
};

class FillGIFCompInfo : public FillInfo
{
	public:

		FillGIFCompInfo(TreeContainer& tree) :FillInfo(tree)
		{
			book("comp_id"    ,comp_id    );
			book("comp_lay"   ,comp_lay   );
			book("comp_strip" ,comp_strip );
			book("comp_comp"  ,comp_comp  );
			book("comp_time"  ,comp_time  );
			book("comp_timeOn",comp_timeOn);
		}
		virtual ~FillGIFCompInfo() {};

	private:
		std::vector<size16>           comp_id;
		std::vector<size8>            comp_lay;
		std::vector<size8>            comp_strip;
		std::vector<size8>            comp_comp;
		std::vector<size8>            comp_time;
		std::vector<std::vector<int>> comp_timeOn;


		virtual void reset()
		{
			comp_id    .clear();
			comp_lay   .clear();
			comp_strip .clear();
			comp_comp  .clear();
			comp_time  .clear();
			comp_timeOn.clear();
		}

	public:
		void fill(const CSCComparatorDigiCollection& comps, std::vector<std::vector<unsigned short int>> &chamlist);
};


class FillGIFWireInfo : public FillInfo
{
	public:
		FillGIFWireInfo(TreeContainer& tree) :FillInfo(tree)
		{
			book("wire_id"  ,wire_id      );
			book("wire_lay" ,wire_lay     );
			book("wire_grp" ,wire_grp     );
			book("wire_time",wire_time    );
			book("wire_bx"  ,wire_bx      );
			book("wire_nlay",wire_nlay,"I");
		}
		virtual ~FillGIFWireInfo() {};

	private:
		std::vector<size16> wire_id  ;
		std::vector<size8>  wire_lay ;
		std::vector<size8>  wire_grp ;
		std::vector<size8>  wire_time;
		std::vector<int>    wire_bx  ;
		int                 wire_nlay;

		virtual void reset()
		{
			wire_id  .clear();
			wire_lay .clear();
			wire_grp .clear();
			wire_time.clear();
			wire_bx  .clear();
			wire_nlay = -1;
		}

	public:
		void fill(const CSCWireDigiCollection& wires, std::vector<std::vector<unsigned short int>> &chamlist);
};


class FillGIFLCTInfo : public FillInfo
{
	public:

		FillGIFLCTInfo(TreeContainer& tree) :FillInfo(tree)
		{
			book("lct_id"          ,lct_id          );
			book("lct_quality"     ,lct_quality     );
			book("lct_pattern"     ,lct_pattern     );
			book("lct_bend"        ,lct_bend        );
			book("lct_keyWireGroup",lct_keyWireGroup);
			book("lct_keyHalfStrip",lct_keyHalfStrip);
		}
		virtual ~FillGIFLCTInfo() {};

	private:
		 std::vector<size16> lct_id ;
		 std::vector<size8>  lct_quality;
		 std::vector<size8>  lct_pattern;
		 std::vector<size8>  lct_bend;
		 std::vector<size8>  lct_keyWireGroup;
		 std::vector<size8>  lct_keyHalfStrip;

		virtual void reset()
		{
			lct_id          .clear();
			lct_quality     .clear();
			lct_pattern     .clear();
			lct_bend        .clear();
			lct_keyWireGroup.clear();
			lct_keyHalfStrip.clear();
		}

	public:
		void fill(const CSCCorrelatedLCTDigiCollection& lcts, std::vector<std::vector<unsigned short int>> &chamlist);
};


class FillGIFSegmentInfo : public FillInfo
{
	public:

		FillGIFSegmentInfo(TreeContainer& tree) :FillInfo(tree)
		{

			book("segment_id"           ,segment_id           );
			book("segment_pos"          ,segment_pos          );
			book("segment_slope"        ,segment_slope        );
			book("segment_slope_prim"   ,segment_slope_prim   );
			book("segment_chisq"        ,segment_chisq        );
			book("segment_dof"          ,segment_dof          );
			book("segment_nHits"        ,segment_nHits        );
			book("segment_quality"      ,segment_quality      );
			book("segment_time"         ,segment_time         );
			book("segment_cov_dxdz"     ,segment_cov_dxdz     );
			book("segment_cov_dxdz_dydz",segment_cov_dxdz_dydz);
			book("segment_cov_dxdz_x"   ,segment_cov_dxdz_x   );
			book("segment_cov_dxdz_y"   ,segment_cov_dxdz_y   );
			book("segment_cov_dydz"     ,segment_cov_dydz     );
			book("segment_cov_dydz_x"   ,segment_cov_dydz_x   );
			book("segment_cov_dydz_y"   ,segment_cov_dydz_y   );
			book("segment_cov_x"        ,segment_cov_x        );
			book("segment_cov_x_y"      ,segment_cov_x_y      );
			book("segment_cov_y"        ,segment_cov_y        );
			book("segment_recHitIdx_1"  ,segment_recHitIdx_1  );
			book("segment_recHitIdx_2"  ,segment_recHitIdx_2  );
			book("segment_recHitIdx_3"  ,segment_recHitIdx_3  );
			book("segment_recHitIdx_4"  ,segment_recHitIdx_4  );
			book("segment_recHitIdx_5"  ,segment_recHitIdx_5  );
			book("segment_recHitIdx_6"  ,segment_recHitIdx_6  );
		}
		virtual ~FillGIFSegmentInfo() {};

	private:
		std::vector<size16>                          segment_id;
		std::vector<std::vector<std::vector<float>>> segment_pos;
		std::vector<std::vector<float>>              segment_slope;
		std::vector<std::vector<std::vector<float>>> segment_slope_prim;
		std::vector<float>                           segment_chisq ;
		std::vector<size8>                           segment_dof ;
		std::vector<size8>                           segment_nHits ;
		std::vector<int>                             segment_quality ;
		std::vector<float>                           segment_time;
		std::vector<float>                           segment_cov_dxdz;
		std::vector<float>                           segment_cov_dxdz_dydz;
		std::vector<float>                           segment_cov_dxdz_x;
		std::vector<float>                           segment_cov_dxdz_y;
		std::vector<float>                           segment_cov_dydz;
		std::vector<float>                           segment_cov_dydz_x;
		std::vector<float>                           segment_cov_dydz_y;
		std::vector<float>                           segment_cov_x;
		std::vector<float>                           segment_cov_x_y;
		std::vector<float>                           segment_cov_y;
		std::vector<size16>                          segment_recHitIdx_1 ;
		std::vector<size16>                          segment_recHitIdx_2 ;
		std::vector<size16>                          segment_recHitIdx_3 ;
		std::vector<size16>                          segment_recHitIdx_4 ;
		std::vector<size16>                          segment_recHitIdx_5 ;
		std::vector<size16>                          segment_recHitIdx_6 ;

		virtual void reset()
		{
			segment_id           .clear();
			segment_pos          .clear();
			segment_slope        .clear();
			segment_slope_prim   .clear();
			segment_chisq        .clear();
			segment_dof          .clear();
			segment_nHits        .clear();
			segment_quality      .clear();
			segment_time         .clear();
			segment_cov_dxdz     .clear();
			segment_cov_dxdz_dydz.clear();
			segment_cov_dxdz_x   .clear();
			segment_cov_dxdz_y   .clear();
			segment_cov_dydz     .clear();
			segment_cov_dydz_x   .clear();
			segment_cov_dydz_y   .clear();
			segment_cov_x        .clear();
			segment_cov_x_y      .clear();
			segment_cov_y        .clear();
			segment_recHitIdx_1  .clear();
			segment_recHitIdx_2  .clear();
			segment_recHitIdx_3  .clear();
			segment_recHitIdx_4  .clear();
			segment_recHitIdx_5  .clear();
			segment_recHitIdx_6  .clear();
		}

	public:
		// if having problems, try defaulting the recHits argument to = 0 (I changed it) --Riju
		void fill(const CSCGeometry * theCSC,const CSCSegmentCollection& segments, const CSCRecHit2DCollection * recHits, std::vector<std::vector<unsigned short int>> &chamlist);
		size16 findRecHitIdx(const CSCRecHit2D& hit, const CSCRecHit2DCollection* allRecHits);
		int segmentQuality(edm::OwnVector<CSCSegment>::const_iterator segment);
};

class FillGIFCLCTInfo : public FillInfo
{
	public:
		FillGIFCLCTInfo(TreeContainer& tree) :FillInfo(tree)
		{
			book("clct_id"       ,clct_id       );
			book("clct_isvalid"  ,clct_isvalid  );
			book("clct_quality"  ,clct_quality  );
			book("clct_pattern"  ,clct_pattern  );
			book("clct_stripType",clct_stripType);
			book("clct_bend"     ,clct_bend     );
			book("clct_halfStrip",clct_halfStrip);
			book("clct_CFEB"     ,clct_CFEB     );
			book("clct_BX"       ,clct_BX       );
			book("clct_trkNumber",clct_trkNumber);
			book("clct_keyStrip" ,clct_keyStrip );
		}
		virtual ~FillGIFCLCTInfo() {};

	private:
		std::vector<size16> clct_id;
		std::vector<size8>  clct_isvalid;
		std::vector<size8>  clct_quality;
		std::vector<size8>  clct_pattern;
		std::vector<size8>  clct_stripType;
		std::vector<size8>  clct_bend;
		std::vector<size8>  clct_halfStrip;
		std::vector<size8>  clct_CFEB;
		std::vector<size8>  clct_BX;
		std::vector<size8>  clct_trkNumber;
		std::vector<size8>  clct_keyStrip;

		virtual void reset()
		{
			clct_id       .clear();
			clct_isvalid  .clear();
			clct_quality  .clear();
			clct_pattern  .clear();
			clct_stripType.clear();
			clct_bend     .clear();
			clct_halfStrip.clear();
			clct_CFEB     .clear();
			clct_BX       .clear();
			clct_trkNumber.clear();
			clct_keyStrip .clear();
		}

	public:
		void fill(const CSCCLCTDigiCollection& clcts, std::vector<std::vector<unsigned short int>> &chamlist);
};

class FillGIFALCTInfo : public FillInfo
{
	public:
		FillGIFALCTInfo(TreeContainer& tree) :FillInfo(tree)
		{

			book("alct_id"       ,alct_id       );
			book("alct_isvalid"  ,alct_isvalid  );
			book("alct_quality"  ,alct_quality  );
			book("alct_accel"    ,alct_accel    );
			book("alct_collB"    ,alct_collB    );
			book("alct_wireGroup",alct_wireGroup);
			book("alct_BX"       ,alct_BX       );
			book("alct_trkNumber",alct_trkNumber);
		}
		virtual ~FillGIFALCTInfo() {};

	private:
		std::vector<size16> alct_id;
		std::vector<size8>  alct_isvalid;
		std::vector<size8>  alct_quality;
		std::vector<size8>  alct_accel;
		std::vector<size8>  alct_collB;
		std::vector<size8>  alct_wireGroup;
		std::vector<size8>  alct_BX;
		std::vector<size8>  alct_trkNumber;

		virtual void reset()
		{
			alct_id       .clear();
			alct_isvalid  .clear();
			alct_quality  .clear();
			alct_accel    .clear();
			alct_collB    .clear();
			alct_wireGroup.clear();
			alct_BX       .clear();
			alct_trkNumber.clear();
		}

	public:
		void fill(const CSCALCTDigiCollection& alcts, std::vector<std::vector<unsigned short int>> &chamlist);
};

#endif
