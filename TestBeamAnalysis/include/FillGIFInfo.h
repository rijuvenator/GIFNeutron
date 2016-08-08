#ifndef GIF_CSCDIGITUPLES_FILLCSCINFO_H
#define GIF_CSCDIGITUPLES_FILLCSCINFO_H

#include "FWCore/Framework/interface/Event.h"

#include <DataFormats/CSCRecHit/interface/CSCRecHit2DCollection.h>
#include <DataFormats/CSCDigi/interface/CSCStripDigiCollection.h>
#include <DataFormats/CSCDigi/interface/CSCWireDigiCollection.h>
#include <DataFormats/CSCDigi/interface/CSCComparatorDigiCollection.h>
#include <DataFormats/CSCDigi/interface/CSCCorrelatedLCTDigiCollection.h>
#include <DataFormats/CSCRecHit/interface/CSCSegmentCollection.h>
#include <DataFormats/CSCDigi/interface/CSCCLCTDigiCollection.h>
#include <DataFormats/CSCDigi/interface/CSCALCTDigiCollection.h>
#include "Gif/TestBeamAnalysis/include/GIFHelper.h"

#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/Math/interface/deltaPhi.h"

typedef   unsigned char        size8 ; // 8 bit 0->255
typedef   unsigned short int   size16; //16 bit 0->65536
typedef   unsigned int         size  ; //32 bit 0->4294967296

class GifTreeContainer {
public:
  GifTreeContainer(/*TString fileName,*/ TString treeName, TString treeTitle){
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

class FillGIFInfo {
public:
  FillGIFInfo(GifTreeContainer& tree) : fTree(&tree) {reset();};
  virtual ~FillGIFInfo() {};
protected:
  virtual void reset() {};


  //Book single variable
  template<class T>
  void    book(const char *name, T& var, const char *type) { fTree->tree->Branch(name, &var, TString(name).Append("/").Append(type).Data()); }

  //Book vector
  template<class T>
  void    book(const char *name, std::vector<T>& varv)   { fTree->tree->Branch(name, &varv); }

  GifTreeContainer * fTree;

};


class FillGIFEventInfo : public FillGIFInfo {
public:

  FillGIFEventInfo(GifTreeContainer& tree) :FillGIFInfo(tree) {
    book("Event_EventNumber",Event_EventNumber,"I");
    book("Event_RunNumber"  ,Event_RunNumber  ,"I");
    book("Event_LumiSection",Event_LumiSection,"I");
    book("Event_BXCrossing" ,Event_BXCrossing ,"I");
  }
  virtual ~FillGIFEventInfo() {};

private:
  int Event_EventNumber;
  int Event_RunNumber  ;
  int Event_LumiSection;
  int Event_BXCrossing ;

  virtual void reset(){
    Event_EventNumber  = -1;
    Event_RunNumber    = -1;
    Event_LumiSection  = -1;
    Event_BXCrossing   = -1;
  }

  public:

  void fill(const edm::Event& iEvent);

};


class FillGIFRecHitInfo : public FillGIFInfo {
public:

  FillGIFRecHitInfo(GifTreeContainer& tree) :FillGIFInfo(tree) {
    book("rh_id"          ,rh_id          );
    book("rh_lay"         ,rh_lay         );
    book("rh_pos_x"       ,rh_pos_x       );
    book("rh_pos_y"       ,rh_pos_y       );
    book("rh_strip_1"     ,rh_strip_1 );
    book("rh_strip_2"     ,rh_strip_2 );
    book("rh_strip_3"     ,rh_strip_3 );
    book("rh_pos_strip"   ,rh_pos_strip   );
    book("rh_n_wiregroups",rh_n_wiregroups);
    book("n_rhs",nRH,"I");


  }
  virtual ~FillGIFRecHitInfo() {};

private:
  std::vector<size16>   rh_id          ;
  std::vector<size8>    rh_lay         ;
  std::vector<float>    rh_pos_x       ;
  std::vector<float>    rh_pos_y       ;
  std::vector<size8>    rh_strip_1  ;
  std::vector<size8>    rh_strip_2  ;
  std::vector<size8>    rh_strip_3  ;
  std::vector<float>    rh_pos_strip   ;
  std::vector<size8>    rh_n_wiregroups;
  int nRH;


  virtual void reset(){
    rh_id          .clear();
    rh_lay         .clear();
    rh_pos_x       .clear();
    rh_pos_y       .clear();
    rh_strip_1  .clear();
    rh_strip_2  .clear();
    rh_strip_3  .clear();
    rh_pos_strip   .clear();
    rh_n_wiregroups.clear();
    nRH = -1;
  }

  public:

  void fill(const CSCRecHit2DCollection& recHits);

};

class FillGIFStripInfo : public FillGIFInfo {
public:

  FillGIFStripInfo(GifTreeContainer& tree) :FillGIFInfo(tree) {
    book("strip_id"           ,strip_id           );
    book("strip_lay"          ,strip_lay          );
    book("strip_number"       ,strip_number      );
    book("n_strips", nStrip,"I");



  }
  virtual ~FillGIFStripInfo() {};

private:
  std::vector<size16>   strip_id     ;
  std::vector<size8>    strip_lay    ;
  std::vector<size8>    strip_number ;
  int nStrip; 


  virtual void reset(){
    strip_id     .clear();
    strip_lay    .clear();
    strip_number .clear();
    nStrip = -1;
  }

  public:

  void fill(const CSCStripDigiCollection& strips);

};

class FillGIFCompInfo : public FillGIFInfo {
public:

  FillGIFCompInfo(GifTreeContainer& tree) :FillGIFInfo(tree) {
    book("comp_id"      ,comp_id          );
    book("comp_lay"     ,comp_lay         );
    book("comp_strip"   ,comp_strip       );
    book("comp_comp"    ,comp_comp        );



  }
  virtual ~FillGIFCompInfo() {};

private:
  std::vector<size16> comp_id    ;
  std::vector<size8>  comp_lay   ;
  std::vector<size8>  comp_strip ;
  std::vector<size8>  comp_comp  ;


  virtual void reset(){
    comp_id    .clear();
    comp_lay   .clear();
    comp_strip .clear();
    comp_comp  .clear();
  }

  public:

  void fill(const CSCComparatorDigiCollection& strips);

};


class FillGIFWireInfo : public FillGIFInfo {
public:

  FillGIFWireInfo(GifTreeContainer& tree) :FillGIFInfo(tree) {
    book("wire_id"     ,wire_id         );
    book("wire_lay"    ,wire_lay        );
    book("wire_grp"    ,wire_grp        );
    book("wire_time"   ,wire_time       );
    book("wire_nlay"   ,wire_nlay,   "I");
    book("n_wires"   ,nWG,   "I");



  }
  virtual ~FillGIFWireInfo() {};

private:
  std::vector<size16>     wire_id  ;
  std::vector<size8>      wire_lay ;
  std::vector<size8>      wire_grp ;
  std::vector<size8>      wire_time;
  int wire_nlay;
  int                     nWG;


  virtual void reset(){
    wire_id   .clear();
    wire_lay  .clear();
    wire_nlay     = -1;
    wire_grp  .clear();
    wire_time .clear();
    nWG = -1;
  }

  public:

  void fill(const CSCWireDigiCollection& wires);

};


class FillGIFLCTInfo : public FillGIFInfo {
public:

  FillGIFLCTInfo(GifTreeContainer& tree) :FillGIFInfo(tree) {

    book("lct_id"          ,lct_id          );
    book("lct_quality"     ,lct_quality     );
    book("lct_pattern"     ,lct_pattern     );
    book("lct_bend"        ,lct_bend        );
    book("lct_keyWireGroup",lct_keyWireGroup);
    book("lct_keyHalfStrip",lct_keyHalfStrip);
    book("n_lcts",nLCT,"I");



  }
  virtual ~FillGIFLCTInfo() {};

private:
   std::vector<size16> lct_id          ;
   std::vector<size8>  lct_quality     ;
   std::vector<size8>  lct_pattern     ;
   std::vector<size8>  lct_bend        ;
   std::vector<size8>  lct_keyWireGroup;
   std::vector<size8>  lct_keyHalfStrip;
   int nLCT;


  virtual void reset(){
    lct_id           .clear();
    lct_quality      .clear();
    lct_pattern      .clear();
    lct_bend         .clear();
    lct_keyWireGroup .clear();
    lct_keyHalfStrip .clear();
    nLCT = -1;
  }

  public:

  void fill(const CSCCorrelatedLCTDigiCollection& lcts);

};


class FillGIFSegmentInfo : public FillGIFInfo {
public:

  FillGIFSegmentInfo(GifTreeContainer& tree) :FillGIFInfo(tree) {

    book("segment_id"          ,segment_id         );
    book("segment_pos_x"       ,segment_pos_x      );
    book("segment_pos_y"       ,segment_pos_y      );
    book("segment_dxdz"        ,segment_dxdz  );
    book("segment_dydz"        ,segment_dydz    );
    book("segment_dx"        ,segment_dx  );
    book("segment_dy"        ,segment_dy    );
    book("segment_chisq"       ,segment_chisq      );
    book("segment_dof"         ,segment_dof      );
    book("segment_nHits"       ,segment_nHits      );
    book("segment_quality"         ,segment_quality      );
    book("segment_recHitIdx_1" ,segment_recHitIdx_1);
    book("segment_recHitIdx_2" ,segment_recHitIdx_2);
    book("segment_recHitIdx_3" ,segment_recHitIdx_3);
    book("segment_recHitIdx_4" ,segment_recHitIdx_4);
    book("segment_recHitIdx_5" ,segment_recHitIdx_5);
    book("segment_recHitIdx_6" ,segment_recHitIdx_6);
    book("n_segments",nSegments,"I");



  }
  virtual ~FillGIFSegmentInfo() {};

private:
     std::vector<size16>  segment_id             ;
     std::vector<float>   segment_pos_x          ;
     std::vector<float>   segment_pos_y          ;
     std::vector<float>   segment_dxdz      ;
     std::vector<float>   segment_dydz        ;
     std::vector<float>   segment_dx      ;
     std::vector<float>   segment_dy        ;
     std::vector<float>   segment_chisq          ;
     std::vector<size8>   segment_dof          ;
     std::vector<size8>   segment_nHits          ;
     std::vector<int>   segment_quality          ;
     std::vector<size16>  segment_recHitIdx_1    ;
     std::vector<size16>  segment_recHitIdx_2    ;
     std::vector<size16>  segment_recHitIdx_3    ;
     std::vector<size16>  segment_recHitIdx_4    ;
     std::vector<size16>  segment_recHitIdx_5    ;
     std::vector<size16>  segment_recHitIdx_6    ;
     int nSegments;


  virtual void reset(){
    segment_id          .clear();
    segment_pos_x       .clear();
    segment_pos_y       .clear();
    segment_dxdz        .clear();
    segment_dydz        .clear();
    segment_dx        .clear();
    segment_dy        .clear();
    segment_chisq       .clear();
    segment_dof         .clear();
    segment_nHits       .clear();
    segment_quality         .clear();
    segment_recHitIdx_1 .clear();
    segment_recHitIdx_2 .clear();
    segment_recHitIdx_3 .clear();
    segment_recHitIdx_4 .clear();
    segment_recHitIdx_5 .clear();
    segment_recHitIdx_6 .clear();
    nSegments = -1;

  }

  public:

  void fill(const CSCSegmentCollection& segments, const CSCRecHit2DCollection * recHits = 0);
  size16 findRecHitIdx(const CSCRecHit2D& hit, const CSCRecHit2DCollection* allRecHits);

  int segmentQuality(edm::OwnVector<CSCSegment>::const_iterator segment);

};

class FillGIFCLCTInfo : public FillGIFInfo {
public:

  FillGIFCLCTInfo(GifTreeContainer& tree) :FillGIFInfo(tree) {

    book("clct_id"         , clct_id        );
    book("clct_isvalid"    , clct_isvalid   );
    book("clct_quality"    , clct_quality   );
    book("clct_pattern"    , clct_pattern   );
    book("clct_stripType"  , clct_stripType );
    book("clct_bend"       , clct_bend      );
    book("clct_halfStrip"  , clct_halfStrip );
    book("clct_CFEB"       , clct_CFEB      );
    book("clct_BX"         , clct_BX        );
    book("clct_trkNumber"  , clct_trkNumber );
    book("clct_keyStrip"   , clct_keyStrip  );
    book("n_clcts",nCLCT,"I");



  }
  virtual ~FillGIFCLCTInfo() {};

private:
   std::vector<size16> clct_id          ;
   std::vector<size8>  clct_isvalid     ;
   std::vector<size8>  clct_quality     ;
   std::vector<size8>  clct_pattern     ;
   std::vector<size8>  clct_stripType   ;
   std::vector<size8>  clct_bend        ;
   std::vector<size8>  clct_halfStrip   ;
   std::vector<size8>  clct_CFEB        ;
   std::vector<size8>  clct_BX          ;
   std::vector<size8>  clct_trkNumber   ;
   std::vector<size8>  clct_keyStrip    ;
   int nCLCT;


  virtual void reset(){
    clct_id         .clear();
    clct_isvalid    .clear();
    clct_quality    .clear();
    clct_pattern    .clear();
    clct_stripType  .clear();
    clct_bend       .clear();
    clct_halfStrip  .clear();
    clct_CFEB       .clear();
    clct_BX         .clear();
    clct_trkNumber  .clear();
    clct_keyStrip   .clear();
    nCLCT = -1;
  }

  public:

  void fill(const CSCCLCTDigiCollection& clcts);

};

class FillGIFALCTInfo : public FillGIFInfo {
public:

  FillGIFALCTInfo(GifTreeContainer& tree) :FillGIFInfo(tree) {

    book("alct_id"         , alct_id        );
    book("alct_isvalid"    , alct_isvalid   );
    book("alct_quality"    , alct_quality   );
    book("alct_accel"      , alct_accel     );
    book("alct_collB"      , alct_collB     );
    book("alct_wireGroup"  , alct_wireGroup );
    book("alct_BX"         , alct_BX        );
    book("alct_trkNumber"  , alct_trkNumber );
    book("n_alcts",nALCT,"I");



  }
  virtual ~FillGIFALCTInfo() {};

private:
   std::vector<size16> alct_id          ;
   std::vector<size8>  alct_isvalid     ;
   std::vector<size8>  alct_quality     ;
   std::vector<size8>  alct_accel       ;
   std::vector<size8>  alct_collB       ;
   std::vector<size8>  alct_wireGroup   ;
   std::vector<size8>  alct_BX          ;
   std::vector<size8>  alct_trkNumber   ;
   int nALCT;


  virtual void reset(){
    alct_id         .clear();
    alct_isvalid    .clear();
    alct_quality    .clear();
    alct_accel      .clear();
    alct_collB      .clear();
    alct_wireGroup  .clear();
    alct_BX         .clear();
    alct_trkNumber  .clear();
    nALCT = -1;
  }

  public:

  void fill(const CSCALCTDigiCollection& alcts);

};

#endif /*GIF_CSCDIGITUPLES_FILLCSCINFO_H*/
