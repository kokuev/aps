__author__ = 'ak'
from sympy import latex, count_ops
from sympy.polys.polyfuncs import horner


def simplex_table_to_tex_table_only(table):
    ret = """\\begin{tabular}{|c|"""
    ret += ("c|"*(table.amount_of_vars + 1))
    ret += "} \\hline"

    ret += " & \\T \\B $ "
    for j in range(table.amount_of_vars):
        ret += "$&$"
        ret += "x_{"+"{0:<2}".format(j) +"}"
    ret += "$\\\\ \\hline "

    for i in range(table.amount_of_equations):
        ret += "$x_{" + "{0:<2}".format(table.basis[i]) + "}$"
        ret += "& \\T \\B $ "
        ret += latex(table.free[i])
        for j in range(table.amount_of_vars):
            ret += "$&$"
            ret += latex(table.limits[i][j])
        ret += "$\\\\ \\hline "

    ret += "$\Psi$ & $"
    ret += latex(table.target_free)
    for j in range(table.amount_of_vars):
        ret += "$&\\T \\B$"
        ret += latex(table.target[j])
    ret += "$\\\\ \\hline "

    ret += """\\end{tabular}"""
    return ret

def simplex_table_to_tex_assumptions(table):
    if not table.pots.is_valid(): return ('', [])
    assumps_by_pot = list()
    all_assumps = list()
    for pot in table.pots.pots:
        assumps = list()
        for s in pot.new_symbol_intervals:
            assumps += pot.new_symbol_intervals[s].get_assumptions(s)
        assumps += pot.new_assumptions
        assumps_by_pot.append(assumps)
        all_assumps += assumps

    n = len(assumps_by_pot)
    common_assumps = list()
    while len(all_assumps) > 0:
        current_assumpt = all_assumps[0]
        new_all_assumps = list()
        i = 0
        for assumpt in all_assumps:
            if assumpt == current_assumpt:
                i += 1
            else:
                new_all_assumps.append(assumpt)
        all_assumps = new_all_assumps
        if i == n:
            common_assumps.append(current_assumpt)

    new_assumps_by_pot = list()
    for pot in assumps_by_pot:
        new_pot = list()
        for a in pot:
            common = False
            for ca in common_assumps:
                if a == ca:
                    common = True
                    break
            if not common:
                new_pot.append(a)

        if len(new_pot) == 0: continue

        bad = False
        for pot in new_assumps_by_pot:
            diff = False
            for a1 in new_pot:
                found = False
                for a2 in pot:
                    if a1 == a2:
                        found = True
                        break
                if not found:
                    diff = True
                    break
            for a1 in pot:
                found = False
                for a2 in new_pot:
                    if a1 == a2:
                        found = True
                        break
                if not found:
                    diff = True
                    break
            if not diff:
                bad = True
                break

        if not bad:
            new_assumps_by_pot.append(new_pot)

    has_curly = True
    if len(common_assumps) == 0: has_curly = False
    if len(common_assumps) == 1 and len(new_assumps_by_pot) == 0: has_curly = False

    ret = '$$'
    if has_curly :# and len(new_assumps_by_pot) != 0: #or len(new_assumps_by_pot) > 0:
        ret += '\\left\\{ \\begin{array}{l}'
    for a in common_assumps:
        ret += a.to_tex() + '\\\\'
        #ret += a.to_tex() + ' \\mbox{\ ' + str(a.exp.count_ops(visual=True)) + '} \\\\'
    #ret += '\\mbox{'+ str(count_ops([ x.exp for x in common_assumps ], visual=True) ) + ' ' + str(len(common_assumps)) +'*CMP '+ '} \\\\'

    total_cmp = 0
    if len(new_assumps_by_pot) > 0:
        ret += '\\left[ \\begin{array}{l}'
        for pot in new_assumps_by_pot:
            if len(pot) > 1:
                ret += '\\left\\{ \\begin{array}{l}'
            for a in pot:
                ret += a.to_tex() + ' \\\\'
                #ret += a.to_tex() + '\\mbox{\ ' + str(a.exp.count_ops(visual=True)) + '} \\\\'
                total_cmp += 1
            if len(pot) > 1:
                ret += '\\end{array} \\right. \\\\'
        ret += '\\end{array} \\right.'

    #ret += '\\\\ \\mbox{'+ str(count_ops([ x.exp for x in common_assumps ] + [ a.exp for pot in new_assumps_by_pot for a in pot], visual=True) ) + ' ' + str(len(common_assumps) + total_cmp) +'*CMP '+ '} \\\\'

    if has_curly:
        ret += '\\end{array} \\right.'

    ret += '$$'

    return ret

def simplex_table_to_tex_solution_good(self):
    solution = '\\begin{eqnarray*}'
    var, target = self.solution
    for i in range(self.amount_of_vars):
        solution += "x_{" + "{0:<2}".format(i) + "} &=& " + latex(var[i]) + ' \\\\'
        #solution += "x_{" + "{0:<2}".format(i) + "} &=& " + latex(var[i]) + '\\mbox{' + str(horner(var[i]).count_ops(visual=True))  +'} \\\\'
    solution += '\Psi &=& ' + latex(target)
    #solution += '\Psi &=& ' + latex(target) + '\\mbox{' + str(horner(target).count_ops(visual=True))  +'}'
    return solution + '\\end{eqnarray*}'

def simplex_table_to_tex_solution_only(table):
    solution = ''
    var, target = table.solution
    for i in range(table.amount_of_vars):
        solution += "$x_{" + "{0:<2}".format(i) + "} = " + latex(var[i]) + '$\\\\'
    solution += '$\Psi = ' + latex(target) + '$'
    return solution

"""
def simplex_table_to_tex_pots_symbol_assumptions(pot):
    ret = ''
    sv = pot.symbol_variants.variants
    if len(sv) == 0: return ret
    for i, variant in enumerate(sv):
        ret += 'symbol variant \#' + str(i) + ':' + '\\\\'
        for assumption in variant.assumptions:
            ret += "$" + assumption.to_tex() + "$ \\\\"
        for symbol in variant.symbol_assumptions:
            for sign in variant.symbol_assumptions[symbol]:
                for assumption in variant.symbol_assumptions[symbol][sign]:
                    ret += "$" + latex(symbol) + sign + latex(assumption) + "$ \\\\"
    return ret
"""

def simplex_table_to_tex_pots_full(table):
    ret = ''
    if table.pots.is_valid():
        ret += 'pots: \\\\'
        for i, pot in enumerate(table.pots.pots):
            ret += 'pot \#' + str(i) + ':' + '\\\\'
            ret += 'new:\\\\'
            for s in pot.new_symbol_intervals:
                ret += 'symbol $' + latex(s) + '$ : $' + pot.symbol_intervals[s].to_tex() + "$ \\\\"
            for s in pot.new_assumptions:
                ret += "$" + s.to_tex() + "$ \\\\"
            ret += 'all:\\\\'
            for s in pot.symbol_intervals:
                ret += 'symbol $' + latex(s) + '$ : $' + pot.symbol_intervals[s].to_tex() + "$ \\\\"
            for s in pot.assumptions:
                ret += "$" + s.to_tex() + "$ \\\\"
            #ret += 'symbols:\\\\'
            #ret += simplex_table_to_tex_pots_symbol_assumptions(pot)
    return ret

def simplex_table_to_tex_full(table):
    if len(table.path) == 0:
        number = ' initial'
        out_basis, in_basis = -1, -1
    else:
        number = ""
        for (i, bi, j) in table.path:
            if number: number = number + "." + str(i)
            else: number = str(i)
        out_basis, out_basis_,in_basis = table.path[-1]

    header = '\\begin{flushleft} \\large Table \#'+number + '\\\\'
    if out_basis != -1 and in_basis != -1:
        header += ' Moving out basis: $x_{' + str(out_basis_) + '}$ from line: ' + str(out_basis) + '\\\\ Moving to basis: $x_{' + str(in_basis) + '}$'
        #header += 'Basis: ' + str(self.basis)
    header += '\\end{flushleft}'
    header += """\\flushleft """

    tbl = simplex_table_to_tex_table_only(table) + "\\\\\\vspace{0.2cm} """
    formulas = ''
    if table.pots.is_valid(): formulas = simplex_table_to_tex_pots_full(table)
    solution = ''
    if table.solution: solution = 'Solution: \\\\' + simplex_table_to_tex_solution_only(table)
    return  header + formulas + '\\vspace{0.2cm}' + tbl + solution