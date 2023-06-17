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
gi.require_version('GtkSource', '4')
from gi.repository import Gdk
from gi.repository import GtkSource

from setzer.helpers.observable import Observable


class Content(Observable):

    def __init__(self, language, document):
        Observable.__init__(self)
        self.document = document

        self.source_buffer = GtkSource.Buffer()
        self.source_view = GtkSource.View.new_with_buffer(self.source_buffer)

        self.source_buffer.connect('modified-changed', self.on_modified_changed)

    def on_modified_changed(self, buffer):
        self.add_change_code('modified_changed')

    def initially_set_text(self, text):
        self.source_buffer.begin_not_undoable_action()
        self.source_buffer.set_text(text)
        self.source_buffer.end_not_undoable_action()
        self.source_buffer.set_modified(False)

    def get_all_text(self):
        return self.source_buffer.get_text(self.source_buffer.get_start_iter(), self.source_buffer.get_end_iter(), True)

    def get_selected_text(self):
        bounds = self.source_buffer.get_selection_bounds()
        if len(bounds) == 2:
            return self.source_buffer.get_text(bounds[0], bounds[1], True)
        else:
            return None

    def place_cursor(self, line_number, offset=0):
        text_iter = self.source_buffer.get_iter_at_line_offset(line_number, offset)
        self.source_buffer.place_cursor(text_iter)

    def cut(self):
        self.copy()
        self.delete_selection()

    def copy(self):
        text = self.get_selected_text()
        if text != None:
            clipboard = self.source_view.get_clipboard(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(text, -1)

    def paste(self):
        self.source_view.emit('paste-clipboard')

    def delete_selection(self):
        self.source_buffer.delete_selection(True, True)

    def select_all(self, widget=None):
        self.source_buffer.select_range(self.source_buffer.get_start_iter(), self.source_buffer.get_end_iter())

    def get_modified(self):
        return self.source_buffer.get_modified()

    def set_modified(self, modified):
        self.source_buffer.set_modified(modified)

    def undo(self):
        self.source_buffer.undo()

    def redo(self):
        self.source_buffer.redo()


