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

from setzer.document.document import Document
import setzer.document.document_controller as document_controller
import setzer.document.document_presenter as document_presenter
import setzer.document.context_menu.context_menu as context_menu
import setzer.document.shortcutsbar.shortcutsbar_presenter as shortcutsbar_presenter
import setzer.document.document_viewgtk as document_view
import setzer.document.document_switcher_item.document_switcher_item as document_switcher_item
import setzer.document.search.search as search
import setzer.document.spellchecker.spellchecker as spellchecker
import setzer.document.parser.bibtex_parser as bibtex_parser
import setzer.document.preview.preview as preview
import setzer.document.state_manager.state_manager_bibtex as state_manager_bibtex
import setzer.document.source_buffer.source_buffer as source_buffer
from setzer.helpers.observable import Observable
from setzer.app.service_locator import ServiceLocator


class DocumentBibTeX(Document):

    def __init__(self):
        Document.__init__(self)
        self.is_master = False

        self.state_manager = state_manager_bibtex.StateManagerBibTeX(self)
        self.view = document_view.DocumentView(self, self.source_buffer.view)
        self.document_switcher_item = document_switcher_item.DocumentSwitcherItem(self)
        self.search = search.Search(self, self.view, self.view.search_bar)

        self.presenter = document_presenter.DocumentPresenter(self, self.view)
        self.shortcutsbar = shortcutsbar_presenter.ShortcutsbarPresenter(self, self.view)
        self.controller = document_controller.DocumentController(self, self.view)
        self.context_menu = context_menu.ContextMenu(self, self.view)

        self.spellchecker = spellchecker.Spellchecker(self.view.source_view)
        self.parser = bibtex_parser.BibTeXParser(self)

    def get_bibitems(self):
        labels_dict = self.parser.get_labels()
        return labels_dict['bibitems']

    def comment_uncomment(self):
        pass

    def get_folded_regions(self):
        return []

    def get_included_files(self):
        return set()

    def get_file_ending(self):
        return 'bib'

    def is_latex_document(self):
        return False

    def is_bibtex_document(self):
        return True

    def get_gsv_language_name(self):
        return 'bibtex'


