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

from setzer.app.service_locator import ServiceLocator


class PreviewPanelPresenter(object):
    
    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.notebook = self.main_window.preview_panel.notebook
        self.notebook_page_ids_by_document = dict()

        self.workspace.register_observer(self)
        self.activate_blank_page()

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_document':
            document = parameter
            if document.is_latex_document():
                page_id = self.notebook.append_page(document.preview.view, None)
                self.notebook_page_ids_by_document[document] = page_id

        if change_code == 'document_removed':
            document = parameter
            if document.is_latex_document():
                page_id = self.notebook_page_ids_by_document[document]
                self.notebook.remove_page(page_id)
                del(self.notebook_page_ids_by_document[document])

        if change_code == 'new_active_document':
            self.set_preview_document()

        if change_code == 'master_state_change':
            self.set_preview_document()

    def activate_blank_page(self):
        self.notebook.set_current_page(0)

    def set_preview_document(self):
        if self.workspace.get_active_document() == None:
            self.activate_blank_page()
        else:
            if self.workspace.master_document != None:
                page_id = self.notebook_page_ids_by_document[self.workspace.master_document]
                self.notebook.set_current_page(page_id)
            elif self.workspace.active_document.is_latex_document():
                page_id = self.notebook_page_ids_by_document[self.workspace.active_document]
                self.notebook.set_current_page(page_id)
            else:
                self.activate_blank_page()


