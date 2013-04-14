from interval import intervals, interval

def _get_linear_data_intervals(sym_lims, exp):
    data = exp.data
    ret = intervals(interval(0, True, 0, True))
    for (k, mn) in data:
        one = intervals(interval(k, True, k, True))
        for m in mn:
            if m in sym_lims:
                one = one.get_mult_intervals(sym_lims[m].get_intervals_by_pow(mn[m]))
            else:
                one = one.get_mult_intervals(intervals(interval(float('-inf'), True, float('inf'), True)))
        ret = ret.get_add_intervals(one)
    return ret

def get_linear_data_intervals(sym_lims, exp):
    ret = intervals(interval(0, True, 0, True))
    expcd = exp.as_coefficients_dict()
    for mn in expcd:
        k = expcd[mn]
        one = intervals(interval(k, False, k, False))
        c, mns = mn.as_coeff_mul()
        for omns in mns:
            pomns = omns.as_powers_dict()
            for s in pomns:
                p = pomns[s]
                if s in sym_lims:
                    one = one.get_mult_intervals(sym_lims[s].get_intervals_by_pow(p))
                else:
                    one = one.get_mult_intervals(intervals(interval(float('-inf'), True, float('inf'), True)))
        ret = ret.get_add_intervals(one)
    return ret

def test_linear_assumption(sym_lims, a):
    a_interval = get_linear_data_intervals(sym_lims, a.exp)
    if a.sign == '>=': need = intervals(interval(0, False, float('inf'), True))
    elif a.sign == '>': need = intervals(interval(0, True, float('inf'), True))
    elif a.sign == '<': need = intervals(interval(float('-inf'), True, 0, True))
    elif a.sign == '<=': need = intervals(interval(float('-inf'), True, 0, False))
    elif a.sign == '==': need = intervals(interval(0, False, 0, False))
    elif a.sign == '!=': need = intervals(interval(float('-inf'), True, 0, True)) + interval(0, True, float('inf'), True)
    else: raise Exception('unknown sign: ', a.sign)
    result = a_interval * need
    return not result.is_zero()

def get_ration_data_intervals(sym_lims, exp):
    num, denom = exp.as_numer_denom()
    denom_intervals = get_linear_data_intervals(sym_lims, denom)
    num_intervals = get_linear_data_intervals(sym_lims, num)
    denom_intervals = denom_intervals.get_dived_intervals()
    return num_intervals.get_mult_intervals(denom_intervals)


if __name__ == "__main__":
    from sympy import Symbol
    from sympy.parsing.sympy_parser import parse_expr

    print(get_linear_data_intervals(dict(), parse_expr('4')))
    print(get_linear_data_intervals({Symbol('a'): intervals(interval(float(1), True, float('+inf'), True)) }, parse_expr('4*a')))
    print(get_linear_data_intervals({Symbol('a'): intervals(interval(float(1), False, float('+inf'), True)) }, parse_expr('4*a')))