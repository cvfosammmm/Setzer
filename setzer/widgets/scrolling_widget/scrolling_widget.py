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
from gi.repository import GObject, Gdk, Gtk

import time

from setzer.helpers.observable import Observable


class ScrollingWidget(Observable):

    def __init__(self):
        Observable.__init__(self)

        self.scrolling_offset_x, self.scrolling_offset_y = 0, 0
        self.width, self.height = 0, 0
        self.cursor_x, self.cursor_y = None, None
        self.scrolling_multiplier = 2.5
        self.last_cursor_scrolling_change = time.time()

        self.view = Gtk.Overlay()
        self.content = Gtk.DrawingArea()
        self.view.set_child(self.content)

        self.scrollbar_x = Gtk.Scrollbar.new(Gtk.Orientation.HORIZONTAL)
        self.scrollbar_x.set_valign(Gtk.Align.END)
        self.scrollbar_x.get_style_context().add_class('bottom')
        self.scrollbar_x.get_style_context().add_class('overlay-indicator')
        self.adjustment_x = self.scrollbar_x.get_adjustment()
        self.view.add_overlay(self.scrollbar_x)

        self.scrollbar_y = Gtk.Scrollbar.new(Gtk.Orientation.VERTICAL)
        self.scrollbar_y.set_halign(Gtk.Align.END)
        self.scrollbar_y.get_style_context().add_class('right')
        self.scrollbar_y.get_style_context().add_class('overlay-indicator')
        self.adjustment_y = self.scrollbar_y.get_adjustment()
        self.view.add_overlay(self.scrollbar_y)

        self.scrolling_controller = Gtk.EventControllerScroll()
        self.scrolling_controller.set_flags(Gtk.EventControllerScrollFlags.BOTH_AXES | Gtk.EventControllerScrollFlags.KINETIC)
        self.scrolling_controller.connect('scroll', self.on_scroll)
        self.scrolling_controller.connect('decelerate', self.on_decelerate)
        self.content.add_controller(self.scrolling_controller)

        self.adjustment_x.connect('changed', self.on_adjustment_changed)
        self.adjustment_x.connect('value-changed', self.on_adjustment_changed)
        self.adjustment_y.connect('changed', self.on_adjustment_changed)
        self.adjustment_y.connect('value-changed', self.on_adjustment_changed)
        self.content.connect('resize', self.on_resize)

        self.motion_controller = Gtk.EventControllerMotion()
        self.motion_controller.connect('enter', self.on_enter)
        self.motion_controller.connect('motion', self.on_hover)
        self.motion_controller.connect('leave', self.on_leave)
        self.view.add_controller(self.motion_controller)

        self.primary_click_controller = Gtk.GestureClick()
        self.primary_click_controller.set_button(1)
        self.primary_click_controller.connect('pressed', self.on_primary_button_press)
        self.primary_click_controller.connect('released', self.on_primary_button_release)
        self.content.add_controller(self.primary_click_controller)

        self.secondary_click_controller = Gtk.GestureClick()
        self.secondary_click_controller.set_button(3)
        self.secondary_click_controller.connect('pressed', self.on_secondary_button_press)
        self.content.add_controller(self.secondary_click_controller)

    def queue_draw(self):
        self.content.queue_draw()

    def scroll_to_position(self, position):
        window_width = self.width
        yoffset = max(position[1], 0)
        xoffset = max(position[0], 0)
        self.scroll_now([xoffset, yoffset])

    def scroll_now(self, position):
        self.adjustment_x.set_value(position[0])
        self.adjustment_y.set_value(position[1])

    def on_scroll(self, controller, dx, dy):
        if abs(dx) > 0 and abs(dy / dx) >= 1: dx = 0

        modifiers = Gtk.accelerator_get_default_mod_mask()

        if controller.get_current_event_state() & modifiers == 0:
            if controller.get_unit() == Gdk.ScrollUnit.WHEEL:
                dx *= self.adjustment_x.get_page_size() ** (2/3)
                dy *= self.adjustment_y.get_page_size() ** (2/3)
            else:
                dy *= self.scrolling_multiplier
                dx *= self.scrolling_multiplier

            self.adjustment_x.set_value(self.adjustment_x.get_value() + dx)
            self.adjustment_y.set_value(self.adjustment_y.get_value() + dy)

        if controller.get_current_event_state() & modifiers == Gdk.ModifierType.CONTROL_MASK:
            if controller.get_unit() == Gdk.ScrollUnit.WHEEL:
                zoom_amount = dy * 0.1
            else:
                zoom_amount = (dy + dx) * 0.005
            self.add_change_code('zoom_request', zoom_amount)

    def on_decelerate(self, controller, vel_x, vel_y):
        if abs(vel_x) > 0 and abs(vel_y / vel_x) > 1: vel_x = 0

        data = {'starting_time': time.time(), 'initial_position': self.scrolling_offset_y, 'position': self.scrolling_offset_y, 'vel_y': vel_y * self.scrolling_multiplier}
        self.deceleration(data)

    def deceleration(self, data):
        if data['position'] != self.scrolling_offset_y: return False

        time_elapsed = time.time() - data['starting_time']

        exponential_factor = 2.71828 ** (-4 * time_elapsed)
        position = data['initial_position'] + (1 - exponential_factor) * (data['vel_y'] / 4)
        velocity = data['vel_y'] * exponential_factor

        if abs(velocity) < 0.1: return False

        x = self.scrolling_offset_x
        y = position
        self.scroll_now([x, y])
        data['position'] = y
        GObject.timeout_add(15, self.deceleration, data)

        return False

    def on_resize(self, drawing_area, width, height):
        self.width, self.height = width, height
        self.adjustment_x.set_page_size(width)
        self.adjustment_y.set_page_size(height)
        self.add_change_code('size_changed')
        self.last_cursor_scrolling_change = time.time()
        self.update_scrollbars()
        self.content.queue_draw()

    def on_adjustment_changed(self, adjustment):
        self.scrolling_offset_y = self.adjustment_y.get_value()
        self.scrolling_offset_x = self.adjustment_x.get_value()
        self.add_change_code('scrolling_offset_changed')
        self.last_cursor_scrolling_change = time.time()
        self.update_scrollbars()
        self.content.queue_draw()

    def on_primary_button_press(self, controller, n_press, x, y):
        if n_press != 1: return
        modifiers = Gtk.accelerator_get_default_mod_mask()

        x = self.scrolling_offset_x + x
        y = self.scrolling_offset_y + y
        self.add_change_code('primary_button_press', (x, y, controller.get_current_event_state() & modifiers))

    def on_primary_button_release(self, controller, n_press, x, y):
        if n_press != 1: return
        modifiers = Gtk.accelerator_get_default_mod_mask()

        x = self.scrolling_offset_x + x
        y = self.scrolling_offset_y + y
        self.add_change_code('primary_button_release', (x, y, controller.get_current_event_state() & modifiers))

    def on_secondary_button_press(self, controller, n_press, x, y):
        if n_press != 1: return
        modifiers = Gtk.accelerator_get_default_mod_mask()

        x = self.scrolling_offset_x + x
        y = self.scrolling_offset_y + y
        self.add_change_code('secondary_button_press', (x, y, controller.get_current_event_state() & modifiers))

    def on_enter(self, controller, x, y):
        self.set_cursor_position(x, y)

    def on_hover(self, controller, x, y):
        self.set_cursor_position(x, y)

    def on_leave(self, controller):
        self.set_cursor_position(None, None)

    def set_cursor_position(self, x, y):
        if x != self.cursor_x or y != self.cursor_y:
            self.cursor_x, self.cursor_y = x, y
            self.last_cursor_scrolling_change = time.time()
            self.add_change_code('hover_state_changed')
            self.update_scrollbars()
            self.content.queue_draw()

    def update_scrollbars(self):
        self.scrollbar_x.set_visible(self.adjustment_x.get_upper() - self.adjustment_x.get_page_size() >= 1)
        self.scrollbar_y.set_visible(self.adjustment_y.get_upper() - self.adjustment_y.get_page_size() >= 1)

        if self.cursor_x != None and self.cursor_x > self.width - 24:
            self.scrollbar_y.get_style_context().add_class('hovering')
        else:
            self.scrollbar_y.get_style_context().remove_class('hovering')
            if self.last_cursor_scrolling_change < time.time() - 1.5:
                self.scrollbar_x.get_style_context().add_class('hidden')
                self.scrollbar_y.get_style_context().add_class('hidden')
            else:
                self.scrollbar_x.get_style_context().remove_class('hidden')
                self.scrollbar_y.get_style_context().remove_class('hidden')

        if self.cursor_y != None and self.cursor_y > self.height - 24:
            self.scrollbar_x.get_style_context().add_class('hovering')
        else:
            self.scrollbar_x.get_style_context().remove_class('hovering')
            if self.last_cursor_scrolling_change < time.time() - 1.5:
                self.scrollbar_x.get_style_context().add_class('hidden')
            else:
                self.scrollbar_x.get_style_context().remove_class('hidden')

        GObject.timeout_add(1750, self.update_scrollbars)
        return False


