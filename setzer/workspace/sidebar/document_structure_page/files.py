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
from gi.repository import Gdk

import os.path

import setzer.workspace.sidebar.document_structure_page.structure_widget as structure_widget
import setzer.workspace.sidebar.document_structure_page.files_viewgtk as files_section_view


class FilesSection(structure_widget.StructureWidget):

    def __init__(self, data_provider):
        structure_widget.StructureWidget.__init__(self, data_provider)

        self.view = files_section_view.FilesSectionView()
        self.init_view()

        self.includes = list()

    def on_button_press(self, drawing_area, event):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1 and event.state & modifiers == 0:
            item_num = max(0, min(int((event.y - 9) // self.view.line_height), len(self.includes)))

            if item_num == 0:
                filename = self.data_provider.document.get_filename()
            else:
                filename = self.includes[item_num - 1]['filename']
            document = self.data_provider.workspace.open_document_by_filename(filename)
            document.content.scroll_cursor_onscreen()
            self.data_provider.workspace.active_document.view.source_view.grab_focus()

    def update_items(self, *params):
        self.includes = self.data_provider.get_includes()
        self.height = (len(self.includes) + 1) * self.view.line_height + 33
        self.view.set_size_request(-1, self.height)
        self.set_hover_item(None)
        self.view.queue_draw()

    def draw(self, drawing_area, ctx):
        first_line, last_line = self.get_first_line_last_line(ctx)
        self.drawing_setup(ctx)
        self.draw_background(ctx)

        self.draw_hover_background(ctx, 0)
        self.draw_icon(ctx, 'file-symbolic', 9, 0)
        self.draw_text(ctx, 35, 0, os.path.basename(self.data_provider.document.get_filename()))

        for count, include in enumerate(self.includes):
            if count + 1 >= first_line and count + 1 <= last_line:
                self.draw_hover_background(ctx, count + 1)
                self.draw_icon(ctx, 'file-symbolic', 27, count + 1)
                self.draw_text(ctx, 53, count + 1, os.path.basename(include['filename']))


