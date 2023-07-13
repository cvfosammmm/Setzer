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
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from gi.repository import GLib


class BibTeXShortcutsbar(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.get_style_context().add_class('shortcutsbar')

        self.top_icons = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.right_icons = Gtk.Box()
        self.right_icons.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.center_icons = Gtk.CenterBox()
        self.center_icons.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.center_icons.set_hexpand(True)

        self.populate_top_toolbar()

        self.append(self.top_icons)
        self.append(self.center_icons)
        self.append(self.right_icons)

    def populate_top_toolbar(self):
        return #TODO
        self.entry_button = Gtk.ToolButton()
        icon_widget = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        icon = Gtk.Image.new_from_icon_name('list-add-symbolic', Gtk.IconSize.MENU)
        icon.set_margin_start(4)
        icon_widget.append(icon)
        label_revealer = Gtk.Revealer()
        label = Gtk.Label.new(_('Create New Entry'))
        label.set_margin_start(5)
        label.set_margin_end(4)
        label_revealer.set_child(label)
        label_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        label_revealer.set_reveal_child(True)
        icon_widget.append(label_revealer)

        self.entry_button.set_icon_widget(icon_widget)
        self.entry_button.set_action_name('win.create-new-bibtex-entry')
        self.entry_button.set_focus_on_click(False)
        self.entry_button.set_tooltip_text(_('Create a New BibTeX Entry'))
        self.top_icons.insert(self.entry_button, 0)

        self.entry_button = Gtk.ToolButton()
        icon_widget = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        icon = Gtk.Image.new_from_icon_name('media-playlist-repeat-symbolic', Gtk.IconSize.MENU)
        icon.set_margin_start(4)
        icon_widget.append(icon)
        label_revealer = Gtk.Revealer()
        label = Gtk.Label.new(_('Previously Used Entries'))
        label.set_margin_start(6)
        label.set_margin_end(4)
        label_revealer.set_child(label)
        label_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        label_revealer.set_reveal_child(True)
        icon_widget.append(label_revealer)

        self.entry_button.set_icon_widget(icon_widget)
        self.entry_button.set_action_name('win.show-previous-bibtex-entries')
        self.entry_button.set_focus_on_click(False)
        self.entry_button.set_tooltip_text(_('Add a Previously Used BibTeX Entry'))
        #self.top_icons.insert(self.entry_button, 0)

        self.entry_button = Gtk.ToolButton()
        icon_widget = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        icon = Gtk.Image.new_from_icon_name('globe-alt-symbolic', Gtk.IconSize.MENU)
        icon.set_margin_start(4)
        icon_widget.append(icon)
        label_revealer = Gtk.Revealer()
        label = Gtk.Label.new(_('Search For Entries Online'))
        label.set_margin_start(6)
        label.set_margin_end(4)
        label_revealer.set_child(label)
        label_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        label_revealer.set_reveal_child(True)
        icon_widget.append(label_revealer)

        self.entry_button.set_icon_widget(icon_widget)
        self.entry_button.set_action_name('win.search-online-for-bibtex-entries')
        self.entry_button.set_focus_on_click(False)
        self.entry_button.set_tooltip_text(_('Add a BibTeX Entry from an Online Database'))
        #self.top_icons.insert(self.entry_button, 0)


