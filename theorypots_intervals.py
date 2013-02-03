from interval import intervals, interval

def get_linear_data_intervals(sym_lims, data):
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

def test_linear_assumption(sym_lims, a):
    a_interval = get_linear_data_intervals(sym_lims, a.exp.data)
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
    denom_intervals = get_linear_data_intervals(sym_lims, exp.denomerator.data)
    num_intervals = get_linear_data_intervals(sym_lims, exp.numerator.data)
    denom_intervals = denom_intervals.get_dived_intervals()
    return num_intervals.get_mult_intervals(denom_intervals)
