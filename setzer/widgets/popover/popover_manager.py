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
from gi.repository import Gtk

from setzer.widgets.popover.popover import Popover
from setzer.widgets.popover.popover_button import PopoverButton
from setzer.helpers.observable import Observable


class PopoverManager(Observable):

    def __init__(self, main_window):
        Observable.__init__(self)

        self.popovers = dict()
        self.popover_buttons = dict()
        self.current_popover_name = None

        self.main_window = main_window
        self.inbetween = Gtk.DrawingArea()
        self.popoverlay = main_window.popoverlay
        self.popoverlay.add_overlay(self.inbetween)

        controller_click = Gtk.GestureClick()
        controller_click.connect('pressed', self.on_click_inbetween)
        controller_click.set_button(1)
        self.inbetween.add_controller(controller_click)

        self.inbetween.set_can_target(False)

    def create_popover(self, name):
        popover = Popover(self)
        self.popovers[name] = popover
        return popover

    def create_popover_button(self, name):
        popover_button = PopoverButton(name, self)
        self.popover_buttons[name] = popover_button
        return popover_button

    def popup_at_button(self, name):
        if self.current_popover_name == name: return

        button = self.popover_buttons[name]
        allocation = button.compute_bounds(self.main_window).out_bounds

        x = allocation.origin.x + allocation.size.width / 2
        y = allocation.origin.y + allocation.size.height

        popover = self.popovers[name]
        window_width = self.main_window.get_width()
        arrow_width = 10
        arrow_border_width = 36
        if x - popover.width / 2 < 0:
            popover.set_margin_start(0)
            popover.arrow.set_margin_start(x - arrow_width / 2)
            popover.arrow_border.set_margin_start(x - arrow_border_width / 2)
        elif x - popover.width / 2 > window_width - popover.width:
            popover.set_margin_start(window_width - popover.width)
            popover.arrow.set_margin_start(x - window_width + popover.width - arrow_width / 2)
            popover.arrow_border.set_margin_start(x - window_width + popover.width - arrow_border_width / 2)
        else:
            popover.set_margin_start(x - popover.width / 2)
            popover.arrow.set_margin_start(popover.width / 2 - arrow_width / 2)
            popover.arrow_border.set_margin_start(popover.width / 2 - arrow_border_width / 2)
        popover.set_margin_top(max(0, y))

        self.current_popover_name = name
        self.popoverlay.add_overlay(popover)
        self.inbetween.set_can_target(True)

        button.set_active(True)

        self.add_change_code('popup', name)

    def popdown(self):
        if self.current_popover_name == None: return

        name = self.current_popover_name
        popover = self.popovers[name]

        self.popoverlay.remove_overlay(popover)
        self.current_popover_name = None
        self.inbetween.set_can_target(False)

        popover.show_page(None, 'main', Gtk.StackTransitionType.NONE)
        if name in self.popover_buttons:
            self.popover_buttons[name].set_active(False)

        self.add_change_code('popdown', name)

    def on_click_inbetween(self, controller, n_press, x, y):
        self.popdown()


