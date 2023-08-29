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
from gi.repository import Gtk, Gdk

import os.path

import setzer.workspace.sidebar.document_structure_page.files_viewgtk as files_section_view


class FilesSection(object):

    def __init__(self, data_provider):
        self.data_provider = data_provider
        self.data_provider.connect('data_updated', self.update_items)

        self.view = files_section_view.FilesSectionView(self)

        self.includes = list()

    def on_button_press(self, controller, n_press, x, y):
        if n_press == 1:
            item_num = int((y - 9) // self.view.line_height)
            if item_num < 0 or item_num > len(self.includes): return

            if item_num == 0:
                document = self.data_provider.document
                self.data_provider.workspace.set_active_document(document)
            else:
                filename = self.includes[item_num - 1]['filename']
                document = self.data_provider.workspace.open_document_by_filename(filename)
            document.scroll_cursor_onscreen()
            self.data_provider.workspace.active_document.view.source_view.grab_focus()

    def update_items(self, *params):
        self.includes = self.data_provider.get_includes()
        self.view.height = (len(self.includes) + 1) * self.view.line_height + 33
        self.view.set_size_request(-1, self.view.height)
        self.view.set_hover_item(None)
        self.view.queue_draw()


