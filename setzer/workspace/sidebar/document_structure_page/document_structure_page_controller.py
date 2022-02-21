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
from gi.repository import Gdk
from gi.repository import Gtk


class DocumentStructurePageController(object):
    
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.scrolled_window.connect('enter-notify-event', self.on_enter)
        self.view.scrolled_window.connect('motion-notify-event', self.on_hover)
        self.view.scrolled_window.connect('leave-notify-event', self.on_leave)
        self.view.content.connect('button-press-event', self.on_button_press)

    def on_enter(self, widget, event):
        self.update_hover_state(event)

    def on_hover(self, widget, event):
        self.update_hover_state(event)

    def on_leave(self, widget, event):
        self.model.set_hover_item(None)

    def update_hover_state(self, event):
        scrolling_offset = self.view.scrolled_window.get_vadjustment().get_value()
        offset = int((scrolling_offset + event.y - 8) // self.view.line_height)
        if offset > len(self.model.nodes_in_line) - 1 or offset < 0:
            self.model.set_hover_item(None)
        else:
            self.model.set_hover_item(offset)

    def on_button_press(self, drawing_area, event):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1 and event.state & modifiers == 0:
            item_num = max(0, min(int((event.y - 8) // self.view.line_height), len(self.model.nodes_in_line) - 1))
            item = self.model.nodes_in_line[item_num]['item']

            filename = item[0]
            line_number = item[1]
            document = self.model.workspace.open_document_by_filename(filename)
            document.content.place_cursor(line_number)
            document.content.scroll_cursor_onscreen()
            self.model.workspace.active_document.view.source_view.grab_focus()


