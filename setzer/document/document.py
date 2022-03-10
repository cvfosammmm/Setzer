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

import setzer.document.content.content as content
import setzer.document.state_manager.state_manager as state_manager
import setzer.document.document_controller as document_controller
import setzer.document.document_presenter as document_presenter
import setzer.document.context_menu.context_menu as context_menu
import setzer.document.document_switcher_item.document_switcher_item as document_switcher_item
import setzer.document.document_viewgtk as document_view
import setzer.document.search.search as search
import setzer.document.shortcutsbar.shortcutsbar_presenter as shortcutsbar_presenter
import setzer.document.spellchecker.spellchecker as spellchecker
import setzer.document.gutter.gutter as gutter
import setzer.document.line_numbers.line_numbers as line_numbers
import setzer.document.preview.preview as preview
import setzer.document.build_system.build_system as build_system
import setzer.document.build_widget.build_widget as build_widget
import setzer.document.autocomplete.autocomplete as autocomplete
import setzer.document.code_folding.code_folding as code_folding
import setzer.document.preview.preview as preview
import setzer.document.parser.parser_dummy as parser_dummy
import setzer.document.parser.parser_bibtex as parser_bibtex
import setzer.document.parser.parser_latex as parser_latex
from setzer.helpers.observable import Observable
from setzer.app.service_locator import ServiceLocator


class Document(Observable):

    def __init__(self, document_type):
        Observable.__init__(self)

        self.font_manager = ServiceLocator.get_font_manager()

        self.document_type = document_type
        self.displayname = ''
        self.filename = None
        self.save_date = None
        self.deleted_on_disk_dialog_shown_after_last_save = False
        self.last_activated = 0
        self.dark_mode = False
        self.is_root = False
        self.root_is_set = False

        self.symbols = dict()
        self.symbols['bibitems'] = set()
        self.symbols['labels'] = set()
        self.symbols['labels_with_offset'] = list()
        self.symbols['included_latex_files'] = set()
        self.symbols['bibliographies'] = set()
        self.symbols['packages'] = set()
        self.symbols['packages_detailed'] = dict()
        self.symbols['blocks'] = list()

        self.content = content.Content(self.document_type, self)
        if self.document_type == 'bibtex': self.parser = parser_bibtex.ParserBibTeX(self)
        elif self.document_type == 'latex': self.parser = parser_latex.ParserLaTeX(self)
        else: self.parser = parser_dummy.ParserDummy(self)

        self.view = document_view.DocumentView(self)
        self.gutter = gutter.Gutter(self, self.view)
        self.search = search.Search(self, self.view, self.view.search_bar)
        self.spellchecker = spellchecker.Spellchecker(self.view.source_view)
        self.document_switcher_item = document_switcher_item.DocumentSwitcherItem(self)
        self.context_menu = context_menu.ContextMenu(self, self.view)
        self.shortcutsbar = shortcutsbar_presenter.ShortcutsbarPresenter(self, self.view)

        self.presenter = document_presenter.DocumentPresenter(self, self.view)
        self.controller = document_controller.DocumentController(self, self.view)

        self.line_numbers = line_numbers.LineNumbers(self, self.view)

        self.state_manager = state_manager.StateManager(self)

    def add_latex_only_modules(self):
        self.preview = preview.Preview(self)
        self.autocomplete = autocomplete.Autocomplete(self, self.view)
        self.build_system = build_system.BuildSystem(self)
        self.build_widget = build_widget.BuildWidget(self)
        self.code_folding = code_folding.CodeFolding(self)

    def set_dark_mode(self, dark_mode):
        self.dark_mode = dark_mode
        self.content.set_use_dark_scheme(dark_mode)

    def get_document_type(self):
        return self.document_type

    def set_filename(self, filename):
        if filename == None:
            self.filename = filename
        else:
            self.filename = os.path.realpath(filename)
        self.add_change_code('filename_change', filename)

    def get_filename(self):
        return self.filename
        
    def get_dirname(self):
        if self.filename != None:
            return os.path.dirname(self.filename)
        else:
            return ''

    def get_displayname(self):
        if self.filename != None:
            return self.get_filename()
        else:
            return self.displayname
        
    def set_displayname(self, displayname):
        self.displayname = displayname
        self.add_change_code('displayname_change')

    def get_basename(self):
        if self.filename != None:
            return os.path.basename(self.filename)
        else:
            return self.displayname

    def get_last_activated(self):
        return self.last_activated
        
    def set_last_activated(self, date):
        self.last_activated = date

    def populate_from_filename(self):
        if self.filename == None: return False
        if not os.path.isfile(self.filename):
            self.set_filename(None)
            return False
        if self.content == None: return False

        with open(self.filename) as f:
            text = f.read()
        self.content.initially_set_text(text)
        self.content.place_cursor(0, 0)
        self.content.scroll_cursor_onscreen()
        self.update_save_date()
        return True
                
    def save_to_disk(self):
        if self.filename == None: return False
        if self.content == None: return False

        text = self.content.get_all_text()
        if text == None: return False

        dirname = os.path.dirname(self.filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(self.filename, 'w') as f:
            f.write(text)
        self.update_save_date()
        self.deleted_on_disk_dialog_shown_after_last_save = False
        self.content.set_modified(False)

    def update_save_date(self):
        self.save_date = os.path.getmtime(self.filename)

    def get_changed_on_disk(self):
        return self.save_date <= os.path.getmtime(self.filename) - 0.001

    def get_deleted_on_disk(self):
        return not os.path.isfile(self.filename)

    def set_root_state(self, is_root, root_is_set):
        self.is_root = is_root
        self.root_is_set = root_is_set
        self.add_change_code('is_root_changed', is_root)

    def is_latex_document(self):
        return self.document_type == 'latex'

    def is_bibtex_document(self):
        return self.document_type == 'bibtex'

    def get_is_root(self):
        return self.is_root

    def get_bibitems(self):
        return self.symbols['bibitems']

    def get_packages(self):
        return self.symbols['packages']

    def get_package_details(self):
        return self.symbols['packages_detailed']

    def get_blocks(self):
        return self.symbols['blocks']

    def set_blocks(self, blocks):
        self.symbols['blocks'] = blocks

    def get_included_latex_files(self):
        return self.symbols['included_latex_files']

    def get_bibliography_files(self):
        return self.symbols['bibliographies']

    def get_labels(self):
        return self.symbols['labels']

    def get_labels_with_offset(self):
        return self.symbols['labels_with_offset']


