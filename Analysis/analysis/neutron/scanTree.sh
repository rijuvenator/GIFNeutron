#!/bin/bash

SUFFIX=$1
COMMAND=$2

TREE=${CMSSW_BASE}/src/Gif/Analysis/analysis/neutron/forest/partTree_${SUFFIX}.root

#cat << EOF > script${SUFFIX}.C
#void script${SUFFIX}()
#{
#	TFile *f = TFile::Open("${TREE}");
#	TTree *t = (TTree*) f->Get("partTree");
#	t->SetScanField(0);
#	t->Scan(${COMMAND});
#}
#EOF
#root -l -q -b script${SUFFIX}.C
#rm script${SUFFIX}.C

cat << EOF > script${SUFFIX}.py
import ROOT as R

f = R.TFile.Open('$TREE')
t = f.Get('partTree')
t.SetScanField(0)
t.Scan($COMMAND)
EOF
python script${SUFFIX}.py
rm script${SUFFIX}.py
