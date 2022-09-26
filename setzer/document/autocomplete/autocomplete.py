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
from gi.repository import Gtk
from gi.repository import Gdk

import time

import setzer.document.autocomplete.autocomplete_viewgtk as view
from setzer.app.service_locator import ServiceLocator
import setzer.helpers.timer as timer


class Autocomplete(object):

    def __init__(self, document, document_view):
        self.document = document
        self.content = document.content
        self.document_view = document_view
        self.source_buffer = self.content.source_buffer

        self.view = view.DocumentAutocompleteView(self)
        self.start_offset = 0
        self.end_offset = 0
        self.last_tabbed_command = None
        self.waiting_for_block_update = False
        self.cursor_unchanged_after_autoclosing_bracket = False

        self.provider = ServiceLocator.get_autocomplete_provider()

        self.state = dict()
        self.state['position'] = 'outside'
        self.state['is_active'] = False

        self.items = list()

        self.content.connect('text_inserted', self.on_text_inserted)
        self.content.connect('text_deleted', self.on_text_deleted)
        self.content.connect('buffer_changed', self.on_buffer_changed)
        self.content.connect('cursor_changed', self.on_cursor_changed)

    def on_text_inserted(self, content, parameter):
        buffer, location_iter, text, text_length = parameter

        if self.state['position'] in ['begin_end_completable', 'begin_end_not_completable']:
            location_offset = location_iter.get_offset()

            if self.matching_env_offset == None: return
            if location_offset < self.start_offset or location_offset > self.end_offset: return

            start_iter = self.source_buffer.get_iter_at_offset(self.start_offset)
            end_iter = self.source_buffer.get_iter_at_offset(self.end_offset)
            full_word = self.source_buffer.get_text(start_iter, end_iter, False)[:location_offset - self.start_offset] + text + self.source_buffer.get_text(start_iter, end_iter, False)[location_offset - self.start_offset:]
            offset = self.start_offset + self.matching_env_offset
            word_len = self.end_offset - self.start_offset
            self.end_offset += len(text)
            if self.matching_env_offset >= 0:
                self.matching_env_offset += len(text)

            self.update_matching_block(offset, word_len, full_word)

    def on_text_deleted(self, content, parameter):
        buffer, start_iter, end_iter = parameter

        if self.state['position'] in ['begin_end_completable', 'begin_end_not_completable']:
            delete_start_offset = start_iter.get_offset()
            delete_end_offset = end_iter.get_offset()

            if self.matching_env_offset == None: return
            if delete_start_offset < self.start_offset or delete_end_offset > self.end_offset: return

            start_iter = self.source_buffer.get_iter_at_offset(self.start_offset)
            end_iter = self.source_buffer.get_iter_at_offset(self.end_offset)
            full_word = self.source_buffer.get_text(start_iter, end_iter, False)[:delete_start_offset - self.start_offset] + self.source_buffer.get_text(start_iter, end_iter, False)[delete_end_offset - self.start_offset:]
            offset = self.start_offset + self.matching_env_offset
            word_len = self.end_offset - self.start_offset
            self.end_offset -= delete_end_offset - delete_start_offset
            if self.matching_env_offset >= 0:
                self.matching_env_offset -= delete_end_offset - delete_start_offset

            self.update_matching_block(offset, word_len, full_word)

    def on_buffer_changed(self, content, buffer):
        if self.waiting_for_block_update: return

        self.update_state_position()
        self.activate_if_possible()
        self.update_items()
        self.update_view()

    def on_cursor_changed(self, content):
        if self.waiting_for_block_update: return

        self.cursor_unchanged_after_autoclosing_bracket = False

        self.update_state_position()
        self.update_items()
        self.update_view()

    def on_keypress(self, event):
        ''' returns whether the keypress has been handled. '''

        modifiers = Gtk.accelerator_get_default_mod_mask()

        if self.is_visible():
            if event.keyval == Gdk.keyval_from_name('Down'):
                if event.state & modifiers == 0:
                    self.view.select_next()
                    return True

            if event.keyval == Gdk.keyval_from_name('Up'):
                if event.state & modifiers == 0:
                    self.view.select_previous()
                    return True

        if self.is_active():
            if event.keyval == Gdk.keyval_from_name('Escape'):
                if event.state & modifiers == 0:
                    self.deactivate()
                    return True

            if event.keyval == Gdk.keyval_from_name('Return'):
                if event.state & modifiers == 0:
                    self.submit()
                    return True

        if not self.is_active():
            left_bracket_vals = [Gdk.keyval_from_name('parenleft'), Gdk.keyval_from_name('bracketleft'), Gdk.keyval_from_name('braceleft')]
            right_bracket_vals = [Gdk.keyval_from_name('parenright'), Gdk.keyval_from_name('bracketright'), Gdk.keyval_from_name('braceright'), Gdk.keyval_from_name('backslash')]
            if event.keyval in left_bracket_vals:
                if event.keyval == Gdk.keyval_from_name('bracketleft'):
                    self.autoclose_brackets('[')
                if event.keyval == Gdk.keyval_from_name('braceleft'):
                    self.autoclose_brackets('{')
                if event.keyval == Gdk.keyval_from_name('parenleft'):
                    self.autoclose_brackets('(')
                return True

            if self.cursor_unchanged_after_autoclosing_bracket and event.keyval in right_bracket_vals:
                if event.keyval == Gdk.keyval_from_name('bracketright'):
                    self.handle_autoclosing_bracket_overwrite(']')
                if event.keyval == Gdk.keyval_from_name('braceright'):
                    self.handle_autoclosing_bracket_overwrite('}')
                if event.keyval == Gdk.keyval_from_name('parenright'):
                    self.handle_autoclosing_bracket_overwrite(')')
                if event.keyval == Gdk.keyval_from_name('backslash'):
                    self.handle_autoclosing_bracket_overwrite('\\')
                return True

        tab_keyvals = [Gdk.keyval_from_name('Tab'), Gdk.keyval_from_name('ISO_Left_Tab')]
        if event.keyval in tab_keyvals:
            if event.state & modifiers == 0:
                return self.on_tab_press()
            elif event.state & modifiers == Gdk.ModifierType.SHIFT_MASK:
                return self.on_shift_tab_press()

    def update_matching_block(self, offset, word_len, full_word):
        self.waiting_for_block_update = True

        if offset == None or word_len == None: return

        self.source_buffer.begin_user_action()
        mark1 = Gtk.TextMark.new('mark1-' + str(time.time()), True)
        mark2 = Gtk.TextMark.new('mark2-' + str(time.time()), False)
        start_iter = self.source_buffer.get_iter_at_offset(offset)
        end_iter = self.source_buffer.get_iter_at_offset(offset + word_len)
        self.source_buffer.add_mark(mark1, start_iter)
        self.source_buffer.add_mark(mark2, end_iter)
        GLib.idle_add(self.replace_text_between_marks, full_word, mark1, mark2)

    def replace_text_between_marks(self, text, mark1, mark2):
        self.waiting_for_block_update = False

        start_iter = self.source_buffer.get_iter_at_mark(mark1)
        end_iter = self.source_buffer.get_iter_at_mark(mark2)
        self.content.replace_range_no_user_action(start_iter, end_iter, text)
        self.source_buffer.delete_mark(mark1)
        self.source_buffer.delete_mark(mark2)
        self.source_buffer.end_user_action()

    def update_items(self):
        if self.state['position'] in ['begin_end_completable', 'begin_end_not_completable']:
            current_word = self.get_current_word()
            self.items = self.provider.get_begin_end_items(current_word, self.last_tabbed_command)
            self.populate(len(current_word))
        elif self.state['position'] == 'ends_completable_word':
            current_word = self.get_latex_command_at_cursor()
            self.items = self.provider.get_items_for_completion_window(current_word, self.last_tabbed_command)
            self.populate(len(current_word))

    def update_view(self):
        self.view.update_position()
        self.view.update_visibility()
        self.view.update_margins()

    def get_current_word(self):
        if self.state['position'] in ['begin_end_completable', 'begin_end_not_completable']:
            cursor_offset = self.content.get_cursor_offset()
            start_iter = self.source_buffer.get_iter_at_offset(self.start_offset)
            cursor_iter = self.source_buffer.get_iter_at_offset(cursor_offset)
            return self.source_buffer.get_text(start_iter, cursor_iter, False)
        elif self.state['position'] == 'ends_completable_word':
            return self.get_latex_command_at_cursor()
        else:
            return None

    def get_current_word_len(self):
        current_word = self.get_current_word()
        if current_word != None:
            return len(current_word)
        else:
            return 0

    def on_tab_press(self):
        if self.state['position'] in ['begin_end_completable', 'ends_completable_word'] and self.is_active():
            if len(self.items) == 1:
                self.submit()
                return True
            elif len(self.items) > 1:
                current_word = self.get_current_word()
                i = self.get_number_of_matching_letters_on_tabpress(current_word, 0)
                command = self.view.list.get_selected_row().get_child().command
                if len(command['command']) == len(current_word) + i:
                    self.last_tabbed_command = None
                    self.submit()
                    return True
                else:
                    if self.state['position'] == 'begin_end_completable':
                        if i >= 1:
                            text = (command['command'])[len(current_word):len(current_word) + i]
                            self.last_tabbed_command = command['command'][1:]
                            self.content.insert_text_at_cursor(text)
                            self.content.scroll_cursor_onscreen()
                            return True
                        else:
                            current_word_new = (command['command'])[:len(current_word) + 1]
                            i = self.get_number_of_matching_letters_on_tabpress(current_word_new, 0)

                            if len(command['command']) == len(current_word_new) + i:
                                self.last_tabbed_command = None
                                self.submit()
                                return True
                            else:
                                text = (command['command'])[len(current_word):len(current_word_new) + i]
                                self.last_tabbed_command = command['command']
                                self.content.insert_text_at_cursor(text)
                                self.content.scroll_cursor_onscreen()
                                return True
                    if self.state['position'] == 'ends_completable_word':
                        if i >= 1:
                            text = (command['command'])[:len(current_word) + i]
                            self.last_tabbed_command = command['command'][1:]
                            self.replace_latex_command_at_cursor(text, command['dotlabels'])
                            return True
                        else:
                            current_word_new = (command['command'])[:len(current_word) + 1]
                            i = self.get_number_of_matching_letters_on_tabpress(current_word_new, 0)

                            if len(command['command']) == len(current_word_new) + i:
                                self.last_tabbed_command = None
                                self.submit()
                                return True
                            else:
                                text = (command['command'])[:len(current_word_new) + i]
                                self.last_tabbed_command = command['command']
                                self.replace_latex_command_at_cursor(text, command['dotlabels'])
                                return True

        insert = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        insert.forward_chars(1)
        limit_iter = insert.copy()
        limit_iter.forward_lines(3)
        limit_iter.backward_chars(1)
        result = insert.forward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
        if result != None:
            self.source_buffer.place_cursor(result[0])
            self.source_buffer.select_range(result[0], result[1])
            self.content.scroll_cursor_onscreen()
            return True
        insert.backward_chars(1)
        result = insert.forward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
        if result != None:
            self.source_buffer.select_range(result[0], result[1])
            self.content.scroll_cursor_onscreen()
            return True

        chars_at_cursor = self.content.get_chars_at_cursor(2)
        if chars_at_cursor in ['\\}', '\\)', '\\]']:
            forward_chars = 2
        elif chars_at_cursor[0] in ['}', ')', ']']:
            forward_chars = 1
        else:
            forward_chars = 0

        if forward_chars > 0:
            insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
            insert_iter.forward_chars(forward_chars)
            self.source_buffer.place_cursor(insert_iter)

            while True:
                chars_at_cursor = self.content.get_chars_at_cursor(2)
                if chars_at_cursor in ['\\{', '\\(', '\\[']:
                    forward_chars = 2
                elif chars_at_cursor[0] in ['{', '(', '[']:
                    forward_chars = 1
                else:
                    forward_chars = 0
                if forward_chars > 0:
                    insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
                    insert_iter.forward_chars(forward_chars)
                    self.source_buffer.place_cursor(insert_iter)
                else:
                    break
            return True

        if self.state['position'] in ['begin_end_completable', 'ends_completable_word'] and not self.is_active():
            self.activate_if_possible()
            return self.is_active()

        return False

    def on_shift_tab_press(self):
        insert = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        limit_iter = insert.copy()
        limit_iter.backward_lines(3)
        result = insert.backward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
        if result != None:
            self.source_buffer.select_range(result[0], result[1])
            self.content.scroll_cursor_onscreen()
            return True

        insert.forward_chars(1)
        result = insert.backward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
        if result != None:
            self.source_buffer.select_range(result[0], result[1])
            self.content.scroll_cursor_onscreen()
            return True

    def cursor_at_latex_command_end(self):
        current_word = self.get_latex_command_at_cursor()
        if ServiceLocator.get_regex_object(r'\\(\w*(?:\*){0,1})').fullmatch(current_word):
            return self.content.cursor_ends_word()
        return False

    def cursor_inside_latex_command_or_at_end(self):
        current_word = self.get_latex_command_at_cursor()
        if ServiceLocator.get_regex_object(r'\\(\w*(?:\*){0,1})').fullmatch(current_word):
            return True
        return False

    def get_number_of_matching_letters_on_tabpress(self, current_word, offset):
        if self.state['position'] == 'begin_end_completable':
            items = self.provider.get_begin_end_items(current_word, self.last_tabbed_command)
        elif self.state['position'] == 'ends_completable_word':
            items = self.provider.get_items(current_word)
        else:
            return 0

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

    def autoclose_brackets(self, char):
        buffer = self.content.source_buffer

        closing_char = {'[': ']', '{': '}', '(': ')'}[char]
        if self.content.get_char_before_cursor() == '\\':
            closing_char = '\\' + closing_char

        buffer.begin_user_action()
        buffer.delete_selection(True, True)
        buffer.insert_at_cursor(char + closing_char)
        buffer.end_user_action()

        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        insert_iter.backward_char()
        if closing_char.startswith('\\'):
            insert_iter.backward_char()
        buffer.place_cursor(insert_iter)
        self.cursor_unchanged_after_autoclosing_bracket = True

    def handle_autoclosing_bracket_overwrite(self, char):
        char_at_cursor = self.content.get_chars_at_cursor(1)

        if char_at_cursor == char:
            self.content.overwrite_chars_at_cursor(char)
            if char != '\\':
                self.cursor_unchanged_after_autoclosing_bracket = False
        else:
            self.content.source_buffer.insert_at_cursor(char)

    def submit(self):
        if self.state['position'] == 'begin_end_completable' and self.is_active():
            row = self.view.list.get_selected_row()
            text = row.get_child().command['command']

            self.source_buffer.begin_user_action()
            start_iter = self.source_buffer.get_iter_at_offset(self.start_offset)
            end_iter = self.source_buffer.get_iter_at_offset(self.end_offset)
            self.content.replace_range_no_user_action(start_iter, end_iter, text)
            self.source_buffer.end_user_action()

        elif self.state['position'] == 'ends_completable_word' and self.is_active():
            row = self.view.list.get_selected_row()
            command = row.get_child().command
            if command['command'].startswith('\\begin'):
                self.insert_begin_end(command)
            else:
                self.insert_normal_command(command)

        self.deactivate()

    def insert_begin_end(self, command):
        text = command['command']
        insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        current_word = self.get_latex_command_at_cursor()
        start_iter = insert_iter.copy()
        start_iter.backward_chars(len(current_word))

        replace_previous_command_data = self.insert_begin_end_check_replace(insert_iter, text)
        if replace_previous_command_data[0]:
            self.insert_begin_end_replace(start_iter, insert_iter, replace_previous_command_data)
        else:
            self.replace_latex_command_at_cursor(text, command['dotlabels'], is_full_command=True)

    def insert_begin_end_check_replace(self, insert_iter, text):
        line_part = self.content.get_line(insert_iter.get_line())[insert_iter.get_line_offset():]
        line_regex = ServiceLocator.get_regex_object(r'(\w*(?:\*){0,1})\{([^\{\[\|\(]+)\}')
        line_match = line_regex.match(line_part)
        if line_match:
            document_text = self.content.get_text_after_offset(insert_iter.get_offset() + 1)
            if self.get_end_match_object(document_text, line_match.group(2)):
                return (line_match, text)
        return (None, text)

    def insert_begin_end_replace(self, start_iter_begin, insert_iter, replace_previous_command_data):
        text = replace_previous_command_data[1]
        match_object = replace_previous_command_data[0]

        self.source_buffer.begin_user_action()

        end_iter_begin = insert_iter.copy()
        end_iter_begin.forward_chars(match_object.end())
        start_iter_offset = start_iter_begin.get_offset()

        self.content.replace_range_no_user_action(start_iter_begin, end_iter_begin, text)

        dotindex = text.find('•')
        if dotindex > -1:
            start_iter_begin.backward_chars(abs(dotindex - len(text)))
            bound = start_iter_begin.copy()
            bound.forward_chars(1)
            self.source_buffer.select_range(start_iter_begin, bound)

        end_iter_offset = start_iter_offset + len(text)
        document_text = self.content.get_text_after_offset(end_iter_offset)
        environment_name = ServiceLocator.get_regex_object(r'(\w*(?:\*){0,1})\{([^\{\[\|\(]+)\}').match(match_object.group(0)).group(2)
        end_match_object = self.get_end_match_object(document_text, environment_name)

        if end_match_object != None:
            start_iter_begin = self.content.source_buffer.get_iter_at_offset(end_iter_offset)
            start_iter_end = start_iter_begin.copy()
            start_iter_end.forward_chars(end_match_object.start())
            end_iter_end = start_iter_begin.copy()
            end_iter_end.forward_chars(end_match_object.end())
            end_command = text.replace('\\begin', '\\end')
            end_command_bracket_position = end_command.find('}')
            if end_command_bracket_position:
                end_command = end_command[:end_command_bracket_position + 1]
            self.content.replace_range_no_user_action(start_iter_end, end_iter_end, end_command)

        self.source_buffer.end_user_action()

    def get_end_match_object(self, text, environment_name):
        count = 0
        end_match_object = None
        for match in ServiceLocator.get_regex_object(r'\\(begin|end)\{' + environment_name + r'\}').finditer(text):
            if match.group(1) == 'begin':
                count += 1
            elif match.group(1) == 'end':
                if count == 0:
                    end_match_object = match
                    break
                else:
                    count -= 1
        return end_match_object

    def insert_normal_command(self, command):
        text = command['command']

        replacement_pattern = self.get_replacement_pattern(text)
        if replacement_pattern == None:
            self.replace_latex_command_at_cursor(text, command['dotlabels'], is_full_command=True)
        else:
            command_regex = ServiceLocator.get_regex_object(r'.*' + replacement_pattern[1])
            if command_regex.match(text):
                self.insert_final_replace(text, replacement_pattern)
            else:
                self.replace_latex_command_at_cursor(text, command['dotlabels'], is_full_command=True)

    def get_replacement_pattern(self, command):
        buffer = self.content.source_buffer
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        line_part = self.content.get_line(insert_iter.get_line())[insert_iter.get_line_offset():]
        command_bracket_count = self.get_command_bracket_count(command)

        matches_group = list()
        line_regex = ServiceLocator.get_regex_object(r'((?:\\){0,1}\w*(?:\*){0,1})(?:\{([^\{\[\|\(]+)\}|\[([^\{\[\|\(\\]+)\]|\|([^\{\[\|\(\\]+)\||\(([^\{\[\|\(\\]+)\))*')
        line_match = line_regex.match(line_part)
        if line_match == None: return None
        if not line_regex.fullmatch(command): return None

        line_part = line_part[:line_match.end()]
        line_regex = ServiceLocator.get_regex_object(r'(\w*)|\{([^\{\[\|\(]+)\}|\[([^\{\[\|\(\\]+)\]|\|([^\{\[\|\(\\]+)\||\(([^\{\[\|\(\\]+)\)')
        bracket_count = 0
        command_regex_pattern = r'(\w*(?:\*){0,1})'
        for match in line_regex.finditer(line_part):
            if match.group(0).startswith('{') and bracket_count < command_bracket_count:
                command_regex_pattern += r'\{([^\{\[\|\(]+)\}'
                bracket_count += 1
            if match.group(0).startswith('[') and bracket_count < command_bracket_count:
                command_regex_pattern += r'\[([^\{\[\|\(]+)\]'
                bracket_count += 1
            if match.group(0).startswith('|') and bracket_count < command_bracket_count:
                command_regex_pattern += r'\|([^\{\[\|\(]+)\|'
                bracket_count += 1
            if match.group(0).startswith('(') and bracket_count < command_bracket_count:
                command_regex_pattern += r'\(([^\{\[\|\(]+)\)'
                bracket_count += 1
        line_match = ServiceLocator.get_regex_object(command_regex_pattern).match(line_part)
        if line_match == None: return None

        return (line_match, command_regex_pattern)

    def get_command_bracket_count(self, command):
        count = 0
        line_regex = ServiceLocator.get_regex_object(r'\{([^\{\[\|\(]+)\}|\[([^\{\[\|\(]+)\]|\|([^\{\[\|\(]+)\||\(([^\{\[\|\(]+)\)')
        for match in line_regex.finditer(command):
            count += 1
        return count

    def insert_final_replace(self, command, replacement_pattern):
        match_object = replacement_pattern[0]
        text = ''
        command_regex = ServiceLocator.get_regex_object(r'(?:^\\(\w+(?:\*){0,1}))|\{([^\{\[\|\(]+)\}|\[([^\{\[\|\(]+)\]|\|([^\{\[\|\(]+)\||\(([^\{\[\|\(]+)\)')
        comma_regex = ServiceLocator.get_regex_object(r'•(\,•)*')
        count = 1
        for match in command_regex.finditer(command):
            if match.group(0).startswith('\\'):
                text += '\\' + match.group(1)
            else:
                if match.group(0).startswith('{'):
                    inner_text = match.group(2)
                elif match.group(0).startswith('['):
                    inner_text = match.group(3)
                elif match.group(0).startswith('|'):
                    inner_text = match.group(4)
                elif match.group(0).startswith('('):
                    inner_text = match.group(5)
                if comma_regex.fullmatch(inner_text) and len(match_object.groups()) >= count:
                    for prev_text in match_object.group(count).split(','):
                        inner_text = inner_text.replace('•', prev_text, 1)
                if match.group(0).startswith('{'):
                    text += '{' + inner_text + '}'
                if match.group(0).startswith('['):
                    text += '[' + inner_text + ']'
                if match.group(0).startswith('|'):
                    text += '|' + inner_text + '|'
                if match.group(0).startswith('('):
                    text += '(' + inner_text + ')'
            count += 1

        current_word = self.get_latex_command_at_cursor()
        offset = self.content.get_cursor_offset() - len(current_word)
        length = len(current_word) + match_object.end()
        start_iter = self.source_buffer.get_iter_at_offset(offset)
        end_iter = self.source_buffer.get_iter_at_offset(offset + length)

        text = self.content.indent_text_with_whitespace_at_iter(text, start_iter)
        self.content.replace_range_and_select_dot(start_iter, end_iter, text)

    def activate_if_possible(self):
        if not self.is_active():
            if self.state['position'] in ['begin_end_completable', 'ends_completable_word']:
                self.state['is_active'] = True

            self.update_items()
            self.update_view()

    def deactivate(self):
        if self.is_active():
            self.state['is_active'] = False

            self.update_items()
            self.update_view()

    def is_active(self):
        return self.state['is_active']

    #@timer.timer
    def populate(self, offset):
        self.view.empty_list()
        for command in reversed(self.items):
            item = view.DocumentAutocompleteItem(command, offset)
            self.view.prepend(item)
        if len(self.items) > 0:
            self.view.select_first()

    def update_state_position(self):
        if self.cursor_inside_begin_or_end():
            if not self.source_buffer.get_has_selection() and self.cursor_ends_completable_environment_name():
                self.state['position'] = 'begin_end_completable'
            else:
                self.state['position'] = 'begin_end_not_completable'

            word_offset, word_len = self.get_begin_end_offset_word_len()
            self.start_offset = word_offset
            self.end_offset = word_offset + word_len
            self.matching_env_offset = self.get_matching_begin_end_offset(word_offset)

        elif not self.source_buffer.get_has_selection() and self.cursor_ends_completable_word():
            self.state['position'] = 'ends_completable_word'

        else:
            self.state['position'] = 'outside'

        if not self.state['position'] in ['begin_end_completable', 'ends_completable_word']:
            self.deactivate()

    def get_begin_end_offset_word_len(self):
        line = self.content.get_line_at_cursor()
        offset = self.content.get_cursor_line_offset()
        line = line[:offset] + '%•%' + line[offset:]
        match = ServiceLocator.get_regex_object(r'.*\\(begin|end)\{((?:[^\{\[\(])*)%•%((?:[^\{\[\(])*)\}.*').match(line)
        if match:
            word_offset = self.content.get_cursor_offset() - len(match.group(2))
            word_len = len(match.group(2)) + len(match.group(3))
            return (word_offset, word_len)

    def get_matching_begin_end_offset(self, orig_offset):
        blocks = self.document.get_blocks()
        for block in blocks:
            if block[0] == orig_offset - 7:
                return None if block[1] == None else block[1] + 5 - orig_offset
            elif block[1] == orig_offset - 5:
                return None if block[0] == None else block[0] + 7 - orig_offset
        return None

    def cursor_inside_begin_or_end(self):
        line = self.content.get_line_at_cursor()
        offset = self.content.get_cursor_line_offset()
        line = line[:offset] + '%•%' + line[offset:]
        match_begin_end = ServiceLocator.get_regex_object(r'.*\\(begin|end)\{((?:[^\{\[\(])*)%•%((?:[^\{\[\(])*)\}.*').match(line)
        return match_begin_end

    def cursor_ends_completable_environment_name(self):
        line = self.content.get_line_at_cursor()
        offset = self.content.get_cursor_line_offset()
        line = line[:offset] + '%•%' + line[offset:]
        match_begin_end = ServiceLocator.get_regex_object(r'.*\\(begin|end)\{((?:[^\{\[\(])*)%•%((?:[^\{\[\(])*)\}.*').match(line)
        items = self.provider.get_begin_end_items(match_begin_end.group(2))

        if len(items) <= 0: return False
        if items[0]['command'] == match_begin_end.group(2): return False
        return True

    def cursor_ends_completable_word(self):
        current_word = self.get_latex_command_at_cursor()
        items = self.provider.get_items_for_completion_window(current_word)

        if len(items) <= 0: return False
        if items[0]['command'] == current_word: return False
        return True

    def replace_latex_command_at_cursor(self, text, dotlabels, is_full_command=False):
        insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        current_word = self.get_latex_command_at_cursor()
        start_iter = insert_iter.copy()
        start_iter.backward_chars(len(current_word))

        if is_full_command and text.startswith('\\begin'):
            end_command = text.replace('\\begin', '\\end')
            end_command_bracket_position = end_command.find('}')
            if end_command_bracket_position:
                end_command = end_command[:end_command_bracket_position + 1]
            text += '\n\t•\n' + end_command
            text = self.content.replace_tabs_with_spaces_if_set(text)
            dotlabels += 'content###'
            if end_command.find('•') >= 0:
                dotlabels += 'environment###'

            line_iter = self.source_buffer.get_iter_at_line(start_iter.get_line())
            ws_line = self.source_buffer.get_text(line_iter, start_iter, False)
            lines = text.split('\n')
            ws_number = len(ws_line) - len(ws_line.lstrip())
            whitespace = ws_line[:ws_number]
            text = ''
            for no, line in enumerate(lines):
                if no != 0:
                    text += '\n' + whitespace
                text += line

        parts = text.split('•')
        if len(parts) == 1:
            orig_text = self.source_buffer.get_text(start_iter, insert_iter, False)
            if parts[0].startswith(orig_text):
                self.source_buffer.insert_at_cursor(parts[0][len(orig_text):])
            else:
                part_indented = self.content.indent_text_with_whitespace_at_iter(parts[0], start_iter)
                self.content.replace_range_and_select_dot(start_iter, insert_iter, part_indented)
        else:
            self.source_buffer.begin_user_action()

            self.source_buffer.delete(start_iter, insert_iter)
            insert_offset = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert()).get_offset()
            count = len(parts)
            select_dot_offset = -1
            for part in parts:
                insert_iter = self.source_buffer.get_iter_at_offset(insert_offset)
                insert_offset += len(part)
                self.source_buffer.insert(insert_iter, part)
                if count > 1:
                    insert_iter = self.source_buffer.get_iter_at_offset(insert_offset)
                    self.source_buffer.insert_with_tags(insert_iter, '•', self.content.placeholder_tag)
                    if select_dot_offset == -1:
                        select_dot_offset = insert_offset
                    insert_offset += 1
                count -= 1
            select_dot_iter = self.source_buffer.get_iter_at_offset(select_dot_offset)
            bound = select_dot_iter.copy()
            bound.forward_chars(1)
            self.source_buffer.select_range(select_dot_iter, bound)

            self.source_buffer.end_user_action()

    def get_latex_command_at_cursor(self):
        insert_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        limit_iter = insert_iter.copy()
        limit_iter.backward_chars(50)
        word_start_iter = insert_iter.copy()
        result = word_start_iter.backward_search('\\', Gtk.TextSearchFlags.TEXT_ONLY, limit_iter)
        if result != None:
            word_start_iter = result[0]
        word = word_start_iter.get_slice(insert_iter)
        return word

    def is_visible(self):
        return self.is_active() and self.state['position'] in ['begin_end_completable', 'ends_completable_word'] and self.view.position_is_visible() and not self.view.focus_hide


