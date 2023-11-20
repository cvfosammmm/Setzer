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


class PopoverButton(Gtk.Button):

    def __init__(self, name, popover_manager):
        Gtk.Button.__init__(self)
        self.get_style_context().add_class('popover')

        self.popover_manager = popover_manager
        self.popover_name = name
        self.is_active = False

        controller_click = Gtk.GestureClick()
        controller_click.connect('pressed', self.on_button_press)
        controller_click.set_button(1)
        controller_click.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.add_controller(controller_click)

    def on_button_press(self, controller, n_press, x, y):
        if not self.is_active:
            self.popover_manager.popup_at_button(self.popover_name)

    def set_active(self, is_active):
        self.is_active = is_active
        if is_active:
            self.get_style_context().add_class('active')
        else:
            self.get_style_context().remove_class('active')


