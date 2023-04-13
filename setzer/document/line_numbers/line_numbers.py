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
gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango
from gi.repository import PangoCairo
import cairo

import math

from setzer.helpers.timer import timer
from setzer.app.service_locator import ServiceLocator


class LineNumbers(object):

    def __init__(self, document, document_view):
        self.source_view = document_view.source_view

        self.line_height = 0
        self.char_width = 0
        self.font_desc = None
        self.font_size = None
        self.font_changed = True
        self.glyph_index = None
        self.extents = None
        self.layout = Pango.Layout(self.source_view.get_pango_context())
        self.layout.set_alignment(Pango.Alignment.RIGHT)

        self.size = 0
        self.visible = False
        self.update_size()

        document.gutter.add_widget(self)

        settings = ServiceLocator.get_settings()
        self.set_visibility(settings.get_value('preferences', 'show_line_numbers'))
        settings.connect('settings_changed', self.on_settings_changed)

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter
        if (section, item) == ('preferences', 'show_line_numbers'):
            self.set_visibility(value)

    def set_font_desc(self, font_desc):
        self.font_desc = font_desc
        self.font_size = self.font_desc.get_size() * 4 / (3 * Pango.SCALE)
        self.font_changed = True

    def set_char_dimensions(self, line_height, char_width):
        self.line_height = line_height
        self.char_width = char_width
        self.font_changed = True

    def update_colors(self):
        self.font_changed = True

    def on_click(self, event):
        return False

    def on_pointer_movement(self, event):
        pass

    #@timer
    def on_draw(self, gutter, drawing_area, ctx, lines, current_line, offset):
        self.layout.set_font_description(self.font_desc)
        self.layout.set_width((self.size - self.char_width) * Pango.SCALE)

        markup = ''
        for line in lines:
            if current_line != None and line[0] == current_line[0]:
                markup += '<b>' + str(line[0]) + '</b>'
            else:
                markup += str(line[0])
            markup += '\n' * (line[2] // self.line_height)

        ctx.move_to(offset, int(lines[0][1]))
        self.layout.set_markup(markup)
        PangoCairo.show_layout(ctx, self.layout)

    def update_size(self):
        self.size = (1 + math.ceil(math.log(self.source_view.get_buffer().get_line_count() + 1, 10))) * self.char_width

    def get_size(self):
        return self.size

    def set_visibility(self, value):
        self.visible = value
        self.source_view.queue_draw()

    def is_visible(self):
        return self.visible


