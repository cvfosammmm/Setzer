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


class DocumentStructurePageView(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.get_style_context().add_class('sidebar-document-structure')

        self.tabs_box = Gtk.HBox()
        self.tabs_box.get_style_context().add_class('tabs-box')
        self.tabs_box.pack_start(Gtk.Label('Document Structure'), False, False, 0)
        self.pack_start(self.tabs_box, False, False, 0)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.vbox = Gtk.VBox()
        self.vbox.get_style_context().add_class('treeview-container')
        self.scrolled_window.add(self.vbox)
        self.pack_start(self.scrolled_window, True, True, 0)

        self.tree_view = Gtk.TreeView()

        self.tree_store = Gtk.TreeStore(str, int, str, str)
        self.tree_view.set_model(self.tree_store)

        self.tree_view.set_headers_visible(False)
        self.tree_view.set_activate_on_single_click(True)
        self.tree_view.get_selection().set_mode(Gtk.SelectionMode.NONE)
        self.tree_view.set_show_expanders(False)
        self.tree_view.set_level_indentation(18)
        self.tree_view.set_can_focus(False)

        renderer = Gtk.CellRendererPixbuf()
        renderer.set_sensitive(True)
        renderer.set_property('width', 23)
        renderer.set_property('xalign', 1)
        column = Gtk.TreeViewColumn()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'icon_name', 2)

        renderer = Gtk.CellRendererText()
        renderer.set_sensitive(True)
        renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        renderer.set_property('xpad', 8)
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 3)

        self.tree_view.append_column(column)
        self.vbox.pack_start(self.tree_view, True, True, 0)

        self.show_all()


