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
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk
from gi.repository import GtkSource

import setzer.document.shortcutsbar.shortcutsbar_viewgtk as shortcutsbar_view
import setzer.document.search.search_viewgtk as search_view


class DocumentView(Gtk.HBox):
    
    def __init__(self, document):
        Gtk.HBox.__init__(self)
        
        self.vbox = Gtk.VBox()        
        self.scrolled_window = Gtk.ScrolledWindow()
        
        self.search_bar = search_view.SearchBar()
        self.shortcuts_bar_bottom = shortcutsbar_view.ShortcutsBarBottom()
        self.wizard_button = shortcutsbar_view.WizardButton()

        self.source_view = GtkSource.View.new_with_buffer(document.get_buffer())
        self.source_view.set_monospace(True)
        self.source_view.set_smart_home_end(True)
        self.source_view.set_auto_indent(True)
        self.source_view.set_left_margin(6)
        self.scrolled_window.add(self.source_view)

        self.menu_item_undo = Gtk.MenuItem.new_with_label('Undo')
        self.menu_item_redo = Gtk.MenuItem.new_with_label('Redo')
        self.menu_item_cut = Gtk.MenuItem.new_with_label('Cut')
        self.menu_item_copy = Gtk.MenuItem.new_with_label('Copy')
        self.menu_item_paste = Gtk.MenuItem.new_with_label('Paste')
        self.menu_item_delete = Gtk.MenuItem.new_with_label('Delete')
        self.menu_item_select_all = Gtk.MenuItem.new_with_label('Select All')
        self.context_menu = Gtk.Menu()
        self.context_menu.append(self.menu_item_undo)
        self.context_menu.append(self.menu_item_redo)
        self.context_menu.append(Gtk.SeparatorMenuItem())
        self.context_menu.append(self.menu_item_cut)
        self.context_menu.append(self.menu_item_copy)
        self.context_menu.append(self.menu_item_paste)
        self.context_menu.append(self.menu_item_delete)
        self.context_menu.append(Gtk.SeparatorMenuItem())
        self.context_menu.append(self.menu_item_select_all)

        if document.is_latex_document():
            self.context_menu.append(Gtk.SeparatorMenuItem())
            self.menu_item_show_in_preview = Gtk.MenuItem.new_with_label('Show in Preview')
            self.context_menu.append(self.menu_item_show_in_preview)

        self.vbox.pack_start(self.scrolled_window, True, True, 0)
        self.vbox.pack_start(self.search_bar, False, False, 0)
        self.pack_start(self.vbox, True, True, 0)

        self.show_all()

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 200, 600


