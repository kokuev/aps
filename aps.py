#!/usr/bin/env python3
__author__ = 'ak'

import time
import argparse
from simplex_task import simplex_task

def main():
    parser = argparse.ArgumentParser(description='automatic problem solver. makes solution tree from task-file.')
    parser.add_argument('input', type=argparse.FileType('r'), help='input task file [yaml]')
    parser.add_argument('output', type=str, help='output soultion file [pck]')
    parser.add_argument('-m', nargs='?', dest='m', const=-1, default=None, type=int, help='forces to use multiprocess algorithm and sets amount of processes')

    args = parser.parse_args()
    #print(args)

    t = simplex_task()
    t.set_from_yaml(args.input.name)
    t1 = time.time()
    t.calculate(args.m)
    t2 = time.time()
    t.save_solution(args.output)

    print('calculation time: ', t2 - t1)

if __name__ == "__main__":

    main()