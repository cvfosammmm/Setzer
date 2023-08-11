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
from gi.repository import Gdk
from gi.repository import Gtk


class BuildLogController(object):
    
    def __init__(self, build_log, build_log_view):
        self.build_log = build_log
        self.view = build_log_view

        event_controller = Gtk.GestureClick()
        event_controller.connect('pressed', self.on_button_press)
        event_controller.set_button(1)
        self.view.list.add_controller(event_controller)

        motion_controller = Gtk.EventControllerMotion()
        motion_controller.connect('enter', self.on_enter)
        motion_controller.connect('motion', self.on_hover)
        motion_controller.connect('leave', self.on_leave)
        self.view.list.add_controller(motion_controller)

    def on_enter(self, controller, x, y):
        self.update_hover_state(y)

    def on_hover(self, controller, x, y):
        self.update_hover_state(y)

    def on_leave(self, controller):
        self.build_log.set_hover_item(None)

    def update_hover_state(self, y):
        offset = self.view.scrolled_window.get_vadjustment().get_value()
        item_num = int((y) // self.view.list.line_height)

        if item_num < 0 or item_num > (len(self.build_log.items) - 1):
            self.build_log.set_hover_item(None)
        else:
            self.build_log.set_hover_item(item_num)

    def on_button_press(self, event_controller, n_press, x, y):
        if n_press != 1: return False

        if self.build_log.document == None: return
        modifiers = Gtk.accelerator_get_default_mod_mask()

        item_num = int(y / self.view.list.line_height)
        if item_num < 0 or item_num > (len(self.build_log.items) - 1): return True

        item = self.build_log.items[item_num]
        if item[2] == None: return True

        self.build_log.workspace.open_document_by_filename(item[2])
        line_number = item[3] - 1
        if line_number < 0: return True

        self.build_log.workspace.active_document.place_cursor(item[3] - 1)
        self.build_log.workspace.active_document.scroll_cursor_onscreen()
        self.build_log.workspace.active_document.source_view.grab_focus()
        return True


