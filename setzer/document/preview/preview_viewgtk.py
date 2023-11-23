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
from gi.repository import Gdk
from gi.repository import Gio

from setzer.widgets.scrolling_widget.scrolling_widget import ScrollingWidget


class PreviewView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('preview')

        self.content = ScrollingWidget()
        self.drawing_area = self.content.content

        self.blank_slate = BlankSlateView()

        self.stack = Gtk.Stack()
        self.stack.set_vexpand(True)
        self.stack.add_named(self.blank_slate, 'blank_slate')
        self.stack.add_named(self.content.view, 'pdf')

        self.overlay = Gtk.Overlay()
        self.overlay.set_vexpand(True)
        self.overlay.set_child(self.stack)
        self.append(self.overlay)

        self.target_label = Gtk.Label()
        self.target_label.set_halign(Gtk.Align.START)
        self.target_label.set_valign(Gtk.Align.END)
        self.target_label.set_can_target(False)
        self.target_label.get_style_context().add_class('target-label')
        self.overlay.add_overlay(self.target_label)
        self.set_link_target_string('')

    def set_layout_data(self, layout_data):
        self.layout_data = layout_data

    def set_link_target_string(self, target_string):
        self.target_label.set_text(target_string)
        self.target_label.set_visible(target_string != '')


class BlankSlateView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('preview_blank')

        drawing_area = Gtk.DrawingArea()
        drawing_area.set_vexpand(True)
        self.append(drawing_area)

        image = Gtk.Image.new_from_icon_name('own-no-preview-symbolic')
        image.set_pixel_size(150)
        self.append(image)

        header = Gtk.Label.new(_('No preview available'))
        header.get_style_context().add_class('header')
        self.append(header)

        body = Gtk.Label.new(_('To show a .pdf preview of your document, click the build button in the headerbar.'))
        body.get_style_context().add_class('body')
        body.set_wrap(True)
        self.append(body)

        drawing_area = Gtk.DrawingArea()
        drawing_area.set_vexpand(True)
        self.append(drawing_area)


