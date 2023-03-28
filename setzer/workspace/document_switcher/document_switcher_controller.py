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
from setzer.dialogs.dialog_locator import DialogLocator


class DocumentSwitcherController(object):
    ''' Mediator between workspace and view. '''
    
    def __init__(self, document_switcher, workspace):
        self.document_switcher = document_switcher
        self.workspace = workspace
        self.button = ServiceLocator.get_main_window().headerbar.center_widget
        self.view = self.button.open_docs_popover

        self.observe_document_switcher_view()

    def observe_document_switcher_view(self):
        self.view.document_list.connect('add', self.on_doclist_row_added)
        self.view.document_list.connect('row-activated', self.on_doclist_row_activated)
        self.view.document_list.connect('button-release-event', self.on_doclist_row_button_release)
        self.view.connect('closed', self.on_doclist_row_popdown)
        self.view.set_root_document_button.connect('clicked', self.set_selection_mode)
        self.view.unset_root_document_button.connect('clicked', self.unset_root_document)

    def on_doclist_row_added(self, doclist, row, data=None):
        row.document_close_button.connect('clicked', self.on_doclist_close_clicked, row.document)
        row.document_close_button.connect('button-release-event', self.on_doclist_close_button_release, row.document)

    def on_doclist_row_activated(self, box, row, data=None):
        if self.view.in_selection_mode:
            self.document_switcher.set_mode('normal')
            self.workspace.set_one_document_root(row.document)
        else:
            self.view.popdown()
            self.workspace.set_active_document(row.document)

    def on_doclist_row_button_release(self, box, event, data=None):
        if event.button != 2: return False
        if self.view.in_selection_mode: return False

        row = box.get_row_at_y(event.y)
        if row.get_window() != event.window: return False

        row.document_close_button.clicked()
        return True

    def on_doclist_row_popdown(self, popover, data=None):
        self.document_switcher.set_mode('normal')
        self.view.document_list.unselect_all()

    def set_selection_mode(self, action, parameter=None):
        self.document_switcher.set_mode('selection')
        return True

    def unset_root_document(self, action, parameter=None):
        self.document_switcher.set_mode('normal')
        self.workspace.unset_root_document()

    def on_doclist_close_button_release(self, button_object, event, document):
        if event.button != 2: return False
        if self.view.in_selection_mode: return False

        button_object.clicked()
        return True

    def on_doclist_close_clicked(self, button_object, document):
        if document.content.get_modified():
            dialog = DialogLocator.get_dialog('close_confirmation')
            not_save_to_close = dialog.run([document])['not_save_to_close_documents']
            if document not in not_save_to_close:
                self.workspace.remove_document(document)
        else:
            self.workspace.remove_document(document)
        

