__author__ = 'ak'
from sympy import latex


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

def simplex_table_to_tex_solution_only(table):
    solution = ''
    var, target = table.solution
    for i in range(table.amount_of_vars):
        solution += "$x_{" + "{0:<2}".format(i) + "} = " + latex(var[i]) + '$\\\\'
    solution += '$\Psi = ' + latex(target) + '$'
    return solution

def simplex_table_to_tex_pots_full(table):
    ret = ''
    if table.pots.is_valid():
        ret += 'pots: \\\\'
        for i, pot in enumerate(table.pots.pots):
            ret += 'pot \#' + str(i) + ':' + '\\\\'
            for s in pot.symbol_intervals:
                ret += 'symbol $' + latex(s) + '$ : $' + pot.symbol_intervals[s].to_tex() + "$ \\\\"
            for s in pot.assumptions:
                ret += "$" + s.to_tex() + "$ \\\\"
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