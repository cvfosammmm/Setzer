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

from setzer.app.service_locator import ServiceLocator


class BuilderBuild(object):

    def __init__(self):
        self.config_folder = ServiceLocator.get_config_folder()
        self.doc_regex = ServiceLocator.get_build_log_doc_regex()
        self.item_regex = ServiceLocator.get_build_log_item_regex()
        self.badbox_line_number_regex = ServiceLocator.get_build_log_badbox_line_number_regex()
        self.other_line_number_regex = ServiceLocator.get_build_log_other_line_number_regex()
        self.bibtex_log_item_regex = ServiceLocator.get_bibtex_log_item_regex()

        self.process = None

    def run(self, query):
        with tempfile.TemporaryDirectory() as tmp_directory_name:
            tex_file = tmp_directory_name + '/' + os.path.basename(query.tex_filename)
            with open(tex_file, 'w') as f: f.write(query.build_data['text'])

            if self.latex_build(query, tex_file):
                self.parse_bibtex_log(query, tex_file[:-3] + 'blg')
                query.forward_sync_data['build_pathname'] = self.copy_synctex_file(query, tex_file)
                self.move_build_files(query, tex_file)

                if self.process != None:
                    if query.error_count == 0:
                        pdf_filename = tmp_directory_name + '/' + os.path.basename(tex_file).rsplit('.tex', 1)[0] + '.pdf'
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
                else:
                    self.move_build_files(query, tex_file)
            self.process = None

    def latex_build(self, query, tex_filename):
        if query.force_building_to_stop: return False

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
            return False
        self.process.communicate()
        try:
            self.process.wait()
        except AttributeError:
            pass

        # parse results
        try:
            if self.parse_build_log(query, tex_filename):
                self.latex_build(query, tex_filename)
        except FileNotFoundError as e:
            self.move_build_files(query, tex_filename)
            self.throw_build_error(query, 'interpreter_not_working', 'log file missing')
        return True

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
                            return self.bibtex_build(query, tex_filename)

                        elif line.startswith('No file ') and line.find(tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1]) >= 0 and (line.find('.gls.') >= 0 or line.find('.acr.') >= 0):
                            return self.glossaries_build(query, tex_filename)

                        elif line.startswith('LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.'):
                            return True

                        elif line.startswith('Package natbib Warning: Citation(s) may have changed.'):
                            return True

                        elif line.startswith('No file ') and line.find(tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1]) >= 0 and (line.find('.toc.') >= 0 or line.find('.aux.') >= 0):
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

    def throw_build_error(self, query, error, error_arg):
        with query.build_result_lock:
            query.build_result = {'error': error,
                                 'error_arg': error_arg}

    def glossaries_build(self, query, tex_filename):
        if query.force_building_to_stop: return False

        basename = os.path.basename(tex_filename).rsplit('.', 1)[0]
        arguments = ['makeglossaries']
        arguments.append(basename)
        try:
            self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(tex_filename))
        except FileNotFoundError:
            self.move_build_files(query, tex_filename)
            self.throw_build_error(query, 'interpreter_not_working', 'makeglossaries missing')
            return False
        self.process.wait()
        for ending in ['.gls', '.acr']:
            move_from = os.path.join(os.path.dirname(tex_filename), basename + ending)
            move_to = os.path.join(os.path.dirname(query.tex_filename), basename + ending)
            try: shutil.move(move_from, move_to)
            except FileNotFoundError: pass
        self.cleanup_build_files(query, tex_filename)

        return True

    def bibtex_build(self, query, tex_filename):
        if query.force_building_to_stop: return False

        arguments = ['bibtex']
        arguments.append(tex_filename.rsplit('/', 1)[1][:-3] + 'aux')
        custom_env = os.environ.copy()
        custom_env['BIBINPUTS'] = os.path.dirname(query.tex_filename) + ':' + os.path.dirname(tex_filename)
        try:
            self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(tex_filename), env=custom_env)
        except FileNotFoundError:
            self.move_build_files(query, tex_filename)
            self.throw_build_error(query, 'interpreter_not_working', 'bibtex missing')
            return False
        self.process.wait()

        return True

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

    def move_build_files(self, query, tex_file_name):
        if query.build_data['do_cleanup']:
            self.cleanup_build_files(query, query.tex_filename)
            self.cleanup_glossaries_files(query)
        else:
            self.rename_build_files(query, tex_file_name)

    def cleanup_build_files(self, query, tex_file_name):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' , '.ilg',
                        '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc',
                        '.ist', '.glo', '.glg', '.acn', '.alg']
        for ending in file_endings:
            try: os.remove(os.path.splitext(tex_file_name)[0] + ending)
            except FileNotFoundError: pass

    def cleanup_glossaries_files(self, query):
        for ending in ['.gls', '.acr']:
            try: os.remove(os.path.splitext(query.tex_filename)[0] + ending)
            except FileNotFoundError: pass

    def rename_build_files(self, query, tex_file_name):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' ,
                        '.ilg', '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc',
                        '.ist', '.glo', '.glg', '.acn', '.alg']
        for ending in file_endings:
            move_from = os.path.splitext(tex_file_name)[0] + ending
            move_to = os.path.splitext(query.tex_filename)[0] + ending
            try: shutil.move(move_from, move_to)
            except FileNotFoundError: pass


