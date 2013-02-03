import yaml
from assumption import assumption
import simplex
from expression import expr
import pickle

def get_solution(table, ttl):
    if ttl == 0: return table, list()
    next_tables = list()
    for x in table.get_next_tables():
        next_tables.append(get_solution(x, ttl - 1))
    if len(next_tables) == 0:
        table.make_solution()
    return table, next_tables

class simplex_task:
    def calculate(self):
        self.solution = get_solution(self.root_table, 4)

    def check(self, limits, free, target_free, target, basis, assumptions):
        # TODO: some checks =)
        return True

    def set(self, limits, free, target_free, target, basis, assumptions):

        er = self.check(limits, free, target_free, target, basis, assumptions)
        if not (isinstance(er, bool) and er == True):
            return er

        self.root_table = simplex.simplex_table()
        self.root_table.limits = limits
        self.root_table.free = free
        self.root_table.target_free = target_free
        self.root_table.target = target
        self.root_table.basis = basis
        self.root_table.amount_of_vars = len(target)
        self.root_table.amount_of_equations = len(free)
        for i in free:
            assumptions.append(assumption(i, '>=', expr(.0)))
        res, pot = self.root_table.test_and_add_assumptions(assumptions)
        self.root_table.pots = pot

    def set_from_yaml(self, filename):
        try:
            cfg = yaml.load(open(filename))
        except:
            raise 'cannot load or parse: ' + filename

        if 'matrix' not in cfg:
            raise('no matrix in file: ' + filename)

        limits = []
        for row in cfg['matrix']:
            temp = []
            for column in row:
                temp.append(expr(column))
            limits.append(temp)

        if 'free' not in cfg:
            raise('no free in file: ' + filename)

        free = []
        for e in cfg['free']:
            free.append(expr(e))

        if 'target' not in cfg or len(cfg['target']) < 2:
            raise('no valid target in file: ' + filename)

        target_free = expr(cfg['target'][0])

        target = []
        for e in cfg['target'][1:]:
            target.append(expr(e))

        if 'basis' not in cfg:
            raise('no basis in file: ' + filename)

        basis = cfg['basis']

        assumptions = []
        if 'assumptions' in cfg:
            for assum in cfg['assumptions']:
                a, b, c = assum
                assumptions.append(assumption(expr(a), b, expr(c)))

        self.set(limits, free, target_free, target, basis, assumptions)

    def save_solution(self, filename):
        f = open(filename, 'wb')
        pickle.dump(self.solution, f)
        f.close()