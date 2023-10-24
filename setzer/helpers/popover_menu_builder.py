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
from gi.repository import GLib
from gi.repository import Gio


class PopoverMenu(Gtk.Popover):

    def __init__(self):
        Gtk.Popover.__init__(self)

        stack = Gtk.Stack()
        stack.set_vhomogeneous(False)

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        stack.add_named(box, 'main')

        self.set_child(stack)

        self.connect('closed', self.on_close)

    def add_page(self, pagename, label):
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        button = Gtk.Button()
        button_box = Gtk.CenterBox()
        button_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        button.set_child(button_box)
        button.get_style_context().add_class('header')
        button.connect('clicked', self.show_page, 'main', Gtk.StackTransitionType.SLIDE_LEFT)

        button_box.set_center_widget(Gtk.Label.new(label))
        button_box.set_start_widget(Gtk.Image.new_from_icon_name('pan-start-symbolic'))
        box.append(button)

        self.get_child().add_named(box, pagename)

    def add_widget(self, widget, pagename='main'):
        box = self.get_child().get_child_by_name(pagename)
        box.append(widget)

    def show_page(self, button, page_name, transition_type):
        self.get_child().set_transition_type(transition_type)
        self.get_child().set_visible_child_name(page_name)

    def on_close(self, popover):
        self.show_page(None, 'main', Gtk.StackTransitionType.NONE)


class MenuBuilder():

    def create_menu():
        menu = PopoverMenu()
        return menu

    def create_button(label, icon_name=None, shortcut=None):
        button = Gtk.Button()
        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        button.set_child(button_box)
        button.get_style_context().add_class('action')

        if icon_name == 'placeholder':
            icon = Gtk.DrawingArea()
            icon.set_size_request(24, 16)
            button_box.append(icon)
        elif icon_name != None:
            icon = Gtk.Image.new_from_icon_name(icon_name)
            icon.get_style_context().add_class('icon')
            button_box.append(icon)

        button_box.append(Gtk.Label.new(label))

        if shortcut != None:
            shortcut_label = Gtk.Label.new(shortcut)
            shortcut_label.get_style_context().add_class('shortcut')
            shortcut_label.set_xalign(1)
            shortcut_label.set_hexpand(True)
            button_box.append(shortcut_label)

        return button

    def create_menu_button(label):
        button = Gtk.Button()
        button_box = Gtk.CenterBox()
        button_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        button.set_child(button_box)
        button.get_style_context().add_class('menu')

        button_box.set_start_widget(Gtk.Label.new(label))
        button_box.set_end_widget(Gtk.Image.new_from_icon_name('pan-end-symbolic'))

        return button


