## To make `bunchstructures`:
  1. Make `runlist`
    * print out `t.Event_RunNumber`
    * `uniq` it (for convenience)
  2. Make `filllist`
    * go to [WBM's Fill Report](https://cmswbm.cern.ch/cmsdb/servlet/FillReport)
    * put in the fill range that has all the fills needed
    * download the `.csv`
    * do `awk 'BEGIN {FS="\t"} {print $1, $25}' FILENAME | tail -n +2` (gets the fills and runs, strips the first line)
	* do `for i in $(cat runlist); do grep $i fills; done | sort | uniq`
  3. Make `bunchstructures`
    * `python printBXPatterns.py > bunchstructures`
