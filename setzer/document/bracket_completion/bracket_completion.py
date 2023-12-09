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
from gi.repository import Gtk, Gdk


class BracketCompletion(object):

    def __init__(self, document):
        self.document = document
        self.source_buffer = document.source_buffer

        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self.on_keypress)
        key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.document.view.source_view.add_controller(key_controller)

    def on_keypress(self, controller, keyval, keycode, state):
        if self.document.autocomplete.is_active: return False

        modifiers = Gtk.accelerator_get_default_mod_mask()

        if keyval == Gdk.keyval_from_name('bracketleft'):
            self.autoclose_brackets('[')
            return True

        if keyval == Gdk.keyval_from_name('braceleft'):
            self.autoclose_brackets('{')
            return True

        if keyval == Gdk.keyval_from_name('parenleft'):
            self.autoclose_brackets('(')
            return True

        return False

    def autoclose_brackets(self, char):
        start_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        end_iter = start_iter.copy()
        end_iter.backward_char()

        closing_char = {'[': ']', '{': '}', '(': ')'}[char]
        if self.source_buffer.get_text(start_iter, end_iter, False) == '\\':
            closing_char = '\\' + closing_char

        self.source_buffer.begin_user_action()
        self.source_buffer.delete_selection(True, True)
        self.source_buffer.insert_at_cursor(char + closing_char)
        self.source_buffer.end_user_action()

        insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        insert_iter.backward_char()
        if closing_char.startswith('\\'):
            insert_iter.backward_char()
        self.source_buffer.place_cursor(insert_iter)


