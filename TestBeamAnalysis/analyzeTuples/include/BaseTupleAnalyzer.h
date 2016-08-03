#ifndef GIF_CSCDIGITUPLES_ANALYZETUPLES_BASETUPLEANALYZER_H
#define GIF_CSCDIGITUPLES_ANALYZETUPLES_BASETUPLEANALYZER_H

#include <TFile.h>
#include <TString.h>
#include <TTree.h>
#include <assert.h>
#include <iostream>

class BaseTupleAnalyzer{
public:
  BaseTupleAnalyzer(TString fileName, TString treeName) : eventNumber(0){
    std::clog << "Loading file: "<< fileName <<" and tree: " << treeName <<std::endl;
    file = TFile::Open(fileName,"READ");
    assert(file);
    tree = (TTree*)(file->Get(treeName) );
    assert(tree);
    tree->SetBranchStatus("*",0);
    std::clog << tree->GetEntries() << " entries to process" << std::endl;
  }

  virtual ~BaseTupleAnalyzer()
  {
    file->Close();
    delete file;
  }
  virtual void analyze(int reportFrequency = 1000000) {
    while(nextEvent(reportFrequency)){runAEvent();eventNumber++;}
  }
  virtual void runAEvent() = 0;

  //Load the next event from the tree....return false if there are no more events in the tree
  bool nextEvent(int reportFrequency = 1000000)
  {
    if(eventNumber >= tree->GetEntries()) return false;
    tree->GetEntry(eventNumber);

    if(eventNumber%reportFrequency == 0)
      std::clog << "Processing event " << eventNumber << std::endl;

    return true;
  }

  template<typename varType>
  void setBranchAddress(const std::string varName, varType **var, bool require = false, bool verbose = true){
    TString tBranchName = varName.c_str();
    if(tree->GetBranch(tBranchName)){
      tree->SetBranchStatus(tBranchName,1);
      tree->SetBranchAddress(tBranchName,var);
    }
    else {
      if(require) throw std::invalid_argument(( TString("TreeReader::setBranchAddress could not load variable: " ) + tBranchName).Data() );
      if(verbose)std::clog << " -" <<tBranchName;
    }
  }

  template<typename varType>
  void setBranchAddress(const std::string varName, varType *var, bool require = false, bool verbose = true){
    TString tBranchName = varName.c_str();
    if(tree->GetBranch(tBranchName)){
      tree->SetBranchStatus(tBranchName,1);
      tree->SetBranchAddress(tBranchName,var);
    }
    else {
      if(require) throw std::invalid_argument(( TString("TreeReader::setBranchAddress could not load variable: " ) + tBranchName).Data() );
      if(verbose)std::clog << " -" <<tBranchName;
    }
  }

  TFile * file;
  TTree * tree;
  int     eventNumber; //current event number
};
#endif
