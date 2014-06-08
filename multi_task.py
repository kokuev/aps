import multiprocessing

def worker(q_in, q_out):
	while True:
		num, obj = q_in.get()
		if not num: break

		i = 1
		for x in obj.get_next_tables():
			q_out.put((num, i, x))
			i += 1

		l = i - 1
		q_out.put( (num, 0, l) )


def _dict_to_list(d):
	return [d[x] for x in sorted(d)]

def make_solution(r):
	t, d = r
	if not d:
		t.make_solution()
		return t, list()
	ret = list()
	for x in sorted(d):
		ret.append(make_solution(d[x]))
	return t, ret

def _place_table(ret, path, next_table):
	t, d = ret
	if len(path) == 1:
		d[path[-1]] = ( next_table, dict() )
	else:
		_place_table(d[path[-1]], path[:-1], next_table )

def place_table(ret, solution, task_id, next_id, next_table):
	t = task_id
	path = list()
	path.append(next_id)
	while t in solution:
		t, s = solution[t]
		path.append(s)

	if path[-1] == 0: del path[-1]
	_place_table(ret, path, next_table)


def get_solution(table, m):
	tasks = multiprocessing.Queue()
	result = multiprocessing.Queue()

	if m <= 0: m = 4
	cpu_count = m
	pool = list()

	for x in range(cpu_count):
		p = multiprocessing.Process(target=worker, args=(tasks, result ))
		p.start()
		pool.append(p)

	tasks.put( (1, table) )
	ret = (table, dict() )

	solution = dict()
	solution[1] = (0, 0)
	next_task_id = 2
	to_be_solved = 1

	while True:
		task_id, next_id, next_table = result.get()

		if next_id == 0:
			to_be_solved -= 1
			if to_be_solved == 0:
				for x in range(cpu_count):
					tasks.put( (0, None) )
				break
		else:
			place_table(ret, solution, task_id, next_id, next_table)

			solution[next_task_id] = (task_id, next_id)
			to_be_solved += 1
			tasks.put( (next_task_id, next_table) )
			next_task_id += 1

	for p in pool:
		p.join()

	return make_solution(ret)
