__author__ = 'ak'

from copy import deepcopy
from interval import intervals
from expression import expr
from assumption import result, assumption
from theorypots_linear_assumptions_for_pot import assumption_ratio_to_linear
from theorypots_numerical import decompose # TODO: names refactoring
from theorypots_symbol_assumptions import pot_symbol_variants
from theorypots_intervals import test_linear_assumption

class theorypot:
    def __init__(self):
        self.symbol_intervals = dict()
        self.assumptions = list()
        self.new_symbol_intervals = dict()
        self.new_assumptions = list()
        self.symbol_variants = pot_symbol_variants()

    def __str__(self):
        ret = ""
        for s in self.symbol_intervals:
            ret += 'symbol ' + str(s) + ':' + str(self.symbol_intervals[s]) + "\n"
        for s in self.assumptions:
            ret += "\t" + str(s) + "\n"
        return ret

    def clean_new_lists(self):
        self.new_symbol_intervals = dict()
        self.new_assumptions = list()

    def linear_assumption_basic_test_on_possibility(self, linear_assumption):
        assumption_deps = linear_assumption.depends()
        deps_len = len(assumption_deps)
        if deps_len == 0:
            if linear_assumption.test() == result.not_possible: return False
            return True

        if deps_len == 1:
            symbol = assumption_deps[0]
            if symbol not in self.symbol_intervals: return True
            lim = decompose(linear_assumption)
            if not lim:
                print("[warn] decompose failed:", linear_assumption)
                return True

            res = deepcopy(self.symbol_intervals[symbol])
            res *= lim
            if res.is_zero():
                return False
            return True

        return True

    def has_already(self, linear_assumption):
        for assumption in self.assumptions:
            if assumption == linear_assumption:
                return True
        return False

    def _add_linear_assumption(self, linear_assumption):
        assumption_deps = linear_assumption.depends()
        deps_len = len(assumption_deps)
        if deps_len == 0:
            if linear_assumption.test() == result.not_possible: return False
            return True

        if deps_len == 1:
            symbol = assumption_deps[0]
            if symbol not in self.symbol_intervals:
                self.symbol_intervals[symbol] = intervals()
            lim = decompose(linear_assumption)
            if not lim:
                print("[warn] decompose failed:", linear_assumption)
                return False

            res = deepcopy(self.symbol_intervals[symbol])
            res *= lim
            if res.is_zero(): return False
            if self.symbol_intervals[symbol] != res:
                self.new_symbol_intervals[symbol] = res
            self.symbol_intervals[symbol] = res

            if not self.symbol_variants.test_by_symbol_intervals(self.symbol_intervals):
                print("[info] filtered by test_by_symbol_intervals()")
                return False
            return True

        if self.has_already(linear_assumption):
            return True

        if not test_linear_assumption(self.symbol_intervals, linear_assumption):
            print("[info] filtered by test_linear_assumption")
            return False

        if not self.symbol_variants.linear_assumption_decompose(self, linear_assumption, assumption_deps):
            return False

        self.assumptions.append(linear_assumption)
        self.new_assumptions.append(linear_assumption)

        return True

    def add_linear_assumptions(self, linear_assumptions):
        for linear_assumption in linear_assumptions:
            if not self._add_linear_assumption(linear_assumption):
                return False
        return True

def apply_assumption_to_pot(pot, assumption):
    result_pots = list()
    linear_variations_variations = assumption_ratio_to_linear(assumption, pot)
    for linear_assumptions in linear_variations_variations:
        temp_pot = deepcopy(pot)
        if temp_pot.add_linear_assumptions(linear_assumptions):
            result_pots.append(temp_pot)

    return result_pots

def apply_assumptions_to_pot(pot, assumptions):
    first_pot = deepcopy(pot)
    first_pot.clean_new_lists()
    current_pots = [ first_pot , ]

    for assumption in assumptions:
        new_current_pots = list()
        for cp in current_pots:
            new_current_pots += apply_assumption_to_pot(cp, assumption)
        current_pots = new_current_pots
    return current_pots

def apply_or_assumptions_to_pot(pot, or_assumptions):
    new_pots = list()
    for assumptions in or_assumptions:
        temp_pot = deepcopy(pot)
        new_pots += apply_assumptions_to_pot(temp_pot, assumptions)
    return new_pots

class theorypots:
    def __init__(self):
        self.pots = list()
        self.pots.append(theorypot())

    def is_valid(self):
        if len(self.pots) == 0: return False
        else: return True

    def add_or_assumptions(self, or_assumptions):
        new_pots = list()
        for pot in self.pots:
            new_pots += apply_or_assumptions_to_pot(pot, or_assumptions)
        self.pots = new_pots
        return self.is_valid()

    def add_assumptions(self, assumpts):
        new_pots = list()
        for pot in self.pots:
            new_pots += apply_assumptions_to_pot(pot, assumpts)
        self.pots = new_pots
        return self.is_valid()

    def __str__(self):
        ret = ""
        if len(self.pots) == 0: return "no pots\n"
        for i, pot in enumerate(self.pots):
            ret += 'pot #' + str(i) + ':' + '\n'
            ret += str(pot) + '\n'
        return ret

import time

if __name__ == "__main__":
    from assumption import assumption
    from expression import expr

    t = theorypots()

    b1 = expr('b1')
    b2 = expr('b2')
    a11 = expr('a11')
    a12 = expr('a12')
    a21 = expr('a21')
    a22 = expr('a22')
    c1 = expr('c1')
    c2 = expr('c2')

    t1 = time.clock()

    print('ret:', t.add_assumptions([assumption(b2, '>=', expr(0)), assumption(b1, '>=', expr(0)), assumption(c1, '<', expr(0)), assumption(a11, '>', expr(0))] ))
    #print(t)
    print('ret:', t.add_or_assumptions([ [assumption(a21, '<=', expr(0))], [assumption(a21, '>', expr(0)), assumption(b2*a11-b1*a21, '>=', expr(0))] ]))
    #print('+' * 60)
    #print(t)
    print('ret:', t.add_assumptions([assumption( (c1*a12-c2*a11)/a11 , '>', 0) , assumption( (a11*a22-a12*a21)/a11 , '>', 0) ] ))
    #print(t)
    print('ret:', t.add_or_assumptions([ [assumption( a12/a11, '<=', expr(0))],
                                         [
                                             assumption(a12/a11, '>', expr(0)),
                                             assumption( (b1*a11*a22 - a12*b2*a11)/(a12*a11*a22-a12*a12*a21), '>=', expr(0))]
    ]))
    print('ret:', t.add_assumptions([assumption( a22 , '>', 0) , assumption( (c1*a22-c2*a21) , '>', 0) ] ))
    print('pots:', t, sep='\n')
    t2 = time.clock()

    print('calculation time: ', t2 - t1)
