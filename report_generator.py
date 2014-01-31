__author__ = 'ak'

import pickle
from report_generator_tex import tex_page_renderer, tex_image_renderer
from report_generator_dot import dot_renderer
from report_generator_to_tex import simplex_table_to_tex_full, simplex_table_to_tex_table_only, simplex_table_to_tex_assumptions, simplex_table_to_tex_solution_good

result_file_name = 'result/task_2x2.pck'
report_graph_file_name = 'reports/task.png'
report_full_file_name = 'reports/task.pdf'


def add_node(tr, dr, i, pid, table):
    (t, chs) = table
    table_img_path = tr.put_some(simplex_table_to_tex_table_only(t))
    assumps = simplex_table_to_tex_assumptions(t)
    c_img_path = tr.put_some(assumps)
    np = list()

    """c, pp = simplex_table_to_tex_assumptions(t)
    c_img_path = ''
    if len(c) > 0: c_img_path = tr.put_some(c)
    np = list()
    for p in pp:
        p_img_path = ''
        if len(p) > 0: p_img_path = tr.put_some(p)
        np.append(p_img_path)"""

    if not t.solution:
        dr.add_node(i, pid, table_img_path, c_img_path, np)
    else:
        solution_img_path = tr.put_some(simplex_table_to_tex_solution_good(t))
        dr.add_node_solution(i, pid, table_img_path, solution_img_path, c_img_path, np)
    _i = i + 1
    for ch in chs:
        _i = add_node(tr, dr, _i, i, ch)
    return _i


def add_nodes(tr, dr, solution):
    (t, chs) = solution
    img_path = tr.put_some(simplex_table_to_tex_table_only(t))
    dr.add_node_lonely(0, img_path)
    i = 1
    for ch in chs:
        i = add_node(tr, dr, i, 0, ch)


def full_add_node(tr, table):
    (t, chs) = table
    tr.put_some(simplex_table_to_tex_full(t))
    tr.put_newpage()
    for ch in chs:
        full_add_node(tr, ch)


def full_add_nodes(tr, solution):
    (t, chs) = solution
    tr.put_some(simplex_table_to_tex_full(t))
    tr.put_newpage()
    for ch in chs:
        full_add_node(tr, ch)


def main():
    solution = pickle.load(open(result_file_name, 'rb'))
    #tr = tex_page_renderer()
    #full_add_nodes(tr, solution)
    #tr.compile(report_full_file_name)

    tr = tex_image_renderer()
    dr = dot_renderer()
    add_nodes(tr, dr, solution)
    tr.compile_images()
    dr.compile(report_graph_file_name)


if __name__ == "__main__":
    main()
