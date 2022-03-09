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
from gi.repository import Gdk
from gi.repository import Gtk


class ModeBlank(object):

    def __init__(self, autocomplete, document):
        self.autocomplete = autocomplete
        self.document = document
        self.will_show = False

    def on_insert_text(self, buffer, location_iter, text, text_length):
        pass

    def on_delete_range(self, buffer, start_iter, end_iter):
        pass

    def on_keypress(self, event):
        ''' returns whether the keypress has been handled. '''

        modifiers = Gtk.accelerator_get_default_mod_mask()

        tab_keyvals = [Gdk.keyval_from_name('Tab'), Gdk.keyval_from_name('ISO_Left_Tab')]
        if event.keyval in tab_keyvals:
            if event.state & modifiers == 0:
                return self.on_tab_press()

        if event.keyval == Gdk.keyval_from_name('backslash') and event.state & modifiers == 0:
            char = self.document.content.get_char_at_cursor()
            if char.isalpha():
                self.add_backslash_with_space()
                return True
            return False

        bracket_vals = [Gdk.keyval_from_name('parenleft'), Gdk.keyval_from_name('bracketleft'), Gdk.keyval_from_name('braceleft')]
        if event.keyval in bracket_vals and not self.document.autocomplete.is_active():
            if event.keyval == Gdk.keyval_from_name('bracketleft'):
                self.document.content.autoadd_latex_brackets('[')
            if event.keyval == Gdk.keyval_from_name('braceleft'):
                self.document.content.autoadd_latex_brackets('{')
            if event.keyval == Gdk.keyval_from_name('parenleft'):
                self.document.content.autoadd_latex_brackets('(')
            return True

        return False

    def on_tab_press(self):
        if self.autocomplete.document.cursor_inside_latex_command_or_at_end():
            self.autocomplete.activate_if_possible()
            self.autocomplete.update()
            if self.cursor_at_latex_command_end():
                return self.autocomplete.is_active()
            else:
                return True
        return False

    def cursor_at_latex_command_end(self):
        content = self.autocomplete.document.content
        current_word = content.get_latex_command_at_cursor()
        if ServiceLocator.get_regex_object(r'\\(\w*(?:\*){0,1})').fullmatch(current_word):
            return content.cursor_ends_word()
        return False

    def add_backslash_with_space(self):
        buffer = self.document.content.source_buffer
        buffer.insert_at_cursor('\\ ')
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        insert_iter.backward_char()
        buffer.place_cursor(insert_iter)

    def update(self):
        self.autocomplete.view.update_position()
        self.autocomplete.view.update_visibility()
        self.autocomplete.view.update_margins()

    def get_offset(self):
        return 0

    def submit(self):
        pass

    def cancel(self):
        pass

    def is_active(self):
        return False

