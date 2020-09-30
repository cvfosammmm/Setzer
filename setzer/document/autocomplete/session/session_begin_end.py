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
from gi.repository import Gtk

from setzer.app.service_locator import ServiceLocator


class SessionBeginEnd(object):

    def __init__(self, autocomplete, word_offset, word_len):
        self.autocomplete = autocomplete
        self.will_show = True

        self.last_tabbed_command = None
        self.current_word = ""

        self.source_buffer = self.autocomplete.document.get_buffer()
        start_iter = self.source_buffer.get_iter_at_offset(word_offset)
        end_iter = self.source_buffer.get_iter_at_offset(word_offset + word_len)
        self.source_buffer.add_mark(self.autocomplete.mark_start, start_iter)
        self.source_buffer.add_mark(self.autocomplete.mark_end, end_iter)

    def on_tab_press(self):
        if not self.autocomplete.is_visible():
            return False

        if len(self.autocomplete.items) == 1:
            self.submit()
            return True
        else:
            self.update_current_word()
            i = self.get_number_of_matching_letters_on_tabpress(self.current_word, 0)

            command = self.autocomplete.view.list.get_selected_row().get_child().command
            if len(command['command']) == len(self.current_word) + i:
                self.last_tabbed_command = None
                self.submit()
                return True
            else:
                if i >= 1:
                    text = (command['command'])[len(self.current_word):len(self.current_word) + i]
                    self.last_tabbed_command = command['command'][1:]
                    self.autocomplete.document.insert_text_at_cursor(text, indent_lines=False, scroll=True, select_dot=False)
                    return True
                else:
                    current_word = (command['command'])[:len(self.current_word) + 1]
                    i = self.get_number_of_matching_letters_on_tabpress(current_word, 0)

                    if len(command['command']) == len(current_word) + i:
                        self.last_tabbed_command = None
                        self.submit()
                        return True
                    else:
                        text = (command['command'])[len(self.current_word):len(current_word) + i]
                        self.last_tabbed_command = command['command']
                        self.autocomplete.document.insert_text_at_cursor(text, indent_lines=False, scroll=True, select_dot=False)
                        return True

    def get_number_of_matching_letters_on_tabpress(self, current_word, offset):
        items = self.get_items(current_word)
        i = offset
        letter_ok = True
        while letter_ok and i < 100:
            testletter = None
            for item in items:
                item['command'] = item['command']
                letter = item['command'][len(current_word) + i:len(current_word) + i + 1].lower()
                if testletter == None:
                    testletter = letter
                if testletter != letter or len(letter) == 0:
                    letter_ok = False
                    i -= 1
                    break
            i += 1
        return i

    def update(self):
        if self.autocomplete.mark_start.get_deleted() or self.autocomplete.mark_end.get_deleted():
            self.cancel()
            return

        cursor_offset = self.autocomplete.document.get_cursor_offset()
        start_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.mark_start).get_offset()
        end_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.mark_end).get_offset()
        if cursor_offset < start_offset:
            self.cancel()
            return
        if cursor_offset > end_offset:
            self.cancel()
            return

        self.update_current_word()
        self.autocomplete.items = self.get_items()
        if len(self.autocomplete.items) > 0:
            self.autocomplete.populate(len(self.current_word))
            self.autocomplete.update_visibility()
        else:
            self.cancel()
            return

    def get_items(self, word=None):
        if word == None:
            word = self.current_word
        return self.autocomplete.provider.get_begin_end_items(word, self.last_tabbed_command)

    def get_offset(self):
        self.update_current_word()
        return len(self.current_word)

    def update_current_word(self):
        cursor_offset = self.autocomplete.document.get_cursor_offset()
        start_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.mark_start).get_offset()
        start_iter = self.source_buffer.get_iter_at_offset(start_offset)
        cursor_iter = self.source_buffer.get_iter_at_offset(cursor_offset)
        self.current_word = self.source_buffer.get_text(start_iter, cursor_iter, False)

    def submit(self):
        row = self.autocomplete.view.list.get_selected_row()
        text = row.get_child().command['command']
        start_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.mark_start).get_offset()
        end_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.mark_end).get_offset()
        self.autocomplete.document.replace_range(start_offset, end_offset - start_offset, text, indent_lines=False, select_dot=False)
        self.delete_marks()
        self.autocomplete.end_session()

    def cancel(self):
        self.delete_marks()
        self.autocomplete.end_session()

    def delete_marks(self):
        if not self.autocomplete.mark_start.get_deleted():
            self.source_buffer.delete_mark(self.autocomplete.mark_start)
        if not self.autocomplete.mark_end.get_deleted():
            self.source_buffer.delete_mark(self.autocomplete.mark_end)

    def is_active(self):
        return True


