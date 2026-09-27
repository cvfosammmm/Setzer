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

import math

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, Pango, PangoCairo

from setzer.app.color_manager import ColorManager


class FixedWidthLabel(Gtk.DrawingArea):

    def __init__(self, width):
        Gtk.DrawingArea.__init__(self)

        self.width = width
        self.set_size_request(width, -1)
        self.layout = Pango.Layout(self.get_pango_context())
        self.layout.set_text('')
        self.layout.set_width(width * Pango.SCALE)
        self.layout.set_alignment(Pango.Alignment.CENTER)
        self.set_draw_func(self.draw)
        self.queue_draw()

    def set_text(self, text):
        self.layout.set_text(text)

        # grow (never shrink) if the text doesn't fit, e.g. in longer translations.
        # the size request includes css padding, so the text only gets what is left of it.
        self.layout.set_width(-1)
        text_width = math.ceil(self.layout.get_size()[0] / Pango.SCALE)
        padding = self.get_style_context().get_padding()
        padding_width = padding.left + padding.right
        if text_width + padding_width > self.width:
            self.width = text_width + padding_width
            self.set_size_request(self.width, -1)
        self.layout.set_width((self.width - padding_width) * Pango.SCALE)

        self.queue_draw()

    def draw(self, drawing_area, ctx, width, height):
        fg_color = ColorManager.get_ui_color('window_fg_color')
        Gdk.cairo_set_source_rgba(ctx, fg_color)
        PangoCairo.show_layout(ctx, self.layout)


