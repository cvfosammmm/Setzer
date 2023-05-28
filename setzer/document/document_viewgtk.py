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
gi.require_version('GtkSource', '4')
from gi.repository import Gtk
from gi.repository import GtkSource

import setzer.document.shortcutsbar.shortcutsbar_viewgtk as shortcutsbar_view
import setzer.document.search.search_viewgtk as search_view


class DocumentView(Gtk.Box):
    
    def __init__(self, document):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.HORIZONTAL)

        self.vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.overlay = Gtk.Overlay()
        self.scrolled_window = Gtk.ScrolledWindow()
        
        self.search_bar = search_view.SearchBar()
        self.shortcutsbar_bottom = shortcutsbar_view.ShortcutsbarBottom()
        self.wizard_button = shortcutsbar_view.WizardButton()

        self.source_view = document.content.source_view
        self.source_view.set_monospace(True)
        self.source_view.set_smart_home_end(True)
        self.source_view.set_auto_indent(True)
        self.source_view.set_bottom_margin(120)
        self.source_view.set_right_margin(12)

        self.scrolled_window.add(self.source_view)
        self.overlay.add(self.scrolled_window)

        self.vbox.pack_start(self.overlay, True, True, 0)
        self.vbox.pack_start(self.search_bar, False, False, 0)
        self.pack_start(self.vbox, True, True, 0)

        self.show_all()

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 200, 600


