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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib

from setzer.app.service_locator import ServiceLocator

import os.path


class HeaderbarPresenter(object):
    ''' Mediator between workspace and view. '''
    
    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.workspace.register_observer(self)
        self.activate_blank_slate_mode()

    '''
    *** notification handlers, get called by observed workspace
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_document': pass

        if change_code == 'document_removed':
            document = parameter
            if self.workspace.active_document == None:
                self.activate_blank_slate_mode()

        if change_code == 'new_active_document':
            document = parameter

            if document.get_modified():
                self.main_window.headerbar.save_document_button.set_sensitive(True)
            elif document.get_filename() == None:
                self.main_window.headerbar.save_document_button.set_sensitive(True)
            else:
                self.main_window.headerbar.save_document_button.set_sensitive(False)

            if document.is_latex_document():
                self.activate_latex_documents_mode()
            elif document.is_bibtex_document():
                self.activate_bibtex_documents_mode()

            self.setup_modified_transform()

        if change_code == 'update_recently_opened_documents':
            items = list()
            data = parameter.values()
            for item in sorted(data, key=lambda val: -val['date']):
                items.append(os.path.split(item['filename']))
            self.main_window.headerbar.document_chooser.update_autosuggest(items)
            if len(data) > 0:
                self.main_window.headerbar.open_document_button.set_sensitive(True)
                self.main_window.headerbar.open_document_button.show_all()
                self.main_window.headerbar.open_document_blank_button.hide()
                self.main_window.headerbar.open_document_blank_button.set_sensitive(False)
            else:
                self.main_window.headerbar.open_document_button.hide()
                self.main_window.headerbar.open_document_button.set_sensitive(False)
                self.main_window.headerbar.open_document_blank_button.set_sensitive(True)
                self.main_window.headerbar.open_document_blank_button.show_all()

        if change_code == 'update_recently_opened_session_files':
            items = list()
            data = parameter.values()
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

        if change_code == 'master_state_change':
            self.set_build_button_state()

    def activate_blank_slate_mode(self):
        self.set_build_button_state()
        self.main_window.headerbar.save_document_button.hide()
        self.main_window.headerbar.preview_toggle.hide()
        self.main_window.headerbar.preview_toggle.set_sensitive(False)
        self.main_window.headerbar.help_toggle.hide()
        self.main_window.headerbar.help_toggle.set_sensitive(False)
        self.main_window.headerbar.sidebar_toggle.hide()
        self.main_window.headerbar.sidebar_toggle.set_sensitive(False)

    def activate_latex_documents_mode(self):
        self.set_build_button_state()
        self.main_window.headerbar.save_document_button.show_all()
        self.main_window.headerbar.preview_toggle.show_all()
        self.main_window.headerbar.preview_toggle.set_sensitive(True)
        self.main_window.headerbar.help_toggle.show_all()
        self.main_window.headerbar.help_toggle.set_sensitive(True)
        self.main_window.headerbar.sidebar_toggle.show_all()
        self.main_window.headerbar.sidebar_toggle.set_sensitive(True)

    def activate_bibtex_documents_mode(self):
        self.set_build_button_state()
        self.main_window.headerbar.save_document_button.show_all()
        self.main_window.headerbar.preview_toggle.hide()
        self.main_window.headerbar.preview_toggle.set_sensitive(False)
        self.main_window.headerbar.help_toggle.hide()
        self.main_window.headerbar.help_toggle.set_sensitive(False)
        self.main_window.headerbar.sidebar_toggle.hide()
        self.main_window.headerbar.sidebar_toggle.set_sensitive(False)

    def set_build_button_state(self):
        if self.workspace.master_document != None:
            document = self.workspace.master_document
        else:
            document = self.workspace.active_document

        headerbar = self.main_window.headerbar
        prev_widget = headerbar.build_wrapper.get_center_widget()
        if prev_widget != None:
            headerbar.build_wrapper.remove(prev_widget)
        if document != None and document.is_latex_document():
            headerbar.build_wrapper.set_center_widget(document.build_widget.view)
            if document.build_widget.view.has_result():
                document.build_widget.view.hide_timer(1600)

    def setup_modified_transform(self):
        headerbar = self.main_window.headerbar

        document = self.workspace.get_active_document()
        if document == None:
            headerbar.save_document_button.set_sensitive(False)
            self.main_window.save_all_action.set_enabled(False)
        else:
            doclist_item = document.document_switcher_item.view
            if headerbar.center_widget.mod_binding != None: headerbar.center_widget.mod_binding.unbind()
            headerbar.center_widget.mod_binding = doclist_item.mlabel.bind_property('label', headerbar.center_widget.document_mod_label, 'label', 0, self.modified_transform_func)

    def modified_transform_func(self, binding, from_value, to_value=None):
        headerbar = self.main_window.headerbar

        if from_value == 'False' and headerbar.center_widget.document_folder_label.get_text() != '':
            headerbar.save_document_button.set_sensitive(False)
        else:
            headerbar.save_document_button.set_sensitive(True)
        if self.workspace.get_unsaved_documents() != None:
            self.main_window.save_all_action.set_enabled(True)
        else:
            self.main_window.save_all_action.set_enabled(False)


