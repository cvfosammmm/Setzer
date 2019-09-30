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
gi.require_version('GtkSource', '3.0')
from gi.repository import GtkSource

import os.path
import pickle
import base64

import model.model_buildlog as model_buildlog
from helpers.observable import *


class Document(Observable):

    def __init__(self, data_pathname, with_buffer=False, document_data=None):
        Observable.__init__(self)
        
        self.displayname = None
        self.filename = None
        self.pdf_filename = None
        self.pdf_date = None
        self.pdf_position = None
        self.last_activated = 0
        
        self.source_buffer = None
        self.search_settings = None
        self.search_context = None
        if with_buffer: self.init_buffer()
        
        self.build_log = model_buildlog.BuildLog()
        
        # possible states: idle, ready_for_building
        # building_in_progress, building_to_stop
        self.state = 'idle'
        
        self.data_pathname = data_pathname
        self.document_data = {'show_build_log': False} if document_data == None else document_data
        
    def set_search_text(self, search_text):
        self.search_settings.set_search_text(search_text)
        
    def init_buffer(self):
        self.source_buffer = GtkSource.Buffer()

        # set source language for syntax highlighting
        self.source_language_manager = GtkSource.LanguageManager()
        self.source_language_manager.set_search_path((os.path.dirname(__file__) + '/../resources/gtksourceview/language-specs',))
        self.source_language = self.source_language_manager.get_language('latex')
        self.source_buffer.set_language(self.source_language)
        self.source_buffer.set_highlight_matching_brackets(False)
        
        self.source_style_scheme_manager = GtkSource.StyleSchemeManager()
        self.source_style_scheme_manager.set_search_path((os.path.dirname(__file__) + '/../resources/gtksourceview/styles',))
        self.source_style_scheme_light = self.source_style_scheme_manager.get_scheme('setzer')
        self.source_style_scheme_dark = self.source_style_scheme_manager.get_scheme('setzer-dark')

        self.search_settings = GtkSource.SearchSettings()
        self.search_context = GtkSource.SearchContext.new(self.source_buffer, self.search_settings)
        self.search_context.set_highlight(True)
        
    def set_use_dark_scheme(self, use_dark_scheme):
        if use_dark_scheme: self.source_buffer.set_style_scheme(self.source_style_scheme_dark)
        else: self.source_buffer.set_style_scheme(self.source_style_scheme_light)
    
    def get_buffer(self):
        return self.source_buffer

    def get_filename(self):
        return self.filename
        
    def set_filename(self, filename):
        self.filename = filename
        self.add_change_code('filename_change', filename)
        if self.filename != None:
            pathname = self.filename.rsplit('/', 1)
            pdf_filename = pathname[0] + '/' + pathname[1].rsplit('.', 1)[0] + '.pdf'
            if os.path.exists(pdf_filename):
                self.set_pdf_filename(pdf_filename)
        
    def get_pdf_filename(self):
        return self.pdf_filename
        
    def set_pdf_filename(self, pdf_filename):
        self.pdf_filename = pdf_filename
        self.set_pdf_date()
        self.add_change_code('pdf_update', pdf_filename)
        
    def set_pdf(self, pdf_filename, pdf_position=None):
        self.pdf_filename = pdf_filename
        self.set_pdf_date()
        self.pdf_position = pdf_position
        self.add_change_code('pdf_update', pdf_filename)
        
    def get_pdf_position(self):
        return self.pdf_position
        
    def set_pdf_date(self):
        if self.pdf_filename != None:
            self.pdf_date = os.path.getmtime(self.pdf_filename)
    
    def get_pdf_date(self):
        return self.pdf_date
        
    def get_displayname(self):
        if self.filename != None:
            return self.get_filename()
        else:
            return self.displayname
        
    def set_displayname(self, displayname):
        self.displayname = displayname
        
    def set_show_build_log(self, show_build_log):
        if show_build_log != self.document_data['show_build_log']:
            self.document_data['show_build_log'] = show_build_log
            self.add_change_code('show_build_log_state_change', show_build_log)

    def get_show_build_log(self):
        return self.document_data['show_build_log']
        
    def get_last_activated(self):
        return self.last_activated
        
    def set_last_activated(self, date):
        self.last_activated = date
        
    def get_modified(self):
        return self.get_buffer().get_modified()
        
    def populate_from_filename(self):
        if self.filename == None: return False
        if not os.path.isfile(self.filename): return False
        if self.get_buffer() == None: return False

        try: filehandle = open(self.data_pathname + '/' + base64.urlsafe_b64encode(str.encode(self.filename)).decode() + '.pickle', 'rb')
        except IOError: pass
        else:
            try: data = pickle.load(filehandle)
            except EOFError: pass
            else:
                self.set_show_build_log(data['show_build_log'])
    
        with open(self.filename) as f:
            text = f.read()
            source_buffer = self.get_buffer()
            source_buffer.begin_not_undoable_action()
            source_buffer.set_text(text)
            source_buffer.end_not_undoable_action()
            source_buffer.set_modified(False)
            source_buffer.place_cursor(source_buffer.get_start_iter())
                
    def save_to_disk(self):
        if self.filename == None: return False
        if self.get_buffer() == None: return False
        else:
            buff = self.get_buffer()
            text = buff.get_text(buff.get_start_iter(), buff.get_end_iter(), True)
            with open(self.filename, 'w') as f:
                f.write(text)
                buff.set_modified(False)
                
    def parse_result_blob(self):
        result = MarkdownResult(self.result_blob)
        self.set_result(result)
        
    def get_state(self):
        return self.state

    def change_state(self, state):
        self.state = state
        self.add_change_code('document_state_change', self.state)

    def save_document_data(self):
        if self.filename != None:
            try: filehandle = open(self.data_pathname + '/' + base64.urlsafe_b64encode(str.encode(self.filename)).decode() + '.pickle', 'wb')
            except IOError: pass
            else: pickle.dump(self.document_data, filehandle)
    

