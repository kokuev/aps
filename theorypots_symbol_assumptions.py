__author__ = 'ak'

from copy import deepcopy
from interval import intervals, interval
#from expression import linear, expr
from sympy import Number
from assumption import  result, assumption
from theorypots_numerical import decompose
from theorypots_sign_lists import combine_signs_list, check_sign_lists, dedup
from theorypots_intervals import get_ration_data_intervals
from theorypots_linear_assumptions_for_pot import assumption_ratio_to_linear

class decomposed_assumption_variant():
    def __init__(self):
        self.assumptions = list()
        self.symbol_assumptions = list()

    def is_null(self):
        if len(self.assumptions) == 0 and len(self.symbol_assumptions) == 0:
            return True
        return False

    def add_assumption(self, assumption):
        self.assumptions.append(assumption)

    def add_symbol_assumption(self, assumption):
        self.symbol_assumptions.append(assumption)

class decomposed_assumption:
    def __init__(self):
        self.variant_groups = list()
        self.variants = list()
        self.variant = decomposed_assumption_variant()

    def new_variant_group(self):
        self.new_variant()
        if len(self.variants) > 0:
            self.variant_groups.append(self.variants)
        self.variants = list()

    def new_variant(self):
        if not self.variant.is_null():
            self.variants.append(self.variant)
        self.variant = decomposed_assumption_variant()

    def add_assumption(self, assumption):
        self.variant.add_assumption(assumption)

    def add_symbol_assumption(self, assumption):
        self.variant.add_symbol_assumption(assumption)

def try_assumpt_linear(assumpt, symbol):
    exp = assumpt.exp
    poly = exp.as_poly(symbol)
    if not poly: return None
    if poly.degree(symbol) != 1: return None
    a, b_ = exp.as_coeff_add(symbol)
    some = Number(0)
    for sb in b_: some += sb

    b = (some / symbol).simplify()

    return a, b


def prepare_decomposed_assumptions(assumpt, assumpt_deps):
    variants = decomposed_assumption()
    for symbol in assumpt_deps:
        res = try_assumpt_linear(assumpt, symbol)
        if not res: continue
        a, b = res

        sign = assumpt.sign

        variants.new_variant_group()

        if sign == '==':
            variants.new_variant()
            variants.add_assumption( assumption(a, '!=', Number(0)) )
            variants.add_symbol_assumption( (symbol, '==', Number(-1)*b/a ) )

            variants.new_variant()
            variants.add_assumption( assumption(a, '==', Number(0)) )
            variants.add_assumption( assumption(b, '==', Number(0)) )

        elif sign == '!=':
            variants.new_variant()
            variants.add_assumption( assumption(a, '!=', Number(0)) )
            variants.add_symbol_assumption( (symbol, '!=', Number(-1)*b/a) )

            variants.new_variant()
            variants.add_assumption( assumption(a, '==', Number(0)) )
            variants.add_assumption( assumption(b, '!=', Number(0)) )

        else:
            if sign == '>': neg_sign = '<'
            elif sign == '>=': neg_sign = '<='
            elif sign == '<': neg_sign = '>'
            else: neg_sign = '>='

            variants.new_variant()
            variants.add_assumption( assumption(a, '>', Number(0)) )
            variants.add_symbol_assumption( (symbol, sign, Number(-1)*b/a) )

            variants.new_variant()
            variants.add_assumption( assumption(a, '<', Number(0)) )
            variants.add_symbol_assumption( (symbol, neg_sign, Number(-1)*b/a) )

            variants.new_variant()
            variants.add_assumption( assumption(a, '==', Number(0)) )
            variants.add_assumption( assumption(b, sign, Number(0)) )

    variants.new_variant_group()
    return variants

class pot_symbol_variant:
    def __init__(self):
        self.symbol_assumptions = dict()
        self.assumptions = list()

    def _check_symbol_assumptions_on_known_limits(self, symbol, symbols_intervals):
        symbol_max, symbol_max_strong, symbol_min, symbol_min_strong = float('+inf'), True, float('-inf'), True

        if '>' in self.symbol_assumptions[symbol]:
            for e in self.symbol_assumptions[symbol]['>']:
                current_max, current_max_strong, current_min, current_min_strong = get_ration_data_intervals(symbols_intervals, e).get_max_min()
                if current_min > symbol_min or (current_min == symbol_min and current_min_strong == True):
                    symbol_min, symbol_min_strong = current_min, current_min_strong
        if '<' in self.symbol_assumptions[symbol]:
            for e in self.symbol_assumptions[symbol]['<']:
                current_max, current_max_strong, current_min, current_min_strong = get_ration_data_intervals(symbols_intervals, e).get_max_min()
                if current_max < symbol_max or (current_max == symbol_max and current_max_strong == True):
                    symbol_max, symbol_max_strong = current_max, current_max_strong
        if '==' in self.symbol_assumptions[symbol]:
            for e in self.symbol_assumptions[symbol]['==']:
                current_max, current_max_strong, current_min, current_min_strong = get_ration_data_intervals(symbols_intervals, e).get_max_min()
                if current_max < symbol_max or (current_max == symbol_max and current_max_strong == True):
                    symbol_max, symbol_max_strong = current_max, current_max_strong
                if current_min > symbol_min or (current_min == symbol_min and current_min_strong == True):
                    symbol_min, symbol_min_strong = current_min, current_min_strong

        if symbol_max < symbol_min or (symbol_min == symbol_max and (symbol_min_strong == True or symbol_max_strong == True)):
            print('[info] gonna be filtered by check_symbol...', symbol, symbol_max, symbol_min)
            return False

        if symbol in symbols_intervals:
            known_interval = deepcopy(symbols_intervals[symbol])
            known_interval *= interval(symbol_min, symbol_min_strong, symbol_max, symbol_max_strong)
            if known_interval.is_zero():
                print('[info] gonna be filtered by check_symbol...', symbol, symbol_max, symbol_min, str(symbols_intervals[symbol]))
                return False
        return True

    def test_by_symbol_intervals(self, symbol_intervals):
        for symbol in self.symbol_assumptions:
            if not self._check_symbol_assumptions_on_known_limits(symbol, symbol_intervals): return False
        return True

    def _update_symbol_assumptions(self):
        for symbol in self.symbol_assumptions:
            combine_signs_list( self.symbol_assumptions[symbol], '>' , '>=', '>'  )
            combine_signs_list( self.symbol_assumptions[symbol], '>' , '!=', '>'  )
            combine_signs_list( self.symbol_assumptions[symbol], '<' , '<=', '<'  )
            combine_signs_list( self.symbol_assumptions[symbol], '<' , '!=', '<'  )
            combine_signs_list( self.symbol_assumptions[symbol], '>=', '<=', '==' )
            combine_signs_list( self.symbol_assumptions[symbol], '>=', '==', '==' )
            combine_signs_list( self.symbol_assumptions[symbol], '>=', '!=', '>'  )
            combine_signs_list( self.symbol_assumptions[symbol], '<=', '==', '==' )
            combine_signs_list( self.symbol_assumptions[symbol], '<=', '!=', '<'  )

    def _test_symbol_assumptions(self):
        for symbol in self.symbol_assumptions:
            if not check_sign_lists(self.symbol_assumptions[symbol], '>' , '<' ): return False
            if not check_sign_lists(self.symbol_assumptions[symbol], '>' , '<='): return False
            if not check_sign_lists(self.symbol_assumptions[symbol], '>' , '=='): return False
            if not check_sign_lists(self.symbol_assumptions[symbol], '<' , '=='): return False
            if not check_sign_lists(self.symbol_assumptions[symbol], '<' , '>='): return False
            if not check_sign_lists(self.symbol_assumptions[symbol], '==', '!='): return False
        return True

    def _add_symbol_assumption(self, symbol_assumption):
        symbol, sign, expression = symbol_assumption
        if symbol not in self.symbol_assumptions:
            self.symbol_assumptions[symbol] = dict()
        if sign not in self.symbol_assumptions[symbol]:
            self.symbol_assumptions[symbol][sign] = list()

        for e in self.symbol_assumptions[symbol][sign]:
            if expression == e: return

        self.symbol_assumptions[symbol][sign].append(expression)

    def try_assumptions(self, pot, decompose_variant):
        self.assumptions += decompose_variant.assumptions
        self.assumptions = dedup(self.assumptions)

        symbol_intervals = deepcopy( pot.symbol_intervals )

        for assumption in self.assumptions:
            assumption_deps = assumption.depends()
            deps_len = len(assumption_deps)
            if deps_len == 0:
                if assumption.test() == result.not_possible: return False
                continue

            if deps_len == 1:
                symbol = assumption_deps[0]
                if symbol not in symbol_intervals:
                    symbol_intervals[symbol] = intervals()
                lim = decompose(assumption)
                if not lim:
                    print("[warn] decompose failed:", assumption)
                    return False

                res = symbol_intervals[symbol]
                res *= lim
                if res.is_zero(): return False
                symbol_intervals[symbol] = res
                continue

        for symbol_assumption in decompose_variant.symbol_assumptions:
            self._add_symbol_assumption(symbol_assumption)

        self._update_symbol_assumptions()
        if not self._test_symbol_assumptions(): return False
        return self.test_by_symbol_intervals(symbol_intervals)

class pot_symbol_variants:
    def __init__(self):
        self.variants = list()
        self.variants.append(pot_symbol_variant())

    def test_by_symbol_intervals(self, symbol_intervals):
        new_variants = list()
        for variant in self.variants:
            if variant.test_by_symbol_intervals(symbol_intervals):
                new_variants.append(variant)
        self.variants = new_variants
        if len(self.variants) == 0: return False
        return True

    def _filter_decomposed_ratio_to_linear(self, pot, decomposed):
        ret = decomposed_assumption()
        for decompose_variant_group in decomposed.variant_groups:
            ret.new_variant_group()
            for decomposed_variant in decompose_variant_group:
                all_variants = [ [ ] ]
                for assumption in decomposed_variant.assumptions:
                    linear_assumptions_groups = assumption_ratio_to_linear(assumption, pot)
                    new_all_variants = list()
                    for linear_assumptions in linear_assumptions_groups:
                        for current_variant in all_variants:
                            new_all_variants.append( current_variant + linear_assumptions )
                    all_variants = new_all_variants

                for variant in all_variants:
                    ret.new_variant()
                    ret.variant.symbol_assumptions = deepcopy(decomposed_variant.symbol_assumptions)
                    ret.variant.assumptions = variant
        ret.new_variant_group()
        return ret

    def linear_assumption_decompose(self, pot, assumpt, assumpt_deps):
        decomposed = prepare_decomposed_assumptions(assumpt, assumpt_deps)
        decomposed = self._filter_decomposed_ratio_to_linear(pot, decomposed)

        current_variants = deepcopy(self.variants)
        for decompose_variant_group in decomposed.variant_groups:
            new_current_variants = list()
            for current_variant in current_variants:
                for decomposed_variant in decompose_variant_group:
                    temp_variant = deepcopy(current_variant)
                    if temp_variant.try_assumptions(pot, decomposed_variant):
                        new_current_variants.append(temp_variant)
            current_variants = new_current_variants
            if len(current_variants) == 0: break
        self.variants = current_variants
        if len(self.variants) == 0: return False
        return True

