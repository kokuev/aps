from assumption import assumption
from expression import linear

def assumption_equal_ratio_to_linear(assumpt):
    variations = list()

    num_mults = list()
    (num, denom) = assumpt.exp.get_mults()

    if assumpt.exp.denomerator.is_calculatable() and assumpt.exp.denomerator.calculate() == 0: return variations

    if not assumpt.exp.numerator.is_calculatable():
        for m in num:
            if not m.is_calculatable():
                num_mults.append(m)
            elif m.calculate() == 0:
                exps = list()
                exps.append(assumption(m, '==', linear(0)))
                variations.append(exps)
                return variations
    else:
        value = assumpt.exp.numerator.calculate()
        if value != 0: return variations
        elif value == 0:
            exps = list()
            exps.append(assumption(linear(0), '==', linear(0)))
            variations.append(exps)
            return variations

    for m in num_mults:
        exps = list()
        exps.append(assumption(m, '==', linear(0)))
        variations.append(exps)

    return variations

def assumption_not_equal_ratio_to_linear(assumpt):
    variations = list()

    num_mults = list()
    (num, denom) = assumpt.exp.get_mults()

    if assumpt.exp.denomerator.is_calculatable() and assumpt.exp.denomerator.calculate() == 0: return variations

    if not assumpt.exp.numerator.is_calculatable():
        for m in num:
            if not m.is_calculatable():
                num_mults.append(m)
            elif m.calculate() == 0:
                return variations
    else:
        value = assumpt.exp.numerator.calculate()
        if value == 0: return variations
        elif value != 0:
            exps = list()
            exps.append(assumption(linear(0), '==', linear(0)))
            variations.append(exps)
            return variations

    exps = list()
    for m in num_mults:
        exps.append(assumption(m, '!=', linear(0)))
    variations.append(exps)

    return variations

def assumption_signed_ratio_to_linear(assumpt):
    variations = list()

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
    if s == 0: return variations

    if sign > 0: all_signs = get_signs(s, 0)
    else: all_signs = get_signs(s, 1)

    if assumpt.sign == '>': strong_sign = True
    else: strong_sign = False

    for signs in all_signs:
        num_signs = signs[:len(num_mults)]
        denom_signs = signs[len(num_mults):]
        exps = list()
        for (m, s) in zip(num_mults, num_signs):
            if not strong_sign:
                if s == '>': s = '>='
                else: s = '<='
            exps.append(assumption(m, s, linear(0)))
        for (m, s) in zip(denom_mults, denom_signs):
            exps.append(assumption(m, s, linear(0)))

        variations.append(exps)
    return variations

def assumption_ratio_to_linear(assumption):
    if assumption.sign == '>' or assumption.sign == '>=': return assumption_signed_ratio_to_linear(assumption)
    elif assumption.sign == '==': return assumption_equal_ratio_to_linear(assumption)
    elif assumption.sign == '!=': return assumption_not_equal_ratio_to_linear(assumption)
    else: raise Exception('unknown sign: ', assumption.sign)

def get_signs(size, sign):
    s = "{0:0>" + str(size) + "b}"
    for i in range(0, 2**size):
        ret = list(s.format(i).replace('1', '<').replace('0','>'))
        if (ret.count('<') % 2) == sign: yield ret

