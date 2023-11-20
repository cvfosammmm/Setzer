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

from setzer.dialogs.dialog_locator import DialogLocator
from setzer.popovers.helpers.popover_menu_builder import MenuBuilder
from setzer.popovers.hamburger_menu.hamburger_menu_viewgtk import HamburgerMenuView


class HamburgerMenu(object):

    def __init__(self, popover_manager, workspace):
        self.popover_manager = popover_manager
        self.workspace = workspace
        self.view = HamburgerMenuView(popover_manager)

        self.session_file_buttons = list()
        self.view.button_restore_session.connect('clicked', self.on_restore_session_click, None)

        self.workspace.connect('update_recently_opened_session_files', self.on_update_recently_opened_session_files)

    def on_update_recently_opened_session_files(self, workspace, recently_opened_session_files):
        items = list()
        data = recently_opened_session_files.values()
        for item in sorted(data, key=lambda val: -val['date']):
            items.append(item['filename'])
        for button in self.session_file_buttons:
            self.view.prev_sessions_box.remove(button)
        self.session_file_buttons = list()
        self.view.session_box_separator.hide()
        if len(items) > 0:
            self.view.session_box_separator.show()
        for item in items:
            button = MenuBuilder.create_button(item)
            button.connect('clicked', self.on_restore_session_click, item)
            self.view.prev_sessions_box.append(button)
            self.session_file_buttons.append(button)

    def on_restore_session_click(self, button, parameter):
        self.popover_manager.popdown()

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


