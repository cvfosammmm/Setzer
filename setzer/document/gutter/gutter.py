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
from setzer.app.service_locator import ServiceLocator


class Gutter(object):

    def __init__(self, document, document_view):
        self.document = document
        self.source_view = document_view.source_view
        self.adjustment = document_view.scrolled_window.get_vadjustment()

        self.font_manager = ServiceLocator.get_font_manager()

        self.view = Gtk.DrawingArea()
        self.view.set_valign(Gtk.Align.FILL)
        self.view.set_halign(Gtk.Align.START)
        self.view.connect('draw', self.on_draw)
        self.view.show_all()
        def on_realize(widget): widget.get_window().set_pass_through(True)
        self.view.connect('realize', on_realize)

        document_view.overlay.add_overlay(self.view)
        document_view.overlay.set_overlay_pass_through(self.view, True)

        self.widgets = list()
        self.total_size = 0
        self.lines = list()
        self.current_line = 0

        self.source_view.connect('button-press-event', self.on_click)

    #@timer
    def on_draw(self, drawing_area, ctx, data = None):
        self.update_sizes()
        if self.total_size != 0:
            self.update_lines()
            style_scheme = self.document.source_buffer.get_style_scheme()
            line_numbers_style = style_scheme.get_style('line-numbers')
            bg_color_string = line_numbers_style.get_property('background')
            if bg_color_string != None:
                bg_color = Gdk.RGBA(0, 0, 0, 0)
                bg_color.parse(bg_color_string)
            else:
                bg_color = self.view.get_style_context().lookup_color('theme_base_color')[1]
            fg_color_string = line_numbers_style.get_property('foreground')
            if fg_color_string != None:
                fg_color = Gdk.RGBA(0, 0, 0, 0)
                fg_color.parse(fg_color_string)
            else:
                self.view.get_style_context().lookup_color('theme_fg_color')[1]

            current_line_style = style_scheme.get_style('current-line')
            cl_color_string = current_line_style.get_property('background')
            if cl_color_string != None:
                cl_color = Gdk.RGBA(0, 0, 0, 0)
                cl_color.parse(cl_color_string)
            else:
                self.view.get_style_context().lookup_color('theme_base_color')[1]

            ctx.rectangle(0, 0, drawing_area.get_allocated_width(), drawing_area.get_allocated_height())
            ctx.set_source_rgba(bg_color.red, bg_color.green, bg_color.blue, bg_color.alpha)
            ctx.fill()

            for count, line in enumerate(self.lines):
                if line[0] == self.current_line:
                    ctx.rectangle(0, line[1], drawing_area.get_allocated_width(), line[2])
                    ctx.set_source_rgba(cl_color.red, cl_color.green, cl_color.blue, cl_color.alpha)
                    ctx.fill()
                    break

            ctx.set_source_rgba(fg_color.red, fg_color.green, fg_color.blue, fg_color.alpha)

            total_size = 0
            for widget in self.widgets:
                if widget.is_visible():
                    widget.on_draw(drawing_area, ctx, self.lines, self.current_line, total_size)
                    total_size += widget.get_size()

    def update_lines(self):
        lines = list()
        y_window = 0
        allocated_height = self.source_view.get_allocated_height()
        last_line_top = None
        offset = self.adjustment.get_value()
        line_height = self.font_manager.get_line_height(self.source_view)
        while y_window <= allocated_height:
            y = y_window + offset
            line_iter, line_top = self.source_view.get_line_at_y(y)
            y2, height = self.source_view.get_line_yrange(line_iter)
            if line_top != last_line_top:
                line = line_iter.get_line() + 1
                lines.append((line, line_top - int(offset), height))
                last_line_top = line_top
            y_window += line_height - 1
            if y_window > allocated_height and y_window < allocated_height + line_height - 1:
                y_window = allocated_height
        self.lines = lines
        self.current_line = self.document.get_current_line_number() + 1

    def on_click(self, widget, event):
        x, y = self.source_view.window_to_buffer_coords(Gtk.TextWindowType.LEFT, event.x, event.y)
        if event.window == self.source_view.get_window(Gtk.TextWindowType.LEFT):
            x += self.total_size
            total_size = 0
            for widget in self.widgets:
                if widget.is_visible():
                    total_size += widget.get_size()
                    if total_size >= x:
                        return widget.on_click(event)
        return False

    def add_widget(self, widget):
        self.widgets.append(widget)
        self.update_sizes()

    def update_sizes(self):
        total_size = 0
        for widget in self.widgets:
            if widget.is_visible():
                widget.update_size()
                total_size += widget.get_size()
        if total_size != self.total_size:
            self.total_size = total_size
            self.source_view.set_border_window_size(Gtk.TextWindowType.LEFT, self.total_size)
            self.view.set_size_request(self.total_size, 1000)


