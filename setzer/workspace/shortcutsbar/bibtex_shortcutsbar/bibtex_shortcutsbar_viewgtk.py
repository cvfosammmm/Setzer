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
from gi.repository import GLib


class BibTeXShortcutsbar(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.HORIZONTAL)
        self.get_style_context().add_class('shortcutsbar')

        self.current_bottom = None

        self.create_top_toolbar()
        self.populate_top_toolbar()
        self.pack_start(self.top_icons, True, True, 0)

    def create_top_toolbar(self):
        self.top_icons = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        
    def populate_top_toolbar(self):
        self.entry_button = Gtk.Button()
        icon_widget = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        icon = Gtk.Image.new_from_icon_name('list-add-symbolic', Gtk.IconSize.MENU)
        icon.set_margin_left(4)
        icon_widget.pack_start(icon, False, False, 0)
        label_revealer = Gtk.Revealer()
        label = Gtk.Label(_('Create New Entry'))
        label.set_margin_left(5)
        label.set_margin_right(4)
        label_revealer.add(label)
        label_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        label_revealer.set_reveal_child(True)
        icon_widget.pack_start(label_revealer, False, False, 0)

        self.entry_button.add(icon_widget)
        self.entry_button.set_action_name('win.create-new-bibtex-entry')
        self.entry_button.set_focus_on_click(False)
        self.entry_button.set_tooltip_text(_('Create a New BibTeX Entry'))
        self.entry_button.get_style_context().add_class('flat')
        self.top_icons.pack_start(self.entry_button, False, False, 0)

        self.entry_button = Gtk.Button()
        icon_widget = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        icon = Gtk.Image.new_from_icon_name('media-playlist-repeat-symbolic', Gtk.IconSize.MENU)
        icon.set_margin_left(4)
        icon_widget.pack_start(icon, False, False, 0)
        label_revealer = Gtk.Revealer()
        label = Gtk.Label(_('Previously Used Entries'))
        label.set_margin_left(6)
        label.set_margin_right(4)
        label_revealer.add(label)
        label_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        label_revealer.set_reveal_child(True)
        icon_widget.pack_start(label_revealer, False, False, 0)

        self.entry_button.add(icon_widget)
        self.entry_button.set_action_name('win.show-previous-bibtex-entries')
        self.entry_button.set_focus_on_click(False)
        self.entry_button.set_tooltip_text(_('Add a Previously Used BibTeX Entry'))
        self.entry_button.get_style_context().add_class('flat')
        #self.top_icons.pack_start(self.entry_button, False, False, 0)

        self.entry_button = Gtk.Button()
        icon_widget = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        icon = Gtk.Image.new_from_icon_name('globe-alt-symbolic', Gtk.IconSize.MENU)
        icon.set_margin_left(4)
        icon_widget.pack_start(icon, False, False, 0)
        label_revealer = Gtk.Revealer()
        label = Gtk.Label(_('Search For Entries Online'))
        label.set_margin_left(6)
        label.set_margin_right(4)
        label_revealer.add(label)
        label_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        label_revealer.set_reveal_child(True)
        icon_widget.pack_start(label_revealer, False, False, 0)

        self.entry_button.add(icon_widget)
        self.entry_button.set_action_name('win.search-online-for-bibtex-entries')
        self.entry_button.set_focus_on_click(False)
        self.entry_button.set_tooltip_text(_('Add a BibTeX Entry from an Online Database'))
        self.entry_button.get_style_context().add_class('flat')
        #self.top_icons.pack_start(self.entry_button, False, False, 0)


