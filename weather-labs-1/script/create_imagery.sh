#!/bin/sh

rm commands.txt

file_location=$1
ch=$2
start=$3
end=$4
step=$5 #minutes
coords=$6 # fourtuple (min_lon,max_lon,min_lat,max_lat)
resolution=$7


START_IN_SECONDS=$(date -u --date "$start" +%s)
END_IN_SECONDS=$(date -u --date "$end" +%s)
diff=$((CURRENT_IN_SECONDS - START_IN_SECONDS))
#echo $diff

processed=$START_IN_SECONDS          
while [ $processed -lt $END_IN_SECONDS ]           
do             
process_date=$(date -u --date "@$processed" '+%Y-%m-%dT%H:%M:%SZ')	
for composite in $(echo $ch | tr "," " ")
do
	echo python image.py $file_location $composite $process_date \"$coords\" $resolution >> commands.txt
done
processed=$(echo "$processed + $step*60" | bc -l)          
done          

#conda activate MTGX

bash commands.txt



