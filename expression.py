__author__ = 'ak'
from copy import deepcopy

def mul_symbols(s1, s2):
    res = dict()
    s = list(set(list(s1.keys()) + list(s2.keys())))

    for symb in s:
        accum = 0
        if symb in s1: accum += s1[symb]
        if symb in s2: accum += s2[symb]

        if accum != 0: res[symb] = accum

    return res

class linear:
    # [1, [a => 2]]
    def __init__(self, obj = False):
        self.data = list()
        if isinstance(obj, bool):
            pass
        elif isinstance(obj, str):
            d = dict()
            d[obj] = 1
            self.data.append((1., d))
        elif isinstance(obj, float) and obj != 0.0:
            self.data.append((obj, dict()))
        elif isinstance(obj, int) and obj != 0:
            self.data.append((obj, dict()))
        elif isinstance(obj, linear):
            self.data = deepcopy(obj.data)

    def to_linear(self, obj):
        if isinstance(obj, linear): return obj
        if isinstance(obj, str) or isinstance(obj, float) or isinstance(obj, int): return linear(obj)
        return False

    def __add__(self, other):
        result = linear(self)
        other = self.to_linear(other)
        if not isinstance(other, linear): raise Exception('cannot convert to linear')

        result.data += other.data

        result.reduce()
        return result

    def __neg__(self):
        result = linear()

        for (k, mn) in self.data:
            result.data.append((-k, mn))

        return result

    def __sub__(self, other):
        other = self.to_linear(other)
        if not isinstance(other, linear): raise Exception('cannot convert to linear')

        other = -other
        return self + other

    def reduce(self):
        ndata = list()
        mn = list()
        if len(self.data) == 0: return

        for (k, symbs) in self.data:
            if symbs not in mn: mn.append(symbs)

        for symb in mn:
            accum = 0.
            for (k, symbs) in self.data:
                if symbs == symb:
                    accum += k
            if accum != 0.: ndata.append((accum, symb))

        self.data = ndata

    def __mul__(self, other):
        result = linear()
        for (k1, symbols1) in self.data:
            for (k2, symbols2) in other.data:
                result.data.append((k1*k2 , mul_symbols(symbols1, symbols2)))

        result.reduce()
        return result

    def __pow__(self, step):
        result = self
        if not isinstance(step, int) or step < 1: raise Exception('wrong step')

        for k in range(1, step):
            result *= self

        result.reduce()
        return result

    def __str__(self):
        out = ""
        first = True
        if len(self.data) == 0: out = "0.0"
        else:
            for (k, mn) in self.data:
                if k > 0.0:
                    if not first: out += ' + '
                    else: out += ' '
                else:
                    out += ' - '
                if first: first = False
                k = abs(k)
                if k != 1.0 or (k == 1 and len(mn) < 1):
                    out += "{}".format(k)
                    if len(mn) >= 1: out += ' * '
                for symb in mn.keys():
                    step = mn[symb]
                    if step == 1: out += '{} '.format(symb)
                    else: out += '{}^{} '.format(symb, step)
        return out

    def to_rich(self):
        out = ""
        first = True
        if len(self.data) == 0: out = " "
        else:
            for (k, mn) in self.data:
                if k > 0.0:
                    if not first: out += ' + '
                    else: out += ' '
                else:
                    out += ' - '
                if first: first = False
                k = abs(k)
                if k != 1.0 or (k == 1 and len(mn) < 1):
                    out += "{: .2f}".format(float(k))
                    if len(mn) >= 1: out += ' * '
                for symb in mn.keys():
                    step = mn[symb]
                    if step == 1: out += '{} '.format(symb)
                    else: out += '{}<sup>{}</sup> '.format(symb, step)
        return out
    def to_tex(self):
        out = ""
        first = True
        if len(self.data) == 0: out = "0.0"
        else:
            for (k, mn) in self.data:
                if k > 0.0:
                    if not first: out += ' + '
                    else: out += ' '
                else:
                    out += ' - '
                if first: first = False
                k = abs(k)
                if k != 1.0 or (k == 1.0 and len(mn) < 1):
                    out += "{:.2f}".format(float(k))
                    if len(mn) >= 1: out += ' \\cdot '
                for symb in mn.keys():
                    step = mn[symb]
                    if step == 1: out += '{} '.format(symb)
                    else: out += '{}^{} '.format(symb, step)
        return out

    def __eq__(self, other):
        for (k1, mn1) in self.data:
            found = False
            for (k2, mn2) in other.data:
                if mn1 == mn2:
                    found = True
                    if k1 != k2: return False
            if not found: return False
        for (k1, mn1) in other.data:
            found = False
            for (k2, mn2) in self.data:
                if mn1 == mn2:
                    found = True
                    if k1 != k2: return False
            if not found: return False
        return True

    def is_calculatable(self):
        if len(self.depends()) == 0: return True
        return False

    def calculate(self):
        if len(self.data) == 1:
            (k, mn) = self.data[0]
            if len(mn) > 0: return False
        elif len(self.data) == 0:
            k = 0
        else: k = False
        return k

    def depends(self):
        ret = list()
        for (k, mn) in self.data:
            ret += list(mn.keys())

        return list(set(ret))

    def get_common_divisor(self):
        symbs = dict()
        for (k, mn) in self.data:
            for symb in mn.keys():
                if symb not in symbs: symbs[symb] = mn[symb]

        _symbs = dict()
        for s in symbs.keys():
            gfound = True
            for (k, mn) in self.data:
                found = False
                for symb in mn.keys():
                    if s == symb:
                        found = True
                        symbs[s] = min(symbs[s], mn[symb])
                if not found: gfound = False

            if gfound and symbs[s] >= 1: _symbs[s] = symbs[s]

        return _symbs

    def trash_divisor(self, divis, step):
        for (k, mn) in self.data:
            mn[divis] -= step
            if mn[divis] == 0: del(mn[divis])
        return

    def try_linear(self, symb):
        res_a = list()
        res_b = list()
        deps = self.depends()
        if symb not in deps: return False
        max_pow = 0
        for (k, mn) in self.data:
            if symb in mn.keys():
                if mn[symb] > max_pow: max_pow = mn[symb]

        for (k, mn) in self.data:
            if symb not in mn or mn[symb] == 0:
                nmn = deepcopy(mn)
                res_b.append((k, nmn))
            elif mn[symb] == max_pow:
                nmn = deepcopy(mn)
                del(nmn[symb])
                res_a.append((k, nmn))
            else:
                return False
        return res_a, res_b, max_pow

    def try_quadratic(self, symb):
        res_a = list()
        res_b = list()
        res_c = list()
        deps = self.depends()
        if symb not in deps: return False

        max_pow = 0
        for (k, mn) in self.data:
            if symb in mn.keys():
                if mn[symb] > max_pow: max_pow = mn[symb]
        if max_pow % 2 != 0: return False
        mid_pow = max_pow // 2

        for (k, mn) in self.data:
            if symb not in mn or mn[symb] == 0:
                nmn = deepcopy(mn)
                res_c.append((k, nmn))
            elif mn[symb] == max_pow:
                nmn = deepcopy(mn)
                del(nmn[symb])
                res_a.append((k, nmn))
            elif mn[symb] == mid_pow:
                nmn = deepcopy(mn)
                del(nmn[symb])
                res_b.append((k, nmn))
            else:
                return False
        return res_a, res_b, res_c, max_pow

    def try_poly(self, symb):
        deps = self.depends()
        if symb not in deps or len(deps) != 1: return False

        res = dict()
        for (k, mn) in self.data:
            if symb not in mn or mn[symb] == 0:
                if 0 in res: res[0] += k
                else: res[0] = k
            else:
                if mn[symb] in res: res[mn[symb]] += k
                else: res[mn[symb]] = k

        max_pow = max(res.keys())
        for i in range(max_pow):
            if i not in res: res[i] = 0.

        return res, max_pow


    def get_mults(self):
        n = linear(self)
        div = n.get_common_divisor()
        for k in div.keys():
            v = div[k]
            n.trash_divisor(k, v)
        n.trash_koefficient()

        ret = list()
        for k in div.keys():
            ret.append( linear(k) ** div[k] )

        ret.append(n)

        return ret

    def trash_koefficient(self):
        if len(self.data) == 1:
            (k, mn) = self.data[0]
            k /= abs(k)
            del self.data[0]
            self.data.append((k, mn))


class ratio:
    def __init__(self, obj = False):
        self.denomerator = linear()
        self.numerator = linear()

        if isinstance(obj, bool):
            pass
        elif isinstance(obj, str) or isinstance(obj, float) or isinstance(obj, int) or isinstance(obj, linear):
            self.denomerator = linear(1.)
            self.numerator = linear(obj)
        elif isinstance(obj, ratio):
            self.denomerator = linear(obj.denomerator)
            self.numerator = linear(obj.numerator)

    def to_ratio(self, obj):
        if isinstance(obj, ratio): return obj
        if isinstance(obj, str) or isinstance(obj, float) or isinstance(obj, int) or isinstance(obj, linear):
            return ratio(obj)
        return False

    def __add__(self, other):
        result = ratio()

        other = self.to_ratio(other)
        if not isinstance(other, ratio): return

        result.numerator = self.numerator * other.denomerator + self.denomerator * other.numerator
        result.denomerator = self.denomerator * other.denomerator

        result.simplify()
        return result

    def __neg__(self):
        result = ratio(self)
        result.numerator = -result.numerator
        return result

    def __sub__(self, other):
        other = self.to_ratio(other)
        if not isinstance(other, ratio): return

        other = -other
        return self + other

    def __mul__(self, other):
        other = self.to_ratio(other)
        if not isinstance(other, ratio): return

        result = ratio()
        result.numerator = self.numerator * other.numerator
        result.denomerator = self.denomerator * other.denomerator
        result.simplify()
        return result

    def __pow__(self, step):
        result = self
        if not isinstance(step, int) or step < 1: raise Exception('wrong step')

        for k in range(1, step):
            result *= self

        result.simplify()
        return result

    def __truediv__(self, other):
        other = self.to_ratio(other)
        if not isinstance(other, ratio): return

        result = ratio()
        result.numerator = self.numerator * other.denomerator
        result.denomerator = self.denomerator * other.numerator
        result.simplify()
        return result

    def __eq__(self, other):
        #if self.denomerator == other.denomerator and self.numerator == other.numerator: return True
        #return False
        mul1 = self.denomerator * other.numerator
        mul2 = self.numerator * other.denomerator
        if mul1 == mul2: return True
        else: return False

    def simplify(self):
        cd1 = self.numerator.get_common_divisor()
        cd2 = self.denomerator.get_common_divisor()

        for k in cd1.keys():
            if k in cd2: v = min(cd1[k], cd2[k])
            else: continue

            self.numerator.trash_divisor(k, v)
            self.denomerator.trash_divisor(k, v)


        if self.numerator == self.denomerator:
            self.numerator = linear(1.)
            self.denomerator = linear(1.)
        elif self.numerator == linear(0.):
            self.denomerator = linear(1.)

        if self.denomerator.is_calculatable() and self.denomerator.calculate() != 0.:
            self.numerator *= linear(1/self.denomerator.calculate())
            self.denomerator = linear(1.)

    def __str__(self):
        if self.denomerator.data != [(1.0, dict())]:
            return '(' + str(self.numerator) + ') / (' + str(self.denomerator) + ')'
        else: return '(' + str(self.numerator) + ')'

    def to_rich(self):
        if self.denomerator.data != [(1.0, dict())]:
            return  self.numerator.to_rich() + ' <hr />' + self.denomerator.to_rich()
        else: return self.numerator.to_rich()

    def to_tex(self):
        if self.denomerator.data != [(1.0, dict())]:
            return '\\frac{' + self.numerator.to_tex() + '}{' + self.denomerator.to_tex() + '}'
        else: return self.numerator.to_tex()

    def denominator_is_zero(self):
        if self.denomerator.is_calculatable() and self.denomerator.calculate() == 0.: return True
        else: return False

    def is_calculatable(self):
        if self.numerator.is_calculatable() and self.denomerator.is_calculatable(): return True
        else: return False

    def calculate(self):
        v1 = self.numerator.calculate()
        v2 = self.denomerator.calculate()
        return v1 / v2

    def depends(self):
        ret = self.numerator.depends() + self.denomerator.depends()
        return list(set(ret)) # remove duplicates

    def get_mults(self):
        return self.numerator.get_mults(), self.denomerator.get_mults()

def mult_symbols(sym1, sym2):
    """data == [(a, 1), (b, 2), (c, 1)] """
    res = list()
    for (s1, p1) in sym1:
        found = False
        for (s2, p2) in sym2:
            if s1 == s2:
                res.append((s1, p1+p2))
                found = True
        if not found:
            res.append((s1, p1))
    for (s2, p2) in sym2:
        found = False
        for (s1, p1) in sym1:
            if s1 == s2: found = True
        if not found:
            res.append((s2, p2))
    return res

expr = ratio

if __name__ == "__main__":
    a = linear('a')
    print("a: ", a)
    b = linear(3.)
    print("b(3.): ", b)
    print("a + b: ", a + b)
    print("a - b: ", a - b)
    print("a + b + (a): ", a+ b+ linear('a') - linear(4.0))
    e1 = linear('b')
    e2 = linear('c')
    e3 = e1 * e2
    c = linear(e3)
    print('c: ', c)
    print('c*2: ', c*linear(2.))
    print('c*c: ',c*c)
    print('a*b: ',a*b)
    d = (a+b)*(a-b) + linear(1.)
    print('d: ', d)
    print('d*d: ',d*d)
    print('d*0:', d * linear(0))

    fr_a = ratio(a)
    fr_b = ratio(b)
    print(fr_a)
    print(fr_b)
    print(-fr_a)
    print(-fr_b)
    print(fr_a + fr_b)
    print(-(fr_a + fr_b))
    print(fr_a - fr_b)
    print(fr_a * fr_b)
    print(fr_a / fr_b)
    print((fr_a + fr_b)*(fr_a - fr_b))
    print((fr_a + fr_b)*(fr_a - fr_b)/ ((fr_a + fr_b)*(fr_a - fr_b)))
    print(fr_a + ratio(1.))

    print("a == 'a' ?", a == linear('a'))
    print("a == 'b' ?", a == linear('b'))
    print("3.0 == 'a' ?", linear(3.0) == linear('a'))
    print("b == a ?", a == b)

    fr_c = ratio(3.)
    fr_c *= ratio('x')
    fr_c /= ratio('y')
    fr_d = ratio('x')
    fr_d /= ratio('y')
    fr_d *= linear(3.0)
    print(fr_c - fr_d)

    print(ratio('a') - ratio('b'))


