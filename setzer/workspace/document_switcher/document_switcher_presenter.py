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

import os.path

from setzer.app.service_locator import ServiceLocator


class DocumentSwitcherPresenter(object):
    
    def __init__(self, document_switcher, workspace):
        self.document_switcher = document_switcher
        self.workspace = workspace
        self.button = ServiceLocator.get_main_window().headerbar.center_widget
        self.view = self.button.open_docs_popover

        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_inactive_document', self.on_new_inactive_document)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('root_state_change', self.on_root_state_change)
        self.document_switcher.connect('docswitcher_mode_change', self.on_docswitcher_mode_change)

        self.show_welcome_title()

    def on_new_document(self, workspace, document):
        self.view.document_list.add(document.document_switcher_item.view)
        self.activate_mode(self.document_switcher.mode)

    def on_document_removed(self, workspace, document):
        self.view.document_list.remove(document.document_switcher_item.view)
        self.activate_mode(self.document_switcher.mode)
        if self.workspace.active_document == None:
            self.show_welcome_title()

    def on_new_inactive_document(self, workspace, document):
        document.disconnect('filename_change', self.on_filename_change)
        document.disconnect('displayname_change', self.on_displayname_change)
        document.content.disconnect('modified_changed', self.on_modified_changed)

    def on_new_active_document(self, workspace, document):
        self.show_document_name(document)
        self.view.document_list.invalidate_sort()
        document.connect('filename_change', self.on_filename_change)
        document.connect('displayname_change', self.on_displayname_change)
        document.content.connect('modified_changed', self.on_modified_changed)

    def on_root_state_change(self, workspace, state):
        self.activate_mode(self.document_switcher.mode)

    def on_docswitcher_mode_change(self, document_switcher, mode):
        self.activate_mode(mode)

    def on_filename_change(self, document, filename=None):
        self.show_document_name(document)

    def on_displayname_change(self, document):
        self.show_document_name(document)

    def on_modified_changed(self, content):
        document = self.workspace.get_active_document()
        self.show_document_name(document)

    def activate_mode(self, mode):
        if mode == 'normal':
            self.activate_normal_mode()
        elif mode == 'selection':
            self.activate_selection_mode()
    
    def activate_normal_mode(self):
        self.activate_set_root_document_button()
        if self.workspace.root_document != None:
            self.view.unset_root_document_button.set_sensitive(True)
        else:
            self.view.unset_root_document_button.set_sensitive(False)
        self.view.root_explaination_revealer.set_reveal_child(False)
        self.view.document_list.get_style_context().remove_class('selection-mode')
        self.view.document_list.get_style_context().add_class('normal-mode')
        for item in self.view.document_list.get_children():
            item.show()
            item.document_close_button.show()
            item.icon_box.show()
            item.radio_button_hover.hide()
        self.view.in_selection_mode = False

    def activate_selection_mode(self):
        self.view.set_root_document_button.set_sensitive(False)
        self.view.unset_root_document_button.set_sensitive(True)
        self.view.root_explaination_revealer.set_reveal_child(True)
        self.view.set_can_focus(False)
        self.view.document_list.get_style_context().remove_class('normal-mode')
        self.view.document_list.get_style_context().add_class('selection-mode')
        for item in self.view.document_list.get_children():
            item.document_close_button.hide()
            item.icon_box.hide()
            item.radio_button_hover.show()
            if not item.document.is_latex_document():
                item.hide()
        self.view.in_selection_mode = True

    def activate_set_root_document_button(self):
        if len(self.workspace.open_latex_documents) > 0:
            self.view.set_root_document_button.set_sensitive(True)
        else:
            self.view.set_root_document_button.set_sensitive(False)

    def show_welcome_title(self):
        self.button.center_button.set_sensitive(False)
        self.button.set_visible_child_name('welcome')

    def show_document_name(self, document):
        mod_text = '*' if document.content.get_modified() else ''
        self.button.document_name_label.set_text(document.get_basename() + mod_text)
        dirname = document.get_dirname()
        if dirname != '':
            folder_text = dirname.replace(os.path.expanduser('~'), '~')
            self.button.document_folder_label.set_text(folder_text)
            self.button.document_folder_label.show_all()
        else:
            self.button.document_folder_label.hide()
        self.button.center_button.set_sensitive(True)
        self.button.set_visible_child_name('button')


