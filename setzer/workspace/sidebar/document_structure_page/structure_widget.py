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
from gi.repository import Gtk, Gdk, Pango, Graphene


class StructureWidget(Gtk.DrawingArea):

    def __init__(self, model):
        Gtk.DrawingArea.__init__(self)

        self.model = model

        self.icons = dict()
        self.height = 0

        self.font = self.get_pango_context().get_font_description()
        self.font_size = self.font.get_size() / Pango.SCALE

        self.hover_item = None
        self.bg_color = None
        self.hover_color = None
        self.fg_color = None

        click_controller = Gtk.GestureClick()
        click_controller.set_button(1)
        click_controller.connect('pressed', self.model.on_button_press)
        self.add_controller(click_controller)

        motion_controller = Gtk.EventControllerMotion()
        motion_controller.connect('enter', self.on_enter)
        motion_controller.connect('motion', self.on_hover)
        motion_controller.connect('leave', self.on_leave)
        self.add_controller(motion_controller)

    def on_enter(self, controller, x, y):
        self.update_hover_state(y)

    def on_hover(self, controller, x, y):
        self.update_hover_state(y)

    def on_leave(self, controller):
        self.set_hover_item(None)

    def update_hover_state(self, y):
        if y >= 9:
            item_num = int((y - 9) // self.line_height)
            self.set_hover_item(item_num)
        else:
            self.set_hover_item(None)

    def set_hover_item(self, item):
        self.hover_item = item
        self.queue_draw()

    def draw_hover_background(self, snapshot, max_item_num):
        if self.hover_item != None and self.hover_item < max_item_num:
            snapshot.append_color(self.hover_color, Graphene.Rect().init(0, self.hover_item * self.line_height + 9, self.get_allocated_width(), self.line_height))

    def drawing_setup(self):
        self.fg_color = self.get_style_context().lookup_color('view_fg_color')[1]
        self.bg_color = self.get_style_context().lookup_color('view_bg_color')[1]
        self.hover_color = self.get_style_context().lookup_color('view_hover_color')[1]

    def draw_background(self, snapshot):
        snapshot.append_color(self.bg_color, Graphene.Rect().init(0, 0, self.get_allocated_width(), self.height))


