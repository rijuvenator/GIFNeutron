# Database Scraper

For scraping the [CSC GIF Measurements Database](https://oraweb.cern.ch/pls/cms_emu_fast.pro/gif_log.top_page):
  * *scrape.py* is the main engine.
    * Do `./scrape.py > meta` to update *meta* and save all TMB dumps in *tmb/*.
    * Any quirks will print to the terminal (to `stderr`). Follow up on these.
  * *meta* is the scraped database. Each line's format is `Meas Cham HV Source Beam Up Down FF File`.
    * *meta_cam* are Cameron's measurements, along with the modified register values.
  * *starlord.sh* finds the number of files for each raw file with a `*` in it.
    * Update *starlord.sh* with the cutoff for `/raid/` vs. `/mnt/backup/raid/`.
    * Do `./starlord.sh > star_exploded` to update *star_exploded*.
  * *star_exploded* is a list of measurements with how many files are associated with them.
  * *autopass.sh* is an `expect` script for ssh'ing or scp'ing automatically.
  * *trig.sh* makes a table from the TMB dumps in `tmb/`, output to `trigdata`.
    * Usage is `./autopass.sh PASSWORD COMMAND`
    * *trig_cam.sh* reads Cameron's measurements and makes a table, output to `trigdata_cam`
  * *byFilter.sh* makes a list of TMB dumps by chamber and downstream attenuation. Good for sorting.
  * *kat* contains the script for the silly renaming scheme and some filenames split up somehow. I haven't looked at this in a while.
  * *notes* contains a record of quirks.
    * There is a list of empty records. Igor needs to remove these from the database.
    * I have edited the database for everything else, so there should be no errors.
  * *urls/* contains two scripts for making *dqm_urls* and *bad_urls* from *meta*
    * *makeURL.sh* makes *dqm_urls* and *bad_urls* using *meta* and *url.awk*
    * *url.awk* is used by *makeURL.sh*, taking in a list of `FILENAME CHAM` with URLs as output
    * *dqm_urls* and *bad_urls* are what they sound like
      * Note that star files are not considered
      * Note that URLs contain `/backup` by default; remove them from the ones in current

## LEGACY SCRAPER README (in *legacy/*)

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
  * Read *notes* for quirks requiring manual edits.
