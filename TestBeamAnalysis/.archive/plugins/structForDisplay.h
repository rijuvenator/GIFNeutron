#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <iostream>
#include <fstream>
#include <list>
#include <vector>
#include "TF1.h"
#include <TH2.h>
#include <TGraph.h>
#include "TPaveText.h"
#include <iomanip>
#include <ctime>
#include <string>
#include <cmath>

//x axis station, y axis ring
/*TH2F* NWireGroup;
TH2F* NStrip;

NWireGroup = new TH2F("NWireGroup", "NWireGroup", 4, 1, 5, 4, 1, 5);
NStrip = new TH2F("NStrip", "NStrip", 4, 1, 5, 4, 1, 5);

NWireGroup->SetBinContent(1, 1, 48);
NWireGroup->SetBinContent(1, 2, 48);
NWireGroup->SetBinContent(1, 3, 48);
NWireGroup->SetBinContent(1, 4, 48);
NWireGroup->SetBinContent(2, 1, 112);
NWireGroup->SetBinContent(3, 1, 96);
NWireGroup->SetBinContent(4, 1, 96);
NWireGroup->SetBinContent(2, 2, 64);
NWireGroup->SetBinContent(3, 2, 64);
NWireGroup->SetBinContent(4, 2, 64);

NStrip->SetBinContent(1, 1, 48);
NStrip->SetBinContent(1, 2, 80);
NStrip->SetBinContent(1, 3, 64);
NStrip->SetBinContent(1, 4, 64);
NStrip->SetBinContent(2, 1, 80);
NStrip->SetBinContent(3, 1, 80);
NStrip->SetBinContent(4, 1, 80);
NStrip->SetBinContent(2, 2, 80);
NStrip->SetBinContent(3, 2, 80);
NStrip->SetBinContent(4, 2, 80);
*/
using namespace std;

inline bool doubleEqual(double a, double b) {
        return abs(a - b) < 1E-6;
}

struct CSCDetID{

        double Endcap;
        double Station;
        double Ring;
        double Chamber;
        double Layer;

        bool operator == (const CSCDetID& id)  {
                return doubleEqual(id.Endcap, this->Endcap)
                        && doubleEqual(id.Station, this->Station)

                        && doubleEqual(id.Chamber, this->Chamber)
                        && doubleEqual(id.Layer, this->Layer);
        }

        CSCDetID(){
                this->Endcap = 0.0;
                this->Station = 0.0;
                this->Ring=0.0;
                this->Chamber = 0.0;
                this->Layer = 0.0;
        }
};

struct  Wire{

  int WireGroup;
  int TimeBin;
  int NumberTimeBin;

  bool operator == ( const Wire& WG) const{

       return WG.WireGroup == this->WireGroup;

  }

  bool operator < ( const Wire& WG) const{

       return this->WireGroup < WG.WireGroup;}

  Wire(){

        this->WireGroup = -99;
        this->TimeBin = -99;
        this->NumberTimeBin = -99;

        }

};


struct Strips{

 int Strip;
 int ADCTotal;
 int MaxADC;
 int ADCMaxTime;
 vector<double> ADC;
 vector<double> TimeBin;

 bool operator == ( const Strips& st) const {

       return st.Strip == this->Strip;

  }

  bool operator < ( const Strips& st) const {

       return  this->Strip < st.Strip;
}
  Strips(){

          this->Strip = -99;
          this->ADCTotal = -99;
          this->MaxADC = -99;
          this->ADCMaxTime = -99;

          }

};


struct Comparator{

 int Strip;
 int TimeBin;
 int ComparatorNumber;

 bool operator < ( const Comparator& com) const{

  return this->ComparatorNumber < com.ComparatorNumber;

  }

};



