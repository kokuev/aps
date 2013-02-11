from assumption import assumption
from interval import intervals, interval
import math
from theorypots_numerical_poly import get_poly_roots,get_fx
from sympy import Number

def get_poly_interval(a, n, sign, roots):
    roots = sorted(roots)
    i = intervals(interval(0, True, 0, True))

    if sign == '==':
        for x in roots:
            i += interval(x, False, x, False)
        return i
    if sign == '!=':
        r = float('-inf')
        for x in roots:
            l, r = r, x
            i += interval(l, True, r, True)
        l, r = r, float('inf')
        i += interval(l, True, r, True)
        return i

    need_neg = False
    strong = True
    if sign == '>=': strong = False
    if sign == '<' or sign == '<=':
        need_neg = True
        if sign == '<=': strong = False

    f = get_fx(a, n)
    neg = False
    if f(float('-inf')) < 0: neg = True

    r = float('-inf')
    for x in roots:
        l, r = r, x
        if not neg ^ need_neg:
            i += interval(l, strong, r, strong)
        neg = not neg

    l, r = r, float('inf')
    if not neg ^ need_neg:
        i += interval(l, strong, r, strong)

    return i

def get_linear(res, sign):
    a_, b_, p = res
    if len(a_) == 1 and len(b_) <= 1 and p > 0:
        a, mn_a = a_[0]
        if len(b_) == 1: b, mn_b = b_[0]
        else: b, mn_b = 0., []
        if len(mn_a) == 0 and len(mn_b) == 0:
            c = -b / a
            if a < 0:
                if sign == '>': sign = '<'
                elif sign == '>=': sign = '<='
            if p % 2 == 0:
                if c <= 0:
                    if sign == '>':
                        return intervals(interval(0,  True, float('inf'), True))
                    elif sign == '>=':
                        return intervals(interval(0, False, float('inf'), True))
                    elif sign == '==':
                        if c == 0: return intervals(interval(0, False, 0, False))
                        else: intervals(interval(0, True, 0, True))
                    elif sign == '!=':
                        if c == 0: return intervals(interval(0, True, float('inf'), True))
                        else: return intervals(interval(0, False, float('inf'), True))
                    else:
                        if sign == '<=' and c == 0:
                            return intervals(interval(0, False, 0, False))
                        return intervals(interval(0, True, 0, True))
                d = math.pow(c, 1 / p)
                if sign == '>':
                    return intervals(interval(float('-inf'), True, -d, True)) + interval(d, True, float('inf'), True)
                elif sign == '>=':
                    return intervals(interval(float('-inf'), True, -d, False)) + interval(d, False, float('inf'), True)
                elif sign == '<':
                    return intervals(interval(-d, True, d, True))
                elif sign == '<=':
                    return intervals(interval(-d, False, d, False))
                elif sign == '==':
                    return intervals(interval(d, False, d, False)) + interval(-d, False, -d, False)
                elif sign == '!=':
                    return intervals(interval(float('-inf'), True, -d, True)) + interval(-d, True, d, True) + interval(d, True, float('inf'), True)
                else: raise Exception('unknown sign: ' + sign)
            if c < 0: d = -math.pow(-c, 1 / p)
            else: d = math.pow(c, 1 / p)
            if sign == '>':
                return intervals(interval(d, True, float('inf'), True))
            elif sign == '>=':
                return intervals(interval(d, False, float('inf'), True))
            elif sign == '<':
                return intervals(interval(float('-inf'), True, d, True))
            elif sign == '<=':
                return intervals(interval(float('-inf'), True, d, False))
            elif sign == '==':
                return intervals(interval(d, False, d, False))
            elif sign == '!=':
                return intervals(interval(float('-inf'), True, d, True)) + interval(d, True, float('inf'), True)
            else: raise Exception('unknown sign: ' + sign)
    return None

def get_quadratic(res, sign):
    a_, b_, c_, p = res
    if len(a_) == 1 and len(b_) <= 1 and len(c_) <= 1 and p == 2:
        a, mn_a = a_[0]
        if len(b_) == 1: b, mn_b = b_[0]
        else: b, mn_b = 0., []
        if len(c_) == 1: c, mn_c = c_[0]
        else: c, mn_c = 0., []

        if len(mn_a) == 0 and len(mn_b) == 0 and len(mn_c) == 0:
            d = b*b - 4*a*c
            if d < 0:
                return get_poly_interval({0: c, 1: b, 2: a}, 2, sign, [])
            elif d == 0:
                return get_poly_interval({0: c, 1: b, 2: a}, 2, sign, [-b / (2 * a)])
            else:
                return get_poly_interval({0: c, 1: b, 2: a}, 2, sign, [(-b - math.sqrt(d))/(2*a), (-b + math.sqrt(d))/(2*a)])
    return None


cached_poly = dict()

def get_poly(res, sign):
    a, p = res
    key = list()
    for r in sorted(a.keys()):
        key.append(a[r])
    key = tuple(key)
    if key in cached_poly: er, roots = cached_poly[key]
    else:
        er, roots = get_poly_roots(a, p)
        cached_poly[key] = (er, roots)
    if not er: return None

    return get_poly_interval(a, p, sign, roots)

def _decompose(assumpt):
    deps = assumpt.depends()
    if len(deps) != 1: return None
    symb = deps[0]
    res = assumpt.exp.try_linear(symb)
    if res: res = get_linear(res, assumpt.sign)
    if res:
        return res
    res = assumpt.exp.try_quadratic(symb)
    if res: res = get_quadratic(res, assumpt.sign)
    if res: return res
    res = assumpt.exp.try_poly(symb)
    if res: res = get_poly(res, assumpt.sign)
    if res: return res
    return None

def get_intervals(poly, sign, roots, minimum):
    i = intervals(interval(0, True, 0, True))

    if sign == '==':
        for x in roots:
            i += interval(x, False, x, False)
        return i
    if sign == '!=':
        r = float('-inf')
        for x in roots:
            l, r = r, x
            i += interval(l, True, r, True)
        l, r = r, float('inf')
        i += interval(l, True, r, True)
        return i

    need_neg = False
    strong = True
    if sign == '>=': strong = False
    if sign == '<' or sign == '<=':
        need_neg = True
        if sign == '<=': strong = False

    neg = False
    if poly(minimum - Number(100)).is_negative:
        neg = True

    r = float('-inf')
    for x in roots:
        l, r = r, x
        if not neg ^ need_neg:
            i += interval(l, strong, r, strong)
        neg = not neg

    l, r = r, float('inf')
    if not neg ^ need_neg:
        i += interval(l, strong, r, strong)

    return i

def decompose(assumpt):
    deps = assumpt.depends()
    if len(deps) != 1: return None
    poly = assumpt.exp.as_poly()
    if not poly: return None

    minimum = None
    roots = poly.all_roots()
    for root in roots:
        if not root.is_number or not root.is_real:
            return None
        if minimum == None or root < minimum:
            minimum = root

    return get_intervals(poly, assumpt.sign, roots, minimum)

if __name__ == "__main__":
    from expression import linear
    from sympy import Number, Symbol
    """print(decompose(assumption(linear(4)*linear('x') , '>', linear(2))))
    print(decompose(assumption(linear(4)*linear('x') , '>', linear(-2))))
    print(decompose(assumption(linear(4)*linear('x')*linear('x') , '>', linear(2))))
    print(decompose(assumption(linear(4)*linear('x')*linear('x') , '>=', linear(2))))
    print(decompose(assumption(linear(4)*linear('x')*linear('x') , '<', linear(0))))
    print(decompose(assumption(linear(4)*linear('x')*linear('x') , '<=', linear(0))))
    print(decompose(assumption(linear(4)*linear('x')*linear('x')*linear('x') , '<=', linear(2))))
    print(decompose(assumption(linear(4)*linear('x')*linear('x')*linear('x') , '<', linear(2))))
    print(decompose(assumption(linear(4)*linear('x')*linear('x')*linear('x') , '<', linear(-2))))"""
    a = Number(-1)
    b = Number(20)
    c = Number(11)
    d = Number(-100)
    x = Symbol('x')
    """print(decompose(assumption(a*x*x*x + b*x*x + c*x + d, '>', linear(0.))))
    print(decompose(assumption(a*x*x*x + b*x*x + c*x + d, '>=', linear(0.))))
    print(decompose(assumption(a*x*x*x + b*x*x + c*x + d, '<', linear(0.))))
    print(decompose(assumption(a*x*x*x + b*x*x + c*x + d, '<=', linear(0.))))"""

    a = Number(1)
    b = Number(2000)
    c = Number(1999)
    print(decompose(assumption(a*x*x + b*x + c, '>', Number(0.))))
    print(decompose(assumption(a*x*x + b*x + c, '>=', Number(0.))))
    print(decompose(assumption(a*x*x + b*x + c, '<', Number(0.))))
    print(decompose(assumption(a*x*x + b*x + c, '<=', Number(0.))))

    a = Number(-1)
    b = Number(-1999)
    c = Number(2000)
    print(decompose(assumption(a*x*x + b*x + c, '>', Number(0.))))
    print(decompose(assumption(a*x*x + b*x + c, '>=', Number(0.))))
    print(decompose(assumption(a*x*x + b*x + c, '<', Number(0.))))
    print(decompose(assumption(a*x*x + b*x + c, '<=', Number(0.))))

    a = Number(1)
    b = Number(0)
    c = Number(0)
    print(decompose(assumption(a*x*x + b*x + c, '>', Number(0.))))
    print(decompose(assumption(a*x*x + b*x + c, '>=', Number(0.))))
    print(decompose(assumption(a*x*x + b*x + c, '<', Number(0.))))
    print(decompose(assumption(a*x*x + b*x + c, '<=', Number(0.))))
