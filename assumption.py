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

        """if self.exp.denominator_is_zero(): return result.not_possible
        if self.exp.is_calculatable():
            value = self.exp.calculate()
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
        else: return result.possible"""

    """def isobjects(self, assumpt):
        if self.exp == assumpt.exp:
            if self.sign == assumpt.sign: return test_result.not_objects
            if (self.sign, assumpt.sign) == ('>', '>=') or (self.sign, assumpt.sign) == ('>=', '>'): return test_result.not_objects
            return test_result.objects
        elif self.exp == -assumpt.exp:
            if (self.sign, assumpt.sign) == ('>=', '>='): return test_result.not_objects
            if (self.sign, assumpt.sign) == ('>', '>=') or (self.sign, assumpt.sign) == ('>=', '>'): return test_result.objects
            if self.sign == assumpt.sign: return test_result.objects
            return test_result.not_objects

        return test_result.not_objects

    def is_objects(self, assumpt):
        signs = (self.sign, assumpt.sign)
        if self.exp == assumpt.exp:
            if signs == ('>', '==') or signs == ('==', '>'): return test_result.objects
            if signs == ('==', '!=') or signs == ('!=', '=='): return test_result.objects
            return test_result.not_objects
        elif self.exp == -assumpt.exp:
            if signs == ('>', '>'): return test_result.objects
            if signs == ('>', '>=') or signs == ('>=', '>'): return test_result.objects
            if signs == ('>', '==') or signs == ('==', '>'): return test_result.objects
            if signs == ('==', '!=') or signs == ('!=', '=='): return test_result.objects
            return test_result.not_objects
        return test_result.not_objects"""

if __name__ == "__main__":
    from sympy.parsing.sympy_parser import parse_expr
    #a = linear('a')
    #b = linear(2.)*a*a + linear(-5.)*a + linear(3)
    #_try_(b)
    #b = linear(4.)*a*a + linear(4.)*a + linear(1)
    #_try_(b)
    #b = linear(4.)*a*a + linear(1.)*a + linear(4)
    #_try_(b)

    #b = linear(-2.)*a*a + linear(5.)*a + linear(-3)
    #_try_(b)
    #b = linear(-4.)*a*a + linear(-4.)*a + linear(-1)
    #_try_(b)
    #b = linear(-4.)*a*a + linear(-1.)*a + linear(-4)
    #_try_(b)
    #a = assumption( (expr(-20)-expr(30)*expr('a')+expr(10.)*expr('b'))/(expr(4)-expr(2)*expr('a')+expr(-6)*expr('a')*expr('a')), '>=', expr(0))
    #print(a)
    a = parse_expr('3*a')
    b = parse_expr('5*a - 2*a - 3')
    c = assumption(b, '>', a)
    print(c.test())