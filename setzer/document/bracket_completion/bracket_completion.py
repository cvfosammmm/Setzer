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

from setzer.app.service_locator import ServiceLocator


class BracketCompletion(object):

    def __init__(self, document):
        self.document = document
        self.source_buffer = document.source_buffer

        self.autoclose_enabled = self.document.settings.get_value('preferences', 'enable_bracket_completion')
        self.bracket_selection_enabled = self.document.settings.get_value('preferences', 'bracket_selection')

        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self.on_keypress)
        key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.document.view.source_view.add_controller(key_controller)

        self.completion_marks = list()
        self.document.connect('cursor_position_changed', self.on_cursor_position_changed)
        self.document.connect('changed', self.on_buffer_changed)
        self.document.settings.connect('settings_changed', self.on_settings_changed)

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter

        if item == 'enable_bracket_completion':
            self.autoclose_enabled = value
            if not self.autoclose_enabled:
                self.reconsider_completion_marks()

        if item == 'bracket_selection':
            self.bracket_selection_enabled = value

    def on_keypress(self, controller, keyval, keycode, state):
        if self.document.autocomplete.is_active: return False

        modifiers = Gtk.accelerator_get_default_mod_mask()

        if self.source_buffer.get_has_selection():
            if keyval == Gdk.keyval_from_name('backslash'):
                return self.bracket_selection('\\')
            if keyval == Gdk.keyval_from_name('bracketleft'):
                return self.bracket_selection('[')
            if keyval == Gdk.keyval_from_name('braceleft'):
                return self.bracket_selection('{')
            if keyval == Gdk.keyval_from_name('parenleft'):
                return self.bracket_selection('(')
        else:
            if keyval == Gdk.keyval_from_name('bracketleft'):
                return self.autoclose_brackets('[')
            if keyval == Gdk.keyval_from_name('braceleft'):
                return self.autoclose_brackets('{')
            if keyval == Gdk.keyval_from_name('parenleft'):
                return self.autoclose_brackets('(')

            if keyval == Gdk.keyval_from_name('bracketright'):
                return self.handle_autoclosing_bracket_overwrite(']')
            if keyval == Gdk.keyval_from_name('braceright'):
                return self.handle_autoclosing_bracket_overwrite('}')
            if keyval == Gdk.keyval_from_name('parenright'):
                return self.handle_autoclosing_bracket_overwrite(')')
            if keyval == Gdk.keyval_from_name('backslash'):
                return self.handle_autoclosing_bracket_overwrite('\\')

        return False

    def on_cursor_position_changed(self, document):
        self.reconsider_completion_marks()

    def on_buffer_changed(self, document):
        self.reconsider_completion_marks()

    def bracket_selection(self, char):
        if not self.bracket_selection_enabled: return False

        # if backslash or opening brackets are typed, don't replace selected text
        # but put a backslash or brackets around it.

        bounds = self.source_buffer.get_selection_bounds()
        closing_char = {'[': ']', '{': '}', '(': ')', '\\': ''}[char]
        if self.document.get_chars_at_iter(bounds[0], -1) == '\\' and char in ['[', '{', '(']:
            closing_char = '\\' + closing_char
        offset_start = bounds[0].get_offset()
        text = char + self.document.get_selected_text() + closing_char

        self.source_buffer.begin_user_action()
        self.source_buffer.delete_selection(True, True)
        self.source_buffer.insert_at_cursor(text)
        start_iter = self.source_buffer.get_iter_at_offset(offset_start + 1)
        end_iter = self.source_buffer.get_iter_at_offset(offset_start + len(text) - len(closing_char))
        self.source_buffer.select_range(start_iter, end_iter)
        self.source_buffer.end_user_action()
        return True

    def autoclose_brackets(self, char):
        if not self.autoclose_enabled: return False

        closing_char = {'[': ']', '{': '}', '(': ')'}[char]
        if self.document.get_chars_at_cursor(-1) == '\\':
            closing_char = '\\' + closing_char

        self.source_buffer.begin_user_action()
        self.source_buffer.insert_at_cursor(char + closing_char)
        self.source_buffer.end_user_action()

        insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        insert_iter.backward_chars(len(closing_char))
        self.source_buffer.place_cursor(insert_iter)

        self.add_completion_marks(insert_iter, len(closing_char), len(closing_char))

        return True

    def add_completion_marks(self, insert_iter, len_before, len_after):
        # marks are added to the text buffer, to signal that a completion took place
        # these are remove whenever the cursor moves outside the bracketed area

        start_iter = insert_iter.copy()
        start_iter.backward_chars(len_before)
        start_mark = self.source_buffer.create_mark('brackets_autoclose_start_' + str(ServiceLocator.get_increment('brackets_autoclose_start')), start_iter, True)

        end_iter = insert_iter.copy()
        end_iter.forward_chars(len_after)
        end_mark = self.source_buffer.create_mark('brackets_autoclose_end_' + str(ServiceLocator.get_increment('brackets_autoclose_end')), end_iter, True)

        self.completion_marks.append([start_mark, end_mark])

    def reconsider_completion_marks(self):
        # remove completion marks when the cursor is outside the bracketed area.

        completion_marks = list()

        for marks in self.completion_marks:
            start_mark, end_mark = marks
            start_iter = self.source_buffer.get_iter_at_mark(start_mark)
            end_iter = self.source_buffer.get_iter_at_mark(end_mark)
            insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())

            if self.autoclose_enabled and start_iter.get_offset() < insert_iter.get_offset() and end_iter.get_offset() > insert_iter.get_offset():
                completion_marks.append([start_mark, end_mark])
            else:
                self.source_buffer.delete_mark(start_mark)
                self.source_buffer.delete_mark(end_mark)

        self.completion_marks = completion_marks

    def handle_autoclosing_bracket_overwrite(self, char):
        # if there's a mark indicating that a completion took place, closing brackets
        # are just skipped over when they are typed and a similar bracket is already present
        # at the cursor.

        if not self.document.get_chars_at_cursor(1) == char: return False

        if char == '\\':
            insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
            insert_iter.forward_chars(2)
            for mark in insert_iter.get_marks():
                if mark != None and mark.get_name() != None and mark.get_name().startswith('brackets_autoclose_end_'):
                    self.source_buffer.begin_user_action()
                    insert_iter.backward_chars(1)
                    self.source_buffer.place_cursor(insert_iter)
                    self.source_buffer.end_user_action()
                    self.reconsider_completion_marks()
                    return True
        else:
            insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
            insert_iter.forward_chars(1)
            for mark in insert_iter.get_marks():
                if mark != None and mark.get_name() != None and mark.get_name().startswith('brackets_autoclose_end_'):
                    self.source_buffer.begin_user_action()
                    self.source_buffer.place_cursor(insert_iter)
                    self.source_buffer.end_user_action()
                    self.reconsider_completion_marks()
                    return True

        return False


