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
from gi.repository import cairo

from setzer.helpers.timer import timer
import setzer.helpers.drawing as drawing_helper


class DocumentStructurePagePresenter(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.nodes_in_line = list()

        self.view_width = None

        self.bg_color = None
        self.hover_color = None
        self.fg_color = None
        self.icon_infos = dict()
        self.icons = dict()
        self.first_line = None
        self.last_line = None

        for icon_name in self.model.levels:
            self.icon_infos[icon_name] = Gtk.IconTheme.get_default().lookup_icon(icon_name + '-symbolic', 16 * self.view.get_scale_factor(), 0)

        self.view.content.connect('draw', self.draw)

    #@timer
    def draw(self, drawing_area, ctx):
        style_context = drawing_area.get_style_context()

        ctx.set_font_size(self.view.font_size)
        ctx.select_font_face(self.view.font.get_family(), cairo.FontSlant.NORMAL, cairo.FontWeight.NORMAL)

        offset = self.view.scrolled_window.get_vadjustment().get_value()
        self.view_width = self.view.scrolled_window.get_allocated_width()
        view_height = self.view.scrolled_window.get_allocated_height()
        additional_height = ctx.get_target().get_height() - view_height
        additional_lines = additional_height // self.view.line_height + 2
        self.first_line = max(int(offset // self.view.line_height) - additional_lines, 0)
        self.last_line = int((offset + view_height) // self.view.line_height) + additional_lines

        self.bg_color = style_context.lookup_color('theme_base_color')[1]
        self.hover_color = style_context.lookup_color('theme_bg_color')[1]
        fg_color = style_context.lookup_color('theme_fg_color')[1]

        if not self.fg_color or fg_color.red != self.fg_color.red or fg_color.green != self.fg_color.green or fg_color.blue != self.fg_color.blue or fg_color.alpha != self.fg_color.alpha:
            self.fg_color = fg_color
            self.icons = dict()
            for icon_name, icon_info in self.icon_infos.items():
                pixbuf, was_symbolic = icon_info.load_symbolic(self.fg_color, self.fg_color, self.fg_color, self.fg_color)
                surface = Gdk.cairo_surface_create_from_pixbuf(pixbuf, self.view.get_scale_factor())
                self.icons[icon_name + '-symbolic'] = surface

        self.draw_background(drawing_area, ctx)
        self.nodes_in_line = list()
        self.draw_nodes(self.model.nodes, 0, 0, drawing_area, ctx)
        self.model.nodes_in_line = self.nodes_in_line

    def draw_background(self, drawing_area, ctx):
        ctx.set_source_rgba(self.bg_color.red, self.bg_color.green, self.bg_color.blue, self.bg_color.alpha)
        ctx.rectangle(0, 0, self.view_width, self.model.height)
        ctx.fill()

    def draw_nodes(self, nodes, level, count, drawing_area, ctx):
        for node in nodes:
            self.nodes_in_line.append(node)
            if count >= self.first_line and count <= self.last_line:
                if count == self.model.hover_item:
                    ctx.set_source_rgba(self.hover_color.red, self.hover_color.green, self.hover_color.blue, self.hover_color.alpha)
                    ctx.rectangle(0, count * self.view.line_height + 8, self.view_width, self.view.line_height)
                    ctx.fill()

                ctx.move_to(9 + level * 18, count * self.view.line_height + 12)
                surface = self.icons[node['item'][2]]
                surface.set_device_offset(- (9 + level * 18) * self.view.get_scale_factor(), -(count * self.view.line_height + 12) * self.view.get_scale_factor())
                ctx.set_source_surface(surface)
                ctx.rectangle(9 + level * 18, count * self.view.line_height + 12, 16, 16)
                ctx.fill()

                ctx.set_source_rgba(self.fg_color.red, self.fg_color.green, self.fg_color.blue, self.fg_color.alpha)
                text = drawing_helper.ellipsize_back(ctx, node['item'][3], self.view_width - (53 + level * 18))
                ctx.move_to(35 + level * 18, (count + 1) * self.view.line_height + 1)
                ctx.show_text(text)
            count += 1
            count = self.draw_nodes(node['children'], level + 1, count, drawing_area, ctx)
        return count


