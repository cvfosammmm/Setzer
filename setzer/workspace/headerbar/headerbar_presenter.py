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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib

from setzer.app.service_locator import ServiceLocator


class HeaderbarPresenter(object):
    ''' Mediator between workspace and view. '''
    
    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()

        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('update_recently_opened_documents', self.on_update_recently_opened_documents)
        self.workspace.connect('update_recently_opened_session_files', self.on_update_recently_opened_session_files)
        self.workspace.connect('root_state_change', self.on_root_state_change)

        self.activate_welcome_screen_mode()

    def on_new_document(self, workspace, document): pass

    def on_document_removed(self, workspace, document):
        if self.workspace.active_document == None:
            self.activate_welcome_screen_mode()

    def on_new_active_document(self, workspace, document):
        self.main_window.headerbar.save_document_button.show_all()
        if document.is_latex_document():
            self.activate_latex_document_mode()
        else:
            self.activate_other_document_mode()

    def on_update_recently_opened_documents(self, workspace, recently_opened_documents):
        data = recently_opened_documents.values()
        self.main_window.headerbar.open_document_blank_button.show_all()

    def on_update_recently_opened_session_files(self, workspace, recently_opened_session_files):
        items = list()
        data = recently_opened_session_files.values()
        for item in sorted(data, key=lambda val: -val['date']):
            items.append(item['filename'])
        for button in self.main_window.headerbar.session_file_buttons:
            self.main_window.headerbar.session_box.remove(button)
        if len(self.main_window.headerbar.session_file_buttons) > 0:
            self.main_window.headerbar.session_box.remove(self.main_window.headerbar.session_box_separator)
        self.main_window.headerbar.session_file_buttons = list()
        if len(items) > 0:
            self.main_window.headerbar.session_box.pack_start(self.main_window.headerbar.session_box_separator, False, False, 0)
        for item in items:
            button = Gtk.ModelButton()
            button.set_label(item)
            button.get_child().set_halign(Gtk.Align.START)
            button.set_detailed_action_name(Gio.Action.print_detailed_name('win.restore-session', GLib.Variant('as', [item])))
            button.show_all()
            self.main_window.headerbar.session_box.pack_start(button, False, False, 0)
            self.main_window.headerbar.session_file_buttons.append(button)

    def on_root_state_change(self, workspace, state):
        pass

    def activate_welcome_screen_mode(self):
        self.main_window.headerbar.save_document_button.hide()

    def activate_latex_document_mode(self):
        pass

    def activate_other_document_mode(self):
        pass


