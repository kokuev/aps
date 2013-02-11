__author__ = 'ak'
from assumption import assumption
#from expression import linear
from sympy import Number
from copy import deepcopy

class variations_for_pot:
    def __init__(self, pot):
        self.pot = pot
        self.variations = list()
        self.variation = list()

    def new_variation(self):
        if len(self.variation) > 0: self.variations.append(self.variation)
        self.variation = list()

    def clear_variation(self):
        self.variation = list()

    def add_assumption(self, linear_assumpt):
        if not self.pot.linear_assumption_basic_test_on_possibility(linear_assumpt):
            self.clear_variation()
            return False
        self.variation.append(deepcopy(linear_assumpt))
        return True

    def add_assumptions(self, linear_assumpts):
        for assump in linear_assumpts:
            if self.add_assumption(assump) == False:
                return False
        return True

    def get_linear_assumption_list(self):
        res = self.variations
        if len(self.variation) > 0: res.append(self.variation)
        return res


def assumption_equal_ratio_to_linear(assumpt, pot):
    variations = variations_for_pot(pot)

    num_mults = list()

    assumpt.exp = assumpt.exp.simplify()
    (num, denom) = assumpt.exp.as_numer_denom()

    if denom.is_number and denom.is_zero:
        return variations.get_linear_assumption_list()

    if not num.is_number:
        num_dict = num.combsimp().as_powers_dict()
        for m in num_dict:
            if not m.is_number:
                num_mults.append(m)
            elif m.is_zero:
                variations.add_assumption(assumption(m, '==', Number(0)))
                return variations.get_linear_assumption_list()
    else:
        if not num.is_zero: return variations.get_linear_assumption_list()
        else:
            variations.add_assumption(assumption(Number(0), '==', Number(0)))
            return variations.get_linear_assumption_list()

    for m in num_mults:
        variations.new_variation()
        variations.add_assumption(assumption(m, '==', Number(0)))

    return variations.get_linear_assumption_list()

def assumption_not_equal_ratio_to_linear(assumpt, pot):
    variations = variations_for_pot(pot)

    num_mults = list()

    assumpt.exp = assumpt.exp.simplify()
    (num, denom) = assumpt.exp.as_numer_denom()

    if denom.is_number and denom.is_zero:
        variations.get_linear_assumption_list()

    if not num.is_number:
        num_dict = num.combsimp().as_powers_dict()
        for m in num_dict:
            if not m.is_number:
                num_mults.append(m)
            elif m.is_zero:
                variations.get_linear_assumption_list()
    else:
        if num.is_zero:
            variations.get_linear_assumption_list()
        else:
            variations.add_assumption(assumption(Number(0), '==', Number(0)))
            return variations.get_linear_assumption_list()

    variations.new_variation()
    for m in num_mults:
        if not variations.add_assumption(assumption(m, '!=', Number(0))):
            break

    return variations.get_linear_assumption_list()

def assumption_signed_ratio_to_linear(assumpt, pot):
    variations = variations_for_pot(pot)

    num_possible_neg_mults = list()
    num_possible_zero_mults = list()
    denom_mults = list()
    denom_possible_zero = list()

    assumpt.exp = assumpt.exp.simplify()
    (num, denom) = assumpt.exp.as_numer_denom()

    sign = 1
    if not num.is_number:
        coef, other = num.combsimp().as_coeff_mul()
        if coef.is_negative: sign *= -1
        for o in other:
            ods = o.as_powers_dict()
            for od in ods:
                if ods[od].is_even:
                    num_possible_zero_mults.append(od)
                else:
                    num_possible_neg_mults.append(od)
    elif num.is_negative: sign *= -1

    if not denom.is_number:
        coef, other = denom.combsimp().as_coeff_mul()
        if coef.is_negative: sign *= -1
        for o in other:
            ods = o.as_powers_dict()
            for od in ods:
                if ods[od].is_even:
                    denom_possible_zero.append(od)
                else:
                    denom_mults.append(od)
    elif denom.is_negative: sign *= -1

    if assumpt.sign == '>': strong_sign = True
    else: strong_sign = False

    global_assumpts = list()
    for dpz in denom_possible_zero + denom_mults:
        global_assumpts.append(assumption(dpz, '!=', Number(0)))

    if strong_sign == False and len(num_possible_zero_mults) > 0:
        for npzm in num_possible_zero_mults:
            if not variations.add_assumption(assumption(npzm, '==', Number(0))):
                continue
            if not variations.add_assumptions(global_assumpts):
                continue
            variations.new_variation()

    s = len(num_possible_neg_mults) + len(denom_mults)
    if s == 0: variations.get_linear_assumption_list()

    if sign > 0: all_signs = get_signs(s, 0)
    else: all_signs = get_signs(s, 1)

    for signs in all_signs:
        num_signs = signs[:len(num_possible_neg_mults)]
        denom_signs = signs[len(num_possible_neg_mults):]

        bad_variation = False
        for (m, s) in zip(num_possible_neg_mults, num_signs):
            if not strong_sign:
                if s == '>': s = '>='
                else: s = '<='
            if not variations.add_assumption(assumption(m, s, Number(0))):
                bad_variation = True
                break
        if bad_variation: continue

        for (m, s) in zip(denom_mults, denom_signs):
            if not variations.add_assumption(assumption(m, s, Number(0))):
                bad_variation = True
                break
        if bad_variation: continue

        if not variations.add_assumptions(global_assumpts):
            continue

        variations.new_variation()

    return variations.get_linear_assumption_list()

def assumption_ratio_to_linear(assumption, pot):
    if assumption.sign == '>' or assumption.sign == '>=': return assumption_signed_ratio_to_linear(assumption, pot)
    elif assumption.sign == '==': return assumption_equal_ratio_to_linear(assumption, pot)
    elif assumption.sign == '!=': return assumption_not_equal_ratio_to_linear(assumption, pot)
    else: raise Exception('unknown sign: ', assumption.sign)

def get_signs(size, sign):
    s = "{0:0>" + str(size) + "b}"
    for i in range(0, 2**size):
        ret = list(s.format(i).replace('1', '<').replace('0','>'))
        if (ret.count('<') % 2) == sign: yield ret
