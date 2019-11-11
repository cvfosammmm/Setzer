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

from app.service_locator import ServiceLocator


class DocumentSwitcherController(object):
    ''' Mediator between workspace and view. '''
    
    def __init__(self, document_switcher, workspace):
        self.document_switcher = document_switcher
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.view = self.main_window.headerbar.open_docs_popover

        self.observe_document_switcher_view()

    def observe_document_switcher_view(self):
        self.main_window.headerbar.open_docs_popover.document_list.connect('add', self.on_doclist_row_added)
        self.main_window.headerbar.open_docs_popover.document_list.connect('row-activated', self.on_doclist_row_activated)
        self.main_window.headerbar.open_docs_popover.connect('closed', self.on_doclist_row_popdown)
        self.view.set_master_document_button.connect('clicked', self.set_selection_mode)
        self.view.unset_master_document_button.connect('clicked', self.unset_master_document)

    def on_doclist_row_added(self, doclist, row, data=None):
        row.document_close_button.connect('clicked', self.on_doclist_close_clicked, row.document)

    def on_doclist_row_activated(self, box, row, data=None):
        if self.view.in_selection_mode:
            self.document_switcher.set_mode('normal')
            self.workspace.set_one_document_master(row.document)
        else:
            self.main_window.headerbar.open_docs_popover.popdown()
            self.workspace.set_active_document(row.document)

    def on_doclist_row_popup(self, popover, data=None):
        self.document_switcher.set_mode('normal')

    def on_doclist_row_popdown(self, popover, data=None):
        self.document_switcher.set_mode('normal')
        self.main_window.headerbar.open_docs_popover.document_list.unselect_all()

    def set_selection_mode(self, action, parameter=None):
        self.document_switcher.set_mode('selection')

    def unset_master_document(self, action, parameter=None):
        self.document_switcher.set_mode('normal')
        self.workspace.unset_master_document()

    def on_doclist_close_clicked(self, button_object, document):
        if document.get_modified():
            dialog = ServiceLocator.get_dialog('close_confirmation')
            not_save_to_close = dialog.run([document])['not_save_to_close_documents']
            if document not in not_save_to_close:
                self.workspace.remove_document(document)
        else:
            self.workspace.remove_document(document)
        

