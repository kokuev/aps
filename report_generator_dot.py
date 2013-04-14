__author__ = 'ak'

import os
import subprocess
import tempfile
import shutil

dot_path = '/opt/local/bin/dot'

dot_one_node_lonely = """n{} [label=<<table border="0"><tr border="0"><td border="0"><img src="{}"/></td></tr></table>>];\n"""
dot_one_node = """n{} [label=<<table border="0"><tr border="0"><td border="0"><img src="{}"/></td></tr></table>>]; n{} -> n{} {};\n"""
dot_one_node_solution = """n{} [label=<<table border="0"><tr border="0"><td border="0"><img scale="true" src="{}"/></td></tr><tr border="0"><td border="0" height="20"></td></tr><tr border="0"><td border="0" align="left"><img src="{}"/></td></tr></table>>]; n{} -> n{} {};\n"""
dot_pre = """digraph solution {
node [shape=box];
"""
dot_post = """overlap=scale
landscape=true
}"""

class dot_renderer:
    dot_filename = 'la.dot'
    result_filename = 'la.png'

    def __init__(self):
        self.dir = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(os.path.abspath(os.path.dirname(self.dir)))
        self.dot_file = open(self.dot_filename, 'w')
        self.dot_file.write(dot_pre)
        os.chdir(cwd)

    def __del__(self):
        os.removedirs(self.dir)

    def add_node_lonely(self, i, tableimgpath):
        self.dot_file.write(dot_one_node_lonely.format(i, tableimgpath))

    def _add_node(self, i, pid, tableimgpath, c_img_path, np):
        arc = ''
        has_one = False
        tds = ''
        for p in np:
            if len(p) > 0: has_one = True
            tds += '<td border="0" valign="top"><img src="' + p + '"/></td>'
        if not has_one:
            arc = '[label=<<table border="0"><tr border="0"><td border="0">'
            if len(c_img_path) > 0: arc += '<img src="'+c_img_path+'"/>'
            arc += '</td></tr></table>>]'
        else:
            arc = '[label=<<table border="0"><tr border="0"><td border="0" colspan="'+str(len(np))+'">'
            if len(c_img_path) > 0: arc += '<img src="'+c_img_path+'"/>'
            arc += '</td></tr><tr border="0"><td border="0" height="20"></td></tr>'
            arc += '<tr border="0">' + tds + '</tr></table>>]'
        return arc

    def add_node(self, i, pid, tableimgpath,c_img_path, np):
        arc = self._add_node(i, pid, tableimgpath, c_img_path, np)
        self.dot_file.write(dot_one_node.format(i, tableimgpath, pid, i, arc))

    def add_node_solution(self, i, pid, tableimgpath, solutionimagepath, c_img_path, np):
        arc = self._add_node(i, pid, tableimgpath, c_img_path, np)
        self.dot_file.write(dot_one_node_solution.format(i, tableimgpath, solutionimagepath, pid, i, arc))

    def compile(self, result_file_name):
        self.dot_file.write(dot_post)
        self.dot_file.close()
        cwd = os.getcwd()
        os.chdir(os.path.abspath(os.path.dirname(self.dir)))
        subprocess.call((dot_path, '-Tpng','-o', self.result_filename, self.dot_filename))
        os.chdir(cwd)
        shutil.copyfile(os.path.join(os.path.dirname(self.dir), self.result_filename), os.path.abspath(result_file_name))
        #subprocess.call((dot_path, '-Teps','-o', self.result_filename, self.dot_filename))