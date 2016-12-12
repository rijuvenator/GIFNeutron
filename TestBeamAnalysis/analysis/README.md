# Analysis Scripts

Rates:
  * *makeTMBRates.py* makes the rate plots
  * (DEPRECATED)
    * Wells's code in AnalysisScripts is obsolete
    * I've made *plotter_CLCT_lumi.py* and *card.conf* obsolete as well. We have other code now.

LCTs:
  * *EffTable.py* makes a table of event counts with various criteria
  * *plotVenn.py* makes efficiency plots given any two columns above; will eventually replace *makeLCT.py*
  * *makeLCT.py* makes the LCT efficiency plots
    * anything with *_Y* is for comparing to Yuriy's data

Segments:
  * *CFEBReadOutEff.py* makes a plot of the CFEB read out efficiency
  * *makeSegHits.py* makes a plot of the average number of hits used to make a segment

Event Displays:
  * *EventDisplay.py* makes an event display of wires, comparators, and strip ADC counts
    * It copied Hualin's GIFDisplay code, which we've now made obsolete
  * *RecHitDisplay.py* makes an event display of RecHits
  * *Patterns.py* is used by *EventDisplay.py* to compute coordinates for patterns
  * *DisplayHelper.py* is a version of *Plotter.py* specially designed for event displays

DQM:
  * This is for general exploratory code. Use to quickly make i.e. occupancy plots

Timber:
  * This is for interacting with and making plots of TIMBER data. Mostly for cross-check purposes with L1As
