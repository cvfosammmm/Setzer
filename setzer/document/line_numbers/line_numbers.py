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
from gi.repository import cairo
from gi.repository import Pango

import math

from setzer.helpers.timer import timer
from setzer.app.service_locator import ServiceLocator


class LineNumbers(object):

    def __init__(self, document, document_view):
        self.source_view = document_view.source_view

        self.font_manager = ServiceLocator.get_font_manager()
        self.font_manager.register_observer(self)
        self.line_height = 0
        self.font_desc = self.font_manager.get_font_desc()
        self.char_width = self.font_manager.get_char_width(self.source_view)
        self.font_size = self.font_desc.get_size() * 4 / (3 * Pango.SCALE)

        self.size = 0
        self.visible = False
        self.update_size()

        document.gutter.add_widget(self)

        settings = ServiceLocator.get_settings()
        self.set_visibility(settings.get_value('preferences', 'show_line_numbers'))
        settings.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'font_string_changed':
            self.font_desc = self.font_manager.get_font_desc()
            self.char_width = self.font_manager.get_char_width(self.source_view)
            self.font_size = self.font_desc.get_size() * 4 / (3 * Pango.SCALE)

        if change_code == 'settings_changed':
            section, item, value = parameter
            if (section, item) == ('preferences', 'show_line_numbers'):
                self.set_visibility(value)

    def set_line_height(self, line_height):
        self.line_height = line_height

    def on_click(self, event):
        return False

    #@timer
    def on_draw(self, drawing_area, ctx, lines, current_line, offset):
        ctx.set_font_size(self.font_size)
        font_family = self.font_desc.get_family()
        ctx.select_font_face(font_family, cairo.FontSlant.NORMAL, cairo.FontWeight.NORMAL)

        for line in lines:
            if current_line != None and line[0] == current_line[0]:
                ctx.select_font_face(font_family, cairo.FontSlant.NORMAL, cairo.FontWeight.BOLD)

            extent = ctx.text_extents(str(line[0]))
            yoffset = int(line[1] + (self.line_height + extent.height) / 2)
            xoffset = int(offset + self.size - extent.x_advance)
            ctx.move_to(xoffset, yoffset)
            ctx.show_text(str(line[0]))

            if current_line != None and line[0] == current_line[0]:
                ctx.select_font_face(font_family, cairo.FontSlant.NORMAL, cairo.FontWeight.NORMAL)

    def update_size(self):
        self.size = math.ceil(math.log(self.source_view.get_buffer().get_line_count() + 1, 10)) * self.char_width

    def get_size(self):
        return self.size

    def set_visibility(self, value):
        self.visible = value
        self.source_view.queue_draw()

    def is_visible(self):
        return self.visible


