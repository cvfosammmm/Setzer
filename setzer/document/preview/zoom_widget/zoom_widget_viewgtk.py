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
from gi.repository import Gtk

from setzer.widgets.fixed_width_label.fixed_width_label import FixedWidthLabel
from setzer.helpers.popover_menu_builder import MenuBuilder


class PreviewZoomWidget(Gtk.Revealer):

    def __init__(self, model):
        Gtk.Revealer.__init__(self)
        self.set_transition_type(Gtk.RevealerTransitionType.NONE)

        self.box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.box.get_style_context().add_class('zoom_widget')

        self.zoom_out_button = Gtk.Button.new_from_icon_name('zoom-out-symbolic')
        self.zoom_out_button.set_tooltip_text(_('Zoom out'))
        self.zoom_out_button.get_style_context().add_class('flat')
        self.zoom_out_button.set_can_focus(False)
        self.zoom_out_button.get_style_context().add_class('scbar')
        self.zoom_in_button = Gtk.Button.new_from_icon_name('zoom-in-symbolic')
        self.zoom_in_button.set_tooltip_text(_('Zoom in'))
        self.zoom_in_button.get_style_context().add_class('flat')
        self.zoom_in_button.set_can_focus(False)
        self.zoom_in_button.get_style_context().add_class('scbar')

        self.popover = MenuBuilder.create_menu()

        self.button_fit_to_width = MenuBuilder.create_button(_('Fit to Width'))
        MenuBuilder.add_widget(self.popover, self.button_fit_to_width)
        self.button_fit_to_text_width = MenuBuilder.create_button(_('Fit to Text Width'))
        MenuBuilder.add_widget(self.popover, self.button_fit_to_text_width)
        self.button_fit_to_height = MenuBuilder.create_button(_('Fit to Height'))
        MenuBuilder.add_widget(self.popover, self.button_fit_to_height)
        MenuBuilder.add_separator(self.popover)

        self.zoom_level_buttons = dict()
        for level in model.preview.zoom_manager.get_list_of_zoom_levels():
            self.zoom_level_buttons[level] = MenuBuilder.create_button('{0:.0f}%'.format(level * 100))
            MenuBuilder.add_widget(self.popover, self.zoom_level_buttons[level])

        self.label = FixedWidthLabel(66)
        self.label.get_style_context().add_class('zoom-level-button')
        self.zoom_level_button = Gtk.MenuButton()
        self.zoom_level_button.set_direction(Gtk.ArrowType.DOWN)
        self.zoom_level_button.set_focus_on_click(False)
        self.zoom_level_button.set_popover(self.popover)
        self.zoom_level_button.set_tooltip_text(_('Set zoom level'))
        self.zoom_level_button.get_style_context().add_class('flat')
        self.zoom_level_button.get_style_context().add_class('scbar')
        self.zoom_level_button.set_can_focus(False)
        self.zoom_level_button.set_child(self.label)

        self.box.append(self.zoom_out_button)
        self.box.append(self.zoom_level_button)
        self.box.append(self.zoom_in_button)
        self.set_child(self.box)


