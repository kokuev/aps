#!/bin/bash

while true
do
	for f in `cd tasks && ls task_2x2*`;
	do
		echo $f
		python3.3 aps.py tasks/$f result/$f.pck >> logs/$f.txt;
	done
done
