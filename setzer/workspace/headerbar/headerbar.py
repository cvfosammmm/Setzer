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

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib

from setzer.app.service_locator import ServiceLocator
from setzer.dialogs.dialog_locator import DialogLocator
import setzer.workspace.headerbar.headerbar_controller as headerbar_controller
import setzer.workspace.headerbar.headerbar_presenter as headerbar_presenter


class Headerbar(object):
    
    def __init__(self, workspace):
        self.workspace = workspace
        self.view = ServiceLocator.get_main_window().headerbar
        self.controller = headerbar_controller.HeaderbarController(self, self.view)
        self.presenter = headerbar_presenter.HeaderbarPresenter(self, self.view)

        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('update_recently_opened_documents', self.on_update_recently_opened_documents)
        self.workspace.connect('update_recently_opened_session_files', self.on_update_recently_opened_session_files)
        self.workspace.connect('root_state_change', self.on_root_state_change)

        self.presenter.activate_welcome_screen_mode()

    def on_document_removed(self, workspace, document):
        if self.workspace.active_document == None:
            self.presenter.set_build_button_state()
            self.presenter.activate_welcome_screen_mode()

    def on_new_active_document(self, workspace, document):
        self.presenter.set_build_button_state()
        if document.is_latex_document():
            self.presenter.activate_latex_document_mode()
        else:
            self.presenter.activate_other_document_mode()

    def on_root_state_change(self, workspace, state):
        self.presenter.set_build_button_state()

    def on_update_recently_opened_documents(self, workspace, recently_opened_documents):
        self.presenter.update_recently_opened_documents(recently_opened_documents)

    def on_update_recently_opened_session_files(self, workspace, recently_opened_session_files):
        self.presenter.update_recently_opened_session_files(recently_opened_session_files)

    def on_restore_session_click(self, button, parameter):
        ServiceLocator.get_popover_manager().popdown()

        if parameter == None:
            DialogLocator.get_dialog('open_session').run(self.restore_session_cb)
        else:
            self.restore_session_cb(parameter)

    def restore_session_cb(self, filename):
        if filename == None: return

        documents = self.workspace.get_all_documents()
        unsaved_documents = self.workspace.get_unsaved_documents()
        if unsaved_documents:
            dialog = DialogLocator.get_dialog('close_confirmation')
            dialog.run({'unsaved_documents': unsaved_documents, 'documents': documents, 'session_filename': filename}, self.close_confirmation_cb)
        else:
            if documents != None:
                for document in documents:
                    self.workspace.remove_document(document)
            self.workspace.load_documents_from_session_file(filename)

    def close_confirmation_cb(self, parameters, response):
        not_save_to_close_documents = response['not_save_to_close_documents']

        if len(not_save_to_close_documents) == 0:
            if parameters['documents'] != None:
                for document in parameters['documents']:
                    self.workspace.remove_document(document)
            self.workspace.load_documents_from_session_file(parameters['session_filename'])


