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

from viewgtk.viewgtk_shortcutsbar import *
from viewgtk.viewgtk_document_search import *
from viewgtk.viewgtk_document_autocomplete import *


class DocumentView(Gtk.HBox):
    
    def __init__(self, document, build_log_view):
        Gtk.HBox.__init__(self)
        
        self.vbox = Gtk.VBox()        
        self.scrolled_window = Gtk.ScrolledWindow()
        
        self.search_bar = SearchBar()
        self.shortcuts_bar_bottom = ShortcutsBarBottom()
        self.autocomplete = DocumentAutocompleteView()
        
        self.source_view = GtkSource.View.new_with_buffer(document.get_buffer())
        self.source_view.set_monospace(True)
        self.source_view.set_smart_home_end(True)
        self.source_view.set_insert_spaces_instead_of_tabs(True)
        self.source_view.set_auto_indent(True)
        self.source_view.set_tab_width(4)
        self.source_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.source_view.set_show_line_numbers(True)
        self.source_view.set_left_margin(6)
        self.scrolled_window.add(self.source_view)

        self.document_paned = Gtk.VPaned()
        self.document_paned.get_style_context().add_class("document_paned")
        self.document_paned.pack1(self.vbox, True, False)
        self.document_paned.pack2(build_log_view, False, True)

        self.vbox.pack_start(self.scrolled_window, True, True, 0)
        self.vbox.pack_start(self.search_bar, False, False, 0)
        self.pack_start(self.document_paned, True, True, 0)

        self.show_all()

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 200, 600


class ShortcutsBarBottom(Gtk.Toolbar):

    def __init__(self):
        Gtk.Toolbar.__init__(self)

        self.set_style(Gtk.ToolbarStyle.ICONS)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)
        self.get_style_context().add_class('bottom')

        self.button_build_log = Gtk.ToggleToolButton()
        self.button_build_log.set_icon_name('utilities-system-monitor-symbolic')
        self.button_build_log.set_tooltip_text('Build log (F8)')
        self.insert(self.button_build_log, 0)

        self.button_find_and_replace = Gtk.ToggleToolButton()
        self.button_find_and_replace.set_icon_name('edit-find-replace-symbolic')
        self.button_find_and_replace.set_tooltip_text('Find and Replace (Ctrl+H)')
        self.insert(self.button_find_and_replace, 0)
        
        self.button_find = Gtk.ToggleToolButton()
        self.button_find.set_icon_name('edit-find-symbolic')
        self.button_find.set_tooltip_text('Find (Ctrl+F)')
        self.insert(self.button_find, 0)
        self.show_all()



