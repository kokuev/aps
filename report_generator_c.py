__author__ = 'ak'

import pickle

from sympy import ccode, Symbol

result_file_name = 'result/task.pck'
report_h_file_name = 'reports/tree.h'
report_c_file_name = 'reports/tree.c'


def simplex_table_to_c_assumptions(table):
    if not table.pots.is_valid(): return ('', [])
    assumps_by_pot = list()
    all_assumps = list()
    for pot in table.pots.pots:
        assumps = list()
        for s in pot.new_symbol_intervals:
            assumps += pot.new_symbol_intervals[s].get_assumptions(s)
        assumps += pot.new_assumptions
        assumps_by_pot.append(assumps)
        all_assumps += assumps

    n = len(assumps_by_pot)
    common_assumps = list()
    while len(all_assumps) > 0:
        current_assumpt = all_assumps[0]
        new_all_assumps = list()
        i = 0
        for assumpt in all_assumps:
            if assumpt == current_assumpt:
                i += 1
            else:
                new_all_assumps.append(assumpt)
        all_assumps = new_all_assumps
        if i == n:
            common_assumps.append(current_assumpt)

    new_assumps_by_pot = list()
    for pot in assumps_by_pot:
        new_pot = list()
        for a in pot:
            common = False
            for ca in common_assumps:
                if a == ca:
                    common = True
                    break
            if not common:
                new_pot.append(a)

        if len(new_pot) == 0: continue

        bad = False
        for pot in new_assumps_by_pot:
            diff = False
            for a1 in new_pot:
                found = False
                for a2 in pot:
                    if a1 == a2:
                        found = True
                        break
                if not found:
                    diff = True
                    break
            for a1 in pot:
                found = False
                for a2 in new_pot:
                    if a1 == a2:
                        found = True
                        break
                if not found:
                    diff = True
                    break
            if not diff:
                bad = True
                break

        if not bad:
            new_assumps_by_pot.append(new_pot)

    ret = ''

    common_assumpt_text = list()
    for a in common_assumps:
        common_assumpt_text.append('(' + ccode( a.exp) + ' ' + a.sign + ' 0 )')

    pots_assumpt_text = list()

    for pot in new_assumps_by_pot:

        pot_assumpt_text = list()
        for a in pot:
            pot_assumpt_text.append('(' + ccode( a.exp) + ' ' + a.sign + ' 0 )')

        pots_assumpt_text.append( '(' + " && ".join(pot_assumpt_text) + ')' )

    ret = " && ".join(common_assumpt_text)

    if len(pots_assumpt_text) > 0:
        ret += ' && ' + '(' + " || ".join(pots_assumpt_text) + ')'

    return ret


class cpp_output:
    def __init__(self, filename):
        self.f = open(filename, 'w')

    def __del__(self):
        self.f.close()

    def place_text(self, text):
        print(text, file=self.f)


def out_table(table, level):
    t, chs = table
    if not t.solution:
        ret = ''
        for ch in chs:
            ch_t, ch_chs = ch
            ret += "%sif ( %s ) \n" % ("    "*level, simplex_table_to_c_assumptions(ch_t))
            ret += "%s{\n" % ("    "*level)
            ret += "%s" % out_table(ch, level + 1)
            ret += "%s}\n" % ("    "*level)
            ret += "%selse " % ("    "*level)
        ret += "%sreturn 0;\n" % ("    "*level)
        return ret
    else:
        var, target = t.solution
        ret = ''
        for i in range(t.amount_of_vars):
            ret += "    "*level + "out->x" + str(i) + " = " + ccode(var[i]) + ";\n"
        ret += "    "*level + 'out->psi = ' + ccode(target) + ";\n"
        ret += "    "*level + "return 1;\n"
        return ret

h_text = """#ifndef TREE_H
#define TREE_H

struct input
{
%s
};

struct output
{
%s
};

char get_solution(struct input* in, struct output* out);

#endif
"""

c_text = """ #include "tree.h"

char get_solution(struct input* in, struct output* out)
{
%s
%s
}

"""

def generate_input(solution, init = False):
    t, chs = solution

    symbols = list()

    for i in range(t.amount_of_equations):
        for j in range(t.amount_of_vars):
            symbols += t.limits[i][j].atoms(Symbol)

    for j in range(t.amount_of_equations):
        symbols += t.free[j].atoms(Symbol)

    for i in range(t.amount_of_vars):
        symbols += t.target[i].atoms(Symbol)

    symbols += t.target_free.atoms(Symbol)

    symbols = set(symbols)

    ret = ''
    for symb in symbols:
        ret += "\tdouble " + ccode(symb)
        if init: ret += " = in->" + ccode(symb) + ";\n"
        else: ret += ";\n"

    return ret

def generate_output(solution):
    t, chs = solution
    ret = ''
    for i in range(t.amount_of_vars):
        ret += "\tdouble x" + str(i) + ";\n"

    ret += "\tdouble psi;"
    return ret

def main():
    solution = pickle.load(open(result_file_name, 'rb'))
    out_h = cpp_output(report_h_file_name)
    out_h.place_text(h_text % (generate_input(solution), generate_output(solution)))
    out_c = cpp_output(report_c_file_name)
    out_c.place_text(c_text % ( generate_input(solution, True), out_table( solution, 1)))

if __name__ == "__main__":
    main()