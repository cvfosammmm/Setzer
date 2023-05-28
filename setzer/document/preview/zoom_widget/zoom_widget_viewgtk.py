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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class PreviewZoomWidget(Gtk.Revealer):

    def __init__(self):
        Gtk.Revealer.__init__(self)
        self.set_transition_type(Gtk.RevealerTransitionType.NONE)

        self.box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.box.get_style_context().add_class('zoom_widget')
        
        self.zoom_out_button = Gtk.Button.new_from_icon_name('zoom-out-symbolic', Gtk.IconSize.MENU)
        self.zoom_out_button.set_tooltip_text(_('Zoom out'))
        self.zoom_out_button.get_style_context().add_class('flat')
        self.zoom_out_button.set_can_focus(False)
        self.zoom_in_button = Gtk.Button.new_from_icon_name('zoom-in-symbolic', Gtk.IconSize.MENU)
        self.zoom_in_button.set_tooltip_text(_('Zoom in'))
        self.zoom_in_button.get_style_context().add_class('flat')
        self.zoom_in_button.set_can_focus(False)

        popover = Gtk.PopoverMenu()
        stack = popover.get_child()

        self.zoom_button_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.zoom_button_box.set_margin_top(10)
        self.zoom_button_box.set_margin_bottom(10)
        self.zoom_button_box.set_margin_left(10)
        self.zoom_button_box.set_margin_right(10)
        stack.add_named(self.zoom_button_box, 'main')

        self.label = Gtk.Label('100.0%')
        self.label.set_xalign(0.5)
        self.zoom_level_button = Gtk.MenuButton()
        self.zoom_level_button.set_direction(Gtk.ArrowType.DOWN)
        self.zoom_level_button.set_focus_on_click(False)
        self.zoom_level_button.set_popover(popover)
        self.zoom_level_button.set_tooltip_text(_('Set zoom level'))
        self.zoom_level_button.get_style_context().add_class('flat')
        self.zoom_level_button.get_style_context().add_class('zoom_level_button')
        self.zoom_level_button.set_can_focus(False)
        self.zoom_level_button.add(self.label)
        
        self.box.pack_start(self.zoom_out_button, False, False, 0)
        self.box.pack_start(self.zoom_level_button, False, False, 0)
        self.box.pack_start(self.zoom_in_button, False, False, 0)
        self.add(self.box)
        self.show_all()


