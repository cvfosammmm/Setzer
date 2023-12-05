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

from setzer.widgets.search_entry.search_entry import SearchEntry


class SearchBar(Gtk.Revealer):
    ''' Find text in a document '''
    
    def __init__(self):
        Gtk.Revealer.__init__(self)
        
        self.super_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.box = Gtk.CenterBox()
        self.box.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.super_box.append(self.box)
        self.super_box.get_style_context().add_class('search_bar')

        self.left_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.replace_wrapper = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

        self.entry = SearchEntry()
        self.entry.get_style_context().add_class('search_entry')

        self.arrow = Gtk.Image.new_from_icon_name('own-searchandreplacearrow-symbolic')
        self.arrow.set_margin_start(6)

        self.replace_entry = Gtk.Entry()
        self.replace_entry.set_width_chars(4)
        self.replace_entry.get_style_context().add_class('replace_entry')
        self.replace_entry.set_size_request(105, -1)
        self.replace_entry.set_margin_start(6)

        self.prev_button = Gtk.Button.new_from_icon_name('go-up-symbolic')
        self.prev_button.set_can_focus(False)
        self.prev_button.set_tooltip_text(_('Previous result') + ' (Ctrl+Shift+G)')
        self.next_button = Gtk.Button.new_from_icon_name('go-down-symbolic')
        self.next_button.set_can_focus(False)
        self.next_button.set_tooltip_text(_('Next result') + ' (Ctrl+G)')
        self.replace_button = Gtk.Button.new_with_label(_('Replace'))
        self.replace_button.set_can_focus(False)
        self.replace_button.set_tooltip_text(_('Replace selected result'))
        self.replace_button.set_sensitive(False)
        self.replace_button.set_margin_start(6)
        self.replace_all_button = Gtk.Button.new_with_label(_('All'))
        self.replace_all_button.set_can_focus(False)
        self.replace_all_button.set_tooltip_text(_('Replace all results'))
        self.replace_all_button.set_sensitive(False)
        self.replace_all_button.set_margin_start(6)
        
        self.left_box.append(self.entry)
        self.left_box.append(self.prev_button)
        self.left_box.append(self.next_button)
        self.left_box.append(self.replace_wrapper)
        self.left_box.set_margin_start(6)
        self.left_box.get_style_context().add_class('linked')

        self.match_counter = Gtk.Label()
        self.match_counter.set_halign(Gtk.Align.START)
        self.match_counter.set_xalign(1)
        self.match_counter.set_hexpand(False)
        self.match_counter.set_property('can-target', False)
        self.match_counter.get_style_context().add_class('search_match_counter')

        self.overlay_wrapper = Gtk.Overlay()
        self.overlay_wrapper.set_child(self.super_box)
        self.overlay_wrapper.add_overlay(self.match_counter)

        self.close_button = Gtk.Button.new_from_icon_name('window-close-symbolic')
        self.close_button.get_style_context().add_class('flat')
        self.close_button.set_can_focus(False)

        self.replace_wrapper.append(self.arrow)
        self.replace_wrapper.append(self.replace_entry)
        self.replace_wrapper.append(self.replace_button)
        self.replace_wrapper.append(self.replace_all_button)

        self.box.set_start_widget(self.left_box)
        self.box.set_end_widget(self.close_button)

        self.set_child(self.overlay_wrapper)

        self.replace_wrapper.set_visible(False)
        self.set_reveal_child(False)
        

