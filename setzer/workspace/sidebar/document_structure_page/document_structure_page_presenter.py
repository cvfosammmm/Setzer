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

import os.path
import time

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

        for icon_name in self.model.levels:
            self.icon_infos[icon_name] = Gtk.IconTheme.get_default().lookup_icon(icon_name + '-symbolic', 16 * self.view.get_scale_factor(), 0)
        self.icon_infos['tag'] = Gtk.IconTheme.get_default().lookup_icon('tag-symbolic', 16 * self.view.get_scale_factor(), 0)

        self.view.content_widgets['files'].connect('draw', self.draw_files)
        self.view.content_widgets['structure'].connect('draw', self.draw_structure)
        self.view.content_widgets['labels'].connect('draw', self.draw_labels_widget)

    #@timer
    def draw_files(self, drawing_area, ctx):
        first_line, last_line = self.drawing_setup(drawing_area, ctx, 0)

        self.draw_background(drawing_area, ctx)

        count = 0

        if self.model.files_hover_item == 0:
            ctx.set_source_rgba(self.hover_color.red, self.hover_color.green, self.hover_color.blue, self.hover_color.alpha)
            ctx.rectangle(0, count * self.view.line_height + 9, self.view_width, self.view.line_height)
            ctx.fill()

        ctx.move_to(9, count * self.view.line_height + 13)
        surface = self.icons['file-symbolic']
        surface.set_device_offset(-9 * self.view.get_scale_factor(), -(count * self.view.line_height + 13) * self.view.get_scale_factor())
        ctx.set_source_surface(surface)
        ctx.rectangle(9, count * self.view.line_height + 13, 16, 16)
        ctx.fill()

        ctx.set_source_rgba(self.fg_color.red, self.fg_color.green, self.fg_color.blue, self.fg_color.alpha)
        text = drawing_helper.ellipsize_back(ctx, os.path.basename(self.model.document.get_filename()), self.view_width - 53)
        ctx.move_to(35, (count + 1) * self.view.line_height + 2)
        ctx.show_text(text)

        count += 1

        for include in self.model.includes:
            if count >= first_line and count <= last_line:
                if count == self.model.files_hover_item:
                    ctx.set_source_rgba(self.hover_color.red, self.hover_color.green, self.hover_color.blue, self.hover_color.alpha)
                    ctx.rectangle(0, count * self.view.line_height + 9, self.view_width, self.view.line_height)
                    ctx.fill()

                ctx.move_to(27, count * self.view.line_height + 13)
                surface = self.icons['file-symbolic']
                surface.set_device_offset(-27 * self.view.get_scale_factor(), -(count * self.view.line_height + 13) * self.view.get_scale_factor())
                ctx.set_source_surface(surface)
                ctx.rectangle(27, count * self.view.line_height + 13, 16, 16)
                ctx.fill()

                ctx.set_source_rgba(self.fg_color.red, self.fg_color.green, self.fg_color.blue, self.fg_color.alpha)
                text = drawing_helper.ellipsize_back(ctx, os.path.basename(include['filename']), self.view_width - 71)
                ctx.move_to(53, (count + 1) * self.view.line_height + 2)
                ctx.show_text(text)

            count += 1

    #@timer
    def draw_labels_widget(self, drawing_area, ctx):
        if len(self.model.labels) == 0:
            return True

        first_line, last_line = self.drawing_setup(drawing_area, ctx, self.model.files_view_height + self.view.labels['structure']['inline'].get_allocated_height() * 2 + self.model.structure_view_height)

        self.draw_background(drawing_area, ctx)

        count = 0
        for label in self.model.labels:
            if count >= first_line and count <= last_line:
                if count == self.model.labels_hover_item:
                    ctx.set_source_rgba(self.hover_color.red, self.hover_color.green, self.hover_color.blue, self.hover_color.alpha)
                    ctx.rectangle(0, count * self.view.line_height + 9, self.view_width, self.view.line_height)
                    ctx.fill()

                ctx.move_to(9, count * self.view.line_height + 13)
                surface = self.icons['tag-symbolic']
                surface.set_device_offset(-9 * self.view.get_scale_factor(), -(count * self.view.line_height + 13) * self.view.get_scale_factor())
                ctx.set_source_surface(surface)
                ctx.rectangle(9, count * self.view.line_height + 13, 16, 16)
                ctx.fill()

                ctx.set_source_rgba(self.fg_color.red, self.fg_color.green, self.fg_color.blue, self.fg_color.alpha)
                text = drawing_helper.ellipsize_back(ctx, label[0], self.view_width - 53)
                ctx.move_to(35, (count + 1) * self.view.line_height + 2)
                ctx.show_text(text)

            count += 1

    #@timer
    def draw_structure(self, drawing_area, ctx):
        if len(self.model.nodes) == 0:
            return True

        first_line, last_line = self.drawing_setup(drawing_area, ctx, self.model.files_view_height + self.view.labels['structure']['inline'].get_allocated_height())

        self.draw_background(drawing_area, ctx)
        self.nodes_in_line = list()
        self.draw_nodes(self.model.nodes, first_line, last_line, 0, 0, drawing_area, ctx)
        self.model.nodes_in_line = self.nodes_in_line

    def draw_background(self, drawing_area, ctx):
        ctx.set_source_rgba(self.bg_color.red, self.bg_color.green, self.bg_color.blue, self.bg_color.alpha)
        ctx.rectangle(0, 0, self.view_width, self.model.structure_view_height)
        ctx.fill()

    def draw_nodes(self, nodes, first_line, last_line, level, count, drawing_area, ctx):
        for node in nodes:
            self.nodes_in_line.append(node)
            if count >= first_line and count <= last_line:
                if count == self.model.structure_hover_item:
                    ctx.set_source_rgba(self.hover_color.red, self.hover_color.green, self.hover_color.blue, self.hover_color.alpha)
                    ctx.rectangle(0, count * self.view.line_height + 9, self.view_width, self.view.line_height)
                    ctx.fill()

                ctx.move_to(9 + level * 18, count * self.view.line_height + 13)
                surface = self.icons[node['item'][2]]
                surface.set_device_offset(- (9 + level * 18) * self.view.get_scale_factor(), -(count * self.view.line_height + 13) * self.view.get_scale_factor())
                ctx.set_source_surface(surface)
                ctx.rectangle(9 + level * 18, count * self.view.line_height + 13, 16, 16)
                ctx.fill()

                ctx.set_source_rgba(self.fg_color.red, self.fg_color.green, self.fg_color.blue, self.fg_color.alpha)
                text = drawing_helper.ellipsize_back(ctx, node['item'][3], self.view_width - (53 + level * 18))
                ctx.move_to(35 + level * 18, (count + 1) * self.view.line_height + 2)
                ctx.show_text(text)
            count += 1
            count = self.draw_nodes(node['children'], first_line, last_line, level + 1, count, drawing_area, ctx)
        return count

    def drawing_setup(self, drawing_area, ctx, widget_offset):
        style_context = drawing_area.get_style_context()

        ctx.set_font_size(self.view.font_size)
        ctx.select_font_face(self.view.font.get_family(), cairo.FontSlant.NORMAL, cairo.FontWeight.NORMAL)

        offset = self.view.scrolled_window.get_vadjustment().get_value() - widget_offset
        self.view_width = self.view.scrolled_window.get_allocated_width()
        view_height = self.view.scrolled_window.get_allocated_height()
        additional_height = ctx.get_target().get_height() - view_height
        additional_lines = additional_height // self.view.line_height + 2
        first_line = max(int(offset // self.view.line_height) - additional_lines, 0)
        last_line = int((offset + view_height) // self.view.line_height) + additional_lines

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

        return (first_line, last_line)

    def do_scroll(self):
        if self.model.scroll_to != None:
            adjustment = self.view.scrolled_window.get_vadjustment()
            time_elapsed = time.time() - self.model.scroll_to['time_start']
            if self.model.scroll_to['duration'] == 0:
                time_elapsed_percent = 1
            else:
                time_elapsed_percent = time_elapsed / self.model.scroll_to['duration']
            if time_elapsed_percent >= 1:
                adjustment.set_value(self.model.scroll_to['position_end'])
                self.model.scroll_to = None
                self.view.scrolled_window.set_kinetic_scrolling(True)
                return False
            else:
                adjustment.set_value(self.model.scroll_to['position_start'] * (1 - self.ease(time_elapsed_percent)) + self.model.scroll_to['position_end'] * self.ease(time_elapsed_percent))
                return True
        return False

    def ease(self, time): return (time - 1)**3 + 1


