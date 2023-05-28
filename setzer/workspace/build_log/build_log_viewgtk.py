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
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango

import os.path


class BuildLogView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('buildlog')

        self.scrolled_window = Gtk.ScrolledWindow()
        self.list = Gtk.DrawingArea()
        self.list.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.list.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.scrolled_window.add(self.list)

        style_context = self.list.get_style_context()
        self.font = self.list.get_style_context().get_font(style_context.get_state())
        self.font_size = (self.font.get_size() * 4) / (3 * Pango.SCALE)
        self.line_height = int(self.font_size) + 11
        self.layout = Pango.Layout(self.list.get_pango_context())
        self.layout.set_ellipsize(Pango.EllipsizeMode.START)
        self.fg_color = style_context.lookup_color('theme_fg_color')[1]

        self.header = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.close_button = Gtk.Button.new_from_icon_name('window-close-symbolic', Gtk.IconSize.MENU)
        self.close_button.get_style_context().add_class('flat')
        self.close_button.set_can_focus(False)
        self.close_button.set_action_name('win.close-build-log')
        self.header_label = Gtk.Label()
        self.header_label.set_size_request(300, -1)
        self.header_label.set_xalign(0)
        self.header_label.set_margin_left(0)
        self.header.pack_start(self.header_label, True, True, 0)
        self.header.pack_start(self.close_button, False, False, 0)

        self.setup_icons()
        self.connect('style-updated', self.setup_icons)

        self.pack_start(self.header, False, False, 0)
        self.pack_start(self.scrolled_window, True, True, 0)
        self.set_size_request(200, 200)

    def setup_icons(self, widget=None):
        fg_color = self.get_style_context().lookup_color('theme_fg_color')[1]
        self.icons = dict()
        for icon_type, icon_name in [('Error', 'dialog-error-symbolic'), ('Warning', 'dialog-warning-symbolic'), ('Badbox', 'own-badbox-symbolic')]:
            icon_info = Gtk.IconTheme.get_default().lookup_icon(icon_name, 16 * self.get_scale_factor(), 0)
            pixbuf, was_symbolic = icon_info.load_symbolic(fg_color, fg_color, fg_color, fg_color)
            surface = Gdk.cairo_surface_create_from_pixbuf(pixbuf, self.get_scale_factor())
            self.icons[icon_type] = surface

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE


