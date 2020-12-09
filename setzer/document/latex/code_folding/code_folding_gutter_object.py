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
        self.source_view = self.model.document.source_buffer.view

        self.size = 0
        self.visible = False

    def set_line_height(self, line_height):
        self.size = line_height

    def on_click(self, event):
        x, y = self.source_view.window_to_buffer_coords(Gtk.TextWindowType.LEFT, event.x, event.y)
        line_iter, line_top = self.source_view.get_line_at_y(y)
        line_number = line_iter.get_line()
        if x >= -18 and line_number in self.model.folding_regions:
            if event.type == Gdk.EventType.BUTTON_PRESS:
                self.model.toggle_folding_region(self.model.folding_regions[line_number])
            return True
        return False

    #@timer
    def on_draw(self, drawing_area, ctx, lines, current_line, offset):
        ctx.set_line_width(0)
        for line in lines:
            if (line[0] - 1) in self.model.folding_regions.keys():
                if self.model.folding_regions[line[0] - 1]['is_folded']:
                    ctx.move_to(offset + 3 * self.size / 6, line[1] + 1.5 * self.size / 8)
                    ctx.line_to(offset + 5 * self.size / 6, line[1] + 4 * self.size / 8)
                    ctx.line_to(offset + 3 * self.size / 6, line[1] + 6.5 * self.size / 8)
                    ctx.line_to(offset + 3 * self.size / 6, line[1] + 1.5 * self.size / 8)
                    ctx.stroke_preserve()
                    ctx.fill()
                    ctx.rectangle(offset + 1 * self.size / 11, line[1] + self.size, 2 * self.size / 11, -1)
                    ctx.rectangle(offset + 5 * self.size / 11, line[1] + self.size, 2 * self.size / 11, -1)
                    ctx.rectangle(offset + 9 * self.size / 11, line[1] + self.size, 2 * self.size / 11, -1)
                    ctx.stroke_preserve()
                    ctx.fill()
                    ctx.set_line_width(0)
                else:
                    ctx.move_to(offset + 3 * self.size / 8, line[1] + 2 * self.size / 6)
                    ctx.line_to(offset + 5.5 * self.size / 8, line[1] + 4 * self.size / 6)
                    ctx.line_to(offset + 8 * self.size / 8, line[1] + 2 * self.size / 6)
                    ctx.line_to(offset + 3 * self.size / 8, line[1] + 2 * self.size / 6)
                    ctx.stroke_preserve()
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


