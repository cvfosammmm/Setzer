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
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Gtk

from setzer.app.service_locator import ServiceLocator


class ModeBeginEnd(object):

    def __init__(self, autocomplete, word_offset, word_len):
        self.autocomplete = autocomplete
        self.will_show = False

        self.last_tabbed_command = None
        self.current_word = ""
        self.source_buffer = self.autocomplete.content.source_buffer
        self.delete_marks()
        start_iter = self.source_buffer.get_iter_at_offset(word_offset)
        end_iter = self.source_buffer.get_iter_at_offset(word_offset + word_len)
        self.source_buffer.add_mark(self.autocomplete.mark_start, start_iter)
        self.source_buffer.add_mark(self.autocomplete.mark_end, end_iter)

        matching_env_offset = self.get_matching_begin_end_offset(word_offset)
        if matching_env_offset != None:
            self.has_matching_block = True
            matching_start_iter = self.source_buffer.get_iter_at_offset(matching_env_offset)
            matching_end_iter = self.source_buffer.get_iter_at_offset(matching_env_offset + word_len)
            self.source_buffer.add_mark(self.autocomplete.matching_mark_start, matching_start_iter)
            self.source_buffer.add_mark(self.autocomplete.matching_mark_end, matching_end_iter)
        else:
            self.has_matching_block = False

    def get_matching_begin_end_offset(self, orig_offset):
        blocks = self.autocomplete.document.get_blocks()
        for block in blocks:
            if block[0] == orig_offset - 7:
                return None if block[1] == None else block[1] + 5
            elif block[1] == orig_offset - 5:
                return None if block[0] == None else block[0] + 7
        return None

    def on_insert_text(self, buffer, location_iter, text, text_length):
        location_offset = location_iter.get_offset()
        start_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.mark_start).get_offset()
        end_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.mark_end).get_offset()
        if location_offset >= start_offset and location_offset <= end_offset:
            self.source_buffer.begin_user_action()
            GLib.idle_add(self.update_matching_block)

    def on_delete_range(self, buffer, start_iter, end_iter):
        delete_start_offset = start_iter.get_offset()
        delete_end_offset = end_iter.get_offset()
        start_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.mark_start).get_offset()
        end_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.mark_end).get_offset()
        if delete_start_offset >= start_offset and delete_end_offset <= end_offset:
            self.source_buffer.begin_user_action()
            GLib.idle_add(self.update_matching_block)
        elif delete_start_offset >= start_offset and delete_start_offset <= end_offset:
            self.cancel()
        elif delete_end_offset >= start_offset and delete_end_offset <= end_offset:
            self.cancel()

    def on_buffer_changed(self):
        self.update()

    def on_cursor_changed(self):
        self.update()

    def on_keypress(self, event):
        ''' returns whether the keypress has been handled. '''

        modifiers = Gtk.accelerator_get_default_mod_mask()

        tab_keyvals = [Gdk.keyval_from_name('Tab'), Gdk.keyval_from_name('ISO_Left_Tab')]
        if event.keyval in tab_keyvals:
            if event.state & modifiers == 0:
                return self.on_tab_press()

        if not self.autocomplete.is_visible():
            return False

        if event.keyval == Gdk.keyval_from_name('Down'):
            if event.state & modifiers == 0:
                self.autocomplete.view.select_next()
                return True

        if event.keyval == Gdk.keyval_from_name('Up'):
            if event.state & modifiers == 0:
                self.autocomplete.view.select_previous()
                return True

        if event.keyval == Gdk.keyval_from_name('Escape'):
            if event.state & modifiers == 0:
                self.cancel()
                return True

        if event.keyval == Gdk.keyval_from_name('Return'):
            if event.state & modifiers == 0:
                self.submit()
                return True

        return False

    def update_matching_block(self):
        if not self.autocomplete.mark_start.get_deleted() and not self.autocomplete.mark_end.get_deleted() and not self.autocomplete.matching_mark_start.get_deleted() and not self.autocomplete.matching_mark_end.get_deleted():
            start_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.mark_start).get_offset()
            start_iter = self.source_buffer.get_iter_at_offset(start_offset)
            end_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.mark_end).get_offset()
            end_iter = self.source_buffer.get_iter_at_offset(end_offset)
            full_word = self.source_buffer.get_text(start_iter, end_iter, False)
            start_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.matching_mark_start).get_offset()
            end_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.matching_mark_end).get_offset()
            start_iter = self.source_buffer.get_iter_at_offset(start_offset)
            end_iter = self.source_buffer.get_iter_at_offset(end_offset)
            matching_word = self.source_buffer.get_text(start_iter, end_iter, False)
            if matching_word != full_word:
                self.autocomplete.content.replace_range_no_user_action(start_iter, end_iter, full_word, indent_lines=False, select_dot=False)
        self.source_buffer.end_user_action()

    def on_tab_press(self):
        if not self.autocomplete.is_visible():
            return False

        if len(self.autocomplete.items) == 0:
            return False
        elif len(self.autocomplete.items) == 1:
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
                    self.autocomplete.content.insert_text_at_cursor(text, indent_lines=False, select_dot=False)
                    self.autocomplete.content.scroll_cursor_onscreen()
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
                        self.autocomplete.content.insert_text_at_cursor(text, indent_lines=False, select_dot=False)
                        self.autocomplete.content.scroll_cursor_onscreen()
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
        line = self.autocomplete.content.get_line_at_cursor()
        offset = self.autocomplete.content.get_cursor_line_offset()
        line = line[:offset] + '%•%' + line[offset:]
        match = ServiceLocator.get_regex_object(r'.*\\(begin|end)\{((?:[^\{\[\(])*)%•%((?:[^\{\[\(])*)\}.*').match(line)
        if not match:
            self.cancel()
            return

        if self.autocomplete.matching_mark_start.get_deleted() or self.autocomplete.matching_mark_end.get_deleted():
            self.has_matching_block = False

        cursor_offset = self.autocomplete.content.get_cursor_offset()
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
        if len(self.autocomplete.items) == 1 and len(self.current_word) == len(self.autocomplete.items[0]['command']):
            self.will_show = False
        else:
            items_cond = len(self.autocomplete.items) > 0 and len(self.current_word) != len(self.autocomplete.items[0]['command'])
            self.will_show = self.will_show or (self.autocomplete.is_active() and items_cond)
        self.autocomplete.populate(len(self.current_word))
        self.autocomplete.view.update_position()
        self.autocomplete.view.update_visibility()
        self.autocomplete.view.update_margins()

    def get_items(self, word=None):
        if word == None:
            word = self.current_word
        return self.autocomplete.provider.get_begin_end_items(word, self.last_tabbed_command)

    def get_offset(self):
        self.update_current_word()
        return len(self.current_word)

    def update_current_word(self):
        cursor_offset = self.autocomplete.content.get_cursor_offset()
        start_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.mark_start).get_offset()
        start_iter = self.source_buffer.get_iter_at_offset(start_offset)
        cursor_iter = self.source_buffer.get_iter_at_offset(cursor_offset)
        current_word = self.source_buffer.get_text(start_iter, cursor_iter, False)
        if current_word != self.current_word:
            self.current_word = current_word

    def submit(self):
        row = self.autocomplete.view.list.get_selected_row()
        text = row.get_child().command['command']

        start_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.mark_start).get_offset()
        end_offset = self.source_buffer.get_iter_at_mark(self.autocomplete.mark_end).get_offset()
        self.autocomplete.content.replace_range_by_offset_and_length(start_offset, end_offset - start_offset, text, indent_lines=False, select_dot=False)

        self.will_show = False
        self.update()

    def cancel(self):
        self.delete_marks()
        self.autocomplete.end_mode()

    def delete_marks(self):
        if not self.autocomplete.mark_start.get_deleted():
            self.source_buffer.delete_mark(self.autocomplete.mark_start)
        if not self.autocomplete.mark_end.get_deleted():
            self.source_buffer.delete_mark(self.autocomplete.mark_end)
        if not self.autocomplete.matching_mark_start.get_deleted():
            self.source_buffer.delete_mark(self.autocomplete.matching_mark_start)
        if not self.autocomplete.matching_mark_end.get_deleted():
            self.source_buffer.delete_mark(self.autocomplete.matching_mark_end)

    def is_active(self):
        return True


