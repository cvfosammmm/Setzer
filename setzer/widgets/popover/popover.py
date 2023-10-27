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


class Popover(Gtk.Box):

    def __init__(self, popover_manager):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.START)
        self.get_style_context().add_class('popover')

        self.popover_manager = popover_manager

        self.width = 0

        self.arrow = Gtk.DrawingArea()
        self.arrow.get_style_context().add_class('arrow')
        self.arrow_box = Gtk.CenterBox()
        self.arrow_box.set_start_widget(self.arrow)

        self.arrow_border = Gtk.DrawingArea()
        self.arrow_border.get_style_context().add_class('arrow-border')
        self.arrow_border_box = Gtk.CenterBox()
        self.arrow_border_box.set_start_widget(self.arrow_border)

        self.stack = Gtk.Stack()
        self.stack.set_vhomogeneous(False)

        self.content_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.content_box.get_style_context().add_class('content')
        self.content_box.append(self.arrow_border_box)
        self.content_box.append(self.stack)

        self.append(self.arrow_box)
        self.append(self.content_box)

        self.add_page('main')

    def add_page(self, pagename='main', label=None):
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.stack.add_named(box, pagename)

        if label != None:
            button_box = Gtk.CenterBox()
            button_box.set_orientation(Gtk.Orientation.HORIZONTAL)
            button_box.set_center_widget(Gtk.Label.new(label))
            button_box.set_start_widget(Gtk.Image.new_from_icon_name('pan-start-symbolic'))

            button = Gtk.Button()
            button.set_child(button_box)
            button.get_style_context().add_class('header')
            button.connect('clicked', self.show_page, 'main', Gtk.StackTransitionType.SLIDE_LEFT)

            self.add_widget(button, pagename)

    def add_widget(self, widget, pagename='main'):
        box = self.stack.get_child_by_name(pagename)
        box.append(widget)

    def set_width(self, width):
        self.width = width
        self.set_size_request(width, -1)

    def show_page(self, button, page_name, transition_type):
        self.stack.set_transition_type(transition_type)
        self.stack.set_visible_child_name(page_name)

    def popdown(self):
        self.popover_manager.popdown()


