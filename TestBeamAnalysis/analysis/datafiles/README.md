# Data Files

This is a home for various data files used by other analysis scripts.

  * I've started a convention of *data_* for data files and *old_* for old files
  * *trigdata* should be a symlink to the file in *database_scraper/*
  * *measgrid* is a list of measurement numbers
	* Indexed by attenuation factor, with the list corresponding to DAQ Scan parameters 1-8
  * *attenhut* is mostly a copy of the file in *currents*, except `0` is now `inf`
