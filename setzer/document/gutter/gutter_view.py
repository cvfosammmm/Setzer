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
from gi.repository import Gtk, Gdk, Pango, PangoCairo

import math

from setzer.helpers.timer import timer
from setzer.app.service_locator import ServiceLocator
from setzer.app.color_manager import ColorManager
from setzer.app.font_manager import FontManager


class GutterView(Gtk.DrawingArea):

    def __init__(self, gutter):
        Gtk.DrawingArea.__init__(self)
        self.gutter = gutter

        self.set_halign(Gtk.Align.START)
        self.set_draw_func(self.draw)

    #@timer
    def draw(self, drawing_area, ctx, width, height, data=None):
        if self.total_size == 0: return

        self.draw_background_and_border(ctx, width, height)

        fg_color = ColorManager.get_ui_color('view_fg_color')
        Gdk.cairo_set_source_rgba(ctx, fg_color)

        if self.current_line == self.lines[0]: layout = self.layout_current_line
        else: layout = self.layout_normal

        if self.lines[0] == self.lines[1]:
            ctx.move_to(0, 0)
        else:
            ctx.move_to(0, -self.first_line_offset)
        layout.set_text(str(self.lines[0] + 1))
        PangoCairo.show_layout(ctx, layout)
        last_line = self.lines[0]

        for i, line in enumerate(self.lines[1:]):
            if self.current_line == line: layout = self.layout_current_line
            else: layout = self.layout_normal

            if line != last_line:
                ctx.move_to(0, -self.first_line_offset + (i + 1) * self.line_height)
                layout.set_text(str(line + 1))
                PangoCairo.show_layout(ctx, layout)
            last_line = line

    def draw_background_and_border(self, ctx, width, height):
        bg_color = ColorManager.get_ui_color('view_bg_color')
        border_color = ColorManager.get_ui_color('borders')

        Gdk.cairo_set_source_rgba(ctx, bg_color)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

        Gdk.cairo_set_source_rgba(ctx, border_color)
        ctx.rectangle(width - 1, 0, 1, height)
        ctx.fill()


