#!/bin/bash
# requires crab logs
# crab getlog --short --jobids 1-<end> crab/<project-dir>
# should be something like crab/<project-dir>/results/job_out.<jobid>.0.txt
# place this into the results directory of the CRAB job

grep "== CMSSW:  - Min event:" * | awk '{print $6}' > tmp
sed '/^$/d' tmp > MinEventTimeSummary
wc -l MinEventTimeSummary

grep "== CMSSW:  - Max event:" * | awk '{print $6}' > tmp
sed '/^$/d' tmp > MaxEventTimeSummary
wc -l MaxEventTimeSummary

grep "== CMSSW:  - Avg event:" * | awk '{print $6}' > tmp
sed '/^$/d' tmp > AvgEventTimeSummary
wc -l AvgEventTimeSummary

grep -A2 "== CMSSW:  - Avg event:" * | grep "== CMSSW:  - Total job:" | awk '{print $6}' > tmp
sed '/^$/d' tmp > TotalJobTimeSummary
wc -l TotalJobTimeSummary

grep -A2 "== CMSSW:  - Avg event:" * | grep "== CMSSW:  - Total loop:" | awk '{print $6}' > tmp 
sed '/^$/d' tmp > TotalLoopTimeSummary
wc -l TotalLoopTimeSummary

grep -A2 "== CMSSW:  CPU Summary:" * | grep "== CMSSW:  - Total job:" | awk '{print $6}' > tmp
sed '/^$/d' tmp > TotalLoopCPUTimeSummary
wc -l TotalLoopCPUTimeSummary

grep -A2 "== CMSSW:  CPU Summary:" * | grep "== CMSSW:  - Total loop:" | awk '{print $6}' > tmp
sed '/^$/d' tmp > TotalJobCPUTimeSummary
wc -l TotalJobCPUTimeSummary

grep "== CMSSW:  Event Throughput" * | awk '{print $5}' > tmp
sed '/^$/d' tmp > EventThroughput
wc -l EventThroughput

grep "Dashboard end parameters" * | awk '{print $15}' > tmp 
sed '/^$/d' tmp > CrabUserCpuTime
wc -l CrabUserCpuTime

grep "Dashboard end parameters" * | awk '{print $19}' > tmp
sed '/^$/d' tmp > ExeTime
wc -l ExeTime

rm tmp
