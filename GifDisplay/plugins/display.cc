#include "display.h"
#define analysis_cxx
//#include "analysis.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TGraph.h>
#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include <TGraphErrors.h>
#include "TMath.h"
#include "TF1.h"
#include "TPaveText.h"
#include "TLegend.h"
#include "TLorentzVector.h"
#include <math.h>
#define PI 3.14159265
#include <vector>
#include <list>
#include <iterator>
#include <boost/lexical_cast.hpp>
#include <string>
#include "TPaletteAxis.h"
#include <iostream>
#include <fstream>
#include <algorithm>

void WireStripDisplay(TString address, CSCDetID id, vector<WIRE> &wire, vector<STRIP> &strip, vector<COMPARATOR> &comparator, vector<CSCDetID> &usedChamber, int Run, int Event){


        TH2F* NWireGroup = new TH2F("NWireGroup", "NWireGroup", 4, 1, 5, 4, 1, 5);
        TH2F* NStrip = new TH2F("NStrip", "NStrip", 4, 1, 5, 4, 1, 5);

        NWireGroup->SetBinContent(1, 1, 48);
        NWireGroup->SetBinContent(1, 2, 48);
        NWireGroup->SetBinContent(1, 3, 48);
//        NWireGroup->SetBinContent(1, 4, 48);
        NWireGroup->SetBinContent(2, 1, 112);
        NWireGroup->SetBinContent(3, 1, 96);
        NWireGroup->SetBinContent(4, 1, 96);
        NWireGroup->SetBinContent(2, 2, 64);
        NWireGroup->SetBinContent(3, 2, 64);
        NWireGroup->SetBinContent(4, 2, 64);

        NStrip->SetBinContent(1, 1, 112);
        NStrip->SetBinContent(1, 2, 80);
        NStrip->SetBinContent(1, 3, 64);
//        NStrip->SetBinContent(1, 4, 64);
        NStrip->SetBinContent(2, 1, 80);
        NStrip->SetBinContent(3, 1, 80);
        NStrip->SetBinContent(4, 1, 80);
        NStrip->SetBinContent(2, 2, 80);
        NStrip->SetBinContent(3, 2, 80);
        NStrip->SetBinContent(4, 2, 80);


        if (ChamberUsedForEventDisplay(id, usedChamber)) return;//this chamber has not been used for eventdisplay

           srand (time(NULL));
           TString name = "";
           TString legendName = "";

           SetSaveNameLegendName(name, legendName, address, id, Run, Event);

           vector<int> layer_strip = FindChamberIndex(id, strip);
           vector<int> layer_wire = FindChamberIndex(id, wire);
           vector<int> layer_comparator = FindChamberIndex(id, comparator);

           const int nStrip = NStrip->GetBinContent(id.Station, id.Ring);
//           const int nWire = NWireGroup->GetBinContent(id.Station, id.Ring);
           const int nCFEB = nStrip/16; 


//draw event display
           TCanvas *c1 = new TCanvas("c1", "", 0, 0, 2000, 1400);

           c1->Divide(1,4);

           c1->SetRightMargin(0.15);
           c1->SetBottomMargin(0.20);
           c1->SetTopMargin(0.15);
//strip display
           c1->cd(3)->SetGridy();

           TH2F* stripDis = new TH2F("stripDis", "", nStrip*2+2, 1, nStrip+2, 6, 1, 7);
           TH2F* stripDis_text = new TH2F("stripDis_text", "", nStrip*2+2, 1, nStrip+2, 6, 0.5, 6.5);
           TH1F* cfebNotReadOut = new TH1F("cfebNotReadOut", "", nStrip+1, 1, nStrip+2);
           TPaveText *pt3 = new TPaveText(0.4,0.95,0.6,0.99,"NDC");
           double cfeb[nCFEB] = {};

           StripDisplay(/*c1,*/ id, layer_strip, strip, cfeb, stripDis, stripDis_text, cfebNotReadOut);
           SetTitle(pt3, "Cathode Hit ADC Count");

           stripDis->Draw("COLZ");
           stripDis_text->Draw("text same");
           cfebNotReadOut->Draw("B same");
           pt3->Draw();

//wire display
          c1->cd(1)->SetGridy();

          TH2F* wireDis = new TH2F("wireDis", "", 112, 1, 113, 6, 1, 7);
          TH2F* wireDis_text = new TH2F("wireDis_text", "", 112, 1, 113, 6, 1, 7);
          TPaveText *pt1 = new TPaveText(0.4,.95,0.6,0.99, "NDC");

          WireDisplay(id, layer_wire, wire, wireDis, wireDis_text);
          SetTitle(pt1, "Anode Hit Timing");

          wireDis->Draw("COLZ");
          wireDis_text->Draw("text same");
          pt1->Draw();
//legend
          SetEventDisplayLegend(legendName);

//comparator display
          c1->cd(2)->SetGridy();
          gPad->SetBottomMargin(0.15);
          TH2F* comparatorDis = new TH2F("comparatorDis", "", nStrip*2, 1, nStrip*2+1, 6, 1, 7);
          TH2F* comparatorDis_text = new TH2F("comparatorDis_text", "", nStrip*2, 1, nStrip*2+1, 6, 1, 7);
          TPaveText *pt4 = new TPaveText(0.4,.95,0.6,0.99, "NDC");

          ComparatorDisplay(id, layer_comparator, comparator, comparatorDis, comparatorDis_text);

          comparatorDis->Draw("COLZ");
          comparatorDis_text->Draw("text same");
          SetTitle(pt4, "Comparator Hit Timing");
          pt4->Draw();
//strip hit display
          c1->cd(4)->SetGridy();

          TGraph* stripHitDis;
          TGraph* comparatorHitNotReadOut;
          vector<vector<double> > sHit_cHit_layer = StripHitDisplay(id, layer_strip, layer_comparator, strip, comparator, cfeb);
          double* sHit = &(sHit_cHit_layer[0][0]);
          double* sHitLayer = &(sHit_cHit_layer[1][0]);
          double* cHit = &(sHit_cHit_layer[2][0]);
          double* cHitLayer = &(sHit_cHit_layer[3][0]);

          if (int(sHit_cHit_layer[0].size()) > 0){
          stripHitDis = new TGraph(int(sHit_cHit_layer[0].size()), sHit, sHitLayer);
          TPaveText *pt2 = new TPaveText(0.4,.95,0.6,0.99, "NDC");
          SetTitle(pt2, "Strip Hit");
          stripHitDis->Draw("ap");
          pt2->Draw();
//          stripHitDis->GetXaxis()->SetLimits(1, 82);
//          stripHitDis->GetYaxis()->SetRangeUser(1, 7);
//          stripHitDis->SetMarkerStyle(20);
          SetPlotDetail_StripHit(stripHitDis);

          }

          if (int(sHit_cHit_layer[3].size() > 0)){
          comparatorHitNotReadOut = new TGraph(int(sHit_cHit_layer[2].size()), cHit, cHitLayer);
          comparatorHitNotReadOut->Draw("p same");
          comparatorHitNotReadOut->SetMarkerStyle(24);
          comparatorHitNotReadOut->SetMarkerColor(2);
          }
//        stripHitDis->GetXaxis()->SetRangeUser(1, 82);
//        stripHitDis->GetYaxis()->SetLimits(1, 7);

//        stripHitDis->SetMarkerStyle(20);
//        comparatorHitNotReadOut->Draw("p same");
          cfebNotReadOut->Draw("B same");


          c1->Update();
          c1->SaveAs(name + ".png");

          delete c1;
          delete wireDis;
          delete stripDis;
          delete wireDis_text;
          delete stripDis_text;
          delete comparatorDis;
          delete comparatorDis_text;
          delete cfebNotReadOut;
}




bool ChamberUsedForEventDisplay(CSCDetID id, vector<CSCDetID> usedChamber){

        bool flag = false;


        for (int i = 0; i < int(usedChamber.size()); i++){

            CSCDetID tempID = usedChamber[i];

            if (id.Endcap == tempID.Endcap &&
                id.Station == tempID.Endcap &&
                id.Ring == tempID.Ring &&
                id.Chamber == tempID.Chamber){

                flag = true;

                }

            }

        return flag;
}



void SetSaveNameLegendName(TString& name, TString& legendName, TString address, CSCDetID id, int Run, int Event){

           //int Run = 1;
           //int Event = 1;
  
           if (id.Endcap == 1){
              legendName = "ME+" + NumberToString(id.Station) + "/" + NumberToString(id.Ring) + "/" + NumberToString(id.Chamber) + "   " + "Run #" + NumberToString(Run) + "  " + "Event #" + NumberToString(Event);

              name = address + "/MEPlus" + NumberToString(id.Station) + "_" + NumberToString(id.Ring) + "_" + NumberToString(id.Chamber) +"_"+NumberToString(Run) + "_" + NumberToString(Event);
              }

           if (id.Endcap == 2){
              legendName = "ME-" + NumberToString(id.Station) + "/" + NumberToString(id.Ring) + "/" + NumberToString(id.Chamber)  + "   " + "Run #" + NumberToString(Run) + "  " + "Event #" + NumberToString(Event);

              name = address + "/MEMinus" + NumberToString(id.Station) + "_" + NumberToString(id.Ring) + "_" + NumberToString(id.Chamber) + "_"+NumberToString(Run) + "_"+ NumberToString(Event);

              }


}


void SaveUsedChamber(CSCDetID id, vector<int> layer_strip, vector<int> layer_wire, vector<int> layer_comparator, vector<CSCDetID> &usedChamber){

           CSCDetID tempID;

           if (int(layer_strip.size()) > 0 && int(layer_wire.size()) > 0 && int(layer_comparator.size()) > 0){

              tempID.Endcap = id.Endcap;
              tempID.Station = id.Station;
              tempID.Ring = id.Ring;
              tempID.Chamber = id.Chamber;

              usedChamber.push_back(tempID);

              }


}


void StripDisplay(/*TCanvas* c1,*/ CSCDetID id, vector<int>& layer_strip, vector<STRIP>& strip, double cfeb[], TH2F* stripDis, TH2F* stripDis_text, TH1F* cfebNotReadOut){ 

//         c1->cd(4)->SetGridy();         

/*           TH2F* stripDis = new TH2F("stripDis", "", 162, 1, 82, 6, 1, 7);
           TH2F* stripDis_text = new TH2F("stripDis_text", "", 162, 1, 82, 6, 1, 7);
           TH1F* cfebNotReadOut = new TH1F("cfebNotReadOut", "", 81, 1, 82);
*/
           for (int i = 0; i < int(layer_strip.size()); i++){//in each interesting layer has strip hits

               int tempLayer = strip[layer_strip[i]].first.Layer;
               vector<Strips> tempStrip = strip[layer_strip[i]].second;


               CountCFEB(cfeb, tempStrip);
               int option1 = 1;
               int option2 = 2;

               MakeOneLayerStripDisplay(tempLayer, tempStrip, stripDis, option1);

               if (tempLayer == id.Layer){

                  MakeOneLayerStripDisplay(tempLayer, tempStrip, stripDis_text, option2);

                  }
               }

          BlockUnreadCFEB(cfeb, cfebNotReadOut, (cfebNotReadOut->GetNbinsX())/16);

          SetHistContour(stripDis, 1, 500);

          cfebNotReadOut->SetFillStyle(3001);
          cfebNotReadOut->SetFillColor(15);

          stripDis_text->SetMarkerSize(2);

          stripDis->GetZaxis()->SetLabelSize(0.1);
          stripDis->GetZaxis()->SetRangeUser(1, 500);
          stripDis->SetStats(0);
          stripDis->GetXaxis()->SetTitle("Strip Number");
          stripDis->GetYaxis()->SetTitle("Layer");
          stripDis->GetXaxis()->SetLabelSize(0.1);
          stripDis->GetYaxis()->SetLabelSize(0.1);
          stripDis->GetXaxis()->SetTitleSize(0.11);
          stripDis->GetYaxis()->SetTitleSize(0.11);
          stripDis->GetXaxis()->SetTitleOffset(0.81);
          stripDis->GetYaxis()->SetTitleOffset(0.2);
          stripDis->GetXaxis()->SetNdivisions(1010);
          stripDis->GetYaxis()->SetNdivisions(110);
          stripDis->SetTitle("");
}


void MakeOneLayerStripDisplay(int layer, vector<Strips> &s, TH2F* stripDisplay, int option){

      if (option == 1){

        for (int i = 0; i < int(s.size()); i++){

           int x1 = 2*(s[i].Strip-1) + 1;
           int x2 = 2*(s[i].Strip-1) + 2;
           int x3 = 2*(s[i].Strip-1) + 3;

           if(layer == 1 || layer == 3 || layer == 5){

              stripDisplay->SetBinContent(x2, layer, s[i].MaxADC);
              stripDisplay->SetBinContent(x3, layer, s[i].MaxADC);

             }else  if(layer == 2 || layer == 4 || layer ==6){

                      stripDisplay->SetBinContent(x1, layer, s[i].MaxADC);
                      stripDisplay->SetBinContent(x2, layer, s[i].MaxADC);

                      }

            }

        }else if(option == 2){

                          for (int i = 0; i < int(s.size()); i++){

                            int x1 = 2*(s[i].Strip-1) + 1;
                            int x2 = 2*(s[i].Strip-1) + 2;

                            if (layer == 1 || layer == 3 || layer ==5){

                               stripDisplay->SetBinContent(x2, layer, s[i].MaxADC);

                               }else if(layer == 2 || layer == 4 || layer == 6){

                                        stripDisplay->SetBinContent(x1, layer, s[i].MaxADC);
                                                                                                                                                       
                                        }
                              }

                          }


}


void MakeOneLayerWireDisplay(int layer, vector<Wire> &w, TH2F* wireDisplay){

        for (int i = 0; i < int(w.size()); i++){

            double time = w[i].TimeBin;

            if (w[i].TimeBin == 0){time+=0.1;}

            wireDisplay->SetBinContent(w[i].WireGroup, layer, time);

            }

}


void MakeOneLayerComparatorDisplay(int layer, vector<Comparator> &c, TH2F* comparatorDisplay){

        for (int i = 0; i < int(c.size()); i++){

            double time = c[i].TimeBin;
            if (time==0){time+=0.1;}

            int comparator = 2*(c[i].Strip-1)+c[i].ComparatorNumber+1;

            if (layer == 2 || layer == 4 || layer ==6){

               comparatorDisplay->SetBinContent(comparator, layer, time);

               }else if(layer == 1 || layer == 3 || layer ==5){

                        comparatorDisplay->SetBinContent(comparator+1, layer, time);

                        }
            }

}


vector<vector<double> > StripHitDisplay(CSCDetID id, vector<int>& layer_strip, vector<int>& layer_comparator, vector<STRIP> strip, vector<COMPARATOR> &comparator, double cfeb[]){

        vector<vector<double> > sHit_cHit_layer;

        vector<double> stripHitsContainer;
        vector<double> stripHitsLayerContainer;
        vector<double> comparatorHitsContainer;
        vector<double> comparatorHitsLayerContainer;

        for (int i = 0; i < int(layer_strip.size()); i++){

            double tempLayer = strip[layer_strip[i]].first.Layer;
            vector<Strips> tempStrip = strip[layer_strip[i]].second;

            vector<double> stripHits = MakeStripHit(tempStrip);
            vector<double> stripHitsLayer (int(stripHits.size()), tempLayer+0.5);//make a vector containing strip hits' layer, since using tgraph, make it 1.5, 2.5...
            ShiftStripHits(stripHits, tempLayer);

/*      for (i=0; i<stripHits.size(); i++){

}
*/
            stripHitsContainer.insert(stripHitsContainer.begin(), stripHits.begin(), stripHits.end());
            stripHitsLayerContainer.insert(stripHitsLayerContainer.begin(), stripHitsLayer.begin(), stripHitsLayer.end());

            }


        for (int i = 0; i < int(layer_comparator.size()); i++){

            double tempLayer  = comparator[layer_comparator[i]].first.Layer;
            vector<Comparator> tempComparator = comparator[layer_comparator[i]].second;

            vector<double> comparatorHits = MakeComparatorHitNotReadout(tempComparator, cfeb);
            vector<double> comparatorHitsLayer (int(comparatorHits.size()), tempLayer+0.5);
            ShiftStripHits(comparatorHits, tempLayer);

            comparatorHitsContainer.insert(comparatorHitsContainer.end(), comparatorHits.begin(), comparatorHits.end());
            comparatorHitsLayerContainer.insert(comparatorHitsLayerContainer.end(), comparatorHitsLayer.begin(), comparatorHitsLayer.end());

            }
        sHit_cHit_layer.push_back(stripHitsContainer);
        sHit_cHit_layer.push_back(stripHitsLayerContainer);
        sHit_cHit_layer.push_back(comparatorHitsContainer);
        sHit_cHit_layer.push_back(comparatorHitsLayerContainer);

        return sHit_cHit_layer;
//      stripHitDis = new TGraph(int(stripHitsContainer.size()), sHit, sHitLayer);//stripHitsContainer, stripHitsLayerContainer);
//      comparatorHitNotReadOut = new TGraph(int(comparatorHitsContainer.size()), comparatorHitsContainer, comparatorHitsLayerContainer);


//      stripHitDis->GetXaxis()->SetRangeUser(1, 82);
//      stripHitDis->GetYaxis()->SetRangeUser(1, 7);
}


vector<double> MakeComparatorHitNotReadout(vector<Comparator> c, double cfeb[]){

        vector<double> cHit;

        for (int i = 0; i < int(c.size()); i++){

            if (c[i].Strip < 80 && cfeb[int(c[i].Strip/16)] == 0){

               cHit.push_back(c[i].Strip+0.5);

               }else if(c[i].Strip == 80 && cfeb[4] == 0){

                       cHit.push_back(c[i].Strip+0.5);

                       }

            }

        return cHit;

}




void SetTitle(TPaveText* pt, TString name){


   pt->SetFillColor(0);
   pt->SetTextSize(0.1);
   pt->SetBorderSize(0);
   pt->SetTextAlign(21);
   pt->AddText(name);
}

template <typename T>
string NumberToString( T Number )
{
        stringstream ss;
        ss << Number;
        return ss.str();
}

void CountCFEB(double cfeb[], vector<Strips> s){

        for (int i = 0; i < int(s.size()); i++){

            if (s[i].Strip <= 16){

                cfeb[0]++;

                }else if(s[i].Strip >= 17 && s[i].Strip <= 32){

                        cfeb[1]++;

                        }else if(s[i].Strip >= 33 && s[i].Strip <= 48){

                                   cfeb[2]++;

                                   }else if(s[i].Strip >= 49 && s[i].Strip <= 64){

                                             cfeb[3]++;

                                             }else if(s[i].Strip >= 65){

                                                     cfeb[4]++;

                                                     }

            }

}


void BlockUnreadCFEB(double cfeb[], TH1F* cfebNotReadOut, int nCFEB){

//      gStyle->SetPalette(52, 0);

           for (int i = 0; i < nCFEB; i++){//in each interesting layer has strip hits

               if (cfeb[i] == 0){

//                for (int j = 0; j < 6; j++){//each layer

                      for (int k = 0; k < 16; k++){//each 16 strips for one cfeb

//                      if ()           

                          int x1 = (k+i*16)+1;
//                        int x2 = 2*(k+i*16)+2;
//                        int x3 = 2*(k+i*16)+3;

                          cfebNotReadOut->SetBinContent(x1, 7);

                          }

//                    } 

                  }


               }

cfebNotReadOut->GetYaxis()->SetRangeUser(1,7);

}


void SetHistContour(TH2F* hist, double Min, double Max){

        gStyle->SetNumberContours(Max -Min);
          //here the actually interesting code starts
  const Double_t min = Min;
  const Double_t max = Max;

  const Int_t nLevels = Max - Min;
  Double_t levels[nLevels];


  for(int i = 1; i < nLevels; i++) {
    levels[i] = min + (max - min) / (nLevels - 1) * (i);
  }
  levels[0] = 0;

hist->SetContour((sizeof(levels)/sizeof(Double_t)), levels);
}


vector<double> MakeStripHit(vector<Strips> sp){

        vector<double> stripHits;

        sort(sp.begin(), sp.end());

        if (int(sp.size()) == 1){//one fired strip per layer

           MakeHit1(sp[0], stripHits);

           }else if(int(sp.size() > 1)){//more than one fired strip per layer

                   for (vector<Strips>::iterator it = sp.begin(); it != sp.end(); it++){

                        if ((*it).ADCMaxTime <= 2 || (*it).ADCMaxTime ==7){

                           (*it).MaxADC = 0;

                           }

                        if (it == sp.begin()){//first strip in layer

                           MakeHit2(*it, *(it+1), stripHits);

                           }else if(it == sp.end()-1){//last strip in layer

                                   MakeHit2(*it, *(it-1), stripHits);

                                   }else{

                                        MakeHit3(*it, *(it-1), *(it+1), stripHits);

                                        }

                        }

                   }


        return stripHits;
}


void ShiftStripHits(vector<double>& stripHits, double layer){

        if (layer == 1 || layer == 3 || layer ==5){

           for (int i = 0; i < int(stripHits.size()); i++){

               stripHits[i]+=0.5;

               }

           }

}


void MakeHit1(Strips &s, vector<double>& stripHits){//deal with strip singlet

        double sHitPos = -99;

        if (s.MaxADC >= 25 && s.ADCMaxTime > 2 && s.ADCMaxTime < 7){

           sHitPos = s.Strip + 0.5;

           }

        if (sHitPos > 0){

           stripHits.push_back(sHitPos);

           }

}


void MakeHit2(Strips &s, Strips &sSide, vector<double>& stripHits){// deal with first last fired strip in one layer

        Strips tempStrip;
        tempStrip.ADCTotal = 0;
        tempStrip.MaxADC = 0;

        if (s.Strip < sSide.Strip){//first fired strip in one layer

           if (CheckRight(s, sSide)){//have adjacent fired strip on the right

              if (IsGoodPeak(s, tempStrip, sSide)){//good peak

                   stripHits.push_back(s.Strip + 0.5 + FindRatio(s, tempStrip, sSide));

                   }

              }else{//singlet

                   MakeHit1(s, stripHits);

                   }

           }else if(s.Strip > sSide.Strip){//last fired strip in one layer

                   if (CheckLeft(s, sSide)){//have adjacent fired strip on the left

                      if (IsGoodPeak(s, sSide, tempStrip)){// good peak

                         stripHits.push_back(s.Strip + 0.5 + FindRatio(s, sSide, tempStrip));

                         }

                      }else{//singlet

                           MakeHit1(s, stripHits);

                           }

                   }

}


void MakeHit3(Strips &s, Strips &sSideL, Strips  &sSideR, vector<double>& stripHits){

        bool stripOnTheLeft = CheckLeft(s, sSideL);
        bool stripOnTheRight = CheckRight(s, sSideR);

        if ( !stripOnTheLeft && !stripOnTheRight){//singlet

           MakeHit1(s, stripHits);

           }else if( stripOnTheLeft && !stripOnTheRight ){// left, c, no right

                   MakeHit2(s, sSideL, stripHits);

                   }else if(!stripOnTheLeft && stripOnTheRight){//no left, c, right

                           MakeHit2(s, sSideR, stripHits);

                           }else if(stripOnTheLeft && stripOnTheRight){//left , c, right

                                   if (IsGoodPeak(s, sSideL, sSideR)){

                                      stripHits.push_back(s.Strip + 0.5 + FindRatio(s, sSideL, sSideR));

                                      }

                                   }



}

bool IsGoodPeak(Strips &s, Strips &sSideL, Strips& sSideR){

        bool goodPeak = false;

        if ( (s.MaxADC + sSideL.MaxADC + sSideR.MaxADC) > 25 &&//toal charge of strip cluster > 25
             (s.ADCMaxTime > 2 && s.ADCMaxTime < 7) &&//peak time >2 < 7
             (s.MaxADC >= sSideL.MaxADC && s.MaxADC >= sSideR.MaxADC) ){//is a peak..

           goodPeak = true;

           }


        return goodPeak;
}

double FindRatio(Strips &s, Strips& sSideL, Strips& sSideR){

        double ratio = -99;

        ratio = 0.5*(sSideR.ADCTotal - sSideL.ADCTotal)/(s.ADCTotal - min(sSideL.ADCTotal, sSideR.ADCTotal));

        return ratio;

}

bool CheckRight(Strips &s, Strips &sR){

//      double chargeOfRightStrip = -99;
        bool nextToThisStrip = false;

        if (sR.Strip - s.Strip == 1){

//         chargeOfRightStrip = s2.ADCTotal;
           nextToThisStrip = true;

           }

//      return chargeOfRightStrip;
        return nextToThisStrip;
}

bool CheckLeft(Strips &s, Strips &sL){

//        double chargeOfLeftStrip = -99;
        bool nextToThisStrip = false;

        if (s.Strip - sL.Strip == 1){

//           chargeOfLeftStrip = s2.ADCTotal;
             nextToThisStrip = true;

           }

//        return chargeOfLeftStrip;
        return nextToThisStrip;
}


template <class T>
vector<int> FindChamberIndex(CSCDetID id, vector<T> &vec){

        vector<int> chamber;
        for (int i = 0; i < int(vec.size()); i++){

            CSCDetID tempID = vec[i].first;
            if (id.Endcap == tempID.Endcap &&
                id.Station == tempID.Station &&
                id.Ring == tempID.Ring &&
                id.Chamber == tempID.Chamber){

                chamber.push_back(i);

                }

            }

        return chamber;
}


void WireDisplay(CSCDetID id, vector<int>& layer_wire, vector<WIRE>& wire, TH2F* wireDis, TH2F* wireDis_text){


          for (int i = 0; i < int(layer_wire.size()); i++){//in each interesting layer has wire hits

              int tempLayer = wire[layer_wire[i]].first.Layer;
              vector<Wire> tempWire = wire[layer_wire[i]].second;

              MakeOneLayerWireDisplay(tempLayer, tempWire, wireDis);

              if (tempLayer == id.Layer){

                 MakeOneLayerWireDisplay(tempLayer, tempWire, wireDis_text);

                 }
              }

          SetHistContour(wireDis, 0, 16);

          wireDis_text->SetMarkerSize(2);

          wireDis->GetZaxis()->SetLabelSize(0.1);
          wireDis->GetZaxis()->SetRangeUser(0, 16);
          wireDis->SetStats(0);
          wireDis->GetXaxis()->SetTitle("Wire Group Number");
          wireDis->GetYaxis()->SetTitle("Layer");
          wireDis->GetXaxis()->SetLabelSize(0.1);
          wireDis->GetYaxis()->SetLabelSize(0.1);
          wireDis->GetXaxis()->SetTitleSize(0.11);
          wireDis->GetYaxis()->SetTitleSize(0.11);
          wireDis->GetXaxis()->SetTitleOffset(0.81);
          wireDis->GetYaxis()->SetTitleOffset(0.2);
          wireDis->SetTitle("");//"Anode Hit Timing");
          wireDis->GetXaxis()->SetNdivisions(2012);
          wireDis->GetYaxis()->SetNdivisions(110);
}

void SetEventDisplayLegend(TString legendName){

          TLegend* leg = new TLegend(0.05, 0.95, .2, .99);
          leg->AddEntry((TObject*)0, legendName, "");
          leg->SetFillColor(0);
          leg->SetBorderSize(0);
          leg->SetTextSize(0.1);
          leg->Draw();


}


void ComparatorDisplay(CSCDetID id, vector<int>& layer_comparator, vector<COMPARATOR>& comparator, TH2F* comparatorDis, TH2F* comparatorDis_text){


          for (int i = 0; i < int(layer_comparator.size()); i++){//in each interesting layer has wire hits

              int tempLayer = comparator[layer_comparator[i]].first.Layer;
              vector<Comparator> tempComparator = comparator[layer_comparator[i]].second;

              MakeOneLayerComparatorDisplay(tempLayer, tempComparator, comparatorDis);

              if (tempLayer == id.Layer){

                 MakeOneLayerComparatorDisplay(tempLayer, tempComparator, comparatorDis_text);

                 }
              }

          SetHistContour(comparatorDis, 0, 16);

          comparatorDis_text->SetMarkerSize(2);

          comparatorDis->GetZaxis()->SetLabelSize(0.1);
          comparatorDis->GetZaxis()->SetRangeUser(0, 16);
          comparatorDis->SetStats(0);
          comparatorDis->GetXaxis()->SetTitle("Comparator Number");
          comparatorDis->GetYaxis()->SetTitle("Layer");
          comparatorDis->GetXaxis()->SetLabelSize(0.1);
          comparatorDis->GetYaxis()->SetLabelSize(0.1);
          comparatorDis->GetXaxis()->SetTitleSize(0.11);
          comparatorDis->GetYaxis()->SetTitleSize(0.11);
          comparatorDis->GetXaxis()->SetTitleOffset(0.81);
          comparatorDis->GetYaxis()->SetTitleOffset(0.2);
          comparatorDis->SetTitle("");//"Comparator Hit Timing");
          comparatorDis->GetXaxis()->SetNdivisions(2016);
          comparatorDis->GetYaxis()->SetNdivisions(110);
}


void SetPlotDetail_StripHit(TGraph* stripHitDis){

          stripHitDis->GetXaxis()->SetLimits(1, 114);
          stripHitDis->GetYaxis()->SetRangeUser(1, 7);
          stripHitDis->SetMarkerStyle(20);
          stripHitDis->GetXaxis()->SetTitle("Local X[Strip Width]");
          stripHitDis->GetYaxis()->SetTitle("Layer");
          stripHitDis->GetXaxis()->SetLabelSize(0.1);
          stripHitDis->GetYaxis()->SetLabelSize(0.1);
          stripHitDis->GetXaxis()->SetTitleSize(0.11);
          stripHitDis->GetYaxis()->SetTitleSize(0.11);
          stripHitDis->GetXaxis()->SetTitleOffset(0.81);
          stripHitDis->GetYaxis()->SetTitleOffset(0.2);
          stripHitDis->GetXaxis()->SetNdivisions(1010);
          stripHitDis->GetYaxis()->SetNdivisions(110);
          stripHitDis->SetTitle();//"Strip Hit");


}

