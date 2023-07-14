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
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, Pango, PangoCairo

import math

from setzer.helpers.timer import timer
from setzer.app.service_locator import ServiceLocator
from setzer.app.color_manager import ColorManager
from setzer.app.font_manager import FontManager


class Gutter(object):

    def __init__(self, document, document_view):
        self.document = document
        self.document_view = document_view
        self.source_buffer = document.source_buffer
        self.source_view = document_view.source_view
        self.adjustment = self.document_view.scrolled_window.get_vadjustment()

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_halign(Gtk.Align.START)
        self.document_view.overlay.add_overlay(self.drawing_area)
        self.drawing_area.set_draw_func(self.draw)

        self.total_width = 0
        self.lines = [0]
        self.first_line_offset = 0
        self.current_line = 0
        self.line_height = FontManager.get_line_height()
        self.char_width = FontManager.get_char_width()

        self.line_numbers_visible = True
        self.layout_normal = Pango.Layout(self.source_view.get_pango_context())
        self.layout_normal.set_alignment(Pango.Alignment.RIGHT)
        self.layout_current_line = Pango.Layout(self.source_view.get_pango_context())
        self.layout_current_line.set_alignment(Pango.Alignment.RIGHT)
        font_description = FontManager.get_font_desc()
        font_description.set_weight(Pango.Weight.BOLD)
        self.layout_current_line.set_font_description(font_description)

        self.code_folding_visible = False

        self.update_size()

        self.document.connect('changed', self.on_document_change)
        self.document.connect('cursor_position_changed', self.on_cursor_change)
        self.document_view.scrolled_window.get_vadjustment().connect('changed', self.on_adjustment_changed)
        self.document_view.scrolled_window.get_vadjustment().connect('value-changed', self.on_adjustment_value_changed)

        event_controller = Gtk.GestureClick()
        event_controller.connect('pressed', self.on_button_press)
        event_controller.set_button(1)
        self.drawing_area.add_controller(event_controller)

    def on_document_change(self, document):
        self.update_size()
        self.drawing_area.queue_draw()

    def on_cursor_change(self, document):
        self.drawing_area.queue_draw()

    def on_adjustment_value_changed(self, adjustment):
        self.drawing_area.queue_draw()

    def on_adjustment_changed(self, adjustment):
        self.drawing_area.queue_draw()

    def on_button_press(self, event_controller, n_press, x, y):
        if n_press != 1: return False
        if x > self.total_width: return False

        if self.line_numbers_visible and x <= self.line_numbers_width:
            offset = self.adjustment.get_value()
            target = self.source_view.get_line_at_y(offset + y).target_iter
            self.source_buffer.place_cursor(target)
        else:
            pass
        return True

    def on_scroll(self, event_controller, x, y):
        return False

    def update_size(self):
        total_width = 0
        line_numbers_width = 0
        if self.line_numbers_visible:
            total_width += int(math.log10(self.source_buffer.get_line_count()) + 3) * self.char_width
            line_numbers_width = total_width - self.char_width
        if self.code_folding_visible:
            total_width += 3 * self.char_width

        if total_width != self.total_width or line_numbers_width != self.line_numbers_width:
            self.total_width = total_width
            self.line_numbers_width = line_numbers_width
            self.layout_normal.set_width(line_numbers_width * Pango.SCALE)
            self.layout_current_line.set_width(line_numbers_width * Pango.SCALE)
            self.source_view.set_left_margin(total_width + self.char_width)
            self.drawing_area.set_size_request(total_width + 1, -1)

    #@timer
    def update_lines(self):
        allocated_height = self.source_view.get_allocated_height()
        offset = self.adjustment.get_value()

        lines = list()
        for i in range(int(allocated_height / self.line_height + 2)):
            lines.append(self.source_view.get_line_at_y(offset + self.line_height * i).target_iter.get_line())
        self.lines = lines

        self.current_line = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert()).get_line()
        self.first_line_offset = offset % self.line_height

    #@timer
    def draw(self, drawing_area, ctx, width, height, data=None):
        if self.total_width == 0: return
        self.update_lines()

        self.draw_background_and_border(ctx, width, height)

        fg_color = ColorManager.get_ui_color('theme_fg_color')
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
        bg_color = ColorManager.get_ui_color('theme_base_color')
        border_color = ColorManager.get_ui_color('borders')

        Gdk.cairo_set_source_rgba(ctx, bg_color)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

        Gdk.cairo_set_source_rgba(ctx, border_color)
        ctx.rectangle(width - 1, 0, 1, height)
        ctx.fill()


