#! /bin/bash
DIR_SCRIPTS="Desktop/DisasterSimulator/experiments/temp/reports"

printf "Memory;CPU\n" >> $DIR_SCRIPTS/report_$1_$2.csv
end=$((SECONDS+3600))
while [ $SECONDS -lt $end ]; do
MEMORY=$(free -m | awk 'NR==2{printf "%.2f%%;", $3*100/$2 }')
CPU=$(top -bn1 | grep load | awk '{printf "%.2f%%\n", $(NF-2)}')
echo "$MEMORY$DISK$CPU" >> $DIR_SCRIPTS/report_$1_$2.csv
sleep 0.01
done