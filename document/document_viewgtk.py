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
from gi.repository import Pango

import document.shortcutsbar.shortcutsbar_viewgtk as shortcutsbar_view
import document.search.search_viewgtk as search_view
import document.autocomplete.autocomplete_viewgtk as autocomplete_view


class DocumentView(Gtk.HBox):
    
    def __init__(self, document, build_log_view):
        Gtk.HBox.__init__(self)
        
        self.vbox = Gtk.VBox()        
        self.scrolled_window = Gtk.ScrolledWindow()
        
        self.search_bar = search_view.SearchBar()
        self.shortcuts_bar_bottom = shortcutsbar_view.ShortcutsBarBottom()
        self.wizard_button = shortcutsbar_view.WizardButton()
        self.autocomplete = autocomplete_view.DocumentAutocompleteView()
        self.doclist_item = OpenDocsPopoverItem(document)

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

        self.vbox.pack_start(self.scrolled_window, True, True, 0)
        self.vbox.pack_start(self.search_bar, False, False, 0)
        self.pack_start(self.vbox, True, True, 0)

        self.show_all()

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 200, 600


class OpenDocsPopoverItem(Gtk.ListBoxRow):
    ''' An item in OpenDocsPopover. '''

    def __init__(self, document):
        Gtk.ListBoxRow.__init__(self)
        self.set_selectable(False)
        self.document = document

        self.box = Gtk.HBox()
        self.icon = Gtk.Image.new_from_icon_name('text-x-generic-symbolic', Gtk.IconSize.MENU)
        self.icon.set_margin_bottom(2)
        self.icon.set_margin_right(6)
        self.icon.get_style_context().add_class('icon')
        self.box.pack_start(self.icon, False, False, 0)
        self.label = Gtk.Label('')
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        self.label.set_halign(Gtk.Align.START)
        self.flabel = Gtk.Label('')
        self.mlabel = Gtk.Label('')
        self.box.pack_start(self.label, False, False, 0)
        self.document_close_button = Gtk.Button.new_from_icon_name('window-close-symbolic', Gtk.IconSize.MENU)
        self.document_close_button.get_style_context().add_class('flat')
        self.document_close_button.get_style_context().add_class('image-button')
        self.document_close_button.set_relief(Gtk.ReliefStyle.NONE)
        self.box.pack_end(self.document_close_button, False, False, 0)
        self.add(self.box)

        self.set_name(document.get_filename(), document.get_modified())
        self.show_all()
        
    def set_name(self, filename, modified_state):
        self.title = ''
        self.folder = ''
        if modified_state == True: self.title += '*'
        if filename != None:
            fsplit = filename.rsplit('/', 1)
            if len(fsplit) > 1:
                self.title += fsplit[1]
                self.folder = fsplit[0]
                self.has_title = True
            else:
                self.title += self.document.get_displayname()
                self.has_title = False
        self.label.set_text(self.title)
        self.flabel.set_text(self.folder)
        self.mlabel.set_text(str(modified_state))
        
    def get_has_title(self):
        return self.has_title
    
    def get_title(self):
        return self.title


