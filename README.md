# Gif
Analysis code to produce plots of reconstruction performance.  

Original documentation is at https://twiki.cern.ch/twiki/bin/view/CMS/CSCTestBeamDataTreatment

Process in standard in 7_5_1.  

    cmsrel CMSSW_7_5_1
    cd CMSSW_7_5_1/src/
    cmsenv
    git clone ssh://git@gitlab.cern.ch:7999/CSC-GIF/Gif.git 
    git cms-addpkg EventFilter/CSCRawToDigi
    sed -i 's$int ilayer = 0; /// layer=0 flags entire chamber$int ilayer = 0; /// layer=0 flags entire chamber\n    if (vmecrate == 1 \&\& dmb == 4) {vmecrate = 13; dmb = 1;} // For GIF data, set to a ME2/1 chamber$' EventFilter/CSCRawToDigi/plugins/CSCDCCUnpacker.cc
    scram b
    cd Gif/Gif/test 
    cmsRun gif.py          # Make analysis plots.
    cmsRun gif.py input=1  # Specify a given input file.
    source gif.src         # Process multiple input files.
    makeComparisonPlots.py -i inputME21_Test40.py   # Make comparison plots.
    mergeOutput.py   
    cd ../../../Gif/GifDisplay/test  
    cmsRun gifDisplay.py  # Make event displays.  

Note that at GIF++ the ME2/1 chamber DMB is in the slot (vmecrate = 1; dmb slot = 4) that corresponds to an ME1/2 chamber.  
To get the correct geometry the vmecrate and dmb have to be modified so that the reconstruction thinks it is dealing with an ME2/1 chamber.  
You can get the vmecrate and dmb for a given chamber from the local DQM page, which for a given chamber will list the PCrate and DMB Slot.  
Local DQM page:  http://csc-dqm.cms:20550/urn:xdaq-application:lid=1450
Instructions to access local DQM outside P5:  https://twiki.cern.ch/twiki/bin/view/CMS/CSCDOCshiftInformation#Looking_at_internal_web_pages_fr

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
    
In gifDisplay.py:

    -Specify input file containing fedRawDataCollection produced by running unpacker in IORawData repository.
    -Edit path (eventDisplayDir) to save eventdisplay.
    -Change option "chamberType" to 11 or 21 when dealing with ME1/1 or ME2/1.
    -Provide list of event number in eventList.txt.  

    