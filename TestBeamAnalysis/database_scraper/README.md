# Database Scraper

For scraping the [CSC GIF Measurements Database](https://oraweb.cern.ch/pls/cms_emu_fast.pro/gif_log.top_page):
  * *scrape.sh* is the main engine. Change the password in the argument to `autopass.sh`. Escape carefully.
    * `./scrape.sh` will produce several files. Make sure there is no file named *table* or *tmp*.
      * *all_files* is an `ls` of files on `emugif2`.
      *	*measlist* is the list of measurements on the database.
      * *final* are pairs of measurements and raw files/TMB/Missing_file. Uses *internal/get_logs.sh*
      * *meta* is meta-data: `Meas Cham HV Source Beam Up Down FF`. Uses *internal/get_logs.sh*
      * *tmb/* is a folder with TMB dumps, plus the last line with the duration.
      * *orphan_meas* are measurements without a raw file, or otherwise tagged as TMB or Missing_file.
      * *orphan_raw* are raw files without an associated measurements. Stars are not included.
      * *missing* are measurements whose raw file is not in *all_files*. Compare with */mnt/backup/* on `emugif2`.
      * *dqm_urls* are URLs to DQM plots, generated from the file name. (using *url.awk*)
      * *bad_urls* are URLs that don't exist (fail checked with `curl`)
      * *daq_runs* are runs with FastFilterScanSettings 0-4
  * *autopass.sh* is an `expect` script for ssh'ing or scp'ing automatically.
    * `./autopass.sh PASSWORD COMMAND`
  * Read *notes* for quirks requiring manual edits.
  * *trig.sh* makes a table from the TMB dumps in `tmb/`, output to `trigdata`
  * *byFilter.sh* makes a list of TMB dumps by chamber and downstream attenuation. Good for sorting.
  * *kat* contains the script for the silly renaming scheme and some filenames split up somehow. I haven't looked at this in a while.
