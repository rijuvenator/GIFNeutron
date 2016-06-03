# Gif
Analysis code to produce plots of reconstruction performance.  

Original documentation is at https://twiki.cern.ch/twiki/bin/view/CMS/CSCTestBeamDataTreatment

Process in standard in 7_5_1.  

    cmsrel CMSSW_7_5_1
    cd CMSSW_7_5_1/src/
    cmsenv
    git clone ssh://git@gitlab.cern.ch:7999/CSC-GIF/Gif.git 
    git cms-addpkg EventFilter/CSCRawToDigi
    sed -i 's$int ilayer = 0; /// layer=0 flags entire chamber$int ilayer = 0; /// layer=0 flags entire chamber\n    if (vmecrate == 1 && dmb == 4) {vmecrate = 13; dmb = 1;} // For GIF data, set to a ME2/1 chamber$' EventFilter/CSCRawToDigi/plugins/CSCDCCUnpacker.cc
    scram b
    cd Gif/Gif/test 
    cmsRun gif.py

In gif.py set input file name you obtained from readFile.py and set output name for the root file with the result histograms.
The output is: root file and pdf file with plots. 

    The analysis code itself is in CMSSW_7_x_x/src/Gif/Gif/plugins/Gif.cc
    There are a lot of includes in the top of the file and some of them are not needed, but I'm too lazy to remove the unnecessary.
    Add or modify the declaration of new histograms and variables in class Gif declaration.
    Set up values in Gif class constructor.
    The analysis is done in Gif::analyze method. This contains 4 parts:
    A. Some event setup stuff. 
    B. Work with RecHits (==HITS==) 
    C. Work with wiregroup DIGIs (==WIRES==) 
    D. Work with strip DIGIs (==STRIPS==) 

    Fill your own or modify mine histograms in these parts
    In method Gif::endJob store histograms and other objects to root file (the output for gif.py) and plot pictures to pdf file. Do not forget to add the your new result histograms to output. 
    