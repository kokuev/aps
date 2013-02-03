__author__ = 'ak'

from theorypots import theorypots
from copy import deepcopy
from expression import expr
from assumption import result, assumption

def _filter_possible(assumptions):
    only_possible = list()
    for a in assumptions:
        res = a.test()
        if res == result.not_possible: return result.not_possible, list()
        elif res == result.possible: only_possible.append(a)

    if len(only_possible) == 0: return result.correct, list()
    return result.possible, only_possible

class simplex_table:
    def __init__(self):
        self.amount_of_vars = 0
        self.amount_of_equations = 0
        self.basis = []
        self.limits = []
        self.free = []
        self.target = []
        self.target_free = 0
        self.path = []
        self.pots = theorypots()

        self.solution = False

    def make_solution(self):
        var = list()
        for i in range(self.amount_of_vars):
            var.append(expr(.0))

        for i, z in enumerate(self.basis):
            var[z] = self.free[i]

        self.solution = (var, self.target_free)

    def check(self):
        if len(self.basis) > self.amount_of_equations: return 1
        return 0

    def number(self):
        if len(self.path) == 0:
            number = ' initial'
            out_basis, in_basis = -1, -1
        else:
            number = ""
            for (i, bi, j) in self.path:
                if number: number = number + "." + str(i)
                else: number = str(i)
            out_basis, out_basis_,in_basis = self.path[-1]
        return number

    def test_assumtions(self, assumptions):
        (res, assumps) = _filter_possible(assumptions)
        if res == result.possible:
            t = deepcopy(self.pots)
            res = t.add_assumptions(assumps)
            if not res: return result.not_possible
            return result.possible
        return res

    def test_and_add_assumptions(self, assumptions):
        (res, assumps) = _filter_possible(assumptions)
        if res == result.correct:
            return result.correct, deepcopy(self.pots)
        elif res == result.possible:
            t = deepcopy(self.pots)
            res = t.add_assumptions(assumps)
            if not res: return result.not_possible, None
            return result.possible, t
        else: return result.not_possible, None

    def test_and_add_or_assumptions(self, orassumptions):
        neworassumptions = list()
        had_correct = False
        for assumpts in orassumptions:
            (res, assumps) = _filter_possible(assumpts)
            if res == result.correct:
                had_correct = True
                continue
            elif res == result.not_possible:
                continue
            neworassumptions.append(assumps)

        if len(neworassumptions) == 0:
            if had_correct: return result.correct, deepcopy(self.pots), None
            else: return result.not_possible, None, None

        orass = deepcopy(neworassumptions)
        t = deepcopy(self.pots)
        res = t.add_or_assumptions(neworassumptions)
        if not res: return result.not_possible, None, None
        return result.possible, t, orass

    def get_next_table(self, i, j, pot):
        next = simplex_table()

        next.amount_of_vars = self.amount_of_vars
        next.amount_of_equations = self.amount_of_equations
        next.basis = self.basis[:i] + [j,] + self.basis[i+1:]

        next.free = self.free[:]
        next.limits = deepcopy(self.limits)

        for q in range(next.amount_of_vars):
            if q == j: continue
            next.limits[i][q] /= next.limits[i][j]

        next.free[i] /= next.limits[i][j]
        next.limits[i][j] = expr(1.)

        for w in range(next.amount_of_equations):
            if w == i: continue
            m = next.limits[w][j]
            for q in range(next.amount_of_vars):
                if q == j: continue
                next.limits[w][q] -= ( next.limits[i][q] * m)
            next.free[w] -= (next.free[i] * m)
            next.limits[w][j] = expr(0.)

        next.target = self.target[:]
        next.target_free = self.target_free

        m = next.target[j]
        for q in range(next.amount_of_vars):
            if q == j: continue
            next.target[q] -= ( next.limits[i][q] * m)
        next.target_free -= ( next.free[i] *m)
        next.target[j] = expr(0.)

        next.pots = pot

        next.path = self.path + [(i,self.basis[i],j)]

        return next

    def prepare_or_assumptions(self, i, j):
        alternate1 = list()
        alternate2 = list()
        for e in range(self.amount_of_equations):
            if i == e: continue
            alternate1.append(
                [ assumption(self.limits[e][j], '>', expr(0.)),
                  assumption(self.free[i] / self.limits[i][j] ,'<=', self.free[e] / self.limits[e][j]) ])

            alternate2.append(
                [ assumption(self.limits[e][j], '<=', expr(0.)) ])

        or_assumps = list()
        size = len(alternate1)
        s = "{0:0>" + str(size) + "b}"

        for i in range(0, 2**size):
            ret = list(s.format(i))
            current = list()
            for i, r in enumerate(ret):
                if r == '0': current += deepcopy(alternate1[i])
                else: current += deepcopy(alternate2[i])

            or_assumps.append(current)

        return or_assumps

    def get_next_tables_by_row(self, j, assumps):
        for i in range(self.amount_of_equations):
            if j in self.basis: continue
            assumps2 = list()
            assumps2.append(assumption(self.limits[i][j], '>', expr(0.)))

            or_assumps = self.prepare_or_assumptions(i, j)

            total_assumps = list()
            for a in or_assumps:
                total_assumps.append(assumps + assumps2 + a)

            res, pot, orass = self.test_and_add_or_assumptions(total_assumps)
            if res == result.not_possible: continue
            ret = self.get_next_table(i, j, pot)
            ret.debug_assumps = orass
            yield ret

    def get_next_tables(self):
        global_assumps = list()
        has_doubts = False

        for (j, targ) in enumerate(self.target):
            assumpt = assumption(targ, '<', expr(0.))
            res = self.test_assumtions([assumpt, ])
            if res == result.not_possible: continue
            elif res == result.correct:
                global_assumps.append(assumpt)
                for table in self.get_next_tables_by_row(j, deepcopy(global_assumps)):
                    yield table
                return
            else:
                has_doubts = True
                assumps = deepcopy(global_assumps)
                assumps.append(assumpt)
                for table in self.get_next_tables_by_row(j, assumps):
                    yield table
                global_assumps.append(assumption(targ, '>=', expr(0.)))

        if has_doubts:
            next = simplex_table()
            next.amount_of_vars = self.amount_of_vars
            next.amount_of_equations = self.amount_of_equations
            next.basis = self.basis[:]
            next.free = self.free[:]
            next.limits = deepcopy(self.limits)
            next.target = self.target[:]
            next.target_free = self.target_free

            res, pot = self.test_and_add_assumptions(global_assumps)
            if res != result.not_possible:
                next.pots = pot
                next.path = self.path + [(-1,-1,-1)]
                yield next