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

import setzer.document.autocomplete.autocomplete_viewgtk as view
import setzer.document.autocomplete.modes.mode_blank as mode_blank
import setzer.document.autocomplete.modes.mode_default as mode_default
import setzer.document.autocomplete.modes.mode_begin_end as mode_begin_end
from setzer.app.service_locator import ServiceLocator
import setzer.helpers.timer as timer


class Autocomplete(object):

    def __init__(self, document, document_view):
        self.document = document
        self.document_view = document_view
        self.main_window = ServiceLocator.get_main_window()

        self.view = view.DocumentAutocompleteView(self)
        self.mark_start = Gtk.TextMark.new('ac_session_start', True)
        self.mark_end = Gtk.TextMark.new('ac_session_end', False)
        self.matching_mark_start = Gtk.TextMark.new('ac_session_second_start', True)
        self.matching_mark_end = Gtk.TextMark.new('ac_session_second_end', False)

        self.provider = ServiceLocator.get_autocomplete_provider()

        self.blank_mode = mode_blank.ModeBlank(self, self.document)
        self.mode = self.blank_mode

        self.items = list()

        self.view.list.connect('row-activated', self.on_row_activated)
        self.view.list.connect('row-selected', self.on_row_selected)

        self.document.content.connect('text_inserted', self.on_text_inserted)
        self.document.content.connect('text_deleted', self.on_text_deleted)
        self.document.content.connect('buffer_changed', self.on_buffer_changed)
        self.document.content.connect('insert_mark_set', self.on_insert_mark_set)
        self.document.content.connect('insert_mark_deleted', self.on_insert_mark_deleted)

    def on_text_inserted(self, content, parameter):
        buffer, location_iter, text, text_length = parameter
        self.mode.on_insert_text(buffer, location_iter, text, text_length)

    def on_text_deleted(self, content, parameter):
        buffer, start_iter, end_iter = parameter
        self.mode.on_delete_range(buffer, start_iter, end_iter)

    def on_buffer_changed(self, content, buffer):
        self.activate_if_possible()
        self.update()

    def on_insert_mark_set(self, content):
        self.update()

    def on_insert_mark_deleted(self, content):
        self.update()

    def on_row_activated(self, box, row, user_data=None):
        self.document_view.source_view.grab_focus()
        self.submit()

    def on_row_selected(self, box, row, user_data=None):
        char_width, line_height = self.view.font_manager.get_char_dimensions()

        if row != None:
            command = row.get_child().command
            scroll_min = row.get_index() * line_height
            scroll_max = scroll_min - 4 * line_height
            current_offset = self.view.scrolled_window.get_vadjustment().get_value()
            if scroll_min < current_offset:
                self.view.scrolled_window.get_vadjustment().set_value(scroll_min)
            elif scroll_max > current_offset:
                self.view.scrolled_window.get_vadjustment().set_value(scroll_max)
            self.view.infobox.set_text(command['description'])

    def on_keypress(self, event):
        ''' returns whether the keypress has been handled. '''

        return self.mode.on_keypress(event)

    def submit(self):
        self.mode.submit()

    def update(self):
        if self.is_active():
            self.mode.update()

    def activate_if_possible(self):
        line = self.document.content.get_line_at_cursor()
        offset = self.document.content.get_cursor_line_offset()
        line = line[:offset] + '%•%' + line[offset:]
        match = ServiceLocator.get_regex_object(r'.*\\(begin|end)\{((?:[^\{\[\(])*)%•%((?:[^\{\[\(])*)\}.*').match(line)
        if match:
            word_offset = self.document.content.get_cursor_offset() - len(match.group(2))
            word_len = len(match.group(2)) + len(match.group(3))
            self.start_mode(mode_begin_end.ModeBeginEnd(self, word_offset, word_len))
        else:
            current_word = self.document.content.get_latex_command_at_cursor()
            items = self.provider.get_items(current_word)
            if not items: return
            for item in items:
                if item['command'] == current_word:
                    return
            self.start_mode(mode_default.ModeDefault(self, self.document))

    #@timer.timer
    def populate(self, offset):
        self.view.empty_list()
        for command in reversed(self.items):
            item = view.DocumentAutocompleteItem(command, offset)
            self.view.prepend(item)
        if len(self.items) > 0:
            self.view.select_first()

    def start_mode(self, mode):
        self.mode = mode
        self.mode.update()

    def end_mode(self):
        self.mode = self.blank_mode
        self.mode.update()

    def is_active(self):
        return self.mode.is_active()

    def is_visible(self):
        return self.mode.will_show and self.view.position_is_visible() and not self.view.focus_hide


