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


class WelcomeScreenView(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self)

        self.drawing_area = Gtk.DrawingArea()
        self.overlay = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.overlay.set_hexpand(True)
        self.overlay.get_style_context().add_class('welcome')
        self.header = Gtk.Label.new(_('Write beautiful LaTeX documents with ease!'))
        self.header.set_wrap(True)
        self.header.get_style_context().add_class('welcome-header')
        self.description = Gtk.Label.new(_('Click the open or create buttons in the headerbar above to start editing.'))
        self.description.set_wrap(True)
        self.description.get_style_context().add_class('welcome-description')
        self.overlay.append(self.header)
        self.overlay.append(self.description)
        self.overlay.set_valign(Gtk.Align.CENTER)

        self.hbox = Gtk.CenterBox()
        self.hbox.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.hbox.set_center_widget(self.overlay)

        self.set_child(self.drawing_area)
        self.add_overlay(self.hbox)


