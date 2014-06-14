#!/bin/bash


while true
do
	echo "new iteration"
	for f in `cd tasks && ls task8*`;
	do
		echo $f
		python3.3 aps.py tasks/$f result/$f.pck >> logs/$f.txt;
	done
done
