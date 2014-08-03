__author__ = 'ak'

import os
import subprocess
import tempfile
import shutil

if os.name == 'posix':
    tex_path = '/usr/texbin/latex'
    dvipng_path = '/usr/texbin/dvipng'
    dvips_path = '/usr/texbin/dvips'
else:
    tex_path = 'latex.exe '
    dvipng_path = 'dvipng.exe '
    dvips_path = 'dvips.exe '

tex_preamble = '''
\\documentclass[a4paper,12pt]{article}
\\usepackage[margin=2cm, a4paper]{geometry}
\\usepackage{amsmath}
\\usepackage{amsthm}
\\usepackage{amssymb}
\\usepackage{bm}
\\renewcommand{\leq}{\leqslant}
\\renewcommand{\geq}{\geqslant}

\\newcommand\T{\\rule{0pt}{2.6ex}}
\\newcommand\B{\\rule[-1.2ex]{0pt}{0pt}}
\\pagestyle{empty}
\\begin{document}
'''

class tex_image_renderer:
    tex_filename = 'la.tex'
    dvi_filename = 'la.dvi'
    image_name = 'img{}.png'
    image_mask = 'img%d.png'

    def __init__(self):
        self.dir = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(os.path.abspath(self.dir))
        self.tex_file = open(self.tex_filename, 'w')
        self.tex_file.write(tex_preamble)
        os.chdir(cwd)
        self.counter = 0
    def __del__(self):
        shutil.rmtree(self.dir)
    def _put(self, x):
        self.tex_file.write(x + '\\newpage \n')
        self.counter += 1
        return os.path.join(os.path.abspath(self.dir),self.image_name.format(self.counter))
    def put_formula(self, formula):
        return self._put("\\[\n " + formula +"$\n\\] ")
    def put_inline_formula(self, formula):
        return self._put("$" + formula + "$ \n ")
    def put_some(self, some):
        return self._put(some + " \n ")
    def compile_images(self):
        self.put_some("""\\end{document}""")
        self.tex_file.close()
        if self.counter == 0: return
        cwd = os.getcwd()
        os.chdir(os.path.abspath(self.dir))
        subprocess.call((tex_path, '', self.tex_filename))
        #subprocess.call((dvips_path, '-E','-i','-j','-V', self.dvi_filename))
        subprocess.call((dvipng_path, '-q9','-T','tight','-D','300','-z9','-bg','transparent','-o', self.image_mask, self.dvi_filename))
        os.chdir(cwd)


class tex_page_renderer:
    tex_filename = 'la.tex'
    dvi_filename = 'la.pdf'

    def __init__(self):
        self.dir = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(os.path.abspath(self.dir))
        self.tex_file = open(self.tex_filename, 'w')
        self.tex_file.write(tex_preamble)
        os.chdir(cwd)

    def __del__(self):
        shutil.rmtree(self.dir)

    def put_some(self, some):
        self.tex_file.write(some)

    def put_newpage(self):
        self.tex_file.write('\n \\newpage \n')

    def compile(self, result_file_name):
        self.put_some("""\\end{document}""")
        self.tex_file.close()
        cwd = os.getcwd()
        os.chdir(os.path.abspath(self.dir))
        subprocess.call((tex_path, '-output-format=pdf', self.tex_filename))
        os.chdir(cwd)
        shutil.copyfile(os.path.join(os.path.abspath(self.dir), self.dvi_filename), os.path.abspath(result_file_name))
        shutil.copyfile(os.path.join(os.path.abspath(self.dir), self.tex_filename), os.path.abspath(result_file_name + ".tex"))