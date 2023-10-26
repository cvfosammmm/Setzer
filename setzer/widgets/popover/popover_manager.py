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


class PopoverManager(object):

    popoverlay = None
    popovers = dict()
    popover_buttons = dict()
    current_popover_name = None
    main_window = None
    inbetween = Gtk.DrawingArea()

    def init(main_window):
        PopoverManager.main_window = main_window
        PopoverManager.popoverlay = main_window.popoverlay
        PopoverManager.popoverlay.add_overlay(PopoverManager.inbetween)

        controller_click = Gtk.GestureClick()
        controller_click.connect('pressed', PopoverManager.on_click_inbetween)
        controller_click.set_button(1)
        PopoverManager.inbetween.add_controller(controller_click)

        PopoverManager.inbetween.set_can_target(False)

    def create_popover(name):
        popover = Popover(PopoverManager)
        PopoverManager.popovers[name] = popover
        return popover

    def create_popover_button(name):
        popover_button = PopoverButton(name, PopoverManager)
        PopoverManager.popover_buttons[name] = popover_button
        return popover_button

    def popup_at_button(name):
        if PopoverManager.current_popover_name == name: return

        button = PopoverManager.popover_buttons[name]
        allocation = button.compute_bounds(PopoverManager.main_window).out_bounds

        x = allocation.origin.x + allocation.size.width / 2
        y = allocation.origin.y + allocation.size.height

        popover = PopoverManager.popovers[name]
        window_width = PopoverManager.main_window.get_width()
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

        PopoverManager.current_popover_name = name
        PopoverManager.popoverlay.add_overlay(popover)
        PopoverManager.inbetween.set_can_target(True)

        button.set_active(True)

    def popdown():
        if PopoverManager.current_popover_name == None: return

        name = PopoverManager.current_popover_name
        popover = PopoverManager.popovers[name]

        PopoverManager.popoverlay.remove_overlay(popover)
        PopoverManager.current_popover_name = None
        PopoverManager.inbetween.set_can_target(False)

        popover.show_page(None, 'main', Gtk.StackTransitionType.NONE)
        if name in PopoverManager.popover_buttons:
            PopoverManager.popover_buttons[name].set_active(False)

    def on_click_inbetween(controller, n_press, x, y):
        PopoverManager.popdown()


