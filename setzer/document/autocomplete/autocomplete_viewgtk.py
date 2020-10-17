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
from gi.repository import Gtk, Gio, GLib, Pango


class DocumentAutocompleteView(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)
        self.get_style_context().add_class('autocomplete')

        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.START)

        self.list = Gtk.ListBox()
        self.list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list.set_can_focus(False)
        self.items = list()
        self.selected_index = 0

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.add(self.list)

        self.infobox = Gtk.Label('')
        self.infobox.set_xalign(0)
        self.infobox.set_ellipsize(Pango.EllipsizeMode.END)
        self.infobox.set_max_width_chars(30)
        self.infobox.get_style_context().add_class('infobox')

        self.pack_start(self.scrolled_window, True, True, 0)
        self.pack_start(self.infobox, False, False, 0)
        self.list.show_all()
        self.infobox.show_all()

    def empty_list(self):
        self.items = list()
        self.list.foreach(self.list.remove)

    def prepend(self, item):
        self.items.insert(0, item)
        self.list.prepend(item)

    def select_next(self):
        if self.selected_index >= len(self.items) - 1:
            self.select_first()
        else:
            self.selected_index += 1
            row = self.list.get_row_at_index(self.selected_index)
            self.list.select_row(row)

    def select_previous(self):
        if self.selected_index == 0:
            self.select_last()
        else:
            self.selected_index -= 1
            row = self.list.get_row_at_index(self.selected_index)
            self.list.select_row(row)

    def select_first(self):
        row = self.list.get_row_at_index(0)
        self.list.select_row(row)
        self.selected_index = 0

    def select_last(self):
        row = self.list.get_row_at_index(len(self.items) - 1)
        self.list.select_row(row)
        self.selected_index = len(self.items) - 1

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE


class DocumentAutocompleteItem(Gtk.HBox):

    def __init__(self, command, offset=0):
        Gtk.HBox.__init__(self)

        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.START)

        self.command = command
        if offset != 0:
            command_text = '<b>' + GLib.markup_escape_text(command['command'])[:offset] + '</b>'
            command_text += GLib.markup_escape_text(command['command'])[offset:]
        else:
            command_text = GLib.markup_escape_text(command['command'])

        self.dotlabels = filter(None, command['dotlabels'].split('###'))
        for dotlabel in self.dotlabels:
            command_text = command_text.replace('•', '<span alpha="60%">' + GLib.markup_escape_text(dotlabel) + '</span>', 1)

        self.label = Gtk.Label()
        self.label.set_markup(command_text)
        self.label.get_style_context().add_class('monospace')
        self.pack_start(self.label, True, True, 0)
        self.show_all()

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE


