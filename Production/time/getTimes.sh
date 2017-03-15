#!/bin/bash
# requires crab logs
# crab getlog --short --jobids 1-<end> crab/<project-dir>
# should be something like crab/<project-dir>/results/job_out.<jobid>.0.txt
# place this into the results directory of the CRAB job
grep "== CMSSW:  - Min event:" * | awk '{print $6}' > MinEventTimeSummary
grep "== CMSSW:  - Max event:" * | awk '{print $6}' > MaxEventTimeSummary
grep "== CMSSW:  - Avg event:" * | awk '{print $6}' > AvgEventTimeSummary
grep -A2 "== CMSSW:  - Avg event:" * | grep "== CMSSW:  - Total job:" | awk '{print $6}' > TotalJobTimeSummary
grep -A2 "== CMSSW:  - Avg event:" * | grep "== CMSSW:  - Total loop:" | awk '{print $6}' > TotalLoopTimeSummary
grep -A2 "== CMSSW:  CPU Summary:" * | grep "== CMSSW:  - Total job:" | awk '{print $6}' > TotalLoopCPUSummary
grep -A2 "== CMSSW:  CPU Summary:" * | grep "== CMSSW:  - Total loop:" | awk '{print $6}' > TotalJobCPUSummary
grep "Dashboard end parameters" * | awk '{print $15}' > CrabUserCpuTime
grep "Dashboard end parameters" * | awk '{print $19}' > ExeTime

