# Current Scraper

For scraping currents off the [CSC Current Viewer](http://emugif1.cern.ch:8080/CSC/):
  * To view, either be at CERN or tunnel with `ssh -ND 1081 adasgupt@lxplus.cern.ch`. Change Firefox proxy to Manual, SOCKS Host: localhost, Port: 1081.
  * To scrape, either be at CERN or on lxplus. I haven't figured out how to configure Firefox's proxy settings via Selenium.
  * [Selenium](http://www.seleniumhq.org/) is required. On lxplus, `pip install --user selenium` to install to `.local`. On a Mac, set up a `virtualenv`.
  * *sel.py* (and the modern version) takes in `timedata`, and automates the pointy-clicky to get current measurements. Redirect to a file.
  * `timedata` is produced using `makeTimeData.py`. It requires there be the Automated TMB Dump-style files in *../database_scraper/tmb/*.

  * *curr2hut.py* makes a table (*attenhut*) from the current data from *sel.py*
    * Strip `;`, `[i]`, means (`_m`), and add attenuation factors `A=XX` before measurements
  * *attenhut* contains the relevant current data
  * *plotter_atten_curr.py* makes *attenVcurr.pdf*, a plot of current vs. downstream attenuation.

### From when 'Currents' used to live in 'analysis'
This is a home for `attenhut`, which is just a tabular format for the scraped currents, and for the plotting script.

I didn't automate adding the attenuations out front. It's straightforward; make a list of the measurements, grep/awk on meta, and copy them in.

Note that for TB5, there seems to be some missing data.

The following measurements were borrowed:
  * 3239 copied from 3237
  * 3250 copied from 3249
  * 3254 copied from 3253
