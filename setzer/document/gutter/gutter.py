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
        self.settings = ServiceLocator.get_settings()

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_halign(Gtk.Align.START)
        self.document_view.overlay.add_overlay(self.drawing_area)
        self.drawing_area.set_draw_func(self.draw)

        self.line_numbers_visible = self.settings.get_value('preferences', 'show_line_numbers')
        self.line_numbers_width = None

        self.code_folding_visible = self.document.is_latex_document() and self.settings.get_value('preferences', 'enable_code_folding')
        self.code_folding_width = None

        self.highlight_current_line = self.settings.get_value('preferences', 'highlight_current_line')

        self.char_width = FontManager.get_char_width(self.source_view)
        self.line_height = FontManager.get_line_height(self.source_view)
        self.total_width = None
        self.cursor_x, self.cursor_y = None, None
        self.hovered_folding_region = None

        self.layout = Pango.Layout(self.source_view.get_pango_context())
        self.layout.set_alignment(Pango.Alignment.RIGHT)

        self.update_size()

        self.settings.connect('settings_changed', self.on_settings_changed)
        self.document.connect('changed', self.on_document_change)
        self.document.connect('cursor_position_changed', self.on_cursor_change)
        self.document.code_folding.connect('folding_state_changed', self.on_folding_state_changed)
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

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter

        if item == 'show_line_numbers':
            self.line_numbers_visible = self.settings.get_value('preferences', 'show_line_numbers')
            self.update_hovered_folding_region()
            self.update_size()
            self.drawing_area.queue_draw()

        if item == 'highlight_current_line':
            self.highlight_current_line = self.settings.get_value('preferences', 'highlight_current_line')
            self.drawing_area.queue_draw()

        if item == 'enable_code_folding':
            self.code_folding_visible = self.document.is_latex_document() and self.settings.get_value('preferences', 'enable_code_folding')
            self.update_hovered_folding_region()
            self.update_size()
            self.drawing_area.queue_draw()

    def on_document_change(self, document):
        self.update_hovered_folding_region()
        self.update_size()
        self.drawing_area.queue_draw()

    def on_cursor_change(self, document):
        self.update_hovered_folding_region()
        self.update_size()
        self.drawing_area.queue_draw()

    def on_adjustment_value_changed(self, adjustment):
        self.update_hovered_folding_region()
        self.update_size()
        self.drawing_area.queue_draw()

    def on_adjustment_changed(self, adjustment):
        self.update_hovered_folding_region()
        self.update_size()
        self.drawing_area.queue_draw()

    def on_folding_state_changed(self, code_folding):
        self.update_hovered_folding_region()
        self.update_size()
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
            line = self.source_view.get_line_at_y(self.cursor_y + self.adjustment.get_value()).target_iter.get_line()
            self.hovered_folding_region = self.document.code_folding.get_region_by_line(line)

    def update_size(self):
        self.char_width = FontManager.get_char_width(self.source_view)
        self.line_height = FontManager.get_line_height(self.source_view)
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
            self.layout.set_width((line_numbers_width - self.char_width) * Pango.SCALE)
            self.drawing_area.set_size_request(total_width + self.char_width, -1)
            self.document_view.margin.set_size_request(total_width + self.char_width, -1)

    #@timer
    def draw(self, drawing_area, ctx, width, height, data=None):
        if self.total_width == 0: return

        self.draw_background_and_border(ctx, width, height)
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('view_fg_color'))

        current_line = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert()).get_line()
        line_iter, offset = self.source_view.get_line_at_y(self.adjustment.get_value())
        prev_line = None
        line = -1
        total_lines = self.source_buffer.get_end_iter().get_line()
        while (offset <= self.adjustment.get_value() + height) and line < total_lines:
            line_iter, top = self.source_view.get_line_at_y(offset)
            line = line_iter.get_line()
            line_height = self.source_view.get_line_yrange(line_iter).height
            if line != prev_line:
                drawing_offset = offset - self.adjustment.get_value()
                if drawing_offset < 0:
                    drawing_offset = min(0, drawing_offset + line_height - self.line_height)
                self.draw_line(ctx, line, current_line == line, drawing_offset)

            prev_line = line
            offset += line_height

        self.draw_hovered_folding_region(ctx)

    def draw_background_and_border(self, ctx, width, height):
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('view_bg_color'))
        ctx.rectangle(0, 0, self.total_width, height)
        ctx.fill()

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('borders'))
        ctx.rectangle(self.total_width, 0, 1, height)
        ctx.fill()

    def draw_line(self, ctx, line, is_current, offset):
        if self.line_numbers_visible:
            self.draw_line_number(ctx, line, is_current, offset)

        if self.code_folding_visible:
            self.draw_folding_region(ctx, line, is_current, offset)

    def draw_line_number(self, ctx, line, is_current, offset):
        if is_current:
            text = '<b>' + str(line + 1) + '</b>'
        else:
            text = str(line + 1)

        if is_current and self.highlight_current_line and not self.source_buffer.get_has_selection():
            Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('line_highlighting_color'))
            yrange = self.source_view.get_line_yrange(self.source_buffer.get_iter_at_line(line).iter)
            ctx.rectangle(0, yrange.y - self.adjustment.get_value(), self.total_width, yrange.height)
            ctx.fill()
            ctx.rectangle(self.total_width + 1, yrange.y - self.adjustment.get_value(), self.char_width, yrange.height)
            ctx.fill()
            Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('view_fg_color'))

        self.layout.set_markup(text)

        offset += (self.line_height - self.layout.get_extents().logical_rect.height / Pango.SCALE) / 2 + 1
        ctx.move_to(0, offset)

        PangoCairo.show_layout(ctx, self.layout)

    def draw_folding_region(self, ctx, line, is_current, offset):
        folding_region = self.document.code_folding.get_region_by_line(line)
        if folding_region == None: return

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
        yoff1 = 0
        yoff2 = 2.5 * self.char_width / 4
        yoff3 = 5 * self.char_width / 4
        yoff4 = 0
        yoff5 = 1 * self.char_width / 2
        line_gap_folded = ((self.line_height - self.char_width * 5 / 4) / 2)
        line_gap_unfolded = ((self.line_height - self.char_width * 1 / 2) / 2)

        if folding_region['is_folded']:
            ctx.move_to(self.line_numbers_width + xoff1, offset + line_gap_folded + 0.5)
            ctx.line_to(self.line_numbers_width + xoff2, offset + line_gap_folded + yoff2 + 0.5)
            ctx.line_to(self.line_numbers_width + xoff1, offset + line_gap_folded + yoff3 + 0.5)
            ctx.line_to(self.line_numbers_width + xoff1, offset + line_gap_folded + 0.5)
            ctx.fill()
            for i in range(4):
                ctx.rectangle(self.line_numbers_width + (i + 0.5) * self.char_width, offset + self.line_height, self.char_width / 2, 1)
                ctx.fill()
        else:
            ctx.move_to(self.line_numbers_width + xoff6, offset + line_gap_unfolded)
            ctx.line_to(self.line_numbers_width + xoff7, offset + line_gap_unfolded + yoff5)
            ctx.line_to(self.line_numbers_width + xoff8, offset + line_gap_unfolded)
            ctx.line_to(self.line_numbers_width + xoff6, offset + line_gap_unfolded)
            ctx.fill()

    def draw_hovered_folding_region(self, ctx):
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('code_folding_hover'))
        if self.hovered_folding_region != None:
            region = self.hovered_folding_region
            yrange_1 = self.source_view.get_line_yrange(self.source_buffer.get_iter_at_line(region['starting_line']).iter)
            yrange_2 = self.source_view.get_line_yrange(self.source_buffer.get_iter_at_line(region['ending_line']).iter)

            ctx.rectangle(self.total_width - 1, yrange_1.y - self.adjustment.get_value(), 3, yrange_2.y - yrange_1.y + yrange_2.height)
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


