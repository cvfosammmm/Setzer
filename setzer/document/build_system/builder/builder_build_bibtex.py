#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017-present Robert Griesel
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
from operator import itemgetter

import setzer.document.build_system.builder.builder_build as builder_build
from setzer.app.service_locator import ServiceLocator


class BuilderBuildBibTeX(builder_build.BuilderBuild):

    def __init__(self):
        builder_build.BuilderBuild.__init__(self)

        self.bibtex_log_item_regex = ServiceLocator.get_regex_object(r'Warning--(.*)\n--line ([0-9]+) of file (.*)|I couldn' + "'" + r't open style file (.*)\n---line ([0-9]+) of file (.*)|Warning--(.*)')

    def run(self, query):
        tex_filename = query.tex_filename
        filename = tex_filename.rsplit('/', 1)[1][:-4]

        arguments = ['bibtex']
        arguments.append(filename + '.aux')

        query.bibtex_data['ran_on_files'].append(filename)

        try:
            self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(tex_filename))
        except FileNotFoundError:
            self.cleanup_files(query)
            self.throw_build_error(query, 'interpreter_not_working', 'bibtex missing')
            return
        self.process.wait()

        self.parse_bibtex_log(query, tex_filename[:-3] + 'blg')
        query.jobs.insert(0, 'build_latex')

    def stop_running(self):
        if self.process != None:
            self.process.kill()
            self.process = None

    def parse_bibtex_log(self, query, log_filename):
        try: file = open(log_filename, 'rb')
        except FileNotFoundError as e: pass
        else:
            text = file.read().decode('utf-8', errors='ignore')

            query.bibtex_log_messages = {'error': list(), 'warning': list(), 'badbox': list()}
            for item in self.bibtex_log_item_regex.finditer(text):
                line = item.group(0)

                if line.startswith('I couldn\'t open style file'):
                    query.error_count += 1
                    text = 'I couldn\'t open style file ' + item.group(4) + '.bst'
                    line_number = int(item.group(5).strip())
                    query.bibtex_log_messages['error'].append(('Error', -1, text))
                elif line.startswith('Warning--'):
                    if item.group(1) != None:
                        text = item.group(1)
                        line_number = int(item.group(2).strip())
                    else:
                        text = item.group(7)
                        line_number = -1
                    query.bibtex_log_messages['warning'].append(('Warning', line_number, text))
            query.bibtex_log_messages['error'].sort(key=itemgetter(1))
            query.bibtex_log_messages['warning'].sort(key=itemgetter(1))


