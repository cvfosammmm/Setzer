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
import base64
import shutil
import subprocess

import setzer.document.latex.build_system.builder.builder_build as builder_build
import setzer.document.latex.build_system.latex_log_parser.latex_log_parser as latex_log_parser
from setzer.app.service_locator import ServiceLocator


class BuilderBuildLaTeX(builder_build.BuilderBuild):

    def __init__(self):
        builder_build.BuilderBuild.__init__(self)

        self.config_folder = ServiceLocator.get_config_folder()
        self.latex_log_parser = latex_log_parser.LaTeXLogParser()

    def run(self, query):
        build_command_defaults = dict()
        build_command_defaults['pdflatex'] = 'pdflatex -synctex=1 -interaction=nonstopmode -pdf'
        build_command_defaults['xelatex'] = 'xelatex -synctex=1 -interaction=nonstopmode'
        build_command_defaults['lualatex'] = 'lualatex --synctex=1 --interaction=nonstopmode'
        if query.build_data['use_latexmk']:
            if query.build_data['latex_interpreter'] == 'pdflatex':
                interpreter_option = 'pdf'
            else:
                interpreter_option = query.build_data['latex_interpreter']
            build_command = 'latexmk -' + interpreter_option + ' -synctex=1 -interaction=nonstopmode' + query.build_data['additional_arguments']
        else:
            build_command = build_command_defaults[query.build_data['latex_interpreter']] + query.build_data['additional_arguments']

        arguments = build_command.split()
        arguments.append('-output-directory=' + os.path.dirname(query.tex_filename))
        arguments.append(query.tex_filename)
        try:
            self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(query.tex_filename))
        except FileNotFoundError:
            self.cleanup_files(query)
            self.throw_build_error(query, 'interpreter_missing', arguments[0])
            return
        self.process.communicate()
        try:
            self.process.wait()
        except AttributeError:
            pass

        # parse results
        try:
            if self.parse_build_log(query):
                return
        except FileNotFoundError as e:
            self.cleanup_files(query)
            self.throw_build_error(query, 'interpreter_not_working', 'log file missing')
            return

        query.forward_sync_data['build_pathname'] = self.copy_synctex_file(query)
        self.cleanup_files(query)

        if query.error_count == 0:
            pdf_filename = os.path.dirname(query.tex_filename) + '/' + os.path.basename(query.tex_filename).rsplit('.tex', 1)[0] + '.pdf'
            new_pdf_filename = os.path.splitext(query.tex_filename)[0] + '.pdf'
            try: shutil.move(pdf_filename, new_pdf_filename)
            except FileNotFoundError: new_pdf_filename = None
        else:
            new_pdf_filename = None

        with query.build_result_lock:
            query.build_result = {'pdf_filename': new_pdf_filename, 
                                 'build_pathname': query.forward_sync_data['build_pathname'],
                                 'log_messages': query.log_messages + query.bibtex_log_messages,
                                 'error': None,
                                 'error_arg': None}

    def parse_build_log(self, query):
        query.log_messages = list()
        query.error_count = 0

        log_items = self.latex_log_parser.parse_build_log(query.tex_filename)
        additional_jobs = self.latex_log_parser.get_additional_jobs(log_items, query.tex_filename, query.bibtex_data['ran_on_files'], query.biber_data['ran_on_files'])
        file_no = 0

        for job in additional_jobs:
            query.jobs.insert(0, job)
            return True

        for filename, items in log_items.items():
            query.error_count += len(items['error'])
            if filename == query.tex_filename:
                file_no = 0
            else:
                file_no += 1

            for item in items['error']:
                query.log_messages.append(('Error', item[0], filename, file_no, item[1], item[2]))
            for item in items['warning']:
                query.log_messages.append(('Warning', item[0], filename, file_no, item[1], item[2]))
            for item in items['badbox']:
                query.log_messages.append(('Badbox', item[0], filename, file_no, item[1], item[2]))

        return False

    def copy_synctex_file(self, query):
        move_from = os.path.splitext(query.tex_filename)[0] + '.synctex.gz'
        folder = self.config_folder + '/' + base64.urlsafe_b64encode(str.encode(query.tex_filename)).decode()
        move_to = folder + '/' + os.path.splitext(os.path.basename(query.tex_filename))[0] + '.synctex.gz'

        if not os.path.exists(folder):
            os.makedirs(folder)

        try: shutil.copyfile(move_from, move_to)
        except FileNotFoundError: return None
        else: return query.tex_filename


