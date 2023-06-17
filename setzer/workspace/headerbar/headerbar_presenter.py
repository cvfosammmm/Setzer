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
from setzer.helpers.popover_menu_builder import MenuBuilder


class HeaderbarPresenter(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def update_recently_opened_documents(self, recently_opened_documents):
        data = recently_opened_documents.values()
        self.view.open_document_blank_button.show()

    def update_recently_opened_session_files(self, recently_opened_session_files):
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
            button = MenuBuilder.create_action_button(item)
            button.connect('clicked', self.model.on_restore_session_click, item)
            MenuBuilder.add_button(self.view.prev_sessions_box, button)
            self.view.session_file_buttons.append(button)

    def activate_welcome_screen_mode(self):
        self.view.save_document_button.hide()

    def activate_latex_document_mode(self):
        self.view.save_document_button.show()

    def activate_other_document_mode(self):
        self.view.save_document_button.show()


