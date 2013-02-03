__author__ = 'ak'

from copy import deepcopy
from interval import intervals, interval
from expression import linear, expr
from assumption import  result, assumption
from theorypots_numerical import decompose
from theorypots_intervals import test_linear_assumption, get_ration_data_intervals
from theorypots_ratio_to_linear import assumption_ratio_to_linear
from theorypots_sign_lists import combine_signs_list, check_sign_lists

import time

class theorypot:
    def __init__(self):
        self.symbols_intervals = dict()
        self.symbols_assumptions = dict()

        self.decomposed_symbol_assumptions = list()

    def __str__(self):
        ret = ""
        for s in self.symbols_intervals:
            ret += 'symbol ' + str(s) + ':' + str(self.symbols_intervals[s]) + "\n"
        for s in self.symbols_assumptions:
            for sign in self.symbols_assumptions[s]:
                for e in self.symbols_assumptions[s][sign]:
                    ret += "\t" + str(s) + ' ' + str(sign) + ' ' + str(e) + "\n"
        return ret

    def get_copy(self):
        return deepcopy(self)

    def get_copy_in_list(self):
        ret = list()
        ret.append(self.get_copy())
        return ret

    def get_all_assumtions(self):
        ret = list()
        for inter in self.symbols_intervals:
            ret += self.symbols_intervals[inter].get_assumptions(inter)
        for s in self.symbols_assumptions:
            for sign in self.symbols_assumptions[s]:
                for e in self.symbols_assumptions[s][sign]:
                    ret.append(assumption(expr(s), sign, e))

        return ret


    def get_all_assumtions_to_tex(self):
        ret = ''
        for inter in self.symbols_intervals:
            ret += '$' + str(inter) + ' \in ' + self.symbols_intervals[inter].to_tex() + "$ \\\\ \n"
        for s in self.symbols_assumptions:
            for sign in self.symbols_assumptions[s]:
                for e in self.symbols_assumptions[s][sign]:
                    ret += "$ " + str(s) + ' ' + str(sign) + ' ' + e.to_tex() + " $ \\\\ \n"
        for s in self.decomposed_symbol_assumptions:
            ret += "$ " + s.to_tex() + "$ \\\\ \n"

        return ret


    def _update_symbol_assumptions(self, symbol):
        if symbol not in self.symbols_assumptions: return
        combine_signs_list( self.symbols_assumptions[symbol], '>' , '>=', '>'  )
        combine_signs_list( self.symbols_assumptions[symbol], '>' , '!=', '>'  )
        combine_signs_list( self.symbols_assumptions[symbol], '<' , '<=', '<'  )
        combine_signs_list( self.symbols_assumptions[symbol], '<' , '!=', '<'  )
        combine_signs_list( self.symbols_assumptions[symbol], '>=', '<=', '==' )
        combine_signs_list( self.symbols_assumptions[symbol], '>=', '==', '==' )
        combine_signs_list( self.symbols_assumptions[symbol], '>=', '!=', '>'  )
        combine_signs_list( self.symbols_assumptions[symbol], '<=', '==', '==' )
        combine_signs_list( self.symbols_assumptions[symbol], '<=', '!=', '<'  )

    def _check_symbol_assumptions_on_objects(self, symbol):
        if symbol not in self.symbols_assumptions: return True
        if not check_sign_lists(self.symbols_assumptions[symbol], '>' , '<' ): return False
        if not check_sign_lists(self.symbols_assumptions[symbol], '>' , '<='): return False
        if not check_sign_lists(self.symbols_assumptions[symbol], '>' , '=='): return False
        if not check_sign_lists(self.symbols_assumptions[symbol], '<' , '=='): return False
        if not check_sign_lists(self.symbols_assumptions[symbol], '<' , '>='): return False
        if not check_sign_lists(self.symbols_assumptions[symbol], '==', '!='): return False
        return True

    def _check_symbol_assumptions_on_known_limits(self, symbol):
        if symbol not in self.symbols_assumptions: return True
        #print("_check_symbol_assumptions_on_known_limits", symbol)

        symbol_max, symbol_max_strong, symbol_min, symbol_min_strong = float('+inf'), True, float('-inf'), True
        if '>' in self.symbols_assumptions[symbol]:
            for e in self.symbols_assumptions[symbol]['>']:
                #print('expression:', e)
                current_max, current_max_strong, current_min, current_min_strong = get_ration_data_intervals(self.symbols_intervals, e).get_max_min()
                #print('symbols max_min: ', symbol_max, symbol_max_strong, symbol_min, symbol_min_strong)
                #print('current max_min: ', current_max, current_max_strong, current_min, current_min_strong)
                if current_min > symbol_min or (current_min == symbol_min and current_min_strong == True):
                    symbol_min, symbol_min_strong = current_min, current_min_strong
        if '<' in self.symbols_assumptions[symbol]:
            for e in self.symbols_assumptions[symbol]['<']:
                current_max, current_max_strong, current_min, current_min_strong = get_ration_data_intervals(self.symbols_intervals, e).get_max_min()
                if current_max < symbol_max or (current_max == symbol_max and current_max_strong == True):
                    symbol_max, symbol_max_strong = current_max, current_max_strong
        if '==' in self.symbols_assumptions[symbol]:
            for e in self.symbols_assumptions[symbol]['==']:
                current_max, current_max_strong, current_min, current_min_strong = get_ration_data_intervals(self.symbols_intervals, e).get_max_min()
                if current_max < symbol_max or (current_max == symbol_max and current_max_strong == True):
                    symbol_max, symbol_max_strong = current_max, current_max_strong
                if current_min > symbol_min or (current_min == symbol_min and current_min_strong == True):
                    symbol_min, symbol_min_strong = current_min, current_min_strong
        if symbol_max < symbol_min or (symbol_min == symbol_max and (symbol_min_strong == True or symbol_max_strong == True)): return False

        #print('max_min: ', symbol_max, symbol_max_strong, symbol_min, symbol_min_strong)
        if symbol in self.symbols_intervals:
            known_interval = deepcopy(self.symbols_intervals[symbol])
            known_interval *= interval(symbol_min, symbol_min_strong, symbol_max, symbol_max_strong)
            if known_interval.is_zero(): return False
        return True

    def _check_symbol_assumptions(self, symbol):
        if symbol not in self.symbols_assumptions: return True
        self._update_symbol_assumptions(symbol)
        if not self._check_symbol_assumptions_on_objects(symbol): return False
        if not self._check_symbol_assumptions_on_known_limits(symbol): return False
        return True

    def _check_symbols_assumptions(self):
        for symbol in self.symbols_assumptions:
            if not self._check_symbol_assumptions(symbol): return False
        return True

    def _check_symbols_assumptions_on_known_interval(self):
        #print("_check_symbols_assumptions_on_known_interval")
        for symbol in self.symbols_assumptions:
            if not self._check_symbol_assumptions_on_known_limits(symbol):
            #print("failed check on", symbol)
                return False
        return True

    def _add_symbol_assumption(self, symbol, sign, expression):
        if symbol not in self.symbols_assumptions:
            self.symbols_assumptions[symbol] = dict()
        if sign not in self.symbols_assumptions[symbol]:
            self.symbols_assumptions[symbol][sign] = list()
            # check on dup
        for e in self.symbols_assumptions[symbol][sign]:
            if expression == e:
                return self._check_symbol_assumptions(symbol)
        self.symbols_assumptions[symbol][sign].append(expression)
        return self._check_symbol_assumptions(symbol)

    def _push_assumption_try_linear_decompose(self, assumpt, assumpt_deps):
        current_pots = list()
        current_pots.append(self.get_copy())

        for symbol in assumpt_deps:
            res = assumpt.exp.try_linear(symbol)
            if not res: continue
            a_, b_, p = res
            if p != 1: continue
            a = linear()
            a.data = a_
            b = linear()
            b.data = b_

            new_current_pots = list()

            sign = assumpt.sign

            for pot in current_pots:
                if sign == '==':
                    first_pots = pot.get_copy()._add_assumption(assumption(expr(a), '!=', expr(0) ))
                    nfirst_pots = list()
                    for fpot in first_pots:
                        if fpot._add_symbol_assumption(symbol, '==', expr(-1)*expr(b)/expr(a) ): nfirst_pots.append(fpot)
                    second_pots = pot.get_copy().add_assumptions( [ assumption(expr(a), '==', expr(0) ), assumption(expr(b), '==', expr(0)) ] )
                    new_current_pots += nfirst_pots + second_pots
                elif sign == '!=':
                    first_pots = pot.get_copy()._add_assumption(assumption(expr(a), '!=', expr(0) ))
                    nfirst_pots = list()
                    for fpot in first_pots:
                        if fpot._add_symbol_assumption(symbol, '!=', expr(-1)*expr(b)/expr(a) ): nfirst_pots.append(fpot)
                    second_pots = pot.get_copy().add_assumptions( [ assumption(expr(a), '==', expr(0) ), assumption(expr(b), '!=', expr(0)) ] )
                    new_current_pots += nfirst_pots + second_pots
                else:
                    if sign == '>': neg_sign = '<'
                    elif sign == '>=': neg_sign = '<='
                    elif sign == '<': neg_sign = '>'
                    else: neg_sign = '>='

                    #print(10*'-' + ' > ' + 10*'-')
                    first_pots = pot.get_copy()._add_assumption(assumption(expr(a), '>', expr(0) ))
                    nfirst_pots = list()
                    for fpot in first_pots:
                        if fpot._add_symbol_assumption(symbol, sign, expr(-1)*expr(b)/expr(a)): nfirst_pots.append(fpot)
                        #print('result > : ')
                    #for ppp in nfirst_pots:
                    #    print(ppp)
                    #print(40*'-')

                    #print(10*'-' + ' < ' + 10*'-')
                    second_pots = pot.get_copy()._add_assumption(assumption(expr(a), '<', expr(0) ))
                    nsecond_pots = list()
                    for spot in second_pots:
                        if spot._add_symbol_assumption(symbol, neg_sign, expr(-1)*expr(b)/expr(a)): nsecond_pots.append(spot)
                        #print('result < : ')
                    #for ppp in nsecond_pots:
                    #    print(ppp)
                    #print(40*'-')

                    #print(10*'-' + ' == ' + 10*'-')
                    third_pots = pot.get_copy().add_assumptions( [assumption(expr(a), '==', expr(0)), assumption(expr(b), assumpt.sign, expr(0))] )
                    #print('result == : ')
                    #for ppp in third_pots:
                    #    print(ppp)
                    #print(40*'-')

                    new_current_pots += nfirst_pots + nsecond_pots + third_pots
                    for some_pot in new_current_pots:
                        found = False
                        for ass in some_pot.decomposed_symbol_assumptions:
                            if ass == assumpt:
                                found = True
                                break
                        if not found:
                            some_pot.decomposed_symbol_assumptions.append(assumpt)

            current_pots = new_current_pots

        return current_pots

    def _push_assumption(self, assumpt):
        #print('_push_assumption(', assumpt, ')')
        assumpt_deps = assumpt.depends()
        deps_len = len(assumpt_deps)
        if deps_len == 0:
            if assumpt.test() == result.not_possible: return list()
            return self.get_copy_in_list()

        if deps_len == 1:
            symbol = assumpt_deps[0]
            if symbol not in self.symbols_intervals:
                self.symbols_intervals[symbol] = intervals()
            lim = decompose(assumpt)
            if not lim:
                print("decompose failed: ", assumpt)
                return list()

            res = self.symbols_intervals[symbol]
            res *= lim
            if res.is_zero():
                #print("filtered by symbols_intervals")
                return list()
            self.symbols_intervals[symbol] = res # ?may delete this line, cause res is ref
            if not self._check_symbols_assumptions_on_known_interval():
                #print("filtered by _check_symbols_assumptions_on_known_interval")
                return list()
            return self.get_copy_in_list()

        if not test_linear_assumption(self.symbols_intervals, assumpt):
        #print("filtered by test_linear_assumption")
            return list()

        #print("_push_assumption_gonna_decompose")
        pots = self._push_assumption_try_linear_decompose(assumpt, assumpt_deps)
        npots = list()
        for pot in pots:
            if pot._check_symbols_assumptions(): npots.append(pot)

        pots = npots
        return pots

    def _add_linear_assumptions(self, lassumpts):
        current_pots = list()
        current_pots.append(self.get_copy())
        #print("_add_linear_assumptions: ")
        #for la in lassumpts:
        #	print("\t", la)
        #print("has: \n", self)
        for la in lassumpts:
            new_current_pots = list()
            for cp in current_pots:
                new_current_pots += cp._push_assumption(la)
            current_pots = new_current_pots
            #print('iteration: ', la)
            #print('new_pots:')
            #for ppp in current_pots:
            #    print(ppp)
            #print('iteration_end')
            if len(current_pots) == 0: break
        return current_pots

    def _add_assumption(self, assumpt):
        npots = list()
        #print('_add_assumption(', assumpt, ')')
        for lassumpts in assumption_ratio_to_linear(assumpt):
            npots += self._add_linear_assumptions(lassumpts)
        return npots

    def _add_assumption2(self, linear_assumpt):
        npots = list()
        #print('_add_assumption(', assumpt, ')')
        for lassumpts in linear_assumpt:
            npots += self._add_linear_assumptions(lassumpts)
        return npots

    def _filter_linear_assumptions(self, linear_assumptions):
        nlinear_assumptions = list()
        for lassumpts in linear_assumptions:
            good = True
            for assumpt in lassumpts:
                assumpt_deps = assumpt.depends()
                deps_len = len(assumpt_deps)
                if deps_len == 0:
                    if assumpt.test() == result.not_possible:
                        good = False
                        break

                if deps_len == 1:
                    symbol = assumpt_deps[0]
                    if symbol not in self.symbols_intervals:
                        self.symbols_intervals[symbol] = intervals()
                    lim = decompose(assumpt)
                    if not lim:
                        print("decompose failed: ", assumpt)
                        return list()

                    res = deepcopy(self.symbols_intervals[symbol])
                    res *= lim
                    if res.is_zero():
                        good = False
                        break

            if good:
                nlinear_assumptions.append(lassumpts)
        return nlinear_assumptions

    """def add_assumptions(self, assumpts):
        return self.___add_assumptions(assumpts)
        t1 = time.clock()
        first_pot = theorypot()
        first_pot.symbols_intervals = deepcopy(self.symbols_intervals)
        assumpts_pots = [ first_pot, ]
        for assumpt in assumpts:
            new_assumpts_pots = list()
            for ap in assumpts_pots:
                new_assumpts_pots += ap._add_assumption(assumpt)
            assumpts_pots = new_assumpts_pots
        t2 = time.clock()
        global time_delta
        time_delta += t2 - t1

        lassumpts = list()
        for ap in assumpts_pots:
            assmps = list()
            for inter in ap.symbols_intervals:
                assmps += ap.symbols_intervals[inter].get_assumptions(inter)
            assmps += ap.decomposed_symbol_assumptions
            lassumpts.append(assmps)

        current_pots = list()
        current_pots.append(self.get_copy())

        t1 = time.clock()
        new_current_pots = list()
        for cp in current_pots:
            new_current_pots += cp._add_assumption2(lassumpts)
        t2 = time.clock()
        time_delta += t2 - t1

        return new_current_pots"""


    def add_assumptions(self, assumpts):
        current_pots = list()
        current_pots.append(self.get_copy())
        for assumpt in assumpts:
            linear_assumptions = assumption_ratio_to_linear(assumpt)
            linear_assumptions = self._filter_linear_assumptions(linear_assumptions)

            new_current_pots = list()
            for cp in current_pots:
                new_current_pots += cp._add_assumption2(linear_assumptions)
                #new_current_pots += cp._add_assumption(assumpt)

            current_pots = new_current_pots
            if len(current_pots) == 0: break
        return current_pots

class theorypots:
    def __init__(self):
        self.pots = list()
        self.pots.append(theorypot())

    def is_valid(self):
        if len(self.pots) == 0: return False
        else: return True

    def __str__(self):
        ret = ""
        if len(self.pots) == 0: return "no pots\n"
        for i, pot in enumerate(self.pots):
            ret += 'pot #' + str(i) + ':' + '\n'
            ret += str(pot) + '\n'
        return ret

    def add_or_assumptions(self, or_assumptions):
        npots = list()
        for pot in self.pots:
            for assumptions in or_assumptions:
                temp_pot = pot.get_copy()
                npots += temp_pot.add_assumptions(assumptions)
        self.pots = npots
        return self.is_valid()

    def add_assumptions(self, assumpts):
        npots = list()
        for pot in self.pots:
            npots += pot.add_assumptions(assumpts)
        self.pots = npots
        return self.is_valid()

    def get_all_assumptions_by_pots(self):
        ret = list()
        for pot in self.pots:
            ret.append( pot.get_all_assumtions() )
        return ret


    def get_all_assumptions_by_pots_to_tex(self):
        ret = list()
        for pot in self.pots:
            ret.append( pot.get_all_assumtions_to_tex() )
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