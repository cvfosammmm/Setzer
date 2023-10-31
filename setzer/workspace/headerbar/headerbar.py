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
from setzer.helpers.popover_menu_builder import MenuBuilder


class Headerbar(object):
    
    def __init__(self, workspace):
        self.workspace = workspace
        self.view = ServiceLocator.get_main_window().headerbar

        self.popover_manager = ServiceLocator.get_popover_manager()

        actions = self.workspace.actions.actions
        self.view.button_latex.connect('clicked', self.on_new_document_button_click, actions['new-latex-document'])
        self.view.button_bibtex.connect('clicked', self.on_new_document_button_click, actions['new-bibtex-document'])

        self.view.button_restore_session.connect('clicked', self.on_restore_session_click, None)
        self.view.button_save_session.connect('clicked', self.on_hamburger_button_click, actions['save-session'])

        self.view.button_save_as.connect('clicked', self.on_hamburger_button_click, actions['save-as'])
        self.view.button_save_all.connect('clicked', self.on_hamburger_button_click, actions['save-all'])
        self.view.button_preferences.connect('clicked', self.on_hamburger_button_click, actions['show-preferences-dialog'])
        self.view.button_shortcuts.connect('clicked', self.on_hamburger_button_click, actions['show-shortcuts-dialog'])
        self.view.button_about.connect('clicked', self.on_hamburger_button_click, actions['show-about-dialog'])
        self.view.button_close_all.connect('clicked', self.on_hamburger_button_click, actions['close-all-documents'])
        self.view.button_close_active.connect('clicked', self.on_hamburger_button_click, actions['close-active-document'])
        self.view.button_quit.connect('clicked', self.on_hamburger_button_click, actions['quit'])

        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('update_recently_opened_documents', self.on_update_recently_opened_documents)
        self.workspace.connect('update_recently_opened_session_files', self.on_update_recently_opened_session_files)
        self.workspace.connect('root_state_change', self.on_root_state_change)

        self.activate_welcome_screen_mode()

    def on_new_document_button_click(self, button, action):
        self.popover_manager.popdown()
        action.activate()

    def on_hamburger_button_click(self, button, action):
        self.popover_manager.popdown()
        action.activate()

    def on_document_removed(self, workspace, document):
        if self.workspace.active_document == None:
            self.set_build_button_state()
            self.activate_welcome_screen_mode()

    def on_new_active_document(self, workspace, document):
        self.set_build_button_state()
        self.activate_document_mode()
        self.update_toggles()

    def on_root_state_change(self, workspace, state):
        self.set_build_button_state()
        self.update_toggles()

    def on_update_recently_opened_documents(self, workspace, recently_opened_documents):
        data = recently_opened_documents.values()
        if len(data) > 0:
            self.view.open_document_button.set_sensitive(True)
            self.view.open_document_button.show()
            self.view.open_document_blank_button.hide()
        else:
            self.view.open_document_button.set_sensitive(False)
            self.view.open_document_button.hide()
            self.view.open_document_blank_button.show()

    def on_update_recently_opened_session_files(self, workspace, recently_opened_session_files):
        items = list()
        data = recently_opened_session_files.values()
        for item in sorted(data, key=lambda val: -val['date']):
            items.append(item['filename'])
        for button in self.view.session_file_buttons:
            self.view.prev_sessions_box.remove(button)
        self.view.session_file_buttons = list()
        self.view.session_box_separator.hide()
        if len(items) > 0:
            self.view.session_box_separator.show()
        for item in items:
            button = MenuBuilder.create_button(item)
            button.connect('clicked', self.on_restore_session_click, item)
            self.view.prev_sessions_box.append(button)
            self.view.session_file_buttons.append(button)

    def set_build_button_state(self):
        document = self.workspace.get_root_or_active_latex_document()

        if document != None:
            self.view.build_wrapper.set_end_widget(document.build_widget.view)
            if document.build_widget.view.has_result():
                document.build_widget.view.hide_timer(1600)
        else:
            self.view.build_wrapper.set_end_widget(None)

    def activate_welcome_screen_mode(self):
        self.hide_sidebar_toggles()
        self.hide_preview_help_toggles()
        self.view.save_document_button.hide()
        self.view.get_style_context().add_class('welcome')

    def activate_document_mode(self):
        self.view.save_document_button.show()
        self.view.get_style_context().remove_class('welcome')

    def update_toggles(self):
        if self.workspace.get_active_latex_document():
            self.show_sidebar_toggles()
        else:
            self.hide_sidebar_toggles()

        if self.workspace.get_root_or_active_latex_document():
            self.show_preview_help_toggles()
        else:
            self.hide_preview_help_toggles()

    def hide_sidebar_toggles(self):
        self.view.sidebar_toggles_box.hide()
        self.view.document_structure_toggle.set_sensitive(False)
        self.view.symbols_toggle.set_sensitive(False)

    def hide_preview_help_toggles(self):
        self.view.preview_toggle.hide()
        self.view.preview_toggle.set_sensitive(False)
        self.view.help_toggle.hide()
        self.view.help_toggle.set_sensitive(False)

    def show_sidebar_toggles(self):
        self.view.sidebar_toggles_box.show()
        self.view.document_structure_toggle.set_sensitive(True)
        self.view.symbols_toggle.set_sensitive(True)

    def show_preview_help_toggles(self):
        self.view.preview_toggle.show()
        self.view.preview_toggle.set_sensitive(True)
        self.view.help_toggle.show()
        self.view.help_toggle.set_sensitive(True)

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


