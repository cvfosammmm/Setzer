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
from gi.repository import Gdk
from gi.repository import Pango


class DocumentStructurePageView(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.get_style_context().add_class('sidebar-document-structure')

        self.tabs_box = Gtk.HBox()
        self.tabs_box.get_style_context().add_class('tabs-box')
        self.tabs_box.pack_start(Gtk.Label('Document Structure'), False, False, 0)
        self.pack_start(self.tabs_box, False, False, 0)

        self.content = Gtk.DrawingArea()
        self.content.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.content.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)

        style_context = self.content.get_style_context()
        self.font = self.content.get_style_context().get_font(style_context.get_state())
        self.font_size = (self.font.get_size() * 4) / (3 * Pango.SCALE)
        self.line_height = int(self.font_size) + 11

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.add(self.content)
        self.pack_start(self.scrolled_window, True, True, 0)

        self.show_all()


