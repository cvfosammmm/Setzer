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
from gi.repository import Gdk

import setzer.document.autocomplete.autocomplete_viewgtk as view
import setzer.document.autocomplete.state.state_inactive as state_inactive
import setzer.document.autocomplete.state.state_active_invisible as state_active_invisible
import setzer.document.autocomplete.state.state_active_visible as state_active_visible
from setzer.app.service_locator import ServiceLocator


class Autocomplete(object):

    def __init__(self, document, document_view):
        self.document = document
        self.document_view = document_view
        self.main_window = ServiceLocator.get_main_window()

        self.view = view.DocumentAutocompleteView()
        self.provider = ServiceLocator.get_autocomplete_provider()

        self.states = dict()
        self.states['inactive'] = state_inactive.StateInactive(self)
        self.states['active_invisible'] = state_active_invisible.StateActiveInvisible(self)
        self.states['active_visible'] = state_active_visible.StateActiveVisible(self)
        self.active_state = None
        self.change_state('inactive')

        self.char_width, self.line_height = self.document.get_char_dimensions()
        self.shortcuts_bar_height = 37

        self.insert_iter_offset = None
        self.current_word = ""
        self.current_word_offset = None
        self.height = None
        self.width = None

        self.items = list()
        self.last_tabbed_command = None

        self.view.list.connect('row-activated', self.on_row_activated)
        self.view.list.connect('row-selected', self.on_row_selected)

        self.document_view.scrolled_window.get_vadjustment().connect('value-changed', self.on_adjustment_value_changed)
        self.document_view.scrolled_window.get_hadjustment().connect('value-changed', self.on_adjustment_value_changed)
        self.document_view.source_view.connect('focus-out-event', self.on_focus_out)
        self.document_view.source_view.connect('focus-in-event', self.on_focus_in)
        self.document.get_buffer().connect('changed', self.on_buffer_changed)
        self.document.get_buffer().connect('mark-set', self.on_mark_set)
        self.document.get_buffer().connect('mark-deleted', self.on_mark_deleted)

    def on_adjustment_value_changed(self, adjustment, user_data=None):
        self.update(False)
        return False

    def on_mark_set(self, buffer, insert, mark, user_data=None):
        self.update(False)
    
    def on_buffer_changed(self, buffer, user_data=None):
        self.update(True)
    
    def on_mark_deleted(self, buffer, mark, user_data=None):
        self.update(False)

    def on_row_activated(self, box, row, user_data=None):
        self.document_view.source_view.grab_focus()
        self.submit()

    def on_row_selected(self, box, row, user_data=None):
        if row != None:
            command = row.get_child().command
            self.view.infobox.set_text(command['description'])

    def on_focus_out(self, widget, event, user_data=None):
        self.active_state.focus_hide()

    def on_focus_in(self, widget, event, user_data=None):
        self.active_state.focus_show()

    def on_keypress(self, event):
        ''' returns whether the keypress has been handled. '''
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.keyval == Gdk.keyval_from_name('Down'):
            if event.state & modifiers == 0:
                return self.active_state.on_down_press()

        if event.keyval == Gdk.keyval_from_name('Up'):
            if event.state & modifiers == 0:
                return self.active_state.on_up_press()

        if event.keyval == Gdk.keyval_from_name('Escape'):
            if event.state & modifiers == 0:
                return self.active_state.on_escape_press()

        if event.keyval == Gdk.keyval_from_name('Return'):
            if event.state & modifiers == 0:
                return self.active_state.on_return_press()

        tab_keyvals = [Gdk.keyval_from_name('Tab'), Gdk.keyval_from_name('ISO_Left_Tab')]
        if event.keyval in tab_keyvals:
            if event.state & modifiers == 0:
                return self.active_state.on_tab_press()

    def cursor_inside_word_or_at_end(self):
        buffer = self.document.get_buffer()
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        current_word = self.get_current_word(insert_iter)
        if ServiceLocator.get_regex_object(r'\\(\w*(?:\*){0,1})').fullmatch(current_word):
            return True
        return False

    def cursor_at_word_end(self):
        buffer = self.document.get_buffer()
        text_iter = buffer.get_iter_at_mark(buffer.get_insert())
        current_word = self.get_current_word(text_iter)
        if ServiceLocator.get_regex_object(r'\\(\w*(?:\*){0,1})').fullmatch(current_word):
            return text_iter.ends_word()
        return False

    def get_current_word(self, insert_iter):
        limit_iter = insert_iter.copy()
        limit_iter.backward_chars(50)
        word_start_iter = insert_iter.copy()
        result = word_start_iter.backward_search('\\', Gtk.TextSearchFlags.TEXT_ONLY, limit_iter)
        if result != None:
            word_start_iter = result[0]
        word = word_start_iter.get_slice(insert_iter)
        return word

    def get_current_word_offset(self, insert_iter):
        limit_iter = insert_iter.copy()
        limit_iter.backward_chars(50)
        word_start_iter = insert_iter.copy()
        result = word_start_iter.backward_search('\\', Gtk.TextSearchFlags.TEXT_ONLY, limit_iter)
        if result != None:
            word_start_iter = result[0]
            return word_start_iter.get_offset()
        return None

    def add_text_to_current_word(self, text):
        buffer = self.document.get_buffer()
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        current_word = self.get_current_word(insert_iter)
        start_iter = insert_iter.copy()
        start_iter.backward_chars(len(current_word))

        self.document.replace_range(start_iter, insert_iter, text, indent_lines=True, select_dot=False)

    def submit(self):
        row = self.view.list.get_selected_row()
        text = row.get_child().label.get_text()
        if text.startswith('\\begin'):
            self.insert_begin_end(text)
        else:
            self.insert_normal_command(text)
        self.active_state.hide()

    def insert_begin_end(self, text):
        buffer = self.document.get_buffer()
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        current_word = self.get_current_word(insert_iter)
        start_iter = insert_iter.copy()
        start_iter.backward_chars(len(current_word))

        replace_previous_command_data = self.insert_begin_end_check_replace(insert_iter, text)
        if replace_previous_command_data[0]:
            self.insert_begin_end_replace(start_iter, insert_iter, replace_previous_command_data)
        else:
            self.insert_begin_end_no_replace(text)

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

    def insert_begin_end_no_replace(self, text):
        end_command = text.replace('\\begin', '\\end')
        end_command_bracket_position = end_command.find('}')
        if end_command_bracket_position:
            end_command = end_command[:end_command_bracket_position + 1]
        text += '\n\t•\n' + end_command
        self.replace_current_command(text)

    def insert_normal_command(self, text):
        buffer = self.document.get_buffer()
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())

        replacement_pattern = self.get_replacement_pattern(insert_iter, text)
        if replacement_pattern != None:
            command_regex = ServiceLocator.get_regex_object(r'.*' + replacement_pattern[1])
            if command_regex.match(text):
                self.insert_final_replace(insert_iter, text, replacement_pattern)
                return
        self.replace_current_command(text)

    def get_replacement_pattern(self, insert_iter, command):
        line_part = self.document.get_line(insert_iter.get_line())[insert_iter.get_line_offset():]
        command_bracket_count = self.get_command_bracket_count(command)

        matches_group = list()
        line_regex = ServiceLocator.get_regex_object(r'(\w*(?:\*){0,1})(?:\{([^\{\[\|\(\\]+)\}|\[([^\{\[\|\(\\]+)\]|\|([^\{\[\|\(\\]+)\||\(([^\{\[\|\(\\]+)\))*')
        line_match = line_regex.match(line_part)
        if line_match == None:
            return None
        else:
            line_part = line_part[:line_match.end()]
            line_regex = ServiceLocator.get_regex_object(r'(\w*)|\{([^\{\[\|\(\\]+)\}|\[([^\{\[\|\(\\]+)\]|\|([^\{\[\|\(\\]+)\||\(([^\{\[\|\(\\]+)\)')
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
            if bracket_count > 0:
                return (line_match, command_regex_pattern)
            else:
                return None

    def get_command_bracket_count(self, command):
        count = 0
        line_regex = ServiceLocator.get_regex_object(r'\{([^\{\[\|\(]+)\}|\[([^\{\[\|\(]+)\]|\|([^\{\[\|\(]+)\||\(([^\{\[\|\(]+)\)')
        for match in line_regex.finditer(command):
            count += 1
        return count

    def insert_final_replace(self, insert_iter, command, replacement_pattern):
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

        current_word = self.get_current_word(insert_iter)
        start_iter = insert_iter.copy()
        start_iter.backward_chars(len(current_word))
        end_iter = insert_iter.copy()
        end_iter.forward_chars(match_object.end())
        self.document.replace_range(start_iter, end_iter, text, indent_lines=True, select_dot=True)

    def replace_current_command(self, text):
        buffer = self.document.get_buffer()
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        current_word = self.get_current_word(insert_iter)
        start_iter = insert_iter.copy()
        start_iter.backward_chars(len(current_word))
        self.document.replace_range(start_iter, insert_iter, text, indent_lines=True, select_dot=True)

    def update(self, can_show=False):
        if self.document.get_buffer() == None: return
        if self.active_state != self.states['active_visible'] and can_show == False: return

        if self.current_word_changed_or_is_none() and not can_show:
            self.active_state.hide()
        else:
            buffer = self.document.get_buffer()
            insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
            self.current_word = self.get_current_word(insert_iter)
            self.items = self.provider.get_items_for_completion_window(self.current_word, self.last_tabbed_command)
            if len(self.items) > 0:
                self.update_position()
                if self.position_is_visible():
                    if self.insert_iter_offset_changed() or self.active_state == self.states['inactive']:
                        self.populate()
                    self.active_state.show()
                else:
                    self.active_state.hide()
            else:
                self.active_state.hide()

    def current_word_changed_or_is_none(self):
        buffer = self.document.get_buffer()
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        current_word_offset = self.get_current_word_offset(insert_iter)
        if current_word_offset != self.current_word_offset:
            self.current_word_offset = current_word_offset
            return True
        return (current_word_offset == None)

    def insert_iter_offset_changed(self):
        buffer = self.document.get_buffer()
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        if self.insert_iter_offset == None: self.insert_iter_offset = insert_iter.get_offset()
        if self.insert_iter_offset != insert_iter.get_offset():
            self.insert_iter_offset = insert_iter.get_offset()
            return True
        return False

    def populate(self):
        self.view.empty_list()
        for command in reversed(self.items):
            item = view.DocumentAutocompleteItem(command, len(self.current_word) - 1)
            self.view.prepend(item)
        if len(self.items) > 0:
            self.view.select_first()

    def update_position(self):
        self.height = len(self.items) * self.line_height + 20
        self.width = self.view.get_allocated_width()

        buffer = self.document.get_buffer()
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        iter_location = self.document_view.source_view.get_iter_location(insert_iter)
        gutter = self.document_view.source_view.get_window(Gtk.TextWindowType.LEFT)
        if gutter != None:
            gutter_width = gutter.get_width()
        else:
            gutter_width = 0
        x_offset = - self.document_view.scrolled_window.get_hadjustment().get_value()
        y_offset = - self.document_view.scrolled_window.get_vadjustment().get_value()
        self.x_position = x_offset + iter_location.x - 2 + gutter_width - len(self.current_word) * self.char_width
        self.y_position = y_offset + iter_location.y + self.line_height + self.shortcuts_bar_height

        full_height = 110
        if self.y_position >= self.line_height - 1 + self.shortcuts_bar_height and self.y_position <= self.document_view.scrolled_window.get_allocated_height() - full_height:
            self.view.set_margin_top(self.y_position)
        else:
            self.view.set_margin_top(self.y_position - self.height - self.line_height)
        if self.x_position >= 0 and self.x_position <= self.main_window.preview_paned.get_allocated_width() - self.width:
            self.view.set_margin_left(self.x_position)
        else:
            self.view.set_margin_left(self.x_position - self.width)

    def position_is_visible(self):
        show_x = False
        show_y = False

        full_height = 110
        if self.y_position >= self.line_height - 1 + self.shortcuts_bar_height and self.y_position <= self.document_view.scrolled_window.get_allocated_height() - full_height:
            show_y = True
        elif self.y_position >= self.line_height - 1 + self.shortcuts_bar_height and self.y_position <= self.document_view.scrolled_window.get_allocated_height() + self.shortcuts_bar_height:
            show_y = True
        else:
            show_y = False

        if self.x_position >= 0 and self.x_position <= self.main_window.preview_paned.get_allocated_width() - self.width:
            show_x = True
        elif self.x_position >= 0 and self.x_position <= self.main_window.preview_paned.get_allocated_width():
            show_x = True
        else:
            show_x = False
        return (show_x and show_y)

    def change_state(self, state):
        self.active_state = self.states[state]
        self.active_state.init()

    def is_active(self):
        return self.active_state != self.states['inactive']


