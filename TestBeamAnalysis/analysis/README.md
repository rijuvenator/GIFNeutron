# Analysis Scripts

Currents:
  * *curr2hut.py* makes a table from the current data from *sel.py*
    * Strip `;`, `[i]`, means (`_m`), and add attenuation factors `A=XX` before measurements
  * *plotter_atten_curr.py* makes *attenVcurr.pdf*, a plot of current vs. downstream attenuation.
  * *attenhut* and *rels* contain the relevant current data

Rates:
  * *plotter_CLCT_lumi.py* makes plots with *card.conf* as an input "data card", as an example.
    * Wells's code in AnalysisScripts is obsolete
  * *makePlots.py* makes the rate plots
