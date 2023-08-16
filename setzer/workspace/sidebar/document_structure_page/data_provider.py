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

import time
import os.path

from setzer.helpers.observable import Observable
import setzer.helpers.path as path_helpers


class DataProvider(Observable):

    def __init__(self, sidebar, workspace):
        Observable.__init__(self)

        self.workspace = workspace
        self.document = None

        self.integrated_includes = dict()

        self.signal_id = sidebar.view.connect('realize', self.on_realize)
        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('root_state_change', self.on_root_state_change)

    def on_new_document(self, workspace, document=None):
        self.update_data()

    def on_document_removed(self, workspace, document=None):
        self.update_data()

    def on_new_active_document(self, workspace, document=None):
        self.set_document()

    def on_root_state_change(self, workspace, root_state=None):
        self.set_document()

    def on_buffer_changed(self, document, parameter=None):
        self.update_data()

    def on_is_root_changed(self, document, parameter=None):
        self.update_data()

    def on_realize(self, view, *parameter):
        view.disconnect(self.signal_id)
        self.update_data()

    def set_document(self):
        document = self.workspace.get_root_or_active_latex_document()
        if document != self.document:
            if self.document != None:
                self.document.disconnect('changed', self.on_buffer_changed)
                self.document.disconnect('is_root_changed', self.on_is_root_changed)
            self.document = document
            if self.document != None:
                self.document.connect('changed', self.on_buffer_changed)
                self.document.connect('is_root_changed', self.on_is_root_changed)
            self.update_data()

    def update_data(self, *params):
        if self.document == None: return

        self.update_integrated_includes()
        self.add_change_code('data_updated')

    def update_integrated_includes(self):
        integrated_includes = dict()
        if self.document.get_is_root():
            for filename, offset in self.document.parser.symbols['included_latex_files']:
                filename = path_helpers.get_abspath(filename, self.document.get_dirname())
                document = self.workspace.get_document_by_filename(filename)
                if document:
                    integrated_includes[document] = (document, offset)
                    document.connect('changed', self.on_buffer_changed)
        for document in self.integrated_includes:
            if document not in integrated_includes:
                document.disconnect('changed', self.on_buffer_changed)
        self.integrated_includes = integrated_includes

    def get_includes(self):
        includes = list()
        for filename, offset in self.document.parser.symbols['included_latex_files']:
            filename = path_helpers.get_abspath(filename, self.document.get_dirname())
            document = self.workspace.get_document_by_filename(filename)
            if document and document in self.integrated_includes:
                includes.append({'filename': filename, 'offset': offset, 'document': document})
            else:
                includes.append({'filename': filename, 'offset': offset, 'document': None})
        return includes


