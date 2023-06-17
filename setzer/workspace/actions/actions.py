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
from gi.repository import GLib, Gio

from setzer.app.service_locator import ServiceLocator
from setzer.dialogs.dialog_locator import DialogLocator


class Actions(object):

    def __init__(self, workspace):
        self.workspace = workspace
        main_window = ServiceLocator.get_main_window()
        settings = ServiceLocator.get_settings()

        self.new_latex_document_action = Gio.SimpleAction.new('new-latex-document', None)
        self.new_bibtex_document_action = Gio.SimpleAction.new('new-bibtex-document', None)
        self.open_document_dialog_action = Gio.SimpleAction.new('open-document-dialog', None)
        self.save_action = Gio.SimpleAction.new('save', None)
        self.save_as_action = Gio.SimpleAction.new('save-as', None)
        self.save_all_action = Gio.SimpleAction.new('save-all', None)
        self.save_session_action = Gio.SimpleAction.new('save-session', None)
        self.close_all_action = Gio.SimpleAction.new('close-all-documents', None)
        self.close_document_action = Gio.SimpleAction.new('close-active-document', None)
        self.show_about_action = Gio.SimpleAction.new('show-about-dialog', None)
        self.quit_action = Gio.SimpleAction.new('quit', None)

        main_window.add_action(self.new_latex_document_action)
        main_window.add_action(self.new_bibtex_document_action)
        main_window.add_action(self.open_document_dialog_action)
        main_window.add_action(self.save_action)
        main_window.add_action(self.save_as_action)
        main_window.add_action(self.save_all_action)
        main_window.add_action(self.save_session_action)
        main_window.add_action(self.close_all_action)
        main_window.add_action(self.close_document_action)
        main_window.add_action(self.show_about_action)
        main_window.add_action(self.quit_action)

        self.new_latex_document_action.connect('activate', self.on_new_latex_document_action_activated)
        self.new_bibtex_document_action.connect('activate', self.on_new_bibtex_document_action_activated)
        self.open_document_dialog_action.connect('activate', self.on_open_document_dialog_action_activated)
        self.save_action.connect('activate', self.on_save_button_click)
        self.save_as_action.connect('activate', self.on_save_as_clicked)
        self.save_all_action.connect('activate', self.on_save_all_clicked)
        self.save_session_action.connect('activate', self.on_save_session_clicked)
        self.close_all_action.connect('activate', self.on_close_all_clicked)
        self.close_document_action.connect('activate', self.on_close_document_clicked)
        self.show_about_action.connect('activate', self.show_about_dialog)

        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_inactive_document', self.on_new_inactive_document)
        self.workspace.connect('new_active_document', self.on_new_active_document)

    def _assert_has_active_document(original_function):
        def new_function(self, *args, **kwargs):
            if self.workspace.get_active_document() != None:
                return original_function(self, *args, **kwargs)
        return new_function    

    def on_document_removed(self, workspace, document):
        if self.workspace.active_document == None:
            self.activate_welcome_screen_mode()
            self.update_document_actions(None)
            self.update_save_actions(None)

    def on_new_inactive_document(self, workspace, document):
        document.content.disconnect('modified_changed', self.on_modified_changed)

    def on_new_active_document(self, workspace, document):
        self.activate_document_mode()
        self.update_document_actions(document)
        self.update_save_actions(document)
        document.content.connect('modified_changed', self.on_modified_changed)

    def on_modified_changed(self, content):
        self.update_save_actions(self.workspace.active_document)

    def activate_welcome_screen_mode(self):
        self.save_all_action.set_enabled(False)

    def activate_document_mode(self):
        pass

    def update_save_actions(self, document):
        if document == None:
            self.save_action.set_enabled(False)
            self.save_all_action.set_enabled(False)
        else:
            if document.content.get_modified():
                self.save_action.set_enabled(True)
            elif document.get_filename() == None:
                self.save_action.set_enabled(True)
            else:
                self.save_action.set_enabled(False)

        if self.workspace.get_unsaved_documents() != None:
            self.save_all_action.set_enabled(True)
        else:
            self.save_all_action.set_enabled(False)

    def update_document_actions(self, document):
        if document != None:
            value = True
        else:
            value = False

        self.save_as_action.set_enabled(value)
        self.close_document_action.set_enabled(value)
        self.close_all_action.set_enabled(value)
        self.save_session_action.set_enabled(value)

        if document != None and document.is_latex_document():
            value = True
        else:
            value = False

    def on_new_latex_document_action_activated(self, action=None, parameter=None):
        document = self.workspace.create_latex_document()
        self.workspace.add_document(document)
        self.workspace.set_active_document(document)

    def on_new_bibtex_document_action_activated(self, action=None, parameter=None):
        document = self.workspace.create_bibtex_document()
        self.workspace.add_document(document)
        self.workspace.set_active_document(document)

    def on_open_document_dialog_action_activated(self, action=None, parameter=None):
        DialogLocator.get_dialog('open_document').run()

    @_assert_has_active_document
    def on_save_button_click(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        if active_document.filename == None:
            self.on_save_as_clicked()
        else:
            active_document.save_to_disk()

    @_assert_has_active_document
    def on_save_as_clicked(self, action=None, parameter=None):
        document = self.workspace.get_active_document()
        DialogLocator.get_dialog('save_document').run(document)

    @_assert_has_active_document
    def on_save_all_clicked(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        return_to_active_document = False
        documents = self.workspace.get_unsaved_documents()
        if documents != None: 
            for document in documents:
                if document.get_filename() == None:
                    self.workspace.set_active_document(document)
                    return_to_active_document = True
                    DialogLocator.get_dialog('save_document').run(document)
                else:
                    document.save_to_disk()
            if return_to_active_document == True:
                self.workspace.set_active_document(document)

    @_assert_has_active_document
    def on_save_session_clicked(self, action=None, parameter=None):
        DialogLocator.get_dialog('save_session').run()

    @_assert_has_active_document
    def on_close_all_clicked(self, action=None, parameter=None):
        documents = self.workspace.get_all_documents()
        unsaved_documents = self.workspace.get_unsaved_documents()
        dialog = DialogLocator.get_dialog('close_confirmation')
        dialog.run({'unsaved_documents': unsaved_documents, 'documents': documents}, self.on_close_all_callback)

    def on_close_all_callback(self, parameters, response):
        not_save_to_close_documents = response['not_save_to_close_documents']
        for document in parameters['documents']:
            if document not in not_save_to_close_documents:
                self.workspace.remove_document(document)

    def on_close_document_clicked(self, action=None, parameter=None):
        document = self.workspace.get_active_document()
        if document.content.get_modified():
            dialog = DialogLocator.get_dialog('close_confirmation')
            dialog.run({'unsaved_documents': [document], 'document': document}, self.on_close_document_callback)
        else:
            self.workspace.remove_document(document)

    def on_close_document_callback(self, parameters, response):
        not_save_to_close = response['not_save_to_close_documents']
        if parameters['document'] not in not_save_to_close:
            self.workspace.remove_document(parameters['document'])

    def show_about_dialog(self, action, parameter=''):
        DialogLocator.get_dialog('about').run()


