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

import os
import os.path
import shutil
import subprocess

import setzer.document.build_system.builder.builder_build as builder_build
from setzer.app.service_locator import ServiceLocator


class BuilderBuildBibTeX(builder_build.BuilderBuild):

    def __init__(self):
        builder_build.BuilderBuild.__init__(self)

        self.bibtex_log_item_regex = ServiceLocator.get_regex_object(r'Warning--(.*)\n--line ([0-9]+) of file (.*)|I couldn' + "'" + r't open style file (.*)\n---line ([0-9]+) of file (.*)')

    def run(self, query):
        tex_filename = query.build_data['tmp_tex_filename']

        arguments = ['bibtex']
        arguments.append(tex_filename.rsplit('/', 1)[1][:-3] + 'aux')
        custom_env = os.environ.copy()
        custom_env['BIBINPUTS'] = os.path.dirname(query.tex_filename) + ':' + os.path.dirname(tex_filename)
        try:
            self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(tex_filename), env=custom_env)
        except FileNotFoundError:
            self.move_build_files(query, tex_filename)
            self.throw_build_error(query, 'interpreter_not_working', 'bibtex missing')
            return
        self.process.wait()

        self.parse_bibtex_log(query, tex_filename[:-3] + 'blg')

        query.jobs.insert(0, 'build_latex')

    def parse_bibtex_log(self, query, log_filename):
        try: file = open(log_filename, 'rb')
        except FileNotFoundError as e: pass
        else:
            text = file.read().decode('utf-8', errors='ignore')

            query.bibtex_log_messages = list()
            file_numbers = dict()
            for item in self.bibtex_log_item_regex.finditer(text):
                line = item.group(0)

                if line.startswith('I couldn\'t open style file'):
                    query.error_count += 1
                    text = 'I couldn\'t open style file ' + item.group(4) + '.bst'
                    line_number = int(item.group(5).strip())
                    query.bibtex_log_messages.append(('Error', None, query.tex_filename, 0, -1, text))
                elif line.startswith('Warning--'):
                    filename = os.path.basename(log_filename[:-3] + 'bib')
                    try:
                        file_no = file_numbers[filename]
                    except KeyError:
                        file_no = 10000 + len(file_numbers)
                        file_numbers[filename] = file_no
                    text = item.group(1)
                    line_number = int(item.group(2).strip())
                    query.bibtex_log_messages.append(('Warning', None, filename, file_no, line_number, text))


