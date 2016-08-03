#include "structForDisplay.h"
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

using namespace std;

typedef pair<CSCDetID, vector<Wire> > WIRE;
typedef pair<CSCDetID, vector<Strips> > STRIP;
typedef pair<CSCDetID, vector<Comparator> > COMPARATOR;

void WireStripDisplay(TString address, CSCDetID id, vector<WIRE> &wire, vector<STRIP> &strip, vector<COMPARATOR> &comparator, vector<CSCDetID> &usedChamber, int Run, int Event);
bool ChamberUsedForEventDisplay(CSCDetID id, vector<CSCDetID> usedChamber);
void SetSaveNameLegendName(TString& name, TString& legendName, TString address, CSCDetID id, int Run, int Event);
void SaveUsedChamber(CSCDetID id, vector<int> layer_strip, vector<int> layer_wire, vector<int> layer_comparator, vector<CSCDetID> &usedChamber);
void StripDisplay(CSCDetID id, vector<int>& layer_strip, vector<STRIP>& strip, double cfeb[], TH2F* stripDis, TH2F* stripDis_text, TH1F* cfebNotReadOut);
void MakeOneLayerStripDisplay(int layer, vector<Strips> &s, TH2F* stripDisplay, int option);
void MakeOneLayerWireDisplay(int layer, vector<Wire> &w, TH2F* wireDisplay);
void MakeOneLayerComparatorDisplay(int layer, vector<Comparator> &c, TH2F* comparatorDisplay);
vector<vector<double> > StripHitDisplay(CSCDetID id, vector<int>& layer_strip, vector<int>& layer_comparator, vector<STRIP> strip, vector<COMPARATOR> &comparator, double cfeb[]);
vector<double> MakeComparatorHitNotReadout(vector<Comparator> c, double cfeb[]);
void SetTitle(TPaveText* pt, TString name);
template <typename T>
string NumberToString( T Number );
void CountCFEB(double cfeb[], vector<Strips> s);
void BlockUnreadCFEB(double cfeb[], TH1F* cfebNotReadOut, int nCFEB);
void SetHistContour(TH2F* hist, double Min, double Max);
vector<double> MakeStripHit(vector<Strips> sp);
void ShiftStripHits(vector<double>& stripHits, double layer);
void MakeHit1(Strips &s, vector<double>& stripHits);//deal with strip singlet
void MakeHit2(Strips &s, Strips &sSide, vector<double>& stripHits);// deal with first last fired strip in one layer
void MakeHit3(Strips &s, Strips &sSideL, Strips  &sSideR, vector<double>& stripHits);
bool IsGoodPeak(Strips &s, Strips &sSideL, Strips& sSideR);
double FindRatio(Strips &s, Strips& sSideL, Strips& sSideR);
bool CheckRight(Strips &s, Strips &sR);
bool CheckLeft(Strips &s, Strips &sL);
template <class T>
vector<int> FindChamberIndex(CSCDetID id, vector<T> &vec);
void WireDisplay(CSCDetID id, vector<int>& layer_wire, vector<WIRE>& wire, TH2F* wireDis, TH2F* wireDis_text);
void SetEventDisplayLegend(TString legendName);
void ComparatorDisplay(CSCDetID id, vector<int>& layer_comparator, vector<COMPARATOR>& comparator, TH2F* comparatorDis, TH2F* comparatorDis_text);
void SetPlotDetail_StripHit(TGraph* stripHitDis);

