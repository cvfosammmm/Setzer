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

    def __init__(self, text, document_controller, synctex_arguments, build_command):
        self.text = text
        self.document_controller = document_controller
        self.tex_filename = self.document_controller.document.get_filename()[:]
        self.new_pdf_filename = self.document_controller.document.get_filename().rsplit('.', 1)[0] + '.pdf'
        self.directory_name = os.path.dirname(self.document_controller.document.get_filename())
        self.process = None
        self.result = None
        self.result_lock = thread.allocate_lock()
        self.log_messages = list()
        self.synctex_args = synctex_arguments
        self.build_command = build_command
        self.doc_regex = ServiceLocator.get_build_log_doc_regex()
        self.item_regex = ServiceLocator.get_build_log_item_regex()

    def build(self):
        # create temporary files
        tex_file = tempfile.NamedTemporaryFile(suffix='.tex', dir=self.directory_name)
        with open(tex_file.name, 'w') as f: f.write(self.text)
        pdf_filename = self.directory_name + '/' + os.path.basename(tex_file.name).rsplit('.tex', 1)[0] + '.pdf'
        log_filename = self.directory_name + '/' + os.path.basename(tex_file.name).rsplit('.tex', 1)[0] + '.log'

        # build pdf
        arguments = self.build_command.split()
        arguments = list(map(lambda arg: arg.replace('%OUTDIR', self.directory_name), arguments))
        arguments = list(map(lambda arg: arg.replace('%FILENAME', tex_file.name), arguments))
        try:
            self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
        try: self.parse_build_log(log_filename)
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

            try: shutil.move(pdf_filename, self.new_pdf_filename)
            except FileNotFoundError: self.new_pdf_filename = None

            if self.document_controller.settings.get_value('preferences', 'cleanup_build_files'):
                self.cleanup_build_files(tex_file.name)
            else:
                self.rename_build_files(tex_file.name)

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

    def parse_build_log(self, log_filename):
        try: file = open(log_filename, 'rb')
        except FileNotFoundError as e: raise e
        else:
            text = file.read().decode('utf-8', errors='ignore')
            doc_texts = dict()
            for match in self.doc_regex.finditer(text):
                filename = match.group(1)
                doc_texts[filename] = match.group(2)
            doc_texts[self.tex_filename] = self.doc_regex.sub('', text)
            for filename, text in doc_texts.items():
                for match in self.item_regex.finditer(text):
                    line = match.group(1)

                    if line.startswith('Overfull \hbox'):
                        line_number = line.rsplit(' ', 1)[1].split('--')[0]
                        self.log_messages.append(('Badbox', filename, line_number, line.split('\n')[0]))

                    elif line.startswith('Underfull \hbox'):
                        line_number = line.rsplit(' ', 1)[1].split('--')[0]
                        self.log_messages.append(('Badbox', filename, line_number, line.split('\n')[0]))

                    elif line.startswith('!'):
                        if line.find('l.') != -1:
                            line_number = line.rsplit('l.', 1)[1].split(' ')[0]
                            line = line.split('\n')
                            if line[0].startswith('! Undefined control sequence'):
                                line = ' '.join([line[0], line[1].rsplit(' ', 1)[1]])
                            else:
                                line = line[0]
                            self.log_messages.append(('Error', filename, line_number, line))

                    elif line.startswith('LaTeX Warning:'):
                        pass

                    elif line.startswith('LaTeX Font Warning:'):
                        pass

    def cleanup_build_files(self, tex_file_name):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' , '.ilg',
                        '.ind', '.log', '.nav', '.out', '.pdf', '.snm', '.synctex.gz', '.toc']
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




