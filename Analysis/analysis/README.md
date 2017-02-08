# Analysis Scripts

*BASIC.py* is a skeleton analyzer. It sets up dealing with currents, attenuations, luminosities, and all the different FF types; all that is needed is to fill a "data dictionary" and modify the relevant plotting code.

*TreeTest.py* is a test script that imports all the modules, gets a tree, gets an event, declares all the branches, makes lists of primitives, finds a segment in the paddle region, and matches a segment to an LCT. It prints `Test successful.` if everything works.

Rates:
  * *makeTMBRates.py* makes the rate plots
  * (DEPRECATED)
    * Wells's code in AnalysisScripts is obsolete
    * I've made *plotter_CLCT_lumi.py* and *card.conf* obsolete as well. We have other code now.

LCTs:
  * *EffTable.py* makes a table of event counts with various criteria
  * *plotVenn.py* makes efficiency plots given any two columns above; will eventually replace *makeLCT.py*
  * (DEPRECATED)
    * *makeLCT.py* makes the LCT efficiency plots
      * anything with *_Y* is for comparing to Yuriy's data

Segments:
  * *CFEBReadOutEff.py* makes a plot of the CFEB read out efficiency
  * *avgSegHits.py* makes a plot of the average number of hits used to make a segment
  * *chiSquare.py* makes plots of chi-squared distributions, and plots of their mean and SD
  * *noPrimitives.py* makes a plot of segment inefficiency due to missing primitives
  * *displaced.py* makes various plots that quantify displaced RecHits

Event Displays:
  * *EventDisplay.py* makes an event display of wires, comparators, and strip ADC counts
    * It copied Hualin's GIFDisplay code, which we've now made obsolete
  * *RecHitDisplay.py* makes an event display of RecHits
  * *Patterns.py* is used by *EventDisplay.py* to compute coordinates for patterns
  * *DisplayHelper.py* is a version of *Plotter.py* specially designed for event displays
  * *batchDisplays.sh* shows a demonstration of how to create event displays

DQM:
  * This is for general exploratory code. Use to quickly make i.e. occupancy plots

Timber:
  * This is for interacting with and making plots of TIMBER data. Mostly for cross-check purposes with L1As
