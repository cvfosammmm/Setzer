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
from gi.repository import Gtk, Gdk, GObject, Pango, PangoCairo

import math, time

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

        self.line_numbers_visible = True
        self.line_numbers_width = 0

        self.code_folding_visible = True
        self.code_folding_width = 0

        self.total_width = 0
        self.lines = [0]
        self.first_line_offset = 0
        self.current_line = 0
        self.line_height = FontManager.get_line_height()
        self.char_width = FontManager.get_char_width()
        self.cursor_x, self.cursor_y = None, None
        self.hovered_folding_region = None

        self.layout_normal = Pango.Layout(self.source_view.get_pango_context())
        self.layout_normal.set_alignment(Pango.Alignment.RIGHT)
        self.layout_current_line = Pango.Layout(self.source_view.get_pango_context())
        self.layout_current_line.set_alignment(Pango.Alignment.RIGHT)
        font_description = FontManager.get_font_desc()
        font_description.set_weight(Pango.Weight.BOLD)
        self.layout_current_line.set_font_description(font_description)

        self.update_size()

        self.document.connect('changed', self.on_document_change)
        self.document.connect('cursor_position_changed', self.on_cursor_change)
        self.document_view.scrolled_window.get_vadjustment().connect('changed', self.on_adjustment_changed)
        self.document_view.scrolled_window.get_vadjustment().connect('value-changed', self.on_adjustment_value_changed)

        scrolling_controller = Gtk.EventControllerScroll()
        scrolling_controller.set_flags(Gtk.EventControllerScrollFlags.BOTH_AXES | Gtk.EventControllerScrollFlags.KINETIC)
        scrolling_controller.connect('scroll', self.on_scroll)
        scrolling_controller.connect('decelerate', self.on_decelerate)
        self.drawing_area.add_controller(scrolling_controller)

        event_controller = Gtk.GestureClick()
        event_controller.connect('pressed', self.on_button_press)
        event_controller.set_button(1)
        self.drawing_area.add_controller(event_controller)

        event_controller = Gtk.EventControllerMotion()
        event_controller.connect('enter', self.on_enter)
        event_controller.connect('motion', self.on_hover)
        event_controller.connect('leave', self.on_leave)
        self.drawing_area.add_controller(event_controller)

    def on_document_change(self, document):
        self.update_size()
        self.update_hovered_folding_region()
        self.drawing_area.queue_draw()

    def on_cursor_change(self, document):
        self.update_hovered_folding_region()
        self.drawing_area.queue_draw()

    def on_adjustment_value_changed(self, adjustment):
        self.update_hovered_folding_region()
        self.drawing_area.queue_draw()

    def on_adjustment_changed(self, adjustment):
        self.update_hovered_folding_region()
        self.drawing_area.queue_draw()

    def on_button_press(self, event_controller, n_press, x, y):
        if self.hovered_folding_region != None:
            if self.hovered_folding_region['is_folded']:
                self.document.code_folding.unfold(self.hovered_folding_region)
            else:
                self.document.code_folding.fold(self.hovered_folding_region)
        else:
            offset = self.adjustment.get_value()
            target = self.source_view.get_line_at_y(offset + y).target_iter
            self.source_buffer.place_cursor(target)
        return True

    def on_scroll(self, controller, dx, dy):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if controller.get_current_event_state() & modifiers == 0:
            if controller.get_unit() == Gdk.ScrollUnit.WHEEL:
                dy *= self.adjustment.get_page_size() ** (2/3)
            else:
                dy *= 2.5
            self.document_view.scrolled_window.set_kinetic_scrolling(False)
            self.adjustment.set_value(self.adjustment.get_value() + dy)
            self.document_view.scrolled_window.set_kinetic_scrolling(True)

    def on_decelerate(self, controller, vel_x, vel_y):
        data = {'starting_time': time.time(), 'initial_position': self.adjustment.get_value(), 'position': self.adjustment.get_value(), 'vel_y': vel_y * 2.5}
        self.deceleration(data)

    def deceleration(self, data):
        if data['position'] != self.adjustment.get_value(): return False

        time_elapsed = time.time() - data['starting_time']
        exponential_factor = 2.71828 ** (-4 * time_elapsed)
        position = data['initial_position'] + (1 - exponential_factor) * (data['vel_y'] / 4)
        velocity = data['vel_y'] * exponential_factor
        if abs(velocity) >= 0.1:
            self.adjustment.set_value(position)
            data['position'] = position
            GObject.timeout_add(15, self.deceleration, data)

        return False

    def on_enter(self, controller, x, y):
        self.set_cursor_position(x, y)

    def on_hover(self, controller, x, y):
        self.set_cursor_position(x, y)

    def on_leave(self, controller):
        self.set_cursor_position(None, None)

    def set_cursor_position(self, x, y):
        if x != self.cursor_x or y != self.cursor_y:
            self.cursor_x, self.cursor_y = x, y
            self.drawing_area.queue_draw()
        if self.cursor_x != None and self.cursor_x > self.total_width + 1:
            self.drawing_area.set_cursor_from_name('text')
        else:
            self.drawing_area.set_cursor_from_name('default')
        self.update_hovered_folding_region()

    def update_hovered_folding_region(self):
        self.hovered_folding_region = None
        if self.get_cursor_area() == 'code_folding':
            line_index = int((self.cursor_y + self.first_line_offset) // self.line_height)
            if self.lines[0] == self.lines[1] and self.cursor_y <= self.line_height: line_index = 0
            line = self.lines[line_index]

            if line_index != 0 and self.lines[line_index] == self.lines[line_index - 1]: return
            self.hovered_folding_region = self.document.code_folding.get_region_by_line(line)

    def update_size(self):
        total_width = 0
        line_numbers_width = 0
        if self.line_numbers_visible:
            total_width += int(math.log10(self.source_buffer.get_line_count()) + 3) * self.char_width
            line_numbers_width = total_width
        if self.code_folding_visible:
            total_width += 3 * self.char_width
            self.code_folding_width = 3 * self.char_width
        else:
            self.code_folding_width = 0

        if total_width != self.total_width or line_numbers_width != self.line_numbers_width:
            self.total_width = total_width
            self.line_numbers_width = line_numbers_width
            self.layout_normal.set_width((line_numbers_width - self.char_width) * Pango.SCALE)
            self.layout_current_line.set_width((line_numbers_width - self.char_width) * Pango.SCALE)
            self.source_view.set_left_margin(total_width + self.char_width)
            self.drawing_area.set_size_request(total_width + 2, -1)

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

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('theme_fg_color'))
        if self.lines[0] == self.lines[1]:
            self.draw_line(ctx, self.lines[0], 0)
        else:
            self.draw_line(ctx, self.lines[0], -self.first_line_offset)
        prev_line = self.lines[0]
        for i, line in enumerate(self.lines[1:]):
            if line != prev_line:
                self.draw_line(ctx, line, -self.first_line_offset + (i + 1) * self.line_height)
            prev_line = line

        self.draw_hovered_folding_region(ctx)

    def draw_background_and_border(self, ctx, width, height):
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('theme_base_color'))
        ctx.rectangle(0, 0, self.total_width, height)
        ctx.fill()

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('borders'))
        ctx.rectangle(self.total_width, 0, 1, height)
        ctx.fill()

    def draw_line(self, ctx, line, offset):
        if self.current_line == line: layout = self.layout_current_line
        else: layout = self.layout_normal

        ctx.move_to(0, offset)
        layout.set_text(str(line + 1))
        PangoCairo.show_layout(ctx, layout)

        folding_region = self.document.code_folding.get_region_by_line(line)
        if folding_region != None:
            ctx.set_line_width(0)
            xoff1 = 6.5 * self.char_width / 6
            xoff2 = 9.5 * self.char_width / 6
            xoff3 = 2 * self.char_width / 11
            xoff4 = 10 * self.char_width / 11
            xoff5 = 18 * self.char_width / 11
            xoff6 = 6 * self.char_width / 8
            xoff7 = 11 * self.char_width / 8
            xoff8 = 16 * self.char_width / 8
            xoff9 = 26 * self.char_width / 11
            yoff1 = 1.75 * self.line_height / 8
            yoff2 = 4.25 * self.line_height / 8
            yoff3 = 6.75 * self.line_height / 8
            yoff4 = 2.5 * self.line_height / 6
            yoff5 = 4 * self.line_height / 6
            len1 = 4 * self.char_width / 11

            if folding_region['is_folded']:
                ctx.move_to(self.line_numbers_width + xoff1, int(offset + yoff1))
                ctx.line_to(self.line_numbers_width + xoff2, int(offset + yoff2))
                ctx.line_to(self.line_numbers_width + xoff1, int(offset + yoff3))
                ctx.line_to(self.line_numbers_width + xoff1, int(offset + yoff1))
                ctx.fill()
                for i in range(4):
                    ctx.rectangle(self.line_numbers_width + (i + 0.5) * self.char_width, int(offset + self.line_height), self.char_width / 2, 1)
                    ctx.fill()
            else:
                ctx.move_to(self.line_numbers_width + xoff6, int(offset + yoff4 + 0.5))
                ctx.line_to(self.line_numbers_width + xoff7, int(offset + yoff5 + 0.5))
                ctx.line_to(self.line_numbers_width + xoff8, int(offset + yoff4 + 0.5))
                ctx.line_to(self.line_numbers_width + xoff6, int(offset + yoff4 + 0.5))
                ctx.fill()

    def draw_hovered_folding_region(self, ctx):
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('code_folding_hover'))
        if self.hovered_folding_region != None:
            hover_start = -self.first_line_offset + self.lines.index(self.hovered_folding_region['starting_line']) * self.line_height

            starting_line = self.hovered_folding_region['starting_line']
            ending_line = self.hovered_folding_region['ending_line']

            i = len([line for line in self.lines if line >= starting_line and line <= ending_line])

            if ending_line + 1 == self.source_buffer.get_line_count():
                last_line_height = self.source_view.get_line_yrange(self.source_buffer.get_end_iter()).height
                i = len([line for line in self.lines if line >= starting_line and line < ending_line])
                height = i * self.line_height + last_line_height
            else:
                i = len([line for line in self.lines if line >= starting_line and line <= ending_line])
                height = i * self.line_height

            ctx.rectangle(self.total_width - 1, hover_start, 3, height)
            ctx.fill()

    def get_cursor_area(self):
        if self.cursor_x == None: return None
        offset = 0

        if self.line_numbers_visible:
            offset += self.line_numbers_width
        if self.cursor_x <= offset: return 'line_numbers'

        if self.code_folding_visible:
            offset += self.code_folding_width
        if self.cursor_x <= offset: return 'code_folding'

        return None


