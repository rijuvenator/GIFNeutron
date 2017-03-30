## Documentation

  * simHitMythology prints particle chains and the last line in GEANT logs for each actual SimHit
  * soundOfThunder is mostly a plotter; it plots DeltaS vs ELoss, but you know where the SimHit came from... There's also a line that prints out only the "short" simhits, which can be saved in a file, to be used by the next script
  * selectedMyths uses shorttracks and prints detailed GEANT logs for each one. I used this to see exactly what was happening with the short SimHits
  * SH_CapE_TOF is like simHitMythology, but it prints out different information, specifically the tof and the last neutron energy
  * plotCapETOF makes the scatter plot of CapE vs TOF
