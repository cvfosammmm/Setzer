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

from setzer.app.service_locator import ServiceLocator


class PreviewPanelPresenter(object):
    
    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.notebook = self.main_window.preview_panel.notebook

        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('root_state_change', self.on_root_state_change)

        self.activate_blank_page()

    def on_new_document(self, workspace, document):
        if document.is_latex_document():
            self.notebook.append_page(document.preview.view, None)

    def on_document_removed(self, workspace, document):
        if document.is_latex_document():
            self.notebook.remove_page(self.notebook.page_num(document.preview.view))

    def on_new_active_document(self, workspace, document):
        self.set_preview_document()

    def on_root_state_change(self, workspace, root_state):
        self.set_preview_document()

    def activate_blank_page(self):
        self.notebook.set_current_page(0)

    def set_preview_document(self):
        document = self.workspace.get_root_or_active_latex_document()
        if document == None:
            self.activate_blank_page()
        else:
            self.notebook.set_current_page(self.notebook.page_num(document.preview.view))


