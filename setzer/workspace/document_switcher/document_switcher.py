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

from setzer.helpers.observable import Observable
import setzer.workspace.document_switcher.item.document_switcher_item as document_switcher_item
import setzer.workspace.document_switcher.document_switcher_presenter as document_switcher_presenter
import setzer.workspace.document_switcher.document_switcher_controller as document_switcher_controller
from setzer.dialogs.dialog_locator import DialogLocator


class DocumentSwitcher(Observable):

    def __init__(self, workspace):
        Observable.__init__(self)
        self.workspace = workspace
        self.items = dict()

        self.presenter = document_switcher_presenter.DocumentSwitcherPresenter(self, self.workspace)
        self.controller = document_switcher_controller.DocumentSwitcherController(self, self.workspace)

        # can be normal or selection
        self.mode = 'normal'

        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('root_state_change', self.on_root_state_changed)

    def set_mode(self, mode):
        self.mode = mode
        self.add_change_code('docswitcher_mode_change', mode)

    def on_new_document(self, workspace, document):
        item = document_switcher_item.DocumentSwitcherItem(document)
        item.view.document_close_button.connect('clicked', self.on_close_clicked, document)
        item.set_is_root(document.get_is_root())
        self.items[document] = item
        self.add_change_code('new_item', item)
        document.connect('filename_change', self.on_name_change)
        document.connect('displayname_change', self.on_name_change)
        document.content.connect('modified_changed', self.on_modified_changed)
        document.connect('is_root_changed', self.on_is_root_changed)

    def on_document_removed(self, workspace, document):
        item = self.items[document]
        del(self.items[document])
        self.add_change_code('item_removed', item)
        document.disconnect('filename_change', self.on_name_change)
        document.disconnect('displayname_change', self.on_name_change)
        document.content.disconnect('modified_changed', self.on_modified_changed)
        document.disconnect('is_root_changed', self.on_is_root_changed)

    def on_new_active_document(self, workspace, document):
        self.add_change_code('new_active_document', document)

    def on_name_change(self, document, name=None):
        self.update_item(document)

    def on_is_root_changed(self, document, is_root):
        self.items[document].set_is_root(is_root)
        self.add_change_code('root_state_changed')

    def on_root_state_changed(self, workspace, state):
        self.add_change_code('root_state_changed')

    def on_modified_changed(self, content):
        self.update_item(content.document)

    def update_item(self, document):
        self.items[document].view.set_name(document.get_displayname(), document.content.get_modified())
        if document == self.workspace.get_active_document():
            self.presenter.show_document_name(document)

    def on_close_clicked(self, button, document):
        if document.content.get_modified():
            active_document = self.workspace.get_active_document()
            if document != active_document:
                previously_active_document = active_document
                self.workspace.set_active_document(document)
            else:
                previously_active_document = None

            self.presenter.view.popdown()
            dialog = DialogLocator.get_dialog('close_confirmation')
            dialog.run({'unsaved_documents': [document], 'document': document, 'previously_active_document': previously_active_document}, self.on_close_document_callback)
            return True
        else:
            self.workspace.remove_document(document)

    def on_close_document_callback(self, parameters, response):
        not_save_to_close = response['not_save_to_close_documents']
        if parameters['document'] not in not_save_to_close:
            self.workspace.remove_document(parameters['document'])
        if parameters['previously_active_document'] != None:
            self.workspace.set_active_document(parameters['previously_active_document'])
            self.presenter.view.popup()


