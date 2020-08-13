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

import gi
from gi.repository import GLib, GObject
import time
import _thread as thread, queue
import subprocess
import os
import os.path
import base64
import tempfile
import shutil
import re

from setzer.app.service_locator import ServiceLocator


class BuildSystem(object):

    def __init__(self):
        self.observers = set()
        self.active_query = None
        self.change_code_queue = queue.Queue() # change code for observers are put on here
        GObject.timeout_add(50, self.results_loop)
        GObject.timeout_add(50, self.change_code_loop)

    def change_code_loop(self):
        ''' notify observers '''

        if not self.change_code_queue.empty():
            change_code = self.change_code_queue.get(block=False)
            for observer in self.observers:
                observer.change_notification(change_code['change_code'], self, change_code['parameter'])
        return True
    
    def register_observer(self, observer):
        ''' Observer call this method to register themselves with observable
            objects. They have themselves to implement a method
            'change_notification(change_code, parameter)' which they observable
            will call when it's state changes. '''
        
        self.observers.add(observer)

    def add_change_code(self, change_code, parameter=None):
        self.change_code_queue.put({'change_code': change_code, 'parameter': parameter})
                
    def results_loop(self):
        if self.active_query != None:
            if self.active_query.is_done():
                build_result = self.active_query.get_build_result()
                forward_sync_result = self.active_query.get_forward_sync_result()
                backward_sync_result = self.active_query.get_backward_sync_result()
                if forward_sync_result != None or backward_sync_result != None or build_result != None:
                    self.add_change_code('building_finished', {'build': build_result, 'forward_sync': forward_sync_result, 'backward_sync': backward_sync_result})
                self.active_query = None
        return True
    
    def add_query(self, query):
        if self.active_query != None:
            self.active_query.stop_building()
        self.active_query = query
        thread.start_new_thread(query.execute, ())
        self.add_change_code('reset_timer')
        self.add_change_code('building_started')
        
    def stop_building(self):
        if self.active_query != None:
            self.active_query.stop_building()
            self.active_query = None
        self.add_change_code('building_stopped')


class Query(object):

    def __init__(self):
        self.config_folder = ServiceLocator.get_config_folder()

        self.process = None
        self.build_result = None
        self.build_result_lock = thread.allocate_lock()
        self.forward_sync_result = None
        self.forward_sync_result_lock = thread.allocate_lock()
        self.backward_sync_result = None
        self.backward_sync_result_lock = thread.allocate_lock()
        self.done_executing = False
        self.done_executing_lock = thread.allocate_lock()
        self.synctex_file = None
        self.synctex_file_lock = thread.allocate_lock()

    def stop_building(self):
        if self.process != None:
            self.process.kill()
            self.process = None
            self.force_building_to_stop = True
    
    def get_build_result(self):
        return_value = None
        with self.build_result_lock:
            if self.build_result != None:
                return_value = self.build_result
        return return_value

    def get_forward_sync_result(self):
        return_value = None
        with self.forward_sync_result_lock:
            if self.forward_sync_result != None:
                return_value = self.forward_sync_result
        return return_value

    def get_backward_sync_result(self):
        return_value = None
        with self.backward_sync_result_lock:
            if self.backward_sync_result != None:
                return_value = self.backward_sync_result
        return return_value

    def mark_done(self):
        with self.done_executing_lock:
            self.done_executing = True
    
    def is_done(self):
        with self.done_executing_lock:
            return self.done_executing
    
    def build(self):
        with tempfile.TemporaryDirectory() as tmp_directory_name:
            tex_file = tmp_directory_name + '/' + os.path.basename(self.tex_filename)
            self.build_pathname = tex_file
            with open(tex_file, 'w') as f: f.write(self.text)
            pdf_filename = tmp_directory_name + '/' + os.path.basename(tex_file).rsplit('.tex', 1)[0] + '.pdf'
            log_filename = tmp_directory_name + '/' + os.path.basename(tex_file).rsplit('.tex', 1)[0] + '.log'

            # build pdf
            while (self.do_another_latex_build or self.do_a_bibtex_build or self.do_make_glossaries) and not self.force_building_to_stop:
                if self.do_a_bibtex_build:
                    arguments = ['bibtex']
                    arguments.append(tex_file.rsplit('/', 1)[1][:-3] + 'aux')
                    custom_env = os.environ.copy()
                    custom_env['BIBINPUTS'] = self.directory_name + ':' + tmp_directory_name
                    try:
                        self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=tmp_directory_name, env=custom_env)
                    except FileNotFoundError:
                        self.cleanup_build_files(tex_file)
                        with self.build_result_lock:
                            self.build_result = {'error': 'interpreter_not_working',
                                                 'error_arg': self.latex_interpreter}
                        return
                    self.process.wait()

                    self.do_a_bibtex_build = False
                    self.done_bibtex_build = True
                elif self.do_make_glossaries:
                    for filename in self.glo_files_to_make:
                        arguments = ['makeglossaries']
                        arguments.append(filename)
                        try:
                            self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=tmp_directory_name)
                        except FileNotFoundError:
                            self.cleanup_build_files(tex_file)
                            with self.build_result_lock:
                                self.build_result = {'error': 'interpreter_not_working',
                                                     'error_arg': self.latex_interpreter}
                            return
                        self.process.wait()
                        for ending in ['.gls', '.glg']:
                            move_from = os.path.join(tmp_directory_name, os.path.splitext(filename)[0] + ending)
                            move_to = os.path.join(self.directory_name, os.path.splitext(filename)[0] + ending)
                            try: shutil.move(move_from, move_to)
                            except FileNotFoundError: pass

                    self.do_make_glossaries = False
                    self.glo_files_to_make = []
                    self.glossaries_made = True
                else:
                    arguments = self.build_command.split()
                    arguments.append('-output-directory=' + tmp_directory_name)
                    arguments.append(tex_file)
                    try:
                        self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.directory_name)
                    except FileNotFoundError:
                        self.cleanup_build_files(tex_file)
                        with self.build_result_lock:
                            self.build_result = {'error': 'interpreter_missing',
                                                 'error_arg': arguments[0]}
                        return
                    self.process.communicate()
                    try:
                        self.process.wait()
                    except AttributeError:
                        pass

                    # parse results
                    try:
                        self.parse_build_log(log_filename, tex_file)
                    except FileNotFoundError as e:
                        self.cleanup_build_files(tex_file)
                        with self.build_result_lock:
                            self.build_result = {'error': 'interpreter_not_working',
                                                 'error_arg': 'log file missing'}
                        return
        
            self.parse_bibtex_log(tex_file[:-3] + 'blg')

            self.build_pathname = self.copy_synctex_file(self.build_pathname)

            if self.process != None:
                self.process = None

                if self.do_cleanup:
                    self.cleanup_build_files(self.tex_filename)
                else:
                    self.rename_build_files(tex_file)

                if self.error_count == 0:
                    try: shutil.move(pdf_filename, self.new_pdf_filename)
                    except FileNotFoundError: self.new_pdf_filename = None
                else:
                    self.new_pdf_filename = None

                with self.build_result_lock:
                    self.build_result = {'pdf_filename': self.new_pdf_filename, 
                                         'build_pathname': self.build_pathname,
                                         'log_messages': self.log_messages + self.bibtex_log_messages,
                                         'error': None,
                                         'error_arg': None}
            else:
                self.cleanup_build_files(tex_file)

    def parse_build_log(self, log_filename, tex_filename):
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
                        filename = os.path.normpath(self.directory_name + '/' + filename)
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
            doc_texts[self.tex_filename] = text

            self.log_messages = list()
            self.do_another_latex_build = False
            self.do_a_bibtex_build = False
            self.error_count = 0

            file_no = 0
            for filename, text in doc_texts.items():
                if filename == self.tex_filename:
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

                        if line.startswith('No file ' + tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1] + '.bbl.') and not self.done_bibtex_build:
                            if not self.do_make_glossaries:
                                self.do_another_latex_build = True
                                self.do_a_bibtex_build = True

                        elif line.startswith('Package glossaries Info: Writing glossary file ') and not self.glossaries_made:
                            if not self.do_a_bibtex_build:
                                filename_match = self.glo_file_regex.search(line)
                                if filename_match != None:
                                    filename = filename_match.group(1)
                                    self.glo_files_to_make.append(filename)
                                    self.do_another_latex_build = True
                                    self.do_make_glossaries = True

                        elif line.startswith('LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.'):
                            self.do_another_latex_build = True

                        elif line.startswith('Package natbib Warning: Citation(s) may have changed.'):
                            self.do_another_latex_build = True

                        elif line.startswith('No file ' + tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1] + '.toc.'):
                            self.do_another_latex_build = True

                        elif line.startswith('No file ' + tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1] + '.aux.'):
                            self.do_another_latex_build = True

                        elif line.startswith('Overfull \hbox'):
                            line_number_match = self.badbox_line_number_regex.search(line)
                            if line_number_match != None:
                                line_number = int(line_number_match.group(1))
                                text = line.strip()
                                self.log_messages.append(('Badbox', None, filename, file_no, line_number, text))

                        elif line.startswith('Underfull \hbox'):
                            line_number_match = self.badbox_line_number_regex.search(line)
                            if line_number_match != None:
                                line_number = int(line_number_match.group(1))
                                text = line.strip()
                                self.log_messages.append(('Badbox', None, filename, file_no, line_number, text))

                        elif line.startswith('LaTeX Warning: Reference '):
                            text = line[15:].strip()
                            line_number = self.bl_get_line_number(line, matchiter)
                            self.log_messages.append(('Warning', 'Undefined Reference', filename, file_no, line_number, text))

                        elif line.startswith('Package '):
                            text = line.split(':')[1].strip()
                            line_number = self.bl_get_line_number(line, matchiter)
                            self.log_messages.append(('Warning', None, filename, file_no, line_number, text))
                            if text == 'Rerun to get transparencies right.':
                                self.do_another_latex_build = True

                        elif line.startswith('LaTeX Warning: '):
                            text = line[15:].strip()
                            line_number = self.bl_get_line_number(line, matchiter)
                            self.log_messages.append(('Warning', None, filename, file_no, line_number, text))

                        elif line.startswith('! Undefined control sequence'):
                            text = line.strip()
                            line_number = self.bl_get_line_number(line, matchiter)
                            self.log_messages.append(('Error', 'Undefined control sequence', filename, file_no, line_number, text))
                            self.error_count += 1

                        elif line.startswith('! LaTeX Error'):
                            text = line[15:].strip()
                            line_number = self.bl_get_line_number(line, matchiter)
                            self.log_messages.append(('Error', None, filename, file_no, line_number, text))
                            self.error_count += 1

                        elif line.startswith('No file ') or (line.startswith('File') and line.endswith(' does not exist.\n')):
                            text = line.strip()
                            line_number = -1
                            if not line.startswith('No file ' + os.path.basename(log_filename).rsplit('.log', 1)[0]):
                                self.log_messages.append(('Error', None, filename, file_no, line_number, text))
                                self.error_count += 1

                        elif line.startswith('! I can\'t find file\.'):
                            text = line.strip()
                            line_number = -1
                            self.log_messages.append(('Error', None, filename, file_no, line_number, text))
                            self.error_count += 1

                        elif line.startswith('! File'):
                            text = line[2:].strip()
                            line_number = self.bl_get_line_number(line, matchiter)
                            self.log_messages.append(('Error', None, filename, file_no, line_number, text))
                            self.error_count += 1

                        elif line.startswith('! '):
                            text = line[2:].strip()
                            line_number = self.bl_get_line_number(line, matchiter)
                            self.log_messages.append(('Error', None, filename, file_no, line_number, text))
                            self.error_count += 1

    def parse_bibtex_log(self, log_filename):
        try: file = open(log_filename, 'rb')
        except FileNotFoundError as e: pass
        else:
            text = file.read().decode('utf-8', errors='ignore')

            self.bibtex_log_messages = list()
            file_numbers = dict()
            for item in self.bibtex_log_item_regex.finditer(text):
                line = item.group(0)

                if line.startswith('I couldn\'t open style file'):
                    self.error_count += 1
                    text = 'I couldn\'t open style file ' + item.group(4) + '.bst'
                    line_number = int(item.group(5).strip())
                    self.bibtex_log_messages.append(('Error', None, self.tex_filename, 0, -1, text))
                elif line.startswith('Warning--'):
                    filename = os.path.basename(log_filename[:-3] + 'bib')
                    try:
                        file_no = file_numbers[filename]
                    except KeyError:
                        file_no = 10000 + len(file_numbers)
                        file_numbers[filename] = file_no
                    text = item.group(1)
                    line_number = int(item.group(2).strip())
                    self.bibtex_log_messages.append(('Warning', None, filename, file_no, line_number, text))

    def bl_get_line_number(self, line, matchiter):
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

    def copy_synctex_file(self, tex_file_name):
        move_from = os.path.splitext(tex_file_name)[0] + '.synctex.gz'
        folder = self.config_folder + '/' + base64.urlsafe_b64encode(str.encode(self.tex_filename)).decode()
        move_to = folder + '/' + os.path.splitext(os.path.basename(self.tex_filename))[0] + '.synctex.gz'

        if not os.path.exists(folder):
            os.makedirs(folder)

        try: shutil.copyfile(move_from, move_to)
        except FileNotFoundError: return None
        else: return tex_file_name

    def cleanup_build_files(self, tex_file_name):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' , '.ilg',
                        '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc',
                        '.glo', '.ist']
        for ending in file_endings:
            try: os.remove(os.path.splitext(tex_file_name)[0] + ending)
            except FileNotFoundError: pass

    def rename_build_files(self, tex_file_name):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' ,
                        '.ilg', '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc',
                        '.glo', '.ist']
        for ending in file_endings:
            move_from = os.path.splitext(tex_file_name)[0] + ending
            move_to = os.path.splitext(self.tex_filename)[0] + ending
            try: shutil.move(move_from, move_to)
            except FileNotFoundError: pass

    def forward_sync(self):
        if self.build_pathname == None:
            self.forward_sync_result = None
            return

        synctex_folder = self.config_folder + '/' + base64.urlsafe_b64encode(str.encode(self.tex_filename)).decode()
        arguments = ['synctex', 'view', '-i']
        arguments.append(str(self.synctex_args['line']) + ':' + str(self.synctex_args['line_offset']) + ':' + self.build_pathname)
        arguments.append('-o')
        arguments.append(self.tex_filename[:-3] + 'pdf')
        arguments.append('-d')
        arguments.append(synctex_folder)
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        raw = process.communicate()[0].decode('utf-8')
        process = None

        rectangles = list()
        for match in self.forward_synctex_regex.finditer(raw):
            rectangle = dict()
            rectangle['page'] = int(match.group(1))
            rectangle['h'] = float(match.group(2))
            rectangle['v'] = float(match.group(3))
            rectangle['width'] = float(match.group(4))
            rectangle['height'] = float(match.group(5))
            rectangles.append(rectangle)

        if len(rectangles) > 0:
            self.forward_sync_result = rectangles
        else:
            self.forward_sync_result = None

    def backward_sync(self):
        if self.build_pathname == None:
            self.backward_sync_result = None
            return

        synctex_folder = self.config_folder + '/' + base64.urlsafe_b64encode(str.encode(self.tex_filename)).decode()
        arguments = ['synctex', 'edit', '-o']
        arguments.append(str(self.backward_sync_data['page']) + ':' + str(self.backward_sync_data['x']) + ':' + str(self.backward_sync_data['y']) + ':' + self.tex_filename[:-3] + 'pdf')
        arguments.append('-d')
        arguments.append(synctex_folder)
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        raw = process.communicate()[0].decode('utf-8')
        process = None

        match = self.backward_synctex_regex.search(raw)
        result = None
        if match != None and match.group(1) == self.build_pathname:
            result = dict()
            result['line'] = max(int(match.group(2)) - 1, 0)
            result['word'] = self.backward_sync_data['word']
            result['context'] = self.backward_sync_data['context']

        if result != None:
            self.backward_sync_result = result
        else:
            self.backward_sync_result = None


class QueryBuild(Query):

    def __init__(self, text, tex_filename, latex_interpreter, use_latexmk, additional_arguments, do_cleanup):
        Query.__init__(self)

        self.text = text
        self.tex_filename = tex_filename
        self.build_pathname = None
        self.new_pdf_filename = os.path.splitext(self.tex_filename)[0] + '.pdf'
        self.directory_name = os.path.dirname(self.tex_filename)
        self.additional_arguments = additional_arguments
        self.do_cleanup = do_cleanup

        self.log_messages = list()
        self.bibtex_log_messages = list()
        self.doc_regex = ServiceLocator.get_build_log_doc_regex()
        self.item_regex = ServiceLocator.get_build_log_item_regex()
        self.badbox_line_number_regex = ServiceLocator.get_build_log_badbox_line_number_regex()
        self.glo_file_regex = ServiceLocator.get_build_log_glo_file_regex()
        self.other_line_number_regex = ServiceLocator.get_build_log_other_line_number_regex()
        self.bibtex_log_item_regex = ServiceLocator.get_bibtex_log_item_regex()
        self.force_building_to_stop = False

        self.latex_interpreter = latex_interpreter
        self.build_command_defaults = dict()
        self.build_command_defaults['pdflatex'] = 'pdflatex -synctex=1 -interaction=nonstopmode -pdf'
        self.build_command_defaults['xelatex'] = 'xelatex -synctex=1 -interaction=nonstopmode'
        self.build_command_defaults['lualatex'] = 'lualatex --synctex=1 --interaction=nonstopmode'
        if use_latexmk:
            if self.latex_interpreter == 'pdflatex':
                interpreter_option = 'pdf'
            else:
                interpreter_option = self.latex_interpreter
            self.build_command = 'latexmk -' + interpreter_option + ' -synctex=1 -interaction=nonstopmode' + self.additional_arguments
        else:
            self.build_command = self.build_command_defaults[self.latex_interpreter] + self.additional_arguments

        self.do_another_latex_build = True
        self.do_a_bibtex_build = False
        self.done_bibtex_build = False
        self.do_make_glossaries = False
        self.glo_files_to_make = []
        self.glossaries_made = False
        self.error_count = 0

    def execute(self):
        self.build()
        self.mark_done()


class QueryForwardSync(Query):

    def __init__(self, tex_filename, build_pathname, synctex_arguments):
        Query.__init__(self)

        self.tex_filename = tex_filename
        self.build_pathname = build_pathname
        self.synctex_args = synctex_arguments

        self.forward_synctex_regex = ServiceLocator.get_forward_synctex_regex()

    def execute(self):
        self.forward_sync()
        self.mark_done()


class QueryBackwardSync(Query):

    def __init__(self, tex_filename, build_pathname, backward_sync_data):
        Query.__init__(self)

        self.tex_filename = tex_filename
        self.build_pathname = build_pathname
        self.backward_sync_data = backward_sync_data

        self.backward_synctex_regex = ServiceLocator.get_backward_synctex_regex()

    def execute(self):
        self.backward_sync()
        self.mark_done()


class QueryBuildAndForwardSync(Query):

    def __init__(self, text, tex_filename, latex_interpreter, use_latexmk, additional_arguments, do_cleanup, synctex_arguments):
        Query.__init__(self)

        self.text = text
        self.tex_filename = tex_filename
        self.new_pdf_filename = os.path.splitext(self.tex_filename)[0] + '.pdf'
        self.directory_name = os.path.dirname(self.tex_filename)
        self.synctex_args = synctex_arguments
        self.additional_arguments = additional_arguments
        self.do_cleanup = do_cleanup

        self.log_messages = list()
        self.bibtex_log_messages = list()
        self.doc_regex = ServiceLocator.get_build_log_doc_regex()
        self.item_regex = ServiceLocator.get_build_log_item_regex()
        self.badbox_line_number_regex = ServiceLocator.get_build_log_badbox_line_number_regex()
        self.glo_file_regex = ServiceLocator.get_build_log_glo_file_regex()
        self.other_line_number_regex = ServiceLocator.get_build_log_other_line_number_regex()
        self.bibtex_log_item_regex = ServiceLocator.get_bibtex_log_item_regex()
        self.forward_synctex_regex = ServiceLocator.get_forward_synctex_regex()
        self.force_building_to_stop = False

        self.latex_interpreter = latex_interpreter
        self.build_command_defaults = dict()
        self.build_command_defaults['pdflatex'] = 'pdflatex -synctex=1 -interaction=nonstopmode -pdf'
        self.build_command_defaults['xelatex'] = 'xelatex -synctex=1 -interaction=nonstopmode'
        self.build_command_defaults['lualatex'] = 'lualatex --synctex=1 --interaction=nonstopmode'
        if use_latexmk:
            if self.latex_interpreter == 'pdflatex':
                interpreter_option = 'pdf'
            else:
                interpreter_option = self.latex_interpreter
            self.build_command = 'latexmk -' + interpreter_option + ' -synctex=1 -interaction=nonstopmode' + self.additional_arguments
        else:
            self.build_command = self.build_command_defaults[self.latex_interpreter] + self.additional_arguments

        self.do_another_latex_build = True
        self.do_a_bibtex_build = False
        self.done_bibtex_build = False
        self.do_make_glossaries = False
        self.glo_files_to_make = []
        self.glossaries_made = False
        self.error_count = 0

    def execute(self):
        self.build()
        self.forward_sync()
        self.mark_done()


