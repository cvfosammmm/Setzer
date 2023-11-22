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

import os.path

from setzer.app.service_locator import ServiceLocator
from setzer.dialogs.dialog_locator import DialogLocator
from setzer.popovers.helpers.popover_menu_builder import MenuBuilder
from setzer.popovers.popover_manager import PopoverManager


class Headerbar(object):
    
    def __init__(self, workspace):
        self.workspace = workspace
        self.view = ServiceLocator.get_main_window().headerbar

        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('new_inactive_document', self.on_new_inactive_document)
        self.workspace.connect('update_recently_opened_documents', self.on_update_recently_opened_documents)
        self.workspace.connect('root_state_change', self.on_root_state_change)

        self.activate_welcome_screen_mode()

    def on_document_removed(self, workspace, document):
        if self.workspace.active_document == None:
            self.set_build_button_state()
            self.activate_welcome_screen_mode()

    def on_new_active_document(self, workspace, document):
        self.set_build_button_state()
        self.activate_document_mode()
        self.show_document_name(document)
        self.update_toggles()

        document.connect('filename_change', self.on_name_change)
        document.connect('displayname_change', self.on_name_change)
        document.connect('modified_changed', self.on_modified_changed)

    def on_new_inactive_document(self, workspace, document):
        document.disconnect('filename_change', self.on_name_change)
        document.disconnect('displayname_change', self.on_name_change)
        document.disconnect('modified_changed', self.on_modified_changed)

    def on_root_state_change(self, workspace, state):
        self.set_build_button_state()
        self.update_toggles()

    def on_name_change(self, document, name=None):
        self.show_document_name(document)

    def on_modified_changed(self, document):
        self.show_document_name(document)

    def on_update_recently_opened_documents(self, workspace, recently_opened_documents):
        data = recently_opened_documents.values()
        if len(data) > 0:
            self.view.open_document_button.set_sensitive(True)
            self.view.open_document_button.set_visible(True)
            self.view.open_document_blank_button.set_visible(False)
        else:
            self.view.open_document_button.set_sensitive(False)
            self.view.open_document_button.set_visible(False)
            self.view.open_document_blank_button.set_visible(True)

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
        self.view.save_document_button.set_visible(False)
        self.view.center_button.set_sensitive(False)
        self.view.center_widget.set_visible_child_name('welcome')
        self.view.get_style_context().add_class('welcome')

    def activate_document_mode(self):
        self.view.save_document_button.set_visible(True)
        self.view.center_button.set_sensitive(True)
        self.view.center_widget.set_visible_child_name('button')
        self.view.get_style_context().remove_class('welcome')

    def show_document_name(self, document):
        mod_text = '*' if document.source_buffer.get_modified() else ''
        self.view.document_name_label.set_text(document.get_basename() + mod_text)
        dirname = document.get_dirname()
        if dirname != '':
            folder_text = dirname.replace(os.path.expanduser('~'), '~')
            self.view.document_folder_label.set_text(folder_text)
            self.view.document_folder_label.set_visible(True)
        else:
            self.view.document_folder_label.set_visible(False)

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
        self.view.sidebar_toggles_box.set_visible(False)
        self.view.document_structure_toggle.set_sensitive(False)
        self.view.symbols_toggle.set_sensitive(False)

    def hide_preview_help_toggles(self):
        self.view.preview_toggle.set_visible(False)
        self.view.preview_toggle.set_sensitive(False)
        self.view.help_toggle.set_visible(False)
        self.view.help_toggle.set_sensitive(False)

    def show_sidebar_toggles(self):
        self.view.sidebar_toggles_box.set_visible(True)
        self.view.document_structure_toggle.set_sensitive(True)
        self.view.symbols_toggle.set_sensitive(True)

    def show_preview_help_toggles(self):
        self.view.preview_toggle.set_visible(True)
        self.view.preview_toggle.set_sensitive(True)
        self.view.help_toggle.set_visible(True)
        self.view.help_toggle.set_sensitive(True)


