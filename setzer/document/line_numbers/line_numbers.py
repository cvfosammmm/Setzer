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

        self.line_height = 0
        self.char_width = 0
        self.font_desc = None
        self.font_size = None
        self.font_changed = True
        self.glyph_index = None
        self.extents = None

        self.size = 0
        self.visible = False
        self.update_size()

        document.gutter.add_widget(self)

        settings = ServiceLocator.get_settings()
        self.set_visibility(settings.get_value('preferences', 'show_line_numbers'))
        settings.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'settings_changed':
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

    #@timer
    def on_draw(self, drawing_area, ctx, lines, current_line, offset):
        ctx.set_font_size(self.font_size)
        font_family = self.font_desc.get_family()
        ctx.select_font_face(font_family, cairo.FontSlant.NORMAL, cairo.FontWeight.NORMAL)

        if self.font_changed:
            scaled_font = ctx.get_scaled_font()
            self.font_changed = False
            glyph_index = {}
            glyph_index[0] = scaled_font.text_to_glyphs(0, 0, '0')[0][0][0]
            glyph_index[1] = scaled_font.text_to_glyphs(0, 0, '1')[0][0][0]
            glyph_index[2] = scaled_font.text_to_glyphs(0, 0, '2')[0][0][0]
            glyph_index[3] = scaled_font.text_to_glyphs(0, 0, '3')[0][0][0]
            glyph_index[4] = scaled_font.text_to_glyphs(0, 0, '4')[0][0][0]
            glyph_index[5] = scaled_font.text_to_glyphs(0, 0, '5')[0][0][0]
            glyph_index[6] = scaled_font.text_to_glyphs(0, 0, '6')[0][0][0]
            glyph_index[7] = scaled_font.text_to_glyphs(0, 0, '7')[0][0][0]
            glyph_index[8] = scaled_font.text_to_glyphs(0, 0, '8')[0][0][0]
            glyph_index[9] = scaled_font.text_to_glyphs(0, 0, '9')[0][0][0]
            extents = {}
            extents[0] = int(ctx.text_extents('0').x_advance)
            extents[1] = int(ctx.text_extents('1').x_advance)
            extents[2] = int(ctx.text_extents('2').x_advance)
            extents[3] = int(ctx.text_extents('3').x_advance)
            extents[4] = int(ctx.text_extents('4').x_advance)
            extents[5] = int(ctx.text_extents('5').x_advance)
            extents[6] = int(ctx.text_extents('6').x_advance)
            extents[7] = int(ctx.text_extents('7').x_advance)
            extents[8] = int(ctx.text_extents('8').x_advance)
            extents[9] = int(ctx.text_extents('9').x_advance)
            self.glyph_index = glyph_index
            self.extents = extents

        extra_y = (self.line_height + ctx.text_extents('0').height) / 2
        glyphs_normal = list()
        glyphs_bold = list()
        for line in lines:
            yoffset = int(line[1] + extra_y)
            xoffset = offset + self.size
            cline = line[0]

            if current_line != None and cline == current_line[0]:
                while cline > 0:
                    char = cline % 10
                    xoffset -= self.extents[char]
                    glyphs_bold.append((self.glyph_index[char], xoffset, yoffset))
                    cline = cline // 10
            else:
                while cline > 0:
                    char = cline % 10
                    xoffset -= self.extents[char]
                    glyphs_normal.append((self.glyph_index[char], xoffset, yoffset))
                    cline = cline // 10

        ctx.show_glyphs(glyphs_normal, len(glyphs_normal))

        if glyphs_bold:
            ctx.select_font_face(font_family, cairo.FontSlant.NORMAL, cairo.FontWeight.BOLD)
            ctx.show_glyphs(glyphs_bold, len(glyphs_bold))

    def update_size(self):
        self.size = math.ceil(math.log(self.source_view.get_buffer().get_line_count() + 1, 10)) * self.char_width

    def get_size(self):
        return self.size

    def set_visibility(self, value):
        self.visible = value
        self.source_view.queue_draw()

    def is_visible(self):
        return self.visible


