#!/bin/bash

while true
do
	export f=task_2x2.yaml
	echo $f m1
	python3.3 aps.py tasks/$f result/$f.pck -m 1 >> logs/$f.m1.txt;
	echo $f m2
	python3.3 aps.py tasks/$f result/$f.pck -m 2 >> logs/$f.m2.txt;
	echo $f m3
	python3.3 aps.py tasks/$f result/$f.pck -m 3 >> logs/$f.m3.txt;
	echo $f m4
	python3.3 aps.py tasks/$f result/$f.pck -m 4 >> logs/$f.m4.txt;
done
