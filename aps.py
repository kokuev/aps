__author__ = 'ak'

import time
from simplex_task import simplex_task

def main():
    t = simplex_task()
    t.set_from_yaml('tasks/task_2x2.yaml')
    t1 = time.clock()
    t.calculate()
    t2 = time.clock()
    t.save_solution('result/task_2x2.pck')

    print('calculation time: ', t2 - t1)

if __name__ == "__main__":
    main()