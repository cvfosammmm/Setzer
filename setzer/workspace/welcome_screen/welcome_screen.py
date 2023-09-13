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
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gdk, GObject, Pango, PangoCairo
import cairo

import time

from setzer.app.service_locator import ServiceLocator
from setzer.app.color_manager import ColorManager
from setzer.helpers.timer import timer


class WelcomeScreen(object):

    def __init__(self):
        self.view = ServiceLocator.get_main_window().welcome_screen

        self.font_desc = Pango.FontDescription.from_string('cmr10')
        self.angle = 0.15
        self.alpha = 0.065
        self.font_size = 36
        self.line_height = 70
        self.font_desc.set_size(self.font_size * Pango.SCALE)

        self.is_active = False
        self.lines_per_second = 0.25
        self.animate = False

        self.activate()

        self.gradient_size = None
        self.gradient_surface = None
        self.full_gradient_surface = None

        self.view.drawing_area.set_draw_func(self.draw)
        self.do_draw()

    def activate(self):
        self.is_active = True
        self.do_draw()
        if self.animate:
            GObject.timeout_add(15, self.do_draw)

    def deactivate(self):
        self.is_active = False

    def do_draw(self):
        self.view.drawing_area.queue_draw()
        return self.is_active

    def draw(self, drawing_area, ctx, width, height, data=None):
        self.fg_color = ColorManager.get_ui_color('window_fg_color')
        self.fg_color.alpha = self.alpha
        self.bg_color = ColorManager.get_ui_color('window_bg_color')

        ctx.rotate(-self.angle)
        Gdk.cairo_set_source_rgba(ctx, self.fg_color)

        layout = Pango.Layout(drawing_area.get_pango_context())
        layout.set_font_description(self.font_desc)

        if self.animate:
            y = -self.line_height - int(time.time() * self.line_height * self.lines_per_second) % self.line_height
            line = int(int(time.time() * self.lines_per_second) % self.lines_per_second) + int(self.lines_per_second * (int(time.time()) % int(20 // self.lines_per_second)))
        else:
            y = -70
            line = 0

        text = self.view.text[line:] + self.view.text[:line]
        for paragraph in text:
            ctx.rotate(self.angle)
            y += self.line_height
            ctx.move_to(-50, y)
            ctx.rotate(-self.angle)

            layout.set_text(paragraph)
            PangoCairo.show_layout(ctx, layout)

            if y > (height + width / 3): break

        ctx.rotate(self.angle)


