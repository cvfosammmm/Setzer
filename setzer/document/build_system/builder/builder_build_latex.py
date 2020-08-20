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
import tempfile
import shutil
import subprocess

import setzer.document.build_system.builder.builder_build as builder_build
from setzer.app.service_locator import ServiceLocator


class BuilderBuildLaTeX(builder_build.BuilderBuild):

    def __init__(self):
        builder_build.BuilderBuild.__init__(self)

        self.config_folder = ServiceLocator.get_config_folder()
        self.doc_regex = ServiceLocator.get_build_log_doc_regex()
        self.item_regex = ServiceLocator.get_build_log_item_regex()
        self.badbox_line_number_regex = ServiceLocator.get_build_log_badbox_line_number_regex()
        self.other_line_number_regex = ServiceLocator.get_build_log_other_line_number_regex()

    def run(self, query):
        try:
            tex_filename = query.build_data['tmp_tex_filename']
        except KeyError:
            query.build_data['tmp_directory'] = tempfile.TemporaryDirectory()
            tex_filename = query.build_data['tmp_directory'].name + '/' + os.path.basename(query.tex_filename)
            with open(tex_filename, 'w') as f: f.write(query.build_data['text'])
            query.build_data['tmp_tex_filename'] = tex_filename

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
        arguments.append('-output-directory=' + os.path.dirname(tex_filename))
        arguments.append(tex_filename)
        try:
            self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(query.tex_filename))
        except FileNotFoundError:
            self.move_build_files(query, tex_filename)
            self.throw_build_error(query, 'interpreter_missing', arguments[0])
            return
        self.process.communicate()
        try:
            self.process.wait()
        except AttributeError:
            pass

        # parse results
        try:
            if self.parse_build_log(query, tex_filename):
                return
        except FileNotFoundError as e:
            self.move_build_files(query, tex_filename)
            self.throw_build_error(query, 'interpreter_not_working', 'log file missing')
            return

        query.forward_sync_data['build_pathname'] = self.copy_synctex_file(query, tex_filename)
        self.move_build_files(query, tex_filename)

        if query.error_count == 0:
            pdf_filename = os.path.dirname(tex_filename) + '/' + os.path.basename(tex_filename).rsplit('.tex', 1)[0] + '.pdf'
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

        query.build_data['tmp_directory'].cleanup()

    def parse_build_log(self, query, tex_filename):
        log_filename = os.path.dirname(tex_filename) + '/' + os.path.basename(tex_filename).rsplit('.tex', 1)[0] + '.log'

        try: file = open(log_filename, 'rb')
        except FileNotFoundError as e: raise e
        else:
            text = file.read().decode('utf-8', errors='ignore')
            doc_texts = dict()

            matches = self.doc_regex.split(text)
            buffer = ''
            for match in reversed(matches):
                if not self.doc_regex.fullmatch(match):
                    buffer += match
                else:
                    match = match.strip() + buffer
                    buffer = ''
                    filename = self.doc_regex.match(match).group(2).strip()
                    if not filename.startswith('/'):
                        filename = os.path.normpath(os.path.dirname(query.tex_filename) + '/' + filename)
                    if not filename == tex_filename:
                        open_brackets = 0
                        char_count = 0
                        for char in match:
                            if char == ')':
                                open_brackets -= 1
                            if char == '(':
                                open_brackets += 1
                            char_count += 1
                            if open_brackets == 0:
                                break
                        match = match[:char_count]
                        doc_texts[filename] = match
                        text = text.replace(match, '')
                    buffer = ''
            doc_texts[query.tex_filename] = text

            query.log_messages = list()
            query.error_count = 0

            file_no = 0
            for filename, text in doc_texts.items():
                if filename == query.tex_filename:
                    file_no = 0
                else:
                    file_no += 1

                matches = self.item_regex.split(text)
                buffer = ''
                for match in reversed(matches):
                    if not self.item_regex.fullmatch(match):
                        buffer += match
                    else:
                        match += buffer
                        buffer = ''
                        matchiter = iter(match.splitlines())
                        line = next(matchiter)

                        if line.startswith('No file ') and line.find(tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1]) >= 0 and line.find('.bbl.') >= 0:
                            query.jobs.insert(0, 'build_bibtex')
                            return True

                        elif line.startswith('No file ') and line.find(tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1]) >= 0 and (line.find('.gls.') >= 0 or line.find('.acr.') >= 0):
                            query.jobs.insert(0, 'build_glossaries')
                            return True

                        elif line.startswith('LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.'):
                            query.jobs.insert(0, 'build_latex')
                            return True

                        elif line.startswith('Package natbib Warning: Citation(s) may have changed.'):
                            query.jobs.insert(0, 'build_latex')
                            return True

                        elif line.startswith('No file ') and line.find(tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1]) >= 0 and (line.find('.toc.') >= 0 or line.find('.aux.') >= 0):
                            query.jobs.insert(0, 'build_latex')
                            return True

                        elif line.startswith('Overfull \hbox'):
                            line_number_match = self.badbox_line_number_regex.search(line)
                            if line_number_match != None:
                                line_number = int(line_number_match.group(1))
                                text = line.strip()
                                query.log_messages.append(('Badbox', None, filename, file_no, line_number, text))

                        elif line.startswith('Underfull \hbox'):
                            line_number_match = self.badbox_line_number_regex.search(line)
                            if line_number_match != None:
                                line_number = int(line_number_match.group(1))
                                text = line.strip()
                                query.log_messages.append(('Badbox', None, filename, file_no, line_number, text))

                        elif line.startswith('LaTeX Warning: Reference '):
                            text = line[15:].strip()
                            line_number = self.bl_get_line_number(query, line, matchiter)
                            query.log_messages.append(('Warning', 'Undefined Reference', filename, file_no, line_number, text))

                        elif line.startswith('Package '):
                            text = line.split(':')[1].strip()
                            line_number = self.bl_get_line_number(query, line, matchiter)
                            query.log_messages.append(('Warning', None, filename, file_no, line_number, text))
                            if text == 'Rerun to get transparencies right.':
                                query.jobs.insert(0, 'build_latex')
                                return True

                        elif line.startswith('LaTeX Warning: '):
                            text = line[15:].strip()
                            line_number = self.bl_get_line_number(query, line, matchiter)
                            query.log_messages.append(('Warning', None, filename, file_no, line_number, text))

                        elif line.startswith('! Undefined control sequence'):
                            text = line.strip()
                            line_number = self.bl_get_line_number(query, line, matchiter)
                            query.log_messages.append(('Error', 'Undefined control sequence', filename, file_no, line_number, text))
                            query.error_count += 1

                        elif line.startswith('! LaTeX Error'):
                            text = line[15:].strip()
                            line_number = self.bl_get_line_number(query, line, matchiter)
                            query.log_messages.append(('Error', None, filename, file_no, line_number, text))
                            query.error_count += 1

                        elif line.startswith('No file ') or (line.startswith('File') and line.endswith(' does not exist.\n')):
                            text = line.strip()
                            line_number = -1
                            if not (line.startswith('No file ') and line.find(os.path.basename(log_filename).rsplit('.log', 1)[0]) >= 0):
                                query.log_messages.append(('Error', None, filename, file_no, line_number, text))
                                query.error_count += 1

                        elif line.startswith('! I can\'t find file\.'):
                            text = line.strip()
                            line_number = -1
                            query.log_messages.append(('Error', None, filename, file_no, line_number, text))
                            query.error_count += 1

                        elif line.startswith('! File'):
                            text = line[2:].strip()
                            line_number = self.bl_get_line_number(query, line, matchiter)
                            query.log_messages.append(('Error', None, filename, file_no, line_number, text))
                            query.error_count += 1

                        elif line.startswith('! '):
                            text = line[2:].strip()
                            line_number = self.bl_get_line_number(query, line, matchiter)
                            query.log_messages.append(('Error', None, filename, file_no, line_number, text))
                            query.error_count += 1
        return False

    def bl_get_line_number(self, query, line, matchiter):
        for i in range(10):
            line_number_match = self.other_line_number_regex.search(line)
            if line_number_match != None:
                return int(line_number_match.group(2))
            else:
                try:
                    line += next(matchiter)
                except StopIteration:
                    return -1
        return -1

    def copy_synctex_file(self, query, tex_file_name):
        move_from = os.path.splitext(tex_file_name)[0] + '.synctex.gz'
        folder = self.config_folder + '/' + base64.urlsafe_b64encode(str.encode(query.tex_filename)).decode()
        move_to = folder + '/' + os.path.splitext(os.path.basename(query.tex_filename))[0] + '.synctex.gz'

        if not os.path.exists(folder):
            os.makedirs(folder)

        try: shutil.copyfile(move_from, move_to)
        except FileNotFoundError: return None
        else: return tex_file_name


