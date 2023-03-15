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

from setzer.helpers.timer import timer


class CodeFoldingGutterObject(object):

    def __init__(self, model):
        self.model = model
        self.source_view = self.model.document.view.source_view

        self.hovered_region = None

        self.size = 0
        self.height = 0
        self.visible = False

    def set_font_desc(self, font_desc):
        pass

    def set_char_dimensions(self, line_height, char_width):
        self.size = 2 * char_width
        self.height = line_height

    def update_colors(self):
        pass

    def on_click(self, event):
        x, y = self.source_view.window_to_buffer_coords(Gtk.TextWindowType.LEFT, event.x, event.y)
        line_iter, line_top = self.source_view.get_line_at_y(y)
        line_number = line_iter.get_line()
        if x >= -1.5 * self.size and line_number in self.model.folding_regions:
            if event.type == Gdk.EventType.BUTTON_PRESS:
                self.model.toggle_folding_region(self.model.folding_regions[line_number])
            return True
        return False

    def on_pointer_movement(self, event):
        x, y = self.source_view.window_to_buffer_coords(Gtk.TextWindowType.LEFT, event.x, event.y)
        line_iter, line_top = self.source_view.get_line_at_y(y)
        line_number = line_iter.get_line()
        if x >= -1.5 * self.size and line_number in self.model.folding_regions and event.type != Gdk.EventType.LEAVE_NOTIFY:
            self.hovered_region = self.model.folding_regions[line_number]
            self.source_view.queue_draw()
        elif self.hovered_region != None:
            self.hovered_region = None
            self.source_view.queue_draw()

    #@timer
    def on_draw(self, gutter, drawing_area, ctx, lines, current_line, offset):
        ctx.set_line_width(0)
        xoff1 = offset + 3.25 * self.size / 6
        xoff2 = offset + 4.75 * self.size / 6
        xoff3 = offset + 1 * self.size / 11
        xoff4 = offset + 5 * self.size / 11
        xoff5 = offset + 9 * self.size / 11
        xoff6 = offset + 3 * self.size / 8
        xoff7 = offset + 5.5 * self.size / 8
        xoff8 = offset + 8 * self.size / 8
        xoff9 = offset + 13 * self.size / 11
        yoff1 = 1.5 * self.height / 8
        yoff2 = 4 * self.height / 8
        yoff3 = 6.5 * self.height / 8
        yoff4 = 2.25 * self.height / 6
        yoff5 = 3.75 * self.height / 6
        len1 = 2 * self.size / 11

        line_countdown = 0
        for line in lines:
            ctx.set_source_rgba(gutter.border_color_bold.red, gutter.border_color_bold.green, gutter.border_color_bold.blue, gutter.border_color_bold.alpha)
            if line_countdown > 0:
                ctx.rectangle(xoff6 + 1 + self.size, line[1] + line[2], self.size + 3, -line[2])
                ctx.fill()
                line_countdown -= 1

            if (line[0] - 1) in self.model.folding_regions.keys():
                if self.hovered_region == self.model.folding_regions[(line[0] - 1)]:
                    ctx.rectangle(xoff6 + 1 + self.size, line[1] + line[2], self.size + 3, -line[2])
                    ctx.fill()

                    if not self.model.folding_regions[line[0] - 1]['is_folded']:
                        line_countdown = self.hovered_region['ending_line'] - self.hovered_region['starting_line']

                ctx.set_source_rgba(gutter.fg_color.red, gutter.fg_color.green, gutter.fg_color.blue, gutter.fg_color.alpha)
                if self.model.folding_regions[line[0] - 1]['is_folded']:
                    ctx.move_to(xoff1, line[1] + yoff1)
                    ctx.line_to(xoff2, line[1] + yoff2)
                    ctx.line_to(xoff1, line[1] + yoff3)
                    ctx.line_to(xoff1, line[1] + yoff1)
                    ctx.fill()
                    for i in range(4):
                        ctx.rectangle(offset + (i + 0.5) * self.size / 2, line[1] + self.height, self.size / 4, -1)
                        ctx.fill()
                else:
                    ctx.move_to(xoff6, line[1] + yoff4)
                    ctx.line_to(xoff7, line[1] + yoff5)
                    ctx.line_to(xoff8, line[1] + yoff4)
                    ctx.line_to(xoff6, line[1] + yoff4)
                    ctx.fill()

    def update_size(self):
        pass

    def get_size(self):
        return self.size

    def show(self):
        self.visible = True
        self.source_view.queue_draw()

    def hide(self):
        self.visible = False
        self.source_view.queue_draw()

    def is_visible(self):
        return self.visible


