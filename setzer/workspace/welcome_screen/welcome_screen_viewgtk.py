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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class WelcomeScreenView(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self)

        self.drawing_area = Gtk.DrawingArea()
        self.overlay = Gtk.VBox()
        self.overlay.get_style_context().add_class('welcome')
        self.header = Gtk.Label('Write beautiful LaTeX documents with ease!')
        self.header.set_line_wrap(True)
        self.header.get_style_context().add_class('welcome-header')
        self.description = Gtk.Label('Click the open or create buttons in the headerbar above to start editing.')
        self.description.set_line_wrap(True)
        self.description.get_style_context().add_class('welcome-description')
        self.overlay.pack_start(self.header, False, False, 0)
        self.overlay.pack_start(self.description, False, False, 0)
        self.overlay.set_valign(Gtk.Align.CENTER)

        self.hbox = Gtk.HBox()
        self.hbox.set_center_widget(self.overlay)

        self.add(self.drawing_area)
        self.add_overlay(self.hbox)


