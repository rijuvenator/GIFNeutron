# Plotter Class and Macro

The intent is for these files to be used as templates for all plotting macros. By design, I do not intend `Plotter.py` to be modified.

So whenever a new "type" of plot is desired, copy a fresh `plotterMacro.py` and fill in the relevant details.

The files are well documented, but I'll summarize here.
  * The `Plot` class contains a plot (e.g. a THn, THStack, TGraph, etc.) and some metadata.
  * The `Canvas` class contains a TCanvas, some metadata, and some functions.
  * The basic usage consists of:
    * instantiating `Plot` objects with plots and their metadata
    * instantiating a `Canvas` object with its metadata
    * instantiating the legend (even if no legend will be drawn)
    * adding the plots to the `Canvas` object
    * finishing the `Canvas`
    * drawing it or saving the `Canvas.c` to a file
