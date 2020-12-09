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

        self.widgets = list()
        self.total_size = 0
        self.lines = list()
        self.current_line = 0

        self.font_manager = ServiceLocator.get_font_manager()
        self.font_manager.register_observer(self)

        self.view = Gtk.DrawingArea()
        self.view.set_valign(Gtk.Align.FILL)
        self.view.set_halign(Gtk.Align.START)
        self.view.connect('draw', self.on_draw)
        self.view.show_all()
        def on_realize(widget): widget.get_window().set_pass_through(True)
        self.view.connect('realize', on_realize)
        self.style_context = self.view.get_style_context()
        self.bg_color = Gdk.RGBA(0, 0, 0, 0)
        self.fg_color = Gdk.RGBA(0, 0, 0, 0)
        self.cl_color = Gdk.RGBA(0, 0, 0, 0)
        self.update_colors()
        self.source_view.get_style_context().connect('changed', self.update_colors)

        document_view.overlay.add_overlay(self.view)
        document_view.overlay.set_overlay_pass_through(self.view, True)

        self.line_height = self.font_manager.get_line_height(self.source_view)

        self.source_view.connect('button-press-event', self.on_click)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'font_string_changed':
            self.line_height = self.font_manager.get_line_height(self.source_view)
            for widget in self.widgets:
                widget.set_line_height(self.line_height)

    #@timer
    def on_draw(self, drawing_area, ctx, data = None):
        self.update_sizes()
        if self.total_size != 0:
            self.update_lines()
            self.draw_background(drawing_area, ctx)

            ctx.set_source_rgba(self.fg_color.red, self.fg_color.green, self.fg_color.blue, self.fg_color.alpha)
            total_size = 0
            for widget in self.widgets:
                if widget.is_visible():
                    widget.on_draw(drawing_area, ctx, self.lines, self.current_line, total_size)
                    total_size += widget.get_size()

    #@timer
    def draw_background(self, drawing_area, ctx):
        ctx.set_source_rgba(self.bg_color.red, self.bg_color.green, self.bg_color.blue, self.bg_color.alpha)
        ctx.rectangle(0, 0, self.total_size, self.source_view.get_allocated_height())
        ctx.fill()

        if self.current_line != None:
            ctx.rectangle(0, self.current_line[1], self.total_size, self.current_line[2])
            ctx.set_source_rgba(self.cl_color.red, self.cl_color.green, self.cl_color.blue, self.cl_color.alpha)
            ctx.fill()

    #@timer
    def update_colors(self, style_context=None):
        style_scheme = self.document.source_buffer.get_style_scheme()
        line_numbers_style = style_scheme.get_style('line-numbers')
        bg_color_string = line_numbers_style.get_property('background')
        if bg_color_string != None:
            bg_color = Gdk.RGBA(0, 0, 0, 0)
            bg_color.parse(bg_color_string)
        else:
            theme_base_color = self.style_context.lookup_color('theme_base_color')[1]
            theme_bg_color = self.style_context.lookup_color('theme_bg_color')[1]
            bg_color = Gdk.RGBA(0, 0, 0, 0)
            bg_color.red = theme_base_color.red / 2 + theme_bg_color.red / 2
            bg_color.green = theme_base_color.green / 2 + theme_bg_color.green / 2
            bg_color.blue = theme_base_color.blue / 2 + theme_bg_color.blue / 2
            bg_color.alpha = theme_base_color.alpha / 2 + theme_bg_color.alpha / 2
        self.bg_color = bg_color

        fg_color_string = line_numbers_style.get_property('foreground')
        if fg_color_string != None:
            fg_color = Gdk.RGBA(0, 0, 0, 0)
            fg_color.parse(fg_color_string)
        else:
            fg_color = self.style_context.lookup_color('theme_fg_color')[1]
        self.fg_color = fg_color

        current_line_style = style_scheme.get_style('current-line')
        cl_color_string = current_line_style.get_property('background')
        if cl_color_string != None:
            cl_color = Gdk.RGBA(0, 0, 0, 0)
            cl_color.parse(cl_color_string)
        else:
            cl_color = self.style_context.lookup_color('theme_base_color')[1]
        self.cl_color = cl_color

        for widget in self.widgets:
            widget.update_colors()

        self.view.queue_draw()

    #@timer
    def update_lines(self):
        lines = list()
        y_window = 0
        allocated_height = self.source_view.get_allocated_height()
        last_line_top = None
        line = None
        current_line = None
        current_line_no = self.document.get_current_line_number() + 1
        offset = self.adjustment.get_value()
        while y_window <= allocated_height:
            y = y_window + offset
            line_iter, line_top = self.source_view.get_line_at_y(y)

            if line_top != last_line_top:
                if len(lines):
                    lines[-1][2] = line_top - last_line_top
                    if lines[-1][0] == current_line_no:
                        current_line[2] = line_top - last_line_top

                line = line_iter.get_line() + 1

                lines.append([line, line_top - int(offset), None])
                if line == current_line_no:
                    current_line = [line, line_top - int(offset), None]

                last_line_top = line_top
            y_window += self.line_height - 1
            if y_window > allocated_height and y_window < allocated_height + self.line_height - 1:
                y_window = allocated_height

        y2, height = self.source_view.get_line_yrange(line_iter)
        lines[-1][2] = height
        if lines[-1][0] == current_line_no:
            current_line[2] = height

        self.lines = lines
        self.current_line = current_line

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
        widget.set_line_height(self.line_height)
        widget.update_colors()
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


