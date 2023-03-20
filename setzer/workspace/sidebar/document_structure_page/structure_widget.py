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
from gi.repository import Gdk
from gi.repository import cairo

import setzer.helpers.drawing as drawing_helper


class StructureWidget(object):

    def __init__(self, data_provider):
        self.data_provider = data_provider
        self.data_provider.connect('data_updated', self.update_items)

        self.height = 0
        self.hover_item = None

    def init_view(self):
        self.view.connect('enter-notify-event', self.on_enter)
        self.view.connect('motion-notify-event', self.on_hover)
        self.view.connect('leave-notify-event', self.on_leave)
        self.view.connect('button-press-event', self.on_button_press)
        self.view.connect('draw', self.draw)

    def on_enter(self, widget, event):
        self.update_hover_state(event)

    def on_hover(self, widget, event):
        self.update_hover_state(event)

    def on_leave(self, widget, event):
        self.set_hover_item(None)

    def update_hover_state(self, event):
        if event.y >= 9:
            item_num = int((event.y - 9) // self.view.line_height)
            self.set_hover_item(item_num)
        else:
            self.set_hover_item(None)

    def set_hover_item(self, item):
        self.hover_item = item
        self.view.queue_draw()

    def draw_hover_background(self, ctx, item_num):
        if self.hover_item == item_num:
            ctx.set_source_rgba(self.view.hover_color.red, self.view.hover_color.green, self.view.hover_color.blue, self.view.hover_color.alpha)
            ctx.rectangle(0, item_num * self.view.line_height + 9, self.view_width, self.view.line_height)
            ctx.fill()

    def draw_icon(self, ctx, icon_name, voffset, item_num):
        ctx.move_to(voffset, item_num * self.view.line_height + 13)
        surface = self.view.icons[icon_name]
        surface.set_device_offset(-voffset * self.view.get_scale_factor(), -(item_num * self.view.line_height + 13) * self.view.get_scale_factor())
        ctx.set_source_surface(surface)
        ctx.rectangle(voffset, item_num * self.view.line_height + 13, 16, 16)
        ctx.fill()

    def draw_text(self, ctx, voffset, item_num, text):
        text = drawing_helper.ellipsize_back(ctx, text, self.view_width - (voffset + 18))
        ctx.set_source_rgba(self.view.fg_color.red, self.view.fg_color.green, self.view.fg_color.blue, self.view.fg_color.alpha)
        ctx.move_to(voffset, (item_num + 1) * self.view.line_height + 2)
        ctx.show_text(text)

    def drawing_setup(self, ctx):
        style_context = self.view.get_style_context()

        ctx.set_font_size(self.view.font_size)
        ctx.select_font_face(self.view.font.get_family(), cairo.FontSlant.NORMAL, cairo.FontWeight.NORMAL)

        self.view_width = self.view.get_allocated_width()

        self.view.bg_color = style_context.lookup_color('theme_base_color')[1]
        self.view.hover_color = style_context.lookup_color('theme_bg_color')[1]
        fg_color = style_context.lookup_color('theme_fg_color')[1]

        if not self.view.fg_color or fg_color.red != self.view.fg_color.red or fg_color.green != self.view.fg_color.green or fg_color.blue != self.view.fg_color.blue or fg_color.alpha != self.view.fg_color.alpha:
            self.view.fg_color = fg_color
            self.icons = dict()
            for icon_name, icon_info in self.view.icon_infos.items():
                pixbuf, was_symbolic = icon_info.load_symbolic(self.view.fg_color, self.view.fg_color, self.view.fg_color, self.view.fg_color)
                surface = Gdk.cairo_surface_create_from_pixbuf(pixbuf, self.view.get_scale_factor())
                self.view.icons[icon_name + '-symbolic'] = surface

    def get_first_line_last_line(self, ctx):
        extents = ctx.clip_extents()
        return extents[1] // self.view.line_height, extents[3] // self.view.line_height

    def draw_background(self, ctx):
        ctx.set_source_rgba(self.view.bg_color.red, self.view.bg_color.green, self.view.bg_color.blue, self.view.bg_color.alpha)
        ctx.rectangle(0, 0, self.view_width, self.height)
        ctx.fill()


