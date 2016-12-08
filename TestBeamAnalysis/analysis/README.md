# Analysis Scripts

Currents:
  * *curr2hut.py* makes a table from the current data from *sel.py*
    * Strip `;`, `[i]`, means (`_m`), and add attenuation factors `A=XX` before measurements
  * *plotter_atten_curr.py* makes *attenVcurr.pdf*, a plot of current vs. downstream attenuation.
  * *attenhut* and *rels* contain the relevant current data

Rates:
  * *makeTMBRates.py* makes the rate plots
  * Other scripts in here make other rates plots -- may be moved eventually
  * (DEPRECATED)
    * Wells's code in AnalysisScripts is obsolete
    * I've made *plotter_CLCT_lumi.py* and *card.conf* obsolete as well. We have other code now.

Efficiencies:
  * *EffTable.py* makes a table of event counts with various criteria
  * *makeLCT.py* makes the LCT efficiency plots
    * anything with *_Y* is for comparing to Yuriy's data

Event Displays:
  * *EventDisplay.py* makes an event display of wires, comparators, and strip ADC counts
    * It copied Hualin's GIFDisplay code, which we've now made obsolete
  * *RecHitDisplay.py* makes an event display of RecHits

DQM:
  * This is for general exploratory code. Use to quickly make i.e. occupancy plots

Timber:
  * This is for interacting with and making plots of TIMBER data. Mostly for cross-check purposes with L1As
