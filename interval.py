from assumption import assumption

__author__ = 'ak'

from copy import deepcopy
from expression import linear
import math

class interval:
    def __init__(self, _left_value = float('-inf'), _left_strong = True, _right_value = float('inf'), _right_strong = True):
        self.right_strong = _right_strong
        self.right_value = _right_value
        self.left_strong = _left_strong
        self.left_value = _left_value
        if self.right_value < self.left_value:
            self.right_value, self.left_value = self.left_value, self.right_value
            self.right_strong, self.left_strong = self.left_value, self.right_strong

    def is_zero(self):
        if self.right_value == self.left_value and (self.right_strong == True or self.left_strong == True): return True
        return False

    def is_one_point(self):
        if self.right_value == self.left_value and self.right_strong == False and self.left_strong == False: return True
        return False

    def __str__(self):
        if self.is_zero(): return "ø"
        if self.is_one_point(): return '{ ' + str(self.left_value) + ' }'

        ret = ''
        if self.left_strong: ret += '( '
        else: ret += '[ '
        ret += str(self.left_value)
        ret += ', '
        ret += str(self.right_value)
        if self.right_strong: ret += ' )'
        else: ret += ' ]'
        return ret

    def to_tex(self):
        if self.is_zero(): return "ø"
        if self.is_one_point(): return '{ ' + str(self.left_value) + ' }'

        ret = ''
        if self.left_strong: ret += '( '
        else: ret += '[ '
        ret += str(self.left_value)
        ret += ', '
        ret += str(self.right_value)
        if self.right_strong: ret += ' )'
        else: ret += ' ]'
        return ret

    def __mul__(self, i):
        left = self.left_value
        lstrong = self.left_strong
        right = self.right_value
        rstrong = self.right_strong
        if i.left_value > left:
            left = i.left_value
            lstrong = i.left_strong
        elif i.left_value == left and i.left_strong == True:
            lstrong = True
        if i.right_value < right:
            right = i.right_value
            rstrong = i.right_strong
        elif i.right_value == right and i.right_strong == True:
            rstrong = True

        if right < left: return False
        elif right == left and (lstrong != False or rstrong != False): return False
        else: return interval(left, lstrong, right, rstrong)

    def has(self, x):
        if x < self.left_value: return False
        elif x == self.left_value and self.left_strong == True: return False
        if x > self.right_value: return False
        elif x == self.right_value and self.right_strong == True: return False
        return True

    def is_near_or_intersect(self, i):
        if self.left_value > i.right_value or self.right_value < i.left_value: return False
        if self.left_value == i.right_value and self.left_strong == True and i.right_strong == True: return False
        if self.right_value == i.left_value and self.right_strong == True and i.left_strong == True: return False
        else: return True

    def __add__(self, i):
        left = self.left_value
        lstrong = self.left_strong
        right = self.right_value
        rstrong = self.right_strong
        if i.left_value < left:
            left = i.left_value
            lstrong = i.left_strong
        elif i.left_value == left and i.left_strong == False:
            lstrong = False
        if i.right_value > right:
            right = i.right_value
            rstrong = i.right_strong
        elif i.right_value == right and i.right_strong == False:
            rstrong = False

        if right < left: return False
        elif right == left and (lstrong != False or rstrong != False): return False
        else: return interval(left, lstrong, right, rstrong)

    def __eq__(self, other):
        if self.right_strong != other.right_strong: return False
        if self.right_value != other.right_value: return False
        if self.left_strong != other.left_strong: return False
        if self.left_value != other.left_value: return False

    def get_assumptions(self, symbol):
        ret = list()
        if self.right_value != float('inf'):
            if self.right_strong: ret.append( assumption(linear(symbol), '<', linear(self.right_value)) )
            else: ret.append( assumption(linear(symbol), '<=', linear(self.right_value)) )
        if self.left_value != float('-inf'):
            if self.left_strong: ret.append( assumption(linear(symbol), '>', linear(self.left_value)) )
            else: ret.append( assumption(linear(symbol), '>=', linear(self.left_value)) )
        return ret

    def get_interval_by_pow(self, p):
        max_value = self.right_value
        min_value = self.left_value
        max_strong = self.right_strong
        min_strong = self.left_strong
        if p < 0:
            if self.has(0): raise()
            if max_value == float('inf'): max_value = 0
            elif max_value == 0: max_value = float('-inf')
            else: max_value = 1 / max_value
            if min_value == float('-inf'): min_value = 0
            elif min_value == 0: min_value = float('inf')
            else: min_value = 1 / min_value

            if max_value < min_value:
                min_value, max_value = max_value, min_value
                max_strong, min_strong = min_strong, max_strong
            p *= -1

        if p % 2 == 0:
            if min_value < 0:
                if max_value < 0:
                    min_value, max_value = max_value, min_value
                    max_strong, min_strong = min_strong, max_strong
                else:
                    if -min_value > max_value:
                        max_value = -min_value
                        max_strong = min_strong
                    min_value = 0
                    min_strong = False
        return interval(min_value**p, min_strong, max_value**p, max_strong)

    def get_mult_interval(self, i):
        c = list()
        c.append( (self.right_value * i.right_value , self.right_strong | i.right_strong) )
        c.append( (self.right_value * i.left_value , self.right_strong | i.left_strong) )
        c.append( (self.left_value * i.right_value , self.left_strong | i.right_strong) )
        c.append( (self.left_value * i.left_value , self.left_strong | i.left_strong) )
        c = [(x, y) for x, y in c if not math.isnan(x)]
        if len(c) == 0: return interval()
        nleft, nleft_strong = c[0]
        nright, nright_strong = c[0]
        for x, y in c:
            if x < nleft: nleft, nleft_strong = x, y
            elif x == nleft and nleft_strong: nleft_strong = y
            if x > nright: nright, nright_strong = x, y
            elif x == nright and nright_strong: nright_strong = y

        ret = interval(nleft, nleft_strong, nright, nright_strong)
        if self.has(0) or i.has(0):
            ret += interval(0, False, 0, False)
        return ret

    def get_add_interval(self, i):
        if self.is_zero(): return deepcopy(i)
        if i.is_zero(): return deepcopy(self)
        return interval(self.left_value + i.left_value, self.left_strong | i.left_strong,
            self.right_value + i.right_value, self.right_strong | i.right_strong)


    def get_dived_interval(self):
        y0_strong = self.left_strong
        y1_strong = self.right_strong

        if self.left_value == 0:
            if self.right_value == 0: return interval(0, True, 0, True)
            y0 = float('+inf')
            y0_strong = False
        else: y0 = 1 / self.left_value
        if self.right_value == 0:
            y1 = float('-inf')
            y1_strong = False
        else: y1 = 1 / self.right_value

        if self.left_value >= 0 or self.right_value <= 0:
            if y0 > y1:
                y0, y0_strong, y1, y1_strong = y1, y1_strong, y0, y0_strong
            return interval(y0, y0_strong, y1, y1_strong)
        else:
            return intervals(interval(float('-inf'), True, y0, y0_strong)) + interval(y1, y1_strong, float('+inf'), True)

class intervals:
    def __init__(self, i = False):
        self.lims = list()
        if not isinstance(i, interval): i = interval()
        self.lims.append(i)

    def __str__(self):
        if self.is_zero(): return "ø"
        return " + ".join([str(i) for i in self.lims])

    def to_tex(self):
        if self.is_zero(): return "ø"
        return " + ".join([i.to_tex() for i in self.lims])


    def is_zero(self):
        if len(self.lims) == 0: return True
        for l in self.lims:
            if not l.is_zero(): return False
        return True

    def is_one_point(self):
        if len(self.lims) == 0: return False
        has = False
        for l in self.lims:
            if l.is_one_point():
                if has: return False
                else: has = True
            else: return False
        return True

    def __eq__(self, other):
        if len(self.lims) != len(other.lims): return False
        for l1 in self.lims:
            found = False
            for l2 in other.lims:
                if l1 == l2:
                    found = True
                    break
            if not found: return False
        return True

    def _filter(self):
        new_lims = list()
        for i in self.lims:
            if i.is_zero(): continue
            if i.left_value == float('-inf'): i.left_strong = True
            if i.right_value == float('inf'): i.right_strong = True
            if i.left_value > i.right_value:
                i.left_value, i.left_strong, i.right_value, i.right_strong = i.right_value, i.right_strong, i.left_value, i.left_strong
            new_lims.append(i)

        has_intersections = True
        while has_intersections:
            n_lims = list()
            has_intersections = False
            for i in new_lims:
                i_inters = False
                for j_index, j in enumerate(n_lims):
                    if i.is_near_or_intersect(j):
                        has_intersections = True
                        i_inters = True
                        n_lims[j_index] = j + i
                if not i_inters: n_lims.append(i)
            new_lims = n_lims

        self.lims = new_lims

    def __mul__(self, inter):
        n = intervals()
        n.lims = list()
        if isinstance(inter, interval):
            for i in self.lims:
                res = i * inter
                if not isinstance(res, bool): n.lims.append(res)
        elif isinstance(inter, intervals):
            for inter in inter.lims:
                for i in self.lims:
                    res = i * inter
                    if not isinstance(res, bool): n.lims.append(res)
        else: raise()
        n._filter()
        return n

    def __add__(self, inter):
        n = intervals()
        n.lims = deepcopy(self.lims)
        if isinstance(inter, interval):
            n.lims.append(inter)
        elif isinstance(inter, intervals):
            n.lims += deepcopy(inter.lims)
        else: raise()
        n._filter()
        return n

    def get_assumptions(self, symbol):
        ret = list()
        for l in self.lims:
            ret += l.get_assumptions(symbol)
        return ret

    def has(self, x):
        for l in self.lims:
            if l.has(x): return True
        return False

    def get_max_min(self):
        max_value = float('-inf')
        max_strong = True
        min_value = float('inf')
        min_strong = True
        for x in self.lims:
            if x.right_value > max_value:
                max_value = x.right_value
                max_strong = x.right_strong
            if x.left_value < min_value:
                min_value = x.left_value
                min_strong = x.left_strong
        return max_value, max_strong, min_value, min_strong

    def get_intervals_by_pow(self, p):
        ret = intervals(interval(0, True, 0, True))
        for i in self.lims:
            ret += i.get_interval_by_pow(p)
        ret._filter()
        return ret

    def get_mult_intervals(self, o):
        ret = intervals(interval(0, True, 0, True))
        for i in self.lims:
            for a in o.lims:
                ret += i.get_mult_interval(a)
        ret._filter()
        return ret

    def get_add_intervals(self, o):
        ret = intervals(interval(0, True, 0, True))
        for i in self.lims:
            for a in o.lims:
                ret += i.get_add_interval(a)
        ret._filter()
        return ret

    def get_dived_intervals(self):
        ret = intervals(interval(0, True, 0, True))
        for i in self.lims:
            ret += i.get_dived_interval()
        ret._filter()
        return ret

if __name__ == "__main__":
    some = """	a = interval()
    print(a)
    b1 = interval(0, True, 1, True)
    print(b1)
    b2 = interval(0, False, 1, False)
    print(b2)
    b3 = interval(0, False, 1, True)
    print(b3)
    c1 = interval(1, True, 2, True)
    print(c1)
    c2 = interval(1, False, 2, False)
    print(c2)
    c3 = interval(-2, True, -1, True)
    print(c3)
    c4 = interval(-2, False, -1, False)
    print(c4)
    print(a)
    print(a*b1)
    print(a*b2)
    print(a)
    print(b1*b2)
    print(b2*b1)
    print(b1*b3)
    print(b3*b1)
    print(b2*b3)
    print(b3*b2)
    print(a)
    print(b1*c1)
    print(b1*c2)
    print(b1*c3)
    print(b1*c4)
    print(a)
    print(b2*c1)
    print(b2*c2)
    print(b2*c3)
    print(b2*c4)
    print(a)
    print(b3*c1)
    print(b3*c2)
    print(b3*c3)
    print(b3*c4)
    print(a)
    print(a * interval(float('-inf'), True, 0, False))
    print(a * interval(float('-inf'), True, 0, True))
    print(a)
    print(b1 + b2)
    print(b2 + b1)
    print(b1 + b3)
    print(b3 + b1)
    print(b2 + b3)
    print(b3 + b2)

    print("")
    d = intervals()
    print(d)
    print(d * a)
    print(d * b1)
    print(d * b2)
    print((d * b2) * (d * b1) )

    print("")
    f1 = intervals(c1*c2)
    print(f1)
    f2 = intervals(c3*c4)
    print(f2)
    print(f1*f2)
    print(f1+f2)
    f3 = intervals(b2*b3)
    print(f3)
    print(f1 + f2 + f3)
    print(f1 + f2 + f3 + interval(1, False, 1, False))

    print("*"*40)
    print(f1, f1.get_intervals_by_pow(2), f1.get_intervals_by_pow(3), f1.get_intervals_by_pow(4))
    g = intervals(interval(-2, False, -1, False))
    print(g, g.get_intervals_by_pow(2), g.get_intervals_by_pow(3), g.get_intervals_by_pow(4))
    g = intervals(interval(-2, False, 1, False))
    print(g, g.get_intervals_by_pow(2), g.get_intervals_by_pow(3), g.get_intervals_by_pow(4))
    g = intervals(interval(float('-inf'), True, 1, False))
    print(g, g.get_intervals_by_pow(2), g.get_intervals_by_pow(3), g.get_intervals_by_pow(4))
    g = intervals(interval(float('-inf'), True, -1, False))
    print(g, g.get_intervals_by_pow(2), g.get_intervals_by_pow(3), g.get_intervals_by_pow(4))
    g = intervals(interval(float('-inf'), True, float('inf'), True))
    print(g, g.get_intervals_by_pow(2), g.get_intervals_by_pow(3), g.get_intervals_by_pow(4))
    g = intervals(interval(float('-inf'), True, -1, False)) + interval(0.5, True, float('inf'), False)
    print(g, g.get_intervals_by_pow(2), g.get_intervals_by_pow(3), g.get_intervals_by_pow(4))

    print("*"*40)
    g1 = intervals(interval(float('-inf'), True, -3, False)) + interval(-2, True, -1, False)
    g2 = intervals(interval(-2, True, -3, False))
    print(g1, g2, g1.get_mult_intervals(g2))
    g2 = intervals(interval(-2, False, -3, False))
    print(g1, g2, g1.get_mult_intervals(g2))
    g1 = intervals(interval(float('-inf'), True, -3, False)) + interval(-2, False, -1, False)
    g2 = intervals(interval(-2, True, -3, False))
    print(g1, g2, g1.get_mult_intervals(g2))
    g1 = intervals(interval(1, False, 1, False))
    g2 = intervals(interval(-3, True, -2, False))
    print(g1, g2, g1.get_mult_intervals(g2))

    print("*"*40)
    h1 = intervals(interval(-2, False, 0, False))
    h2 = intervals(interval(-3, False, 1, True))
    h3 = intervals(interval(10, True, 15, False))
    h4 = intervals(interval(10, False, 15, False))
    print(h1, h2, h3, h4, h1.get_add_intervals(h2), h1.get_add_intervals(h2).get_add_intervals(h3), h1.get_add_intervals(h2).get_add_intervals(h4))

    print(h1.has(0), h1.has(1), h1.has(-3), h1.has(-1), h1.has(float('-inf')), h2.has(1))

    print(g2, g2.get_intervals_by_pow(-1), g2.get_intervals_by_pow(-2)) """

    print("*"*40)
    j1 = intervals(interval(float('-inf'), True, 0, True))
    j2 = intervals(interval(0, True, float('inf'), True))
    print(j1.get_mult_intervals(j2))

    j1 = intervals(interval(-1000, False, 0, False))
    print(j1.get_dived_intervals())

    j1 = intervals(interval(0, False, 0, False))
    j2 = intervals(interval(0, True, 0, True))
    print(j1.get_mult_intervals(j2))

    j1 = intervals(interval(0, True, 3, True))
    j2 = intervals(interval(-4, True, 0, False))
    print(j1.get_add_intervals(j2))