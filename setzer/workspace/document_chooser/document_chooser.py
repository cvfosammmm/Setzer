#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017-present Robert Griesel
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

from setzer.app.service_locator import ServiceLocator


class DocumentChooser(object):
    
    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.view = ServiceLocator.get_main_window().headerbar.document_chooser

        self.workspace.connect('update_recently_opened_documents', self.on_update_recently_opened_documents)

        self.view.connect('closed', self.on_document_chooser_closed)
        self.view.search_entry.connect('search-changed', self.on_document_chooser_search_changed)
        auto_suggest_box = self.view.auto_suggest_box
        auto_suggest_box.connect('row-activated', self.on_document_chooser_selection)

    def on_update_recently_opened_documents(self, workspace, recently_opened_documents):
        items = list()
        data = recently_opened_documents.values()
        for item in sorted(data, key=lambda val: -val['date']):
            items.append(os.path.split(item['filename']))
        self.view.update_autosuggest(items)

    def on_document_chooser_closed(self, document_chooser, data=None):
        document_chooser.search_entry.set_text('')
        document_chooser.auto_suggest_box.unselect_all()

    def on_document_chooser_search_changed(self, search_entry):
        self.view.search_filter()
    
    def on_document_chooser_selection(self, box, row):
        self.view.popdown()
        filename = row.folder + '/' + row.filename
        self.workspace.open_document_by_filename(filename)


