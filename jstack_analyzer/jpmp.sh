# Original version: http://blog.tsunanet.net/2010/08/jpmp-javas-poor-mans-profiler.html

# Usage: ./jpmp.sh <pid> <num-samples> <sleep-time-between-samples>

#!/bin/bash
pid=$1
nsamples=$2
sleeptime=$3

for x in $(seq 1 $nsamples)
  do
    jstack $pid
    sleep $sleeptime
  done | \
awk 'BEGIN { s = "" } \
/^"/ { if (s) print s; s = "" } \
/^	at / { sub(/\([^)]*\)?$/, "", $2); sub(/^java/, "j", $2); if (s) s = s "," $2; else s = $2 } \
END { if(s) print s }' | \
sort | uniq -c | sort -rnk1
