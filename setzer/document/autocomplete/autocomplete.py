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

import re, os.path

import setzer.document.autocomplete.autocomplete_controller as autocomplete_controller
import setzer.document.autocomplete.autocomplete_widget as autocomplete_widget
from setzer.app.latex_db import LaTeXDB
from setzer.app.service_locator import ServiceLocator


class Autocomplete(object):

    def __init__(self, document):
        self.document = document
        self.source_buffer = document.source_buffer

        self.is_active = False
        self.current_word_offset = None
        self.current_word = None
        self.items = []
        self.last_tabbed_item = None
        self.first_item_index = None
        self.selected_item_index = None

        self.cursor_unchanged_after_autoclosing_bracket = False

        self.controller = autocomplete_controller.AutocompleteController(self, document)
        self.widget = autocomplete_widget.AutocompleteWidget(self)

    def activate_if_possible(self):
        # Triggered on tab, if ac is inactive,
        # also when text is inserted, if it is a single character.

        # Tries to match a backslash followed by letters from the
        # last backslash before the cursor to the cursor.
        # Then updates items from that match. If there are not at
        # least 2 matching commands, the activation is reversed.
        # So it should not return with an activation if there is
        # nothing to complete.

        insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        line_before_cursor = self.document.get_line(insert_iter.get_line())[:insert_iter.get_line_offset()]
        matching_result = re.search(r'\\[a-zA-Z]+\Z', line_before_cursor)
        if matching_result:
            self.current_word_offset = insert_iter.get_offset() - len(line_before_cursor) + matching_result.start()
            self.is_active = True
            self.update_suggestions()

    def deactivate_if_necessary(self):
        # Deactivates autocomplete if certain invariants don't hold
        # The cursor must be on the same line as the starting point
        # and it must come after it on that line.

        start_iter = self.source_buffer.get_iter_at_offset(self.current_word_offset)
        insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        if start_iter.get_line() != insert_iter.get_line() or start_iter.get_offset() >= insert_iter.get_offset():
            self.deactivate()

    def deactivate(self):
        self.is_active = False

        self.current_word_offset = None
        self.current_word = None
        self.items = []
        self.last_tabbed_item = None
        self.first_item_index = None
        self.selected_item_index = None

    def update_suggestions(self):
        # Placeholders are not considered as such, so matching is literal.

        if not self.is_active: return

        insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        line_before_cursor = self.document.get_line(insert_iter.get_line())[:insert_iter.get_line_offset()]
        line_offset = self.source_buffer.get_iter_at_line(insert_iter.get_line())[1].get_offset()

        self.current_word = line_before_cursor[self.current_word_offset - line_offset:]
        self.items = LaTeXDB.get_items(self.current_word, self.last_tabbed_item)

        if len(self.items) > 0:
            self.first_item_index = 0
            self.selected_item_index = 0
        else:
            self.deactivate()

    def select_next(self):
        self.selected_item_index = (self.selected_item_index + 1) % len(self.items)
        self.update_first_item_index()

    def select_previous(self):
        self.selected_item_index = (self.selected_item_index - 1) % len(self.items)
        self.update_first_item_index()

    def update_first_item_index(self):
        if self.selected_item_index < self.first_item_index:
            self.first_item_index = self.selected_item_index
        elif self.selected_item_index >= self.first_item_index + 5:
            self.first_item_index = self.selected_item_index - 4

    def tab(self):
        # If the selected item matches the beginning of the end of the
        # current line in the buffer in full, just like on submit,
        # the cursor is moved to the end of the match.
        # Otherwise we only consider the longest common prefix of the
        # items that adds at least one character. For example if we
        # have items "abc" and "abd" and the cursor is after "a", we
        # consider "ab". If the cursor is after "b", we consider "abc".
        # Now we move the cursor if the prefix matches the buffer exactly
        # (including placeholders). Otherwise we add the prefix to the
        # buffer.

        if self.items == None or len(self.items) == 0: return
        if self.selected_item_index == None: return

        result = self.match_current_command_with_buffer()
        if result != None:
            start, end = result
            self.move_cursor_to_offset(end)
            self.deactivate()
        else:
            command = self.items[self.selected_item_index]['command']
            matching_prefix = command[:len(self.current_word) + 1]
            matching_items = [item for item in self.items if item['command'].startswith(matching_prefix)]
            lcp = os.path.commonprefix([item['command'] for item in matching_items])
            matching_result = re.match(re.escape(lcp), self.document.get_line_after_offset(self.current_word_offset))
            if matching_result:
                self.last_tabbed_item = self.items[self.selected_item_index]['command']
                self.move_cursor_to_offset(self.current_word_offset + len(lcp))
            else:
                self.last_tabbed_item = self.items[self.selected_item_index]['command']
                self.replace_current_word_in_buffer(lcp)
                self.document.scroll_cursor_onscreen()
                if lcp == command:
                    self.deactivate()

    def submit(self):
        # If the selected item matches with the beginning of the end
        # of the current line in the buffer in full, move the cursor
        # to the end of the match.
        # Placeholder match any sequence of characters.
        # Otherwise we add the command to the buffer.

        if self.items == None or len(self.items) == 0: return
        if self.selected_item_index == None: return

        result = self.match_current_command_with_buffer()
        if result != None:
            start, end = result
            self.move_cursor_to_offset(end)
        else:
            command = self.items[self.selected_item_index]['command']
            self.replace_current_word_in_buffer(command)
            self.document.select_first_dot_around_cursor(offset_before=len(command), offset_after=0)
            self.document.scroll_cursor_onscreen()
        self.deactivate()

    def match_current_command_with_buffer(self):
        command = self.items[self.selected_item_index]['command']
        matching_result = re.match(re.escape(command).replace('•', '.*'), self.document.get_line_after_offset(self.current_word_offset))
        if matching_result:
            return (self.current_word_offset, self.current_word_offset + matching_result.end())
        else:
            return None

    def move_cursor_to_offset(self, offset):
        new_cursor_iter = self.source_buffer.get_iter_at_offset(offset)
        self.source_buffer.place_cursor(new_cursor_iter)
        self.document.scroll_cursor_onscreen()

    def replace_current_word_in_buffer(self, text):
        start_iter = self.source_buffer.get_iter_at_offset(self.current_word_offset)
        insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())

        text = text[len(self.current_word):]
        text = self.document.replace_tabs_with_spaces_if_set(text)
        text = self.document.indent_text_with_whitespace_at_iter(text, start_iter)

        self.source_buffer.begin_user_action()
        self.source_buffer.insert_at_cursor(text)
        self.source_buffer.end_user_action()

    def autoclose_brackets(self, char):
        closing_char = {'[': ']', '{': '}', '(': ')'}[char]
        start_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        end_iter = start_iter.copy()
        end_iter.backward_char()
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
        self.cursor_unchanged_after_autoclosing_bracket = True

    def handle_autoclosing_bracket_overwrite(self, char):
        if not self.cursor_unchanged_after_autoclosing_bracket: return False
        if not self.document.get_chars_at_cursor(1) == char: return False

        insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        insert_iter.forward_chars(1)
        self.source_buffer.begin_user_action()
        self.source_buffer.place_cursor(insert_iter)
        self.source_buffer.end_user_action()
        if char == '\\':
            self.cursor_unchanged_after_autoclosing_bracket = True

    def jump_over_closing_bracket(self):
        chars_at_cursor = self.document.get_chars_at_cursor(2)
        if chars_at_cursor in ['\\}', '\\)', '\\]']: forward_chars = 2
        elif chars_at_cursor[0] in ['}', ')', ']']: forward_chars = 1
        else: forward_chars = 0
        if forward_chars > 0:
            insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
            insert_iter.forward_chars(forward_chars)
            self.source_buffer.place_cursor(insert_iter)
            return True
        else:
            return False

    def placeholder_selected(self):
        return self.document.get_selected_text() == '•'

    def select_next_placeholder(self):
        if self.placeholder_selected():
            insert = self.source_buffer.get_selection_bounds()[1]
        else:
            insert = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())

        limit_iter = insert.copy()
        limit_iter.forward_lines(5)
        limit_iter.backward_chars(1)
        result = insert.forward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
        if result != None:
            self.source_buffer.select_range(result[0], result[1])
            self.document.scroll_cursor_onscreen()
            return True

    def select_previous_placeholder(self):
        if self.placeholder_selected():
            insert = self.source_buffer.get_selection_bounds()[0]
        else:
            insert = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())

        limit_iter = insert.copy()
        limit_iter.backward_lines(5)
        result = insert.backward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
        if result != None:
            self.source_buffer.select_range(result[0], result[1])
            self.document.scroll_cursor_onscreen()
            return True

    def handle_keypress_inside_begin_or_end(self, keyval):
        buffer = self.source_buffer
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        line = self.document.get_line(insert_iter.get_line())
        offset = insert_iter.get_line_offset()
        cursor_offset = insert_iter.get_offset()
        line = line[:offset] + '%•%' + line[offset:]
        match_begin_end = ServiceLocator.get_regex_object(r'.*\\(begin|end)\{((?:[^\{\[\(])*)%•%((?:[^\{\[\(])*)\}').match(line)
        if match_begin_end == None: return False
        if keyval == Gdk.keyval_from_name('BackSpace') and len(match_begin_end.group(2)) == 0: return False
        if keyval == Gdk.keyval_from_name('Delete') and len(match_begin_end.group(3)) == 0: return False

        orig_offset = cursor_offset - insert_iter.get_line_offset() + match_begin_end.start()
        offset = None
        for block in self.document.parser.symbols['blocks']:
            if block[0] == orig_offset:
                if block[1] == None:
                    return False
                else:
                    offset = block[1] + 5 + len(match_begin_end.group(2))
                    break
            elif block[1] == orig_offset:
                if block[0] == None:
                    return False
                else:
                    offset = block[0] + 7 + len(match_begin_end.group(2))
                    break
        if offset == None: return False

        buffer.begin_user_action()
        if keyval == Gdk.keyval_from_name('asterisk'):
            if cursor_offset < offset: offset += 1
            buffer.insert_at_cursor('*')
            buffer.insert(buffer.get_iter_at_offset(offset), '*')
        elif keyval == Gdk.keyval_from_name('BackSpace'):
            if cursor_offset < offset: offset -= 1
            buffer.delete(buffer.get_iter_at_offset(cursor_offset - 1), buffer.get_iter_at_offset(cursor_offset))
            buffer.delete(buffer.get_iter_at_offset(offset - 1), buffer.get_iter_at_offset(offset))
        elif keyval == Gdk.keyval_from_name('Delete'):
            if cursor_offset < offset: offset -= 1
            buffer.delete(buffer.get_iter_at_offset(cursor_offset), buffer.get_iter_at_offset(cursor_offset + 1))
            buffer.delete(buffer.get_iter_at_offset(offset), buffer.get_iter_at_offset(offset + 1))
        else:
            if cursor_offset < offset: offset += 1
            char = Gdk.keyval_name(keyval)
            buffer.insert_at_cursor(char)
            buffer.insert(buffer.get_iter_at_offset(offset), char)
        buffer.end_user_action()

        return True


