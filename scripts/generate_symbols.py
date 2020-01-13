#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import xml.etree.ElementTree as ET
import subprocess, os
import re

width_regex = re.compile('PNG image data, ([0-9]+) x [0-9]+')

folders = [
            'arrows',
            'greek_letters',
            'operators',
            'misc_math',
            'misc_text',
            'relations'
          ]

for folder in folders:
    tree = ET.parse('../resources/symbols/' + folder + '.xml')
    root = tree.getroot()

    for theme in [{'name': 'light', 'color': 'black'}, {'name': 'dark', 'color': 'white'}]:
        for child in root:
            attrib = child.attrib

            tex_file = '''\\documentclass[12pt]{article}\n
\\pagestyle{empty}\n
\\usepackage[T1]{fontenc}\n
\\usepackage{xcolor}\n
'''

            try: tex_file += '\\usepackage{' + attrib['package'] + '}\n'
            except KeyError: pass

            tex_file += '\\begin{document}\n'
            tex_file += '\\color{' + theme['color'] + '}\n'
            
            try: is_math = attrib['math']
            except KeyError: is_math = '0'
            try: command = attrib['gencommand']
            except KeyError: command = attrib['command']
            
            if is_math == '1':
                tex_file += '\\ensuremath{' + command + '}\n'
            else:
                tex_file += command + '\n'

            tex_file += '\\end{document}\n'

            # make dvi
            with open('./temp.tex', 'w') as f: f.write(tex_file)
            arguments = ['latex', 'temp.tex']
            process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
            process.kill()

            # make png / svg
            try: os.mkdir('../resources/symbols/' + theme['name'])
            except FileExistsError: pass
            try: os.mkdir('../resources/symbols/' + theme['name'] + '/' + folder)
            except FileExistsError: pass

            arguments = ['dvipng', '-x', '1440', '-bg', 'Transparent', '-T', 'tight', '-z', '6', '-o', '../resources/symbols/' + theme['name'] + '/' + folder + '/' + attrib['file'], 'temp.dvi']
            process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()

            # get image size
            '''arguments = ['file', '../resources/symbols/' + theme['name'] + '/' + folder + '/' + attrib['file']]
            process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
            output, _ = process.communicate()
            output = output.decode('utf8')
            width_match = width_regex.search(output)
            
            process.kill()
            child.set('original_width', width_match.group(1))
            tree.write('../resources/symbols/' + folder + '.xml')'''

            # delete helper files
            os.remove('temp.tex')
            os.remove('temp.log')
            os.remove('temp.aux')
            os.remove('temp.dvi')


