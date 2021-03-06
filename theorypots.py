__author__ = 'ak'

from copy import deepcopy
from interval import intervals
from assumption import result, assumption
from theorypots_linear_assumptions_for_pot import assumption_ratio_to_linear
from theorypots_numerical import decompose # TODO: names refactoring
from theorypots_symbol_assumptions import pot_symbol_variants
from theorypots_intervals import test_linear_assumption
from sympy import Number

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

        some_res = self.basic_test_linear_assumption(linear_assumption)
        if some_res == result.correct:
            return True
        elif some_res == result.not_possible:
            return False

        if not test_linear_assumption(self.symbol_intervals, linear_assumption):
            return False

        return True

    def has_already(self, linear_assumption):
        for assumption in self.assumptions:
            if assumption == linear_assumption:
                return True
        return False

    def basic_test_linear_assumption(self, linear_assumption):
        lexp, lsign = linear_assumption.exp, linear_assumption.sign
        for assumption in self.assumptions:
            exp, sign = assumption.exp, assumption.sign
            if exp == lexp:
                if   sign == '>'  and lsign == '>' : return result.correct
                elif sign == '>'  and lsign == '>=': return result.correct
                elif sign == '>'  and lsign == '==': return result.not_possible
                elif sign == '>'  and lsign == '!=': return result.correct
                elif sign == '>=' and lsign == '>' : return result.possible
                elif sign == '>=' and lsign == '>=': return result.correct
                elif sign == '>=' and lsign == '==': return result.possible
                elif sign == '>=' and lsign == '!=': return result.possible
                elif sign == '==' and lsign == '>' : return result.not_possible
                elif sign == '==' and lsign == '>=': return result.correct
                elif sign == '==' and lsign == '==': return result.correct
                elif sign == '==' and lsign == '!=': return result.not_possible
                elif sign == '!=' and lsign == '>' : return result.possible
                elif sign == '!=' and lsign == '>=': return result.possible
                elif sign == '!=' and lsign == '==': return result.not_possible
                elif sign == '!=' and lsign == '!=': return result.correct
            elif exp == lexp*Number(-1):
                if   sign == '>'  and lsign == '>' : return result.not_possible
                elif sign == '>'  and lsign == '>=': return result.not_possible
                elif sign == '>'  and lsign == '==': return result.not_possible
                elif sign == '>'  and lsign == '!=': return result.correct
                elif sign == '>=' and lsign == '>' : return result.not_possible
                elif sign == '>=' and lsign == '>=': return result.possible
                elif sign == '>=' and lsign == '==': return result.possible
                elif sign == '>=' and lsign == '!=': return result.possible
                elif sign == '==' and lsign == '>' : return result.not_possible
                elif sign == '==' and lsign == '>=': return result.correct
                elif sign == '==' and lsign == '==': return result.correct
                elif sign == '==' and lsign == '!=': return result.not_possible
                elif sign == '!=' and lsign == '>' : return result.possible
                elif sign == '!=' and lsign == '>=': return result.possible
                elif sign == '!=' and lsign == '==': return result.not_possible
                elif sign == '!=' and lsign == '!=': return result.correct
        return result.possible

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
                #print("[info] filtered by test_by_symbol_intervals()")
                return False
            return True

        some_res = self.basic_test_linear_assumption(linear_assumption)
        if some_res == result.correct:
            return True
        elif some_res == result.not_possible:
            #print("[info] filtered by basic_test_linear_assumption")
            return False

        if not test_linear_assumption(self.symbol_intervals, linear_assumption):
            #print("[info] filtered by test_linear_assumption")
            return False

        self.assumptions.append(linear_assumption)
        self.new_assumptions.append(linear_assumption)

        if not self.symbol_variants.linear_assumption_decompose(self, linear_assumption, assumption_deps):
            #print("[info] filtered by linear_assumption_decompose")
            return False

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

    def get_common_and_not_assumptions(self):
        if not self.is_valid(): return ('', [])
        assumps_by_pot = list()
        all_assumps = list()
        for pot in self.pots:
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

        return (common_assumps, new_assumps_by_pot)



import time

if __name__ == "__main__":
    from assumption import assumption
    #from expression import expr
    from sympy import Symbol, Number

    t = theorypots()

    b1 = Symbol('b1')
    b2 = Symbol('b2')
    a11 = Symbol('a11')
    a12 = Symbol('a12')
    a21 = Symbol('a21')
    a22 = Symbol('a22')
    c1 = Symbol('c1')
    c2 = Symbol('c2')

    t1 = time.clock()

    print('ret:', t.add_assumptions([assumption(b2, '>=', Number(0)), assumption(b1, '>=', Number(0)), assumption(c1, '<', Number(0)), assumption(a11, '>', Number(0))] ))
    #print(t)
    print('ret:', t.add_or_assumptions([ [assumption(a21, '<=', Number(0))], [assumption(a21, '>', Number(0)), assumption(b2*a11-b1*a21, '>=', Number(0))] ]))
    #print('+' * 60)
    #print(t)
    print('ret:', t.add_assumptions([assumption( (c1*a12-c2*a11)/a11 , '>', Number(0)) , assumption( (a11*a22-a12*a21)/a11 , '>', Number(0)) ] ))
    #print(t)
    print('ret:', t.add_or_assumptions([ [assumption( a12/a11, '<=', Number(0))],
                                         [
                                             assumption(a12/a11, '>', Number(0)),
                                             assumption( (b1*a11*a22 - a12*b2*a11)/(a12*a11*a22-a12*a12*a21), '>=', Number(0))]
    ]))
    print('ret:', t.add_assumptions([assumption( a22 , '>', Number(0)) , assumption( (c1*a22-c2*a21) , '>', Number(0)) ] ))
    print('pots:', t, sep='\n')
    t2 = time.clock()

    print('calculation time: ', t2 - t1)
