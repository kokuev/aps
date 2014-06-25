import multiprocessing

finish_task_id = 0

def worker(q_in, q_out, to_be_solved):
    while True:
        task_id, column, row, data, obj = q_in.get()
        if task_id == finish_task_id: break

        if column == None: # just table
            for j, assumpts in obj.get_next_tables_multi(): # doubts is list of pairs (# of row, value of c)
                with to_be_solved.get_lock(): to_be_solved.value += 1
                q_in.put( (task_id, j, None, assumpts, obj) )

            q_out.put((task_id, None, None))
            continue

        if row == None: # column is known, row in unknown
            if column == -1:
                ret = obj.get_next_tables_multi_end_table(data)
                if ret:
                    i = obj.amount_of_equations * (obj.amount_of_equations - 1) + (obj.amount_of_vars - 1) + 1
                    q_out.put( (task_id, i, ret) )
                    continue

                q_out.put((task_id, None, None))
                continue

            if obj.get_next_tables_multi_by_column(data) == True:
                for i in range(obj.amount_of_equations):
                    with to_be_solved.get_lock(): to_be_solved.value += 1
                    q_in.put( (task_id, column, i, data, obj) )

            q_out.put((task_id, None, None))
            continue

        ret = obj.get_next_tables_multi_by_column_and_row(data, column, row)
        if ret:
            num = obj.amount_of_equations * row + column
            q_out.put((task_id, num, ret))
            continue

        q_out.put((task_id, None, None))
        continue

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

    to_be_solved = multiprocessing.Value('i', 0, lock = True)

    for x in range(cpu_count):
        p = multiprocessing.Process(target=worker, args=(tasks, result, to_be_solved))
        p.start()
        pool.append(p)

    to_be_solved.value = 1
    tasks.put( (1, None, None, None, table) )
    ret = (table, dict() )

    solution = dict()
    solution[1] = (0, 0)
    next_task_id = 2

    while True:
        task_id, next_id, next_table = result.get()
        #print(task_id, next_id, next_table, to_be_solved.value)
        with to_be_solved.get_lock(): to_be_solved.value -= 1
        #if next_table: print(task_id, next_id, to_be_solved.value)

        if next_table:
            place_table(ret, solution, task_id, next_id, next_table)

            solution[next_task_id] = (task_id, next_id)
            with to_be_solved.get_lock(): to_be_solved.value += 1
            tasks.put( (next_task_id, None, None, None, next_table) )
            next_task_id += 1

        if to_be_solved.value == 0:
            for x in range(cpu_count):
                tasks.put( (finish_task_id, None, None, None, None) )
            break

    for p in pool:
        p.join()

    return make_solution(ret)
