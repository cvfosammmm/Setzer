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
from gi.repository import GLib
from gi.repository import Gio


class PopoverMenuBuilder(object):

    def __init__(self):
        pass

    def set_box_margin(self, box):
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_left(10)
        box.set_margin_right(10)

    def add_action_button(self, box, label, action_name, action_parameter=None, icon_name=None, keyboard_shortcut=None):
        model_button = Gtk.ModelButton()
        if action_parameter:
            model_button.set_detailed_action_name(Gio.Action.print_detailed_name(action_name, GLib.Variant('as', action_parameter)))
        else:
            model_button.set_action_name(action_name)
        if keyboard_shortcut != None or icon_name != None:
            button_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
            if keyboard_shortcut != None:
                shortcut = Gtk.Label(keyboard_shortcut)
                shortcut.get_style_context().add_class('keyboard-shortcut')
                button_box.pack_end(shortcut, False, False, 0)
            if icon_name != None:
                if icon_name == 'placeholder':
                    placeholder = Gtk.DrawingArea()
                    placeholder.set_size_request(24, 16)
                    button_box.pack_start(placeholder, False, False, 0)
                else:
                    icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
                    icon.set_margin_right(8)
                    button_box.pack_start(icon, False, False, 0)
            description = Gtk.Label(label)
            description.set_halign(Gtk.Align.START)
            button_box.pack_start(description, True, True, 0)
            model_button.remove(model_button.get_child())
            model_button.add(button_box)
        else:
            model_button.set_label(label)
            model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)

    def add_menu_button(self, box, label, menu_name):
        model_button = Gtk.ModelButton()
        model_button.set_property('menu-name', menu_name)
        model_button.set_label(label)
        model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)

    def add_header_button(self, box, label):
        model_button = Gtk.ModelButton()
        model_button.set_property('centered', True)
        model_button.set_property('menu-name', 'main')
        model_button.set_label(label)
        model_button.set_property('inverted', True)
        box.pack_start(model_button, False, False, 0)

    def add_separator(self, box):
        separator = Gtk.SeparatorMenuItem()
        box.pack_start(separator, False, False, 0)


