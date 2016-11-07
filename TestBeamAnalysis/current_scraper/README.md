# Current Scraper

For scraping currents off the [CSC Current Viewer](http://emugif1.cern.ch:8080/CSC/):
  * To view, either be at CERN or tunnel with `ssh -ND 1081 adasgupt@lxplus.cern.ch`. Change Firefox proxy to Manual, SOCKS Host: localhost, Port: 1081.
  * To scrape, either be at CERN or on lxplus. I haven't figured out how to configure Firefox's proxy settings via Selenium.
  * [Selenium](http://www.seleniumhq.org/) is required. On lxplus, `pip install --user selenium` to install to `.local`. On a Mac, set up a `virtualenv`.
  * *sel.py* (and the modern version) takes in `timedata`, and automates the pointy-clicky to get current measurements. Redirect to a file.
  * `timedata` is produced using `makeTimeData.py`. It requires there be the Automated TMB Dump-style files in *../database_scraper/tmb/*.
