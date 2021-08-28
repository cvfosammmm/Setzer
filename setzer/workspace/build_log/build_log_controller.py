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


class BuildLogController(object):
    
    def __init__(self, build_log, build_log_view):
        self.build_log = build_log
        self.view = build_log_view
        self.view.scrolled_window.connect('enter-notify-event', self.on_enter)
        self.view.scrolled_window.connect('motion-notify-event', self.on_hover)
        self.view.scrolled_window.connect('leave-notify-event', self.on_leave)
        self.view.list.connect('button-press-event', self.on_button_press)

    def on_enter(self, widget, event):
        self.update_hover_state(event)

    def on_hover(self, widget, event):
        self.update_hover_state(event)

    def on_leave(self, widget, event):
        self.build_log.set_hover_item(None)

    def update_hover_state(self, event):
        offset = self.view.scrolled_window.get_vadjustment().get_value()
        item_num = max(0, min(int((offset + event.y) // self.view.line_height), len(self.build_log.items) - 1))
        self.build_log.set_hover_item(item_num)

    def on_button_press(self, drawing_area, event):
        if self.build_log.document == None: return
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1 and event.state & modifiers == 0:
            item_num = max(0, min(int(event.y // self.view.line_height), len(self.build_log.items) - 1))
            item = self.build_log.items[item_num]

            if item[2] == self.build_log.document.get_filename():
                line_number = item[3] - 1
                if line_number >= 0:
                    self.build_log.document.place_cursor(line_number)
                    self.build_log.document.content.scroll_cursor_onscreen()
                    self.build_log.document.view.source_view.grab_focus()
            else:
                if item[2] != None:
                    document_candidate = self.build_log.workspace.get_document_by_filename(item[2])
                    if document_candidate != None:
                        self.build_log.workspace.set_active_document(document_candidate)
                    else:
                        self.build_log.workspace.create_document_from_filename(item[2], True)
                    line_number = item[3] - 1
                    if line_number >= 0:
                        self.build_log.workspace.active_document.place_cursor(item[3] - 1)
                        self.build_log.workspace.active_document.content.scroll_cursor_onscreen()
                        self.build_log.workspace.active_document.view.source_view.grab_focus()


