#from expression import linear, expr
from sympy import latex, Symbol, Number

class result:
    possible = 0
    not_possible = 1
    correct = 2

class test_result:
    objects = 0
    not_objects = 1
    part = 2

def test_expr_on_finite(exp):
    for x in exp.atoms(Number):
        if x.is_finite == False:
            return False
    return None

class assumption:

    def __init__(self, exp1, sign, exp2):
        if sign == '>' or sign == '>=':
            self.exp = exp1 - exp2
            self.sign = sign
        elif sign == '<':
            self.exp = exp2 - exp1
            self.sign = '>'
        elif sign == '<=':
            self.exp = exp2 - exp1
            self.sign = '>='
        elif sign == '==':
            self.exp = exp1 - exp2
            self.sign = '=='
        elif sign == '!=':
            self.exp = exp1 - exp2
            self.sign = '!='
        else:
            raise Exception('unknown sign')
        self.exp = self.exp.simplify()


    def __eq__(self, other):
        if self.sign != other.sign: return False
        if self.exp != other.exp: return False
        return True

    def __str__(self):
        return str(self.exp) + self.sign + " 0"

    def to_tex(self):
        sign = ''
        if self.sign == '>' or self.sign == '<':
            sign = self.sign
        elif self.sign == '<=':
            sign = '\\leq'
        elif self.sign == '>=':
            sign = '\\geq'
        elif self.sign == '==':
            sign = '=='
        elif self.sign == '!=':
            sign = '\\ne'
        return latex(self.exp) + sign + "0"

    def depends(self):
        return list(self.exp.atoms(Symbol))

    def test(self):
        if test_expr_on_finite(self.exp) == False: return result.not_possible
        if self.exp.is_number:
            value = self.exp.n()
            if self.sign == '>':
                if value > 0: return result.correct
                else: return result.not_possible
            elif self.sign == '>=':
                if value >= 0: return result.correct
                else: return result.not_possible
            elif self.sign == '==':
                if value == 0: return result.correct
                else: return result.not_possible
            elif self.sign == '!=':
                if value != 0: return result.correct
                else: return result.not_possible
            else:
                raise Exception('unknown assumption')
        return result.possible

if __name__ == "__main__":
    from sympy.parsing.sympy_parser import parse_expr

    a = parse_expr('3*a')
    b = parse_expr('5*a - 2*a - 3')
    c = assumption(b, '>', a)
    print(c.test())