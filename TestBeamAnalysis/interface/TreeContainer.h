#ifndef TREECONTAINER_H
#define TREECONTAINER_H

#include <algorithm>

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/CSCRecHit/interface/CSCRecHit2DCollection.h"
#include "DataFormats/CSCDigi/interface/CSCStripDigiCollection.h"
#include "DataFormats/CSCDigi/interface/CSCWireDigiCollection.h"
#include "DataFormats/CSCDigi/interface/CSCComparatorDigiCollection.h"
#include "DataFormats/CSCDigi/interface/CSCCorrelatedLCTDigiCollection.h"
#include "DataFormats/CSCRecHit/interface/CSCSegmentCollection.h"
#include "DataFormats/CSCDigi/interface/CSCCLCTDigiCollection.h"
#include "DataFormats/CSCDigi/interface/CSCALCTDigiCollection.h"
#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/RecoCandidate/interface/RecoCandidate.h"
#include "DataFormats/MuonReco/interface/MuonFwd.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "Geometry/CSCGeometry/interface/CSCGeometry.h"
#include "Geometry/Records/interface/MuonGeometryRecord.h"

#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TLorentzVector.h"

#include "DataFormats/Math/interface/deltaPhi.h"

#include "Gif/TestBeamAnalysis/interface/GIFHelper.h"

typedef	unsigned char		 size8 ; // 8 bit 0->255
typedef	unsigned short int	 size16; //16 bit 0->65536
typedef	unsigned int		 size  ; //32 bit 0->4294967296

class TreeContainer
{
	public:
		TreeContainer(TString treeName, TString treeTitle){
			edm::Service<TFileService> fs;
			tree = fs->make<TTree>(treeName,treeTitle);
		}
		void write() {
			tree->Write();
		}
		void fill() {tree->Fill();}
		TTree * tree;
};

#endif
