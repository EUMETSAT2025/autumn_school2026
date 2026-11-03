#!/bin/sh

rm a.txt

file_location=$1
ch=$2
start=$3
end=$4
step=$5 #minutes
coords=$6 # fourtuple (min_lon,max_lon,min_lat,max_lat)
resolution=$7


START_IN_SECONDS=$(date --date "$start" +%s)
END_IN_SECONDS=$(date --date "$end" +%s)
diff=$((CURRENT_IN_SECONDS - START_IN_SECONDS))
echo $diff

processed=$START_IN_SECONDS          
while [ $processed -lt $END_IN_SECONDS ]           
do             
process_date=$(date --date "@$processed" '+%Y-%m-%dT%H:%M:%SZ')	
echo python image.py $file_location $ch $process_date \"$coords\" $resolution >> a.txt
processed=$(echo "$processed + $step*60" | bc -l)          
done          
echo $processed 

#conda activate MTGX

#echo python image.py $file_location $ch $start $end $step "("$coords")" $resolution >> a.txt

exit
parallel -j 10 :::: a.txt



