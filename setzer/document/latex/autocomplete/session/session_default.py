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

from setzer.app.service_locator import ServiceLocator


class SessionDefault(object):

    def __init__(self, autocomplete, document):
        self.autocomplete = autocomplete
        self.document = document
        self.will_show = True

        self.last_tabbed_command = None
        self.current_word = ""
        self.current_word_offset = self.document.get_latex_command_at_cursor_offset()

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

    def on_tab_press(self):
        if not self.autocomplete.is_visible():
            return False

        if len(self.autocomplete.items) == 1:
            self.submit()
            return True
        else:
            self.current_word = self.document.get_latex_command_at_cursor()
            i = self.get_number_of_matching_letters_on_tabpress(self.current_word, 0)

            command = self.autocomplete.view.list.get_selected_row().get_child().command
            if len(command['command']) == len(self.current_word) + i:
                self.last_tabbed_command = None
                self.submit()
                return True
            else:
                if i >= 1:
                    text = (command['command'])[:len(self.current_word) + i]
                    self.last_tabbed_command = command['command'][1:]
                    self.document.replace_latex_command_at_cursor(text, command['dotlabels'])
                    return True
                else:
                    current_word = (command['command'])[:len(self.current_word) + 1]
                    i = self.get_number_of_matching_letters_on_tabpress(current_word, 0)

                    if len(command['command']) == len(current_word) + i:
                        self.last_tabbed_command = None
                        self.submit()
                        return True
                    else:
                        text = (command['command'])[:len(current_word) + i]
                        self.last_tabbed_command = command['command']
                        self.document.replace_latex_command_at_cursor(text, command['dotlabels'])
                        return True

    def get_number_of_matching_letters_on_tabpress(self, current_word, offset):
        items = self.autocomplete.provider.get_items(current_word)
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

    def update(self, can_show=False):
        if not self.current_word_changed_or_is_none():
            self.current_word = self.document.get_latex_command_at_cursor()
            self.autocomplete.items = self.autocomplete.provider.get_items_for_completion_window(self.current_word, self.last_tabbed_command)
            if len(self.autocomplete.items) > 0:
                if self.autocomplete.cursor_moved():
                    for item in self.autocomplete.items:
                        item['command'] = item['command']
                    self.autocomplete.populate(len(self.current_word))
                self.autocomplete.update_visibility()
            else:
                self.cancel()
        else:
            self.cancel()

    def get_offset(self):
        self.current_word = self.document.get_latex_command_at_cursor()
        return len(self.current_word)

    def current_word_changed_or_is_none(self):
        current_word_offset = self.document.get_latex_command_at_cursor_offset()
        if current_word_offset != self.current_word_offset:
            return True
        return (current_word_offset == None)

    def submit(self):
        self.autocomplete.end_session()

        row = self.autocomplete.view.list.get_selected_row()
        command = row.get_child().command
        if command['command'].startswith('\\begin'):
            self.insert_begin_end(command)
        else:
            self.insert_normal_command(command)

    def insert_begin_end(self, command):
        text = command['command']
        buffer = self.document.get_buffer()
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        current_word = self.document.get_latex_command_at_cursor()
        start_iter = insert_iter.copy()
        start_iter.backward_chars(len(current_word))

        replace_previous_command_data = self.insert_begin_end_check_replace(insert_iter, text)
        if replace_previous_command_data[0]:
            self.insert_begin_end_replace(start_iter, insert_iter, replace_previous_command_data)
        else:
            self.document.replace_latex_command_at_cursor(text, command['dotlabels'], is_full_command=True)

    def insert_begin_end_check_replace(self, insert_iter, text):
        line_part = self.document.get_line(insert_iter.get_line())[insert_iter.get_line_offset():]
        line_regex = ServiceLocator.get_regex_object(r'(\w*(?:\*){0,1})\{([^\{\[\|\(]+)\}')
        line_match = line_regex.match(line_part)
        if line_match:
            document_text = self.document.get_text_after_offset(insert_iter.get_offset() + 1)
            if self.get_end_match_object(document_text, line_match.group(2)):
                return (line_match, text)
        return (None, text)

    def insert_begin_end_replace(self, start_iter_begin, insert_iter, replace_previous_command_data):
        text = replace_previous_command_data[1]
        match_object = replace_previous_command_data[0]

        self.document.get_buffer().begin_user_action()

        end_iter_begin = insert_iter.copy()
        end_iter_begin.forward_chars(match_object.end())
        start_iter_offset = start_iter_begin.get_offset()
        self.document.get_buffer().replace_range_no_user_action(start_iter_begin, end_iter_begin, text, indent_lines=False, select_dot=True)

        end_iter_offset = start_iter_offset + len(text)
        document_text = self.document.get_text_after_offset(end_iter_offset)
        environment_name = ServiceLocator.get_regex_object(r'(\w*(?:\*){0,1})\{([^\{\[\|\(]+)\}').match(match_object.group(0)).group(2)
        end_match_object = self.get_end_match_object(document_text, environment_name)

        if end_match_object != None:
            start_iter_begin = self.document.get_buffer().get_iter_at_offset(end_iter_offset)
            start_iter_end = start_iter_begin.copy()
            start_iter_end.forward_chars(end_match_object.start())
            end_iter_end = start_iter_begin.copy()
            end_iter_end.forward_chars(end_match_object.end())
            end_command = text.replace('\\begin', '\\end')
            end_command_bracket_position = end_command.find('}')
            if end_command_bracket_position:
                end_command = end_command[:end_command_bracket_position + 1]
            self.document.get_buffer().replace_range_no_user_action(start_iter_end, end_iter_end, end_command, indent_lines=False, select_dot=False)

        self.document.get_buffer().end_user_action()

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
            self.document.replace_latex_command_at_cursor(text, command['dotlabels'], is_full_command=True)
        else:
            command_regex = ServiceLocator.get_regex_object(r'.*' + replacement_pattern[1])
            if command_regex.match(text):
                self.insert_final_replace(text, replacement_pattern)
            else:
                self.document.replace_latex_command_at_cursor(text, command['dotlabels'], is_full_command=True)

    def get_replacement_pattern(self, command):
        buffer = self.document.get_buffer()
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        line_part = self.document.get_line(insert_iter.get_line())[insert_iter.get_line_offset():]
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

        current_word = self.document.get_latex_command_at_cursor()
        offset = self.document.get_cursor_offset() - len(current_word)
        length = len(current_word) + match_object.end()
        self.document.replace_range(offset, length, text, indent_lines=True, select_dot=True)

    def cancel(self):
        self.autocomplete.end_session()

    def is_active(self):
        return True


