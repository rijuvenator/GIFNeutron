
#if !defined(__CINT__) || defined(__MAKECINT__)
#include "include/BaseTupleAnalyzer.h"
#include "include/GIFInfo.h"
#include "include/HistGetter.h"

using namespace std;

class Analyzer : public BaseTupleAnalyzer{
public:
  Analyzer(TString fileName, TString treeName) : BaseTupleAnalyzer(fileName,treeName){
    eventInfo.load(this);
    recHitInfo.load(this);
    stripInfo.load(this);
    compInfo.load(this);
    wireInfo.load(this);
    lctInfo.load(this);
    segmentInfo.load(this);
    clctInfo.load(this);
    alctInfo.load(this);

    bookHistos();
  }

  void bookHistos() {
    plotter.book2D("RecHitMap"    ,"RecHitMap    ;x[cm];y[cm]",60,-30,30,90,-90,90);
    plotter.book2D("StripMap","StripMap;strip # ;layer #",70,-0.5,69.5,10,-0.5,9.5);
    plotter.book1D("stripOccL1","Occupancy of strips with signals (>13 ADC) for layer 1;Strip;N",112,0.5,112.5);
    plotter.book1D("stripOccL2","Occupancy of strips with signals (>13 ADC) for layer 2;Strip;N",112,0.5,112.5);
    plotter.book1D("stripOccL3","Occupancy of strips with signals (>13 ADC) for layer 3;Strip;N",112,0.5,112.5);
    plotter.book1D("stripOccL4","Occupancy of strips with signals (>13 ADC) for layer 4;Strip;N",112,0.5,112.5);
    plotter.book1D("stripOccL5","Occupancy of strips with signals (>13 ADC) for layer 5;Strip;N",112,0.5,112.5);
    plotter.book1D("stripOccL6","Occupancy of strips with signals (>13 ADC) for layer 6;Strip;N",112,0.5,112.5);
    plotter.book1D("stripOccAll","Occupancy of strips with signals (>13 ADC) for all layers;Strip;N",112,0.5,112.5);
    plotter.book2D("CompMap","CompMap;strip # ;layer #",85,-0.5,84.5,10,-0.5,9.5);
    plotter.book2D("LCTMap","LCTMap;half strip # ;wire group #",200,-0.5,199.5,200,-0.5,199.5);
    plotter.book1D("LCTPattern","LCTPattern;pattern #",12,-0.5,11.5);
    plotter.book2D("SegmentMap"    ,"SegmentMap    ;x[cm];y[cm]",60,-30,30,90,-90,90);
    plotter.book1D("SegmentDxDz","SegmentDxDz;#theta",400,-20,20);
    plotter.book1D("SegmentDyDz","SegmentDyDz;#phi",400,-20,20);
    plotter.book1D("SegmentChi2","SegmentChi2;#chi^{2}",200,0,200);
    // Wire Histograms
    plotter.book2D("WireMap","WireMap;wire group # ;layer #",50,-0.5,49.5,10,-0.5,9.5);
    plotter.book2D("wireGroupTime","Anode times;Wire Group;Time Bin",112,0.5,112.5,16,0.5,16.5);
    plotter.book1D("wireNlays","Number of fired anode layers;N(Layers);N",7,0,7);
    plotter.book1D("wireOccL1","Occupancy of wiregroups for layer 1;Wiregroup;N",112,0.5,112.5);
    plotter.book1D("wireOccL2","Occupancy of wiregroups for layer 2;Wiregroup;N",112,0.5,112.5);
    plotter.book1D("wireOccL3","Occupancy of wiregroups for layer 3;Wiregroup;N",112,0.5,112.5);
    plotter.book1D("wireOccL4","Occupancy of wiregroups for layer 4;Wiregroup;N",112,0.5,112.5);
    plotter.book1D("wireOccL5","Occupancy of wiregroups for layer 5;Wiregroup;N",112,0.5,112.5);
    plotter.book1D("wireOccL6","Occupancy of wiregroups for layer 6;Wiregroup;N",112,0.5,112.5);
    plotter.book1D("wireOccAll","Occupancy of wiregroups for all layers;Wiregroup;N",112,0.5,112.5);
    plotter.book1D("wireTimeL1","Average anode time for layer 1;Time bin;N",16,0.5,16.5);
    plotter.book1D("wireTimeL2","Average anode time for layer 2;Time bin;N",16,0.5,16.5);
    plotter.book1D("wireTimeL3","Average anode time for layer 3;Time bin;N",16,0.5,16.5);
    plotter.book1D("wireTimeL4","Average anode time for layer 4;Time bin;N",16,0.5,16.5);
    plotter.book1D("wireTimeL5","Average anode time for layer 5;Time bin;N",16,0.5,16.5);
    plotter.book1D("wireTimeL6","Average anode time for layer 6;Time bin;N",16,0.5,16.5);
    plotter.book1D("wireTimeAll","Average anode time for all layers;Time bin;N",16,0.5,16.5);
  }

  virtual void runAEvent() {
    // Fill RecHit Histograms
    for(unsigned int iH = 0; iH < recHitInfo.rh_pos_x->size(); ++iH){
      plotter.get2D("RecHitMap")->Fill((*recHitInfo.rh_pos_x)[iH],(*recHitInfo.rh_pos_y)[iH]);
    }
    // Fill Strip Histograms
    for(unsigned int iH = 0; iH < stripInfo.strip_number->size(); ++iH){
      plotter.get2D("StripMap")->Fill(stripInfo.strip_number->at(iH),stripInfo.strip_lay->at(iH));
      plotter.get1D("stripOccAll")->Fill(stripInfo.strip_number->at(iH));
      if (stripInfo.strip_lay->at(iH)==1) {
        plotter.get1D("stripOccL1")->Fill(stripInfo.strip_number->at(iH));
      }
      else if (stripInfo.strip_lay->at(iH)==2) {
        plotter.get1D("stripOccL2")->Fill(stripInfo.strip_number->at(iH));
      }
      else if (stripInfo.strip_lay->at(iH)==3) {
        plotter.get1D("stripOccL3")->Fill(stripInfo.strip_number->at(iH));
      }
      else if (stripInfo.strip_lay->at(iH)==4) {
        plotter.get1D("stripOccL4")->Fill(stripInfo.strip_number->at(iH));
      }
      else if (stripInfo.strip_lay->at(iH)==5) {
        plotter.get1D("stripOccL5")->Fill(stripInfo.strip_number->at(iH));
      }
      else if (stripInfo.strip_lay->at(iH)==6) {
        plotter.get1D("stripOccL6")->Fill(stripInfo.strip_number->at(iH));
      }
    }
    // Fill Comparator Histograms
    for(unsigned int iH = 0; iH < compInfo.comp_strip->size(); ++iH){
      plotter.get2D("CompMap")->Fill(compInfo.comp_strip->at(iH),compInfo.comp_lay->at(iH));
    }
    // Fill Wire Histograms
    plotter.get1D("wireNlays")->Fill(wireInfo.wire_nlay);
    for(unsigned int iH = 0; iH < wireInfo.wire_grp->size(); ++iH){
      plotter.get2D("WireMap")->Fill(wireInfo.wire_grp->at(iH),wireInfo.wire_lay->at(iH));
      plotter.get1D("wireOccAll")->Fill(wireInfo.wire_grp->at(iH));
      plotter.get1D("wireTimeAll")->Fill(wireInfo.wire_time->at(iH)+1);
      plotter.get2D("wireGroupTime")->Fill(wireInfo.wire_grp->at(iH),wireInfo.wire_time->at(iH)+1);
      if (wireInfo.wire_lay->at(iH)==1) {
        plotter.get1D("wireOccL1")->Fill(wireInfo.wire_grp->at(iH));
        plotter.get1D("wireTimeL1")->Fill(wireInfo.wire_time->at(iH)+1);
      }
      else if (wireInfo.wire_lay->at(iH)==2) {
        plotter.get1D("wireOccL2")->Fill(wireInfo.wire_grp->at(iH));
        plotter.get1D("wireTimeL2")->Fill(wireInfo.wire_time->at(iH)+1);
      }
      else if (wireInfo.wire_lay->at(iH)==3) {
        plotter.get1D("wireOccL3")->Fill(wireInfo.wire_grp->at(iH));
        plotter.get1D("wireTimeL3")->Fill(wireInfo.wire_time->at(iH)+1);
      }
      else if (wireInfo.wire_lay->at(iH)==4) {
        plotter.get1D("wireOccL4")->Fill(wireInfo.wire_grp->at(iH));
        plotter.get1D("wireTimeL4")->Fill(wireInfo.wire_time->at(iH)+1);
      }
      else if (wireInfo.wire_lay->at(iH)==5) {
        plotter.get1D("wireOccL5")->Fill(wireInfo.wire_grp->at(iH));
        plotter.get1D("wireTimeL5")->Fill(wireInfo.wire_time->at(iH)+1);
      }
      else if (wireInfo.wire_lay->at(iH)==6) {
        plotter.get1D("wireOccL6")->Fill(wireInfo.wire_grp->at(iH));
        plotter.get1D("wireTimeL6")->Fill(wireInfo.wire_time->at(iH)+1);
      }
    }
    // Fill LCT Histograms
    for(unsigned int iH = 0; iH < lctInfo.lct_id->size(); ++iH){
      plotter.get2D("LCTMap")->Fill(lctInfo.lct_keyHalfStrip->at(iH),lctInfo.lct_keyWireGroup->at(iH));
      plotter.get1D("LCTPattern")->Fill(lctInfo.lct_pattern->at(iH));
    }

    unsigned int goodSeg = -1;

    // Fill Segment Histograms
    if(segmentInfo.segment_id->size() == 1)
    for(unsigned int iH = 0; iH < segmentInfo.segment_id->size(); ++iH){
      plotter.get2D("SegmentMap")->Fill(segmentInfo.segment_pos_x->at(iH),segmentInfo.segment_pos_y->at(iH));
      plotter.get1D("SegmentDxDz")->Fill(segmentInfo.segment_dxdz->at(iH));
      plotter.get1D("SegmentDyDz")->Fill(segmentInfo.segment_dydz->at(iH));
      plotter.get1D("SegmentChi2")->Fill(segmentInfo.segment_chisq->at(iH));
    }

  } // end runAEvent()

  void write(TString fileName){ plotter.write(fileName);}

  HistGetter plotter;
  GifEventInfo eventInfo;
  GifRecHitInfo recHitInfo;
  GifStripInfo  stripInfo;
  GifCompInfo  compInfo;
  GifWireInfo  wireInfo;
  GifLCTInfo  lctInfo;
  GifSegmentInfo  segmentInfo;
  GifCLCTInfo  clctInfo;
  GifALCTInfo  alctInfo;

};

#endif

void gifAnalyzeTuples(std::string fileName,std::string treeName = "CSCDigiTree",std::string outFileName = "plots.root"){
  Analyzer a(fileName,treeName);
  a.analyze();
  a.write(outFileName);
}
