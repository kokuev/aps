__author__ = 'ak'

import os
import subprocess
import tempfile
import shutil

gnuplot_path = '/opt/local/bin/gnuplot'

#gnu_pre = """set terminal pngcairo  transparent enhanced font "Helvetica,12" fontscale 1.0 size 1000, 700
#set output 'la.png'"""

gnu_pre = """set terminal epscairo enhanced color font "STIX,12" fontscale 0.45
set output 'la.eps'
"""

class renderer:
    gnu_filename = 'la.gnuplot'
    #png_filename = 'la.png'
    png_filename = 'la.eps'

    def __init__(self):
        self.dir = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(os.path.abspath(self.dir))
        self.gnu_file = open(self.gnu_filename, 'w')
        self.put_some(gnu_pre)
        os.chdir(cwd)

    def __del__(self):
        shutil.rmtree(self.dir)

    def put_some(self, some):
        self.gnu_file.write(some)

    def compile(self, result_file_name):
        self.gnu_file.close()
        cwd = os.getcwd()
        os.chdir(os.path.abspath(self.dir))
        ncwd = os.getcwd()
        subprocess.call((gnuplot_path, '<', './' +  self.gnu_filename))
        os.chdir(cwd)
        shutil.copyfile(os.path.join(os.path.abspath(self.dir), self.png_filename), os.path.abspath(result_file_name))
        shutil.copyfile(os.path.join(os.path.abspath(self.dir), self.gnu_filename), os.path.abspath(result_file_name + ".gnuplot"))