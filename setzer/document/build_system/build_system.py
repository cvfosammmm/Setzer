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
import tempfile
import shutil
import re

from setzer.helpers.helpers import timer
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
        ''' wait for results and add them to their documents '''

        if self.active_query != None:
            result_blob = self.active_query.get_result()
            if result_blob != None:
                self.active_query = None
                self.add_change_code('building_finished', result_blob)
        return True
    
    def add_query(self, query):
        if self.active_query != None:
            self.active_query.stop_building()
        self.active_query = query
        thread.start_new_thread(query.build, ())
        self.add_change_code('reset_timer')
        self.add_change_code('building_started')
        
    def stop_building(self):
        if self.active_query != None:
            self.active_query.stop_building()
            self.active_query = None
        self.add_change_code('building_stopped')
    

class Query(object):

    def __init__(self, text, document_controller, synctex_arguments, latex_interpreter, additional_arguments):
        self.text = text
        self.document_controller = document_controller
        self.tex_filename = self.document_controller.document.get_filename()[:]
        self.new_pdf_filename = os.path.splitext(self.tex_filename)[0] + '.pdf'
        self.directory_name = os.path.dirname(self.document_controller.document.get_filename())
        self.process = None
        self.result = None
        self.result_lock = thread.allocate_lock()
        self.synctex_args = synctex_arguments
        self.additional_arguments = additional_arguments

        self.log_messages = list()
        self.bibtex_log_messages = list()
        self.doc_regex = ServiceLocator.get_build_log_doc_regex()
        self.item_regex = ServiceLocator.get_build_log_item_regex()
        self.badbox_line_number_regex = ServiceLocator.get_build_log_badbox_line_number_regex()
        self.other_line_number_regex = ServiceLocator.get_build_log_other_line_number_regex()
        self.bibtex_log_item_regex = ServiceLocator.get_bibtex_log_item_regex()
        self.force_building_to_stop = False

        self.latex_interpreter = latex_interpreter
        self.build_command_defaults = dict()
        self.build_command_defaults['latexmk'] = 'latexmk -synctex=1 -interaction=nonstopmode -pdf'
        self.build_command_defaults['pdflatex'] = 'pdflatex -synctex=1 -interaction=nonstopmode -pdf'
        self.build_command_defaults['xelatex'] = 'xelatex -synctex=1 -interaction=nonstopmode'
        self.build_command_defaults['lualatex'] = 'lualatex -synctex=1 -interaction=nonstopmode -pdf'
        self.build_command = self.build_command_defaults[self.latex_interpreter] + self.additional_arguments

        self.do_another_latex_build = True
        self.do_a_bibtex_build = False
        self.done_bibtex_build = False
        self.error_count = 0

    def build(self):
        with tempfile.TemporaryDirectory() as tmp_directory_name:
            tex_file = tempfile.NamedTemporaryFile(suffix='.tex', dir=tmp_directory_name)
            with open(tex_file.name, 'w') as f: f.write(self.text)
            pdf_filename = tmp_directory_name + '/' + os.path.basename(tex_file.name).rsplit('.tex', 1)[0] + '.pdf'
            log_filename = tmp_directory_name + '/' + os.path.basename(tex_file.name).rsplit('.tex', 1)[0] + '.log'

            # build pdf
            while (self.do_another_latex_build or self.do_a_bibtex_build) and not self.force_building_to_stop:
                if self.do_a_bibtex_build:
                    arguments = ['bibtex']
                    arguments.append(tex_file.name.rsplit('/', 1)[1][:-3] + 'aux')
                    custom_env = os.environ.copy()
                    custom_env['BIBINPUTS'] = self.directory_name + ':' + tmp_directory_name
                    try:
                        self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=tmp_directory_name, env=custom_env)
                    except FileNotFoundError:
                        self.cleanup_build_files(tex_file.name)
                        with self.result_lock:
                            self.result = {'document_controller': self.document_controller, 
                                           'error': 'interpreter_not_working',
                                           'error_arg': self.latex_interpreter}
                        return
                    self.process.wait()

                    self.do_a_bibtex_build = False
                    self.done_bibtex_build = True
                else:
                    arguments = self.build_command.split()
                    arguments.append('-output-directory=' + tmp_directory_name)
                    arguments.append(tex_file.name)
                    try:
                        self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.directory_name)
                    except FileNotFoundError:
                        self.cleanup_build_files(tex_file.name)
                        with self.result_lock:
                            self.result = {'document_controller': self.document_controller, 
                                           'error': 'interpreter_missing',
                                           'error_arg': arguments[0]}
                        return
                    _ = self.process.communicate()
                    try:
                        self.process.wait()
                    except AttributeError:
                        pass

                    # parse results
                    try:
                        self.parse_build_log(log_filename, tex_file.name)
                    except FileNotFoundError as e:
                        self.cleanup_build_files(tex_file.name)
                        with self.result_lock:
                            self.result = {'document_controller': self.document_controller, 
                                           'error': 'interpreter_not_working',
                                           'error_arg': 'log file missing'}
                        return
        
            self.parse_bibtex_log(tex_file.name[:-3] + 'blg')

            pdf_position = self.parse_synctex(tex_file.name, pdf_filename)
            if self.process != None:
                self.process = None

                if self.document_controller.settings.get_value('preferences', 'cleanup_build_files'):
                    self.cleanup_build_files(self.tex_filename)
                else:
                    self.rename_build_files(tex_file.name)

                if self.error_count == 0:
                    try: shutil.move(pdf_filename, self.new_pdf_filename)
                    except FileNotFoundError: self.new_pdf_filename = None
                else:
                    self.new_pdf_filename = None
                    pdf_position = None

                with self.result_lock:
                    self.result = {'document_controller': self.document_controller,
                                   'pdf_filename': self.new_pdf_filename, 
                                   'log_messages': self.log_messages + self.bibtex_log_messages,
                                   'pdf_position': pdf_position,
                                   'error': None,
                                   'error_arg': None}
            else:
                self.cleanup_build_files(tex_file.name)
            tex_file.close()

    def stop_building(self):
        if self.process != None:
            self.process.kill()
            self.process = None
            self.force_building_to_stop = True
    
    def get_result(self):
        return_value = None
        with self.result_lock:
            if self.result != None:
                return_value = self.result
        return return_value
    
    def parse_synctex(self, tex_name, pdf_name):
        column = 0
        arguments = ['synctex', 'view', '-i']
        arguments.append(str(self.synctex_args['line']) + ':' + str(self.synctex_args['line_offset']) + ':' + tex_name)
        arguments.append('-o')
        arguments.append(pdf_name)
        arguments.append('-x')
        arguments.append('echo "%{page+1};;;%{x};;;%{y};;;%{h};;;%{v};;;%{width};;;%{height}"')
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        raw = process.communicate()[0].decode('utf-8').split('\n')[0].split(';;;')
        process = None
        if len(raw) == 7:
            result = dict()
            result['page'] = int(raw[0])
            result['x'] = float(raw[1])
            result['y'] = float(raw[2])
            result['h'] = float(raw[3])
            result['v'] = float(raw[4])
            result['width'] = float(raw[5])
            result['height'] = float(raw[6])
            return result
        else:
            return None

    #@timer
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
                        if line.startswith('LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.'):
                            self.do_another_latex_build = True

                        elif line.startswith('Package natbib Warning: Citation(s) may have changed.'):
                            self.do_another_latex_build = True

                        elif line.startswith('No file ' + tex_filename.rsplit('.', 1)[0].rsplit('/', 1)[1] + '.bbl.') and not self.done_bibtex_build:
                            self.do_another_latex_build = True
                            self.do_a_bibtex_build = True

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

            '''
if errors none: (There were 2 error messages)
'''

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

    def cleanup_build_files(self, tex_file_name):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' , '.ilg',
                        '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc']
        for ending in file_endings:
            try: os.remove(os.path.splitext(tex_file_name)[0] + ending)
            except FileNotFoundError: pass

    def rename_build_files(self, tex_file_name):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' ,
                        '.ilg', '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc']
        for ending in file_endings:
            move_from = os.path.splitext(tex_file_name)[0] + ending
            move_to = os.path.splitext(self.tex_filename)[0] + ending
            try: shutil.move(move_from, move_to)
            except FileNotFoundError: pass

    def get_document(self):
        return self.document_controller.document



