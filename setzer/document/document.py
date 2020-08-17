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

import os.path
import time

import setzer.document.document_builder as document_builder
import setzer.document.document_controller as document_controller
import setzer.document.document_presenter as document_presenter
import setzer.document.shortcutsbar.shortcutsbar_presenter as shortcutsbar_presenter
import setzer.document.document_viewgtk as document_view
import setzer.document.document_switcher_item.document_switcher_item as document_switcher_item
import setzer.document.build_widget.build_widget as build_widget
import setzer.document.search.search as search
import setzer.document.autocomplete.autocomplete as autocomplete
import setzer.document.spellchecker.spellchecker as spellchecker
import setzer.document.code_folding.code_folding as code_folding
import setzer.document.parser.latex_parser as latex_parser
import setzer.document.parser.bibtex_parser as bibtex_parser
import setzer.document.preview.preview as preview
import setzer.document.state_manager.state_manager_latex as state_manager_latex
import setzer.document.state_manager.state_manager_bibtex as state_manager_bibtex
import setzer.document.source_buffer.source_buffer as source_buffer
from setzer.helpers.observable import Observable
from setzer.app.service_locator import ServiceLocator


class Document(Observable):

    def __init__(self):
        Observable.__init__(self)

        self.settings = ServiceLocator.get_settings()

        self.displayname = ''
        self.filename = None
        self.save_date = None
        self.last_activated = 0

        self.parser = None
        self.source_buffer = source_buffer.SourceBuffer(self)
        self.source_buffer.connect('changed', self.on_buffer_changed)

    def set_search_text(self, search_text):
        self.source_buffer.search_settings.set_search_text(search_text)
        
    def on_buffer_changed(self, buffer):
        try: self.code_folding.on_buffer_changed(buffer)
        except AttributeError: pass

        if self.parser != None:
            self.parser.on_buffer_changed()
        if self.source_buffer.get_end_iter().get_offset() > 0:
            self.add_change_code('document_not_empty')
        else:
            self.add_change_code('document_empty')

    def set_dark_mode(self, dark_mode):
        self.set_use_dark_scheme(dark_mode)

    def set_use_dark_scheme(self, use_dark_scheme):
        self.get_buffer().set_use_dark_scheme(use_dark_scheme)

    def get_buffer(self):
        return self.source_buffer

    def get_search_context(self):
        return self.source_buffer.search_context

    def set_filename(self, filename):
        self.filename = filename
        self.add_change_code('filename_change', filename)

    def get_filename(self):
        return self.filename
        
    def get_displayname(self):
        if self.filename != None:
            return self.get_filename()
        else:
            return self.displayname
        
    def set_displayname(self, displayname):
        self.displayname = displayname
        self.add_change_code('displayname_change')
        
    def get_last_activated(self):
        return self.last_activated
        
    def set_last_activated(self, date):
        self.last_activated = date
        
    def get_modified(self):
        return self.get_buffer().get_modified()
        
    def populate_from_filename(self):
        if self.filename == None: return False
        if not os.path.isfile(self.filename):
            self.filename = None
            return False
        if self.get_buffer() == None: return False

        with open(self.filename) as f:
            text = f.read()
        source_buffer = self.get_buffer()
        source_buffer.begin_not_undoable_action()
        source_buffer.set_text(text)
        source_buffer.end_not_undoable_action()
        source_buffer.set_modified(False)
        source_buffer.place_cursor(source_buffer.get_start_iter())
        self.update_save_date()
        return True
                
    def save_to_disk(self):
        if self.filename == None: return False
        if self.get_buffer() == None: return False
        else:
            text = self.get_text()
            if text != None:
                with open(self.filename, 'w') as f:
                    f.write(text)
                self.update_save_date()
                self.get_buffer().set_modified(False)

    def update_save_date(self):
        self.save_date = os.path.getmtime(self.filename)

    def get_text(self):
        buff = self.get_buffer()
        if buff != None:
            return buff.get_text(buff.get_start_iter(), buff.get_end_iter(), True)
        return None

    def set_initial_folded_regions(self, folded_regions):
        self.code_folding.set_initial_folded_regions(folded_regions)
        
    def place_cursor(self, text_iter):
        buff = self.get_buffer()
        buff.place_cursor(text_iter)
        self.view.source_view.scroll_to_mark(buff.get_insert(), 0, False, 0, 0)

    def insert_before_document_end(self, text):
        self.get_buffer().insert_before_document_end(text)

    def add_packages(self, packages):
        self.get_buffer().add_packages(packages)

    def remove_packages(self, packages):
        self.get_buffer().remove_packages(packages)

    def insert_text_at_iter(self, insert_iter, text, indent_lines=True):
        self.get_buffer().insert_text_at_iter(insert_iter, text, indent_lines)

    def insert_text_at_cursor(self, text, indent_lines=True):
        self.get_buffer().insert_text_at_cursor(text, indent_lines)

    def replace_range(self, start_iter, end_iter, text, indent_lines=True):
        self.get_buffer().replace_range(start_iter, end_iter, text, indent_lines)

    def insert_before_after(self, before, after):
        self.get_buffer().insert_before_after(before, after)

    def comment_uncomment(self):
        if self.is_latex_document():
            self.get_buffer().comment_uncomment()


class LaTeXDocument(Document):

    def __init__(self):
        Document.__init__(self)
        self.is_master = False
        self.has_visible_build_system = False

        # possible states: idle, ready_for_building
        # building_in_progress, building_to_stop
        self.build_state = 'idle'

        # possible values: build, forward_sync, build_and_forward_sync
        self.build_mode = 'build_and_forward_sync'
        self.build_pathname = None
        self.can_forward_sync = False
        self.can_backward_sync = False
        self.backward_sync_data = None

        self.preview = preview.Preview(self)
        self.state_manager = state_manager_latex.StateManagerLaTeX(self)
        self.view = document_view.DocumentView(self, self.source_buffer.view)
        self.document_switcher_item = document_switcher_item.DocumentSwitcherItemLaTeX(self)
        self.search = search.Search(self, self.view, self.view.search_bar)

        self.build_log_items = list()
        self.has_been_built = False
        self.last_build_start_time = None
        self.build_time = None
        self.build_widget = build_widget.BuildWidget(self)

        self.autocomplete = autocomplete.Autocomplete(self, self.view)
        self.builder = document_builder.DocumentBuilder(self)
        self.presenter = document_presenter.DocumentPresenter(self, self.view)
        self.shortcutsbar = shortcutsbar_presenter.ShortcutsbarPresenter(self, self.view)
        self.code_folding = code_folding.CodeFolding(self)
        self.controller = document_controller.DocumentController(self, self.view)

        self.spellchecker = spellchecker.Spellchecker(self.view.source_view)
        self.parser = latex_parser.LaTeXParser(self)

        self.update_can_forward_sync()
        self.update_can_backward_sync()

    def change_build_state(self, state):
        self.build_state = state

        if self.build_mode in ['build', 'build_and_forward_sync']:
            if state == 'ready_for_building':
                self.build_time = None
            elif state == 'building_in_progress':
                self.last_build_start_time = time.time()
            elif state == 'building_to_stop':
                pass
            elif state == 'idle':
                pass
            self.add_change_code('build_state_change', self.build_state)
        else:
            self.add_change_code('build_state_change', self.build_state)

    def show_build_state(self, message):
        self.add_change_code('build_state', message)

    def get_build_state(self):
        return self.build_state

    def set_build_mode(self, mode):
        self.build_mode = mode

    def get_build_mode(self):
        return self.build_mode

    def set_build_pathname(self, pathname):
        self.build_pathname = pathname
        self.update_can_forward_sync()
        self.update_can_backward_sync()

    def update_can_forward_sync(self):
        if self.build_pathname != None and self.preview.pdf_loaded:
            self.can_forward_sync = True
        else:
            self.can_forward_sync = False
        self.add_change_code('can_forward_sync_changed', self.can_forward_sync)

    def update_can_backward_sync(self):
        if self.build_pathname != None and self.preview.pdf_loaded:
            self.can_backward_sync = True
        else:
            self.can_backward_sync = False
        self.add_change_code('can_backward_sync_changed', self.can_backward_sync)

    def forward_sync(self):
        if self.can_forward_sync:
            self.set_build_mode('forward_sync')
            self.start_building()

    def backward_sync(self, page, x, y, word, context):
        if self.can_backward_sync:
            self.backward_sync_data = {'page': page, 'x': x, 'y': y, 'word': word, 'context': context}
            self.set_build_mode('backward_sync')
            self.start_building()

    def build_and_forward_sync(self):
        self.set_build_mode('build_and_forward_sync')
        self.start_building()

    def start_building(self):
        if self.build_mode == 'forward_sync' and self.build_pathname == None: return
        if self.build_mode == 'backward_sync' and self.backward_sync_data == None: return
        if self.filename == None: return

        self.change_build_state('ready_for_building')

    def stop_building(self):
        self.change_build_state('building_to_stop')
        
    def cleanup_build_files(self):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' ,'.ilg', '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc', '.ist', '.glo', '.glg', '.acn', '.alg', '.gls', '.acr']
        for ending in file_endings:
            filename = os.path.splitext(self.get_filename())[0] + ending
            try: os.remove(filename)
            except FileNotFoundError: pass
        self.add_change_code('cleaned_up_build_files')

    def set_is_master(self, is_master):
        self.is_master = is_master
        self.add_change_code('master_state_change', is_master)

    def set_has_visible_build_system(self, has_visible_build_system):
        if self.has_visible_build_system != has_visible_build_system:
            self.has_visible_build_system = has_visible_build_system
            self.add_change_code('build_system_visibility_change', has_visible_build_system)

    def set_invert_pdf(self, invert_pdf):
        self.preview.set_invert_pdf(invert_pdf)

    def set_synctex_position(self, position):
        self.get_buffer().set_synctex_position(position)

    def get_folded_regions(self):
        return self.code_folding.get_folded_regions()

    def get_file_ending(self):
        return 'tex'

    def is_latex_document(self):
        return True

    def is_bibtex_document(self):
        return False

    def get_gsv_language_name(self):
        return 'latex'


class BibTeXDocument(Document):

    def __init__(self):
        Document.__init__(self)
        self.is_master = False

        self.state_manager = state_manager_bibtex.StateManagerBibTeX(self)
        self.view = document_view.DocumentView(self, self.source_buffer.view)
        self.document_switcher_item = document_switcher_item.DocumentSwitcherItemBibTeX(self)
        self.search = search.Search(self, self.view, self.view.search_bar)

        self.autocomplete = None
        self.builder = None
        self.presenter = document_presenter.DocumentPresenter(self, self.view)
        self.shortcutsbar = shortcutsbar_presenter.ShortcutsbarPresenter(self, self.view)
        self.controller = document_controller.DocumentController(self, self.view)

        self.spellchecker = spellchecker.Spellchecker(self.view.source_view)
        self.parser = bibtex_parser.BibTeXParser()

    def get_folded_regions(self):
        return []

    def get_file_ending(self):
        return 'bib'

    def is_latex_document(self):
        return False

    def is_bibtex_document(self):
        return True

    def get_gsv_language_name(self):
        return 'bibtex'


