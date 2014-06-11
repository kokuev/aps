#python3.3 aps.py tasks/task_3x3.yaml result/task_3x3.pck > logs/task_3x3.txt


for f in `cd tasks && ls task_2x2_*`;
do
	python3.3 aps.py tasks/$f result/$f.pck >> logs/$f.txt;
done
