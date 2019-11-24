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

from helpers.helpers import timer
from app.service_locator import ServiceLocator


class BuildSystem(object):

    def __init__(self):
        self.observers = set()
        self.active_queries = dict() # put computation tasks on here
        self.change_code_queue = queue.Queue() # change code for observers are put on here
        GObject.timeout_add(50, self.results_loop)
        GObject.timeout_add(50, self.change_code_loop)

    def change_code_loop(self):
        ''' notify observers '''

        if not self.change_code_queue.empty():
            change_code = self.change_code_queue.get(block=False)
            observers = change_code['observers']
            if observers == 'all':
                for observer in self.observers:
                    observer.change_notification(change_code['change_code'], self, change_code['parameter'])
            else:
                for observer in observers:
                    observer.change_notification(change_code['change_code'], self, change_code['parameter'])
        return True
    
    def register_observer(self, observer):
        ''' Observer call this method to register themselves with observable
            objects. They have themselves to implement a method
            'change_notification(change_code, parameter)' which they observable
            will call when it's state changes. '''
        
        self.observers.add(observer)

    def add_change_code(self, change_code, parameter, observers='all'):
        self.change_code_queue.put({'change_code': change_code, 'parameter': parameter, 'observers': observers})
                
    def results_loop(self):
        ''' wait for results and add them to their documents '''

        for document, query in self.active_queries.items():
            result_blob = query.get_result()
            if result_blob != None:
                document = query.get_document()
                del self.active_queries[document]
                self.add_change_code('building_finished', result_blob, {result_blob['document_controller']})
                break
        return True
    
    def add_query(self, query):
        document = query.get_document()
        if document in self.active_queries:
            query.stop_building()
            del self.active_queries[document]
            self.add_change_code('reset_timer', document, {query.document_controller})
        self.active_queries[document] = query
        thread.start_new_thread(query.build, ())
        self.add_change_code('building_started', query, {query.document_controller})
        
    def stop_building_by_document(self, document):
        if document in self.active_queries:
            query = self.active_queries[document]
            query.stop_building()
            del self.active_queries[document]
            self.add_change_code('building_stopped', document, {query.document_controller})
        
    def stop_building(self):
        for document in self.active_queries:
            query = self.active_queries[document]
            query.stop_building()
            del self.active_queries[document]
            self.add_change_code('building_stopped', document, {query.document_controller})
    

class Query(object):

    def __init__(self, text, document_controller, synctex_arguments, latex_interpreter):
        self.text = text
        self.document_controller = document_controller
        self.tex_filename = self.document_controller.document.get_filename()[:]
        self.new_pdf_filename = self.document_controller.document.get_filename().rsplit('.', 1)[0] + '.pdf'
        self.directory_name = os.path.dirname(self.document_controller.document.get_filename())
        self.process = None
        self.result = None
        self.result_lock = thread.allocate_lock()
        self.synctex_args = synctex_arguments
        self.doc_regex = ServiceLocator.get_build_log_doc_regex()
        self.item_regex = ServiceLocator.get_build_log_item_regex()
        self.badbox_line_number_regex = ServiceLocator.get_build_log_badbox_line_number_regex()
        self.other_line_number_regex = ServiceLocator.get_build_log_other_line_number_regex()
        self.force_building_to_stop = False

        self.latex_interpreter = latex_interpreter
        self.build_command_defaults = dict()
        self.build_command_defaults['latexmk'] = 'latexmk -synctex=1 -interaction=nonstopmode -pdf'
        self.build_command_defaults['pdflatex'] = 'pdflatex -synctex=1 -interaction=nonstopmode -pdf'
        self.build_command_defaults['xelatex'] = 'xelatex -synctex=1 -interaction=nonstopmode -pdf'
        self.build_command_defaults['lualatex'] = 'lualatex -synctex=1 -interaction=nonstopmode -pdf'
        self.build_command = self.build_command_defaults[self.latex_interpreter]

        self.do_another_build = True
        self.error_count = 0

    def build(self):
        with tempfile.TemporaryDirectory() as tmp_directory_name:
            tex_file = tempfile.NamedTemporaryFile(suffix='.tex', dir=tmp_directory_name)
            with open(tex_file.name, 'w') as f: f.write(self.text)
            pdf_filename = tmp_directory_name + '/' + os.path.basename(tex_file.name).rsplit('.tex', 1)[0] + '.pdf'
            log_filename = tmp_directory_name + '/' + os.path.basename(tex_file.name).rsplit('.tex', 1)[0] + '.log'

            # build pdf
            while self.do_another_build and not self.force_building_to_stop:
                arguments = self.build_command.split()
                arguments.append('-output-directory=' + tmp_directory_name)
                arguments.append(tex_file.name)
                try:
                    self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.directory_name)
                except FileNotFoundError:
                    self.cleanup_build_files(tex_file.name)
                    self.result_lock.acquire()
                    self.result = {'document_controller': self.document_controller, 
                                   'error': 'interpreter_missing',
                                   'error_arg': arguments[0]}
                    self.result_lock.release()
                    return
                self.process.wait()

                # parse results
                try: 
                    self.parse_build_log(log_filename, tex_file.name)
                except FileNotFoundError as e:
                    self.cleanup_build_files(tex_file.name)
                    self.result_lock.acquire()
                    self.result = {'document_controller': self.document_controller, 
                                   'error': 'interpreter_not_working',
                                   'error_arg': 'log file missing'}
                    self.result_lock.release()
                    return
        
            pdf_position = self.parse_synctex(tex_file.name, pdf_filename)
            if self.process != None:
                results = self.process.communicate()
                self.process = None

                if self.document_controller.settings.get_value('preferences', 'cleanup_build_files'):
                    self.cleanup_build_files(self.tex_filename)
                else:
                    self.rename_build_files(tex_file.name)

                if self.error_count == 0:
                    try: shutil.move(pdf_filename, self.new_pdf_filename)
                    except FileNotFoundError: self.new_pdf_filename = None
                else:
                    try: os.remove(self.new_pdf_filename)
                    except FileNotFoundError: pass
                    self.new_pdf_filename = None
                    pdf_position = None

                self.result_lock.acquire()
                self.result = {'document_controller': self.document_controller, 
                               'pdf_filename': self.new_pdf_filename, 
                               'log_messages': self.log_messages, 
                               'pdf_position': pdf_position,
                               'error': None,
                               'error_arg': None}
                self.result_lock.release()
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
        self.result_lock.acquire()
        if self.result != None:
            return_value = self.result
        self.result_lock.release()
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
            self.do_another_build = False
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
                            self.do_another_build = True

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
                            line_number = -1
                            self.log_messages.append(('Warning', None, filename, file_no, line_number, text))

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

    def bl_get_line_number(self, line, matchiter):
        for i in range(10):
            line_number_match = self.other_line_number_regex.search(line)
            if line_number_match != None:
                return int(line_number_match.group(2))
            else:
                try:
                    line = next(matchiter)
                except StopIteration:
                    return -1
        return -1

    def cleanup_build_files(self, tex_file_name):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' , '.ilg',
                        '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc']
        for ending in file_endings:
            try: os.remove(tex_file_name.rsplit('.tex', 1)[0] + ending)
            except FileNotFoundError: pass

    def rename_build_files(self, tex_file_name):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' ,
                        '.ilg', '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc']
        for ending in file_endings:
            move_from = tex_file_name.rsplit('.tex', 1)[0] + ending
            move_to = self.tex_filename.rsplit('.tex', 1)[0] + ending
            try: shutil.move(move_from, move_to)
            except FileNotFoundError: pass

    def get_document(self):
        return self.document_controller.document




