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
from gi.repository import Gtk


class SearchBar(Gtk.Revealer):
    ''' Find text in a document '''
    
    def __init__(self):
        Gtk.Revealer.__init__(self)
        
        self.super_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.super_box.pack_start(self.box, False, False, 0)
        self.super_box.get_style_context().add_class('search_bar')

        self.left_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.replace_wrapper = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)

        self.entry = Gtk.SearchEntry()
        self.entry.get_style_context().add_class('search_entry')
        self.entry_css_provider = Gtk.CssProvider()
        self.entry.get_style_context().add_provider(self.entry_css_provider, 800)

        self.arrow = Gtk.Image.new_from_icon_name('own-searchandreplacearrow-symbolic', Gtk.IconSize.LARGE_TOOLBAR)

        self.replace_entry = Gtk.Entry()
        self.replace_entry.set_width_chars(4)
        self.replace_entry.get_style_context().add_class('replace_entry')
        self.replace_entry_css_provider = Gtk.CssProvider()
        self.replace_entry.get_style_context().add_provider(self.replace_entry_css_provider, 800)

        self.icon_name = self.entry.get_icon_name(Gtk.EntryIconPosition.PRIMARY)
        self.prev_button = Gtk.Button.new_from_icon_name('go-up-symbolic', Gtk.IconSize.MENU)
        self.prev_button.set_can_focus(False)
        self.prev_button.set_tooltip_text(_('Previous result') + ' (Ctrl+Shift+G)')
        self.next_button = Gtk.Button.new_from_icon_name('go-down-symbolic', Gtk.IconSize.MENU)
        self.next_button.set_can_focus(False)
        self.next_button.set_tooltip_text(_('Next result') + ' (Ctrl+G)')
        self.replace_button = Gtk.Button.new_with_label(_('Replace'))
        self.replace_button.set_can_focus(False)
        self.replace_button.set_tooltip_text(_('Replace selected result'))
        self.replace_button.set_sensitive(False)
        self.replace_all_button = Gtk.Button.new_with_label(_('All'))
        self.replace_all_button.set_can_focus(False)
        self.replace_all_button.set_tooltip_text(_('Replace all results'))
        self.replace_all_button.set_sensitive(False)
        
        self.left_box.pack_start(self.entry, False, False, 0)
        self.left_box.pack_start(self.prev_button, False, False, 0)
        self.left_box.pack_start(self.next_button, False, False, 0)
        self.left_box.get_style_context().add_class('linked')

        self.match_counter = Gtk.Label('')
        self.match_counter.set_halign(Gtk.Align.END)
        self.match_counter.get_style_context().add_class('search_match_counter')

        self.overlay_wrapper = Gtk.Overlay()
        self.overlay_wrapper.add(self.left_box)
        self.overlay_wrapper.add_overlay(self.match_counter)
        self.overlay_wrapper.set_overlay_pass_through(self.match_counter, True)

        self.close_button = Gtk.Button.new_from_icon_name('window-close-symbolic', Gtk.IconSize.MENU)
        self.close_button.get_style_context().add_class('flat')
        self.close_button.set_can_focus(False)

        self.replace_wrapper.pack_start(self.arrow, False, False, 6)
        self.replace_wrapper.pack_start(self.replace_entry, False, False, 6)
        self.replace_wrapper.pack_start(self.replace_button, False, False, 0)
        self.replace_wrapper.pack_start(self.replace_all_button, False, False, 6)

        self.box.pack_start(self.overlay_wrapper, False, False, 6)
        self.box.pack_end(self.close_button, False, False, 0)

        self.add(self.super_box)
        
        self.show_all()
        self.replace_wrapper.hide()
        self.set_reveal_child(False)
        

