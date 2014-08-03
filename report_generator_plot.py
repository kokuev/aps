__author__ = 'ak'

import pickle

from sympy import ccode, Symbol, latex

from report_generator_gnuplot import renderer as gnu_rend

result_file_name = 'result/task.pck'
#report_plot_file_name = 'reports/plot%s.png'
report_plot_file_name = 'reports/plot%s.eps'

def process_expr_on_symbols(expr, symbols_used):
    for s in expr.atoms(Symbol):
        if s not in symbols_used:
            symbols_used[s] = (float('-inf'), float('+inf'))

def process_table_on_symbols(table, symbols_used):
    for s in symbols_used:
        for pot in table.pots.pots:
            if s in pot.symbol_intervals:
                max_val, _mas, min_val, _mis = pot.symbol_intervals[s].get_max_min()
                _max_val, _min_val = symbols_used[s]
                if max_val != float('+inf') and max_val > _max_val:
                    _max_val = max_val
                if min_val != float('-inf') and min_val < _min_val:
                    _min_val = min_val
                symbols_used[s] = _max_val, _min_val


def simplex_table_to_assumptions(table, symbols_used):
    common_assumps, new_assumps_by_pot = table.pots.get_common_and_not_assumptions()

    ret = ''

    common_assumpt_text = list()
    for a in common_assumps:
        process_expr_on_symbols(a.exp, symbols_used)
        common_assumpt_text.append('(' + ccode( a.exp) + ' ' + a.sign + ' 0 )')

    pots_assumpt_text = list()

    for pot in new_assumps_by_pot:

        pot_assumpt_text = list()
        for a in pot:
            process_expr_on_symbols(a.exp, symbols_used)
            pot_assumpt_text.append('(' + ccode( a.exp) + ' ' + a.sign + ' 0 )')

        pots_assumpt_text.append( '(' + " && ".join(pot_assumpt_text) + ')' )

    ret = " && ".join(common_assumpt_text)

    if len(pots_assumpt_text) > 0:
        if len(common_assumps): ret += ' && '
        ret += '(' + " || ".join(pots_assumpt_text) + ')'

    process_table_on_symbols(table, symbols_used)
    return ret


def out_table(table, symbols_used):
    t, chs = table
    if not t.solution:
        ret = ''
        for ch in chs:
            ch_t, ch_chs = ch
            ret += " ( %s ) ? ( %s ) : " % (simplex_table_to_assumptions(ch_t, symbols_used), out_table(ch, symbols_used))
        ret += "1/0"
        return ret
    else:
        var, target = t.solution
        process_expr_on_symbols(target, symbols_used)
        return ccode(target)


zone = 0
def out_table_zones(table, symbols_used):
    global zone
    t, chs = table
    if not t.solution:
        ret = ''
        for ch in chs:
            ch_t, ch_chs = ch
            ret += " ( %s ) ? ( %s ) : " % (simplex_table_to_assumptions(ch_t, symbols_used), out_table_zones(ch, symbols_used))
        ret += "1/0"
        return ret
    else:
        var, target = t.solution
        zone += 1
        return str(float(zone))


plot_tpl = """
set border 4095 front linetype -1 linewidth 1.000
set samples 50
set isosamples 50

set xlabel "%s"
set xrange [ %f : %f ] %s nowriteback
set ylabel "%s"
set yrange [ %f : %f ] %s nowriteback
#set yrange [ -2.0 : 10.0000 ]
#set zrange [ -0.250000 : 10.00000 ] noreverse nowriteback

set key off
%s
set style line 100 lt 5 lw 0.5
set pm3d hidden3d 100
%s

J(x, y) = %s
splot J(x, y)
"""


def process_maxmin(s):
    _max, _min = s
    if _max == float('-inf'):
        _max = 10
    if _min == float('+inf'):
        _min = -10
    len = abs(_max - _min)
    _max += len*0.1
    _min -= len*0.1
    return (_max, _min)


def process_reverse(v, max, min):
    if v:
        return ('reverse', min, max)
    else:
        return ( 'noreverse', max, min)

def do_it(j_foo, s0, _s0, s1, _s1, is_swap, is_map, zones_amount):

    s0_max, s0_min = process_maxmin(_s0)
    s1_max, s1_min = process_maxmin(_s1)

    j_foo = j_foo.replace(str(s0), 'x')
    j_foo = j_foo.replace(str(s1), 'y')
    j_foo = j_foo.replace('L', '')

    zone_pl = ''
    is_zone = False
    if zones_amount != None:
        is_zone = True
        zone_pl += "set pal maxcolors 4; set pm3d corners2color c1; unset colorbox;"

    map_pl = 'set pm3d\n'
    if is_map: map_pl += 'set pm3d map\n'

    for (x, y) in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        file_mod = list()
        if is_map: file_mod.append('map')
        if is_zone: file_mod.append('zone')
        if is_swap: file_mod.append('swap')

        if x: file_mod.append('rx')
        if y: file_mod.append('ry')
        s0_rev, s0_max, s0_min = process_reverse(x, s0_max, s0_min)
        s1_rev, s1_max, s1_min = process_reverse(y, s1_max, s1_min)
        gr3d = gnu_rend()
        gr3d.put_some(plot_tpl % (latex(s0), s0_min, s0_max, s0_rev, latex(s1), s1_min, s1_max, s1_rev,
                                 map_pl, zone_pl, j_foo) )
        gr3d.compile( report_plot_file_name % ( (len(file_mod) and "_" or "") + "_".join(file_mod) ) )

def main():
    solution = pickle.load(open(result_file_name, 'rb'))

    symbols_used = dict()
    j_foo = out_table(solution, symbols_used)
    if len(symbols_used) != 2:
        raise "Ololo!"
    s0, _s0 = symbols_used.popitem()
    s1, _s1 = symbols_used.popitem()

    do_it(j_foo, s0, _s0, s1, _s1, False, False, None)
    do_it(j_foo, s1, _s1, s0, _s0, True, False, None)
    do_it(j_foo, s0, _s0, s1, _s1, False, True, None)
    do_it(j_foo, s1, _s1, s0, _s0, True, True, None)

    j_foo = out_table_zones(solution, symbols_used)
    global zone

    do_it(j_foo, s0, _s0, s1, _s1, False, True, zone)
    do_it(j_foo, s1, _s1, s0, _s0, True, True, zone)


if __name__ == "__main__":
    main()