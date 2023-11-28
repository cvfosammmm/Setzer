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
from gi.repository import Gtk, Gdk, GObject

from setzer.helpers.observable import Observable


class SearchEntry(Gtk.Entry):

    def __init__(self):
        Gtk.Entry.__init__(self)

        self.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, 'system-search-symbolic')
        self.set_icon_activatable(Gtk.EntryIconPosition.PRIMARY, False)

        self.connect('changed', self.on_search_changed)
        self.connect('icon-press', self.on_icon_press)

        self.key_controller = Gtk.EventControllerKey()
        self.key_controller.connect('key-pressed', self.on_keypress)
        self.add_controller(self.key_controller)

    def on_search_changed(self, entry):
        if self.get_text() == '':
            self.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
            self.set_icon_activatable(Gtk.EntryIconPosition.SECONDARY, False)
        else:
            self.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, 'edit-clear-symbolic')
            self.set_icon_activatable(Gtk.EntryIconPosition.SECONDARY, True)

    def on_keypress(self, controller, keyval, keycode, state):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Down')):
            self.emit('next_match')
            return True

        if (state & modifiers, keyval) == (Gdk.ModifierType.CONTROL_MASK, Gdk.keyval_from_name('g')):
            self.emit('next_match')
            return True

        if (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Up')):
            self.emit('previous_match')
            return True

        if (state & modifiers, keyval) == (Gdk.ModifierType.CONTROL_MASK & Gdk.ModifierType.SHIFT_MASK, Gdk.keyval_from_name('g')):
            self.emit('previous_match')
            return True

        if (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Escape')):
            self.emit('stop_search')
            return True

        return False

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST, return_type=None, arg_types=None)
    def next_match(self): pass

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST, return_type=None, arg_types=None)
    def previous_match(self): pass

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST, return_type=None, arg_types=None)
    def stop_search(self): pass

    def on_icon_press(self, entry, icon_pos):
        if icon_pos == Gtk.EntryIconPosition.SECONDARY:
            self.set_text('')


