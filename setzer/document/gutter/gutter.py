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
        self.font_manager.connect('font_string_changed', self.on_font_string_changed)

        self.view = Gtk.DrawingArea()
        self.view.set_valign(Gtk.Align.FILL)
        self.view.set_halign(Gtk.Align.START)
        self.view.connect('draw', self.on_draw)
        self.view.show_all()
        def on_realize(widget): widget.get_window().set_pass_through(True)
        self.view.connect('realize', on_realize)
        self.style_context = self.view.get_style_context()
        self.color_manager = ServiceLocator.get_color_manager()
        self.bg_color = None
        self.fg_color = None
        self.cl_color = None
        self.border_color = None
        self.update_colors()
        self.source_view.get_style_context().connect('changed', self.update_colors)

        document_view.overlay.add_overlay(self.view)
        document_view.overlay.set_overlay_pass_through(self.view, True)

        self.char_width, self.line_height = self.font_manager.get_char_dimensions()

        self.source_view.connect('button-press-event', self.on_click)
        self.source_view.connect('enter-notify-event', self.on_pointer_movement)
        self.source_view.connect('leave-notify-event', self.on_pointer_movement)
        self.source_view.connect('motion-notify-event', self.on_pointer_movement)

        self.highlight_current_line = False
        settings = ServiceLocator.get_settings()
        self.set_line_highlighting(settings.get_value('preferences', 'highlight_current_line'))
        settings.connect('settings_changed', self.on_settings_changed)

    def on_font_string_changed(self, font_manager):
        self.char_width, self.line_height = self.font_manager.get_char_dimensions()
        for widget in self.widgets:
            widget.set_font_desc(self.font_manager.get_font_desc())
            widget.set_char_dimensions(self.line_height, self.char_width)

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter
        if (section, item) == ('preferences', 'highlight_current_line'):
            self.set_line_highlighting(value)

    #@timer
    def on_draw(self, drawing_area, ctx, data = None):
        self.update_sizes()
        if self.total_size != 0:
            self.update_lines()
            self.draw_background(drawing_area, ctx)

            ctx.set_source_rgba(self.fg_color.red, self.fg_color.green, self.fg_color.blue, self.fg_color.alpha)
            total_size = 3
            for widget in self.widgets:
                if widget.is_visible():
                    widget.on_draw(self, drawing_area, ctx, self.lines, self.current_line, total_size)
                    total_size += widget.get_size()

    #@timer
    def draw_background(self, drawing_area, ctx):
        if self.highlight_current_line and self.current_line != None:
            ctx.rectangle(0, self.current_line[1], self.total_size, self.current_line[2])
            ctx.set_source_rgba(self.cl_color.red, self.cl_color.green, self.cl_color.blue, self.cl_color.alpha)
            ctx.fill()
        ctx.rectangle(self.total_size - 2, 0, 1, drawing_area.get_allocated_height())
        ctx.set_source_rgba(self.border_color.red, self.border_color.green, self.border_color.blue, self.border_color.alpha)
        ctx.fill()

    #@timer
    def update_colors(self, style_context=None):
        style_scheme = self.document.content.get_style_scheme()
        line_numbers_style = style_scheme.get_style('line-numbers')
        bg_color_string = line_numbers_style.get_property('background')
        if bg_color_string != None:
            self.bg_color = self.color_manager.get_rgba_from_string(bg_color_string)
        else:
            self.bg_color = self.color_manager.get_theme_color_mix('theme_base_color', 'theme_bg_color', 0.5)

        fg_color_string = line_numbers_style.get_property('foreground')
        if fg_color_string != None:
            self.fg_color = self.color_manager.get_rgba_from_string(fg_color_string)
        else:
            self.fg_color = self.color_manager.get_theme_color('theme_fg_color')

        current_line_style = style_scheme.get_style('current-line')
        cl_color_string = current_line_style.get_property('background')
        if cl_color_string != None:
            self.cl_color = self.color_manager.get_rgba_from_string(cl_color_string)
        else:
            self.cl_color = self.color_manager.get_theme_color('theme_base_color')

        self.border_color = self.color_manager.get_theme_color_mix('theme_base_color', 'borders', 0.5)
        self.border_color_bold = self.color_manager.get_theme_color_mix('theme_base_color', 'borders', 0.25)

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
        current_line_no = self.document.content.get_current_line_number() + 1
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
            total_size = 3

            for i, widget in enumerate(self.widgets):
                if widget.is_visible():
                    widget_size = widget.get_size()
                    total_size += widget_size
                    if (x <= total_size and x > total_size - widget_size) or i == len(self.widgets) - 1:
                        return widget.on_click(event)
        return False

    def on_pointer_movement(self, widget, event):
        x, y = self.source_view.window_to_buffer_coords(Gtk.TextWindowType.LEFT, event.x, event.y)
        if event.window == self.source_view.get_window(Gtk.TextWindowType.LEFT):
            x += self.total_size
            total_size = 3
            for widget in self.widgets:
                if widget.is_visible():
                    widget_size = widget.get_size()
                    total_size += widget_size
                    widget.on_pointer_movement(event)
        return False

    def add_widget(self, widget):
        self.widgets.append(widget)
        widget.set_font_desc(self.font_manager.get_font_desc())
        widget.set_char_dimensions(self.line_height, self.char_width)
        widget.update_colors()
        self.update_sizes()

    def update_sizes(self):
        total_size = 0
        for widget in self.widgets:
            if widget.is_visible():
                widget.update_size()
                total_size += widget.get_size()

        if total_size != 0:
            total_size += self.char_width + 5

        if total_size != self.total_size:
            self.total_size = total_size
            self.source_view.set_border_window_size(Gtk.TextWindowType.LEFT, self.total_size)
            self.view.set_size_request(self.total_size, 1000)

    def set_line_highlighting(self, value):
        self.highlight_current_line = value
        self.view.queue_draw()



