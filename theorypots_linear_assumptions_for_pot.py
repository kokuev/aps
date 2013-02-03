__author__ = 'ak'
from assumption import assumption
from expression import linear

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
        self.variation.append(linear_assumpt)
        return True

    def get_linear_assumption_list(self):
        res = self.variations
        if len(self.variation) > 0: res.append(self.variation)
        return res


def assumption_equal_ratio_to_linear(assumpt, pot):
    variations = variations_for_pot(pot)

    num_mults = list()
    (num, denom) = assumpt.exp.get_mults()

    if assumpt.exp.denomerator.is_calculatable() and assumpt.exp.denomerator.calculate() == 0:
        return variations.get_linear_assumption_list()

    if not assumpt.exp.numerator.is_calculatable():
        for m in num:
            if not m.is_calculatable():
                num_mults.append(m)
            elif m.calculate() == 0:
                variations.add_assumption(assumption(m, '==', linear(0)))
                return variations.get_linear_assumption_list()
    else:
        value = assumpt.exp.numerator.calculate()
        if value != 0: return variations.get_linear_assumption_list()
        elif value == 0:
            variations.add_assumption(assumption(linear(0), '==', linear(0)))
            return variations.get_linear_assumption_list()

    for m in num_mults:
        variations.new_variation()
        variations.add_assumption(assumption(m, '==', linear(0)))

    return variations.get_linear_assumption_list()

def assumption_not_equal_ratio_to_linear(assumpt, pot):
    variations = variations_for_pot(pot)

    num_mults = list()
    (num, denom) = assumpt.exp.get_mults()

    if assumpt.exp.denomerator.is_calculatable() and assumpt.exp.denomerator.calculate() == 0:
        variations.get_linear_assumption_list()

    if not assumpt.exp.numerator.is_calculatable():
        for m in num:
            if not m.is_calculatable():
                num_mults.append(m)
            elif m.calculate() == 0:
                variations.get_linear_assumption_list()
    else:
        value = assumpt.exp.numerator.calculate()
        if value == 0:  variations.get_linear_assumption_list()
        elif value != 0:
            variations.add_assumption(assumption(linear(0), '==', linear(0)))
            return variations.get_linear_assumption_list()

    variations.new_variation()
    for m in num_mults:
        if not variations.add_assumption(assumption(m, '!=', linear(0))):
            break

    return variations.get_linear_assumption_list()

def assumption_signed_ratio_to_linear(assumpt, pot):
    variations = variations_for_pot(pot)

    num_mults = list()
    denom_mults = list()
    (num, denom) = assumpt.exp.get_mults()

    sign = 1
    if not assumpt.exp.numerator.is_calculatable():
        for m in num:
            if not m.is_calculatable():
                num_mults.append(m)
            elif m.calculate() < 0: sign *= -1
    elif assumpt.exp.numerator.calculate() < 0: sign *= -1

    if not assumpt.exp.denomerator.is_calculatable():
        for m in denom:
            if not m.is_calculatable():
                denom_mults.append(m)
            elif m.calculate() < 0: sign *= -1
    elif assumpt.exp.denomerator.calculate() < 0: sign *= -1

    s = len(num_mults) + len(denom_mults)
    if s == 0: variations.get_linear_assumption_list()

    if sign > 0: all_signs = get_signs(s, 0)
    else: all_signs = get_signs(s, 1)

    if assumpt.sign == '>': strong_sign = True
    else: strong_sign = False

    for signs in all_signs:
        num_signs = signs[:len(num_mults)]
        denom_signs = signs[len(num_mults):]

        bad_variation = False
        for (m, s) in zip(num_mults, num_signs):
            if not strong_sign:
                if s == '>': s = '>='
                else: s = '<='
            if not variations.add_assumption(assumption(m, s, linear(0))):
                bad_variation = True
                break
        if bad_variation: continue

        for (m, s) in zip(denom_mults, denom_signs):
            if not variations.add_assumption(assumption(m, s, linear(0))):
                bad_variation = True
                break
        if bad_variation: continue
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

