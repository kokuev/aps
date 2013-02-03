from expression import linear, expr

class result:
    possible = 0
    not_possible = 1
    correct = 2

class test_result:
    objects = 0
    not_objects = 1
    part = 2

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
        elif sign == '==':
            sign = '=='
        elif sign == '!=':
            sign = '!='
        return self.exp.to_tex() + sign + "0"

    def depends(self):
        return self.exp.depends()

    def test(self):
        if self.exp.denominator_is_zero(): return result.not_possible
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
        else: return result.possible

    def isobjects(self, assumpt):
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
        return test_result.not_objects

    def get_identities(self):
        variations = list()

        num_mults = list()
        denom_mults = list()
        (num, denom) = self.exp.get_mults()

        sign = 1
        if not self.exp.numerator.is_calculatable():
            for m in num:
                if not m.is_calculatable():
                    num_mults.append(m)
                elif m.calculate() < 0: sign *= -1
        elif self.exp.numerator.calculate() < 0: sign *= -1

        if not self.exp.denomerator.is_calculatable():
            for m in denom:
                if not m.is_calculatable():
                    denom_mults.append(m)
                elif m.calculate() < 0: sign *= -1
        elif self.exp.denomerator.calculate() < 0: sign *= -1

        s = len(num_mults) + len(denom_mults)
        if s == 0: return variations

        if sign > 0: all_signs = get_signs(s, 0)
        else: all_signs = get_signs(s, 1)

        if self.sign == '>': strong_sign = True
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

def get_signs(size, sign):
    s = "{0:0>" + str(size) + "b}"
    for i in range(0, 2**size):
        ret = list(s.format(i).replace('1', '<').replace('0','>'))
        if (ret.count('<') % 2) == sign: yield ret


if __name__ == "__main__":
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
    a = assumption( (expr(-20)-expr(30)*expr('a')+expr(10.)*expr('b'))/(expr(4)-expr(2)*expr('a')+expr(-6)*expr('a')*expr('a')), '>=', expr(0))
    print(a)
    for ident in a.get_identities():
        for a in ident:
            print(a)
