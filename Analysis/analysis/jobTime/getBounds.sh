# Get the maximum and minimum time
# Meant to get a rough estimate for the bounds of 
# timing plots
echo "MinEventTimeSummary"
sort -nr data/MinEventTimeSummary | tail -1
sort -n data/MinEventTimeSummary | tail -1
echo "MaxEventTimeSummary"
sort -nr data/MaxEventTimeSummary | tail -1
sort -n data/MaxEventTimeSummary | tail -1
echo "AvgEventTimeSummary"
sort -nr data/AvgEventTimeSummary | tail -1
sort -n data/AvgEventTimeSummary | tail -1
echo "TotalJobTimeSummary"
sort -nr data/TotalJobTimeSummary | tail -1
sort -n data/TotalJobTimeSummary | tail -1
echo "TotalLoopTimeSummary"
sort -nr data/TotalLoopTimeSummary | tail -1
sort -n data/TotalLoopTimeSummary | tail -1
echo "TotalJobCPUTimeSummary"
sort -nr data/TotalJobCPUTimeSummary | tail -1
sort -n data/TotalJobCPUTimeSummary | tail -1
echo "TotalLoopCPUTimeSummary"
sort -nr data/TotalLoopCPUTimeSummary | tail -1
sort -n data/TotalLoopCPUTimeSummary | tail -1
echo "EventThroughput"
sort -nr data/EventThroughput | tail -1
sort -n data/EventThroughput | tail -1
echo "CrabUserCpuTime"
sort -nr data/CrabUserCpuTime | tail -1
sort -n data/CrabUserCpuTime | tail -1
echo "ExeTime"
sort -nr data/ExeTime | tail -1
sort -n data/ExeTime | tail -1
