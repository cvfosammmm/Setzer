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
from gi.repository import Pango


class DocumentStructureView(Gtk.TreeView):

    def __init__(self):
        Gtk.TreeView.__init__(self)

        self.tree_store = Gtk.TreeStore(int, str, str)
        self.set_model(self.tree_store)

        self.set_headers_visible(False)
        self.set_activate_on_single_click(True)
        self.get_selection().set_mode(Gtk.SelectionMode.NONE)
        self.set_show_expanders(False)
        self.set_level_indentation(18)
        self.set_can_focus(False)

        renderer = Gtk.CellRendererPixbuf()
        renderer.set_sensitive(True)
        renderer.set_property('width', 23)
        renderer.set_property('xalign', 1)
        column = Gtk.TreeViewColumn()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'icon_name', 1)

        renderer = Gtk.CellRendererText()
        renderer.set_sensitive(True)
        renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        renderer.set_property('xpad', 8)
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 2)

        self.append_column(column)


