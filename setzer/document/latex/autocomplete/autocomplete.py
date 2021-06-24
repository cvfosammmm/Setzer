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

import setzer.document.latex.autocomplete.autocomplete_viewgtk as view
import setzer.document.latex.autocomplete.session.session_blank as session_blank
import setzer.document.latex.autocomplete.session.session_default as session_default
import setzer.document.latex.autocomplete.session.session_begin_end as session_begin_end
from setzer.app.service_locator import ServiceLocator
import setzer.helpers.timer as timer


class Autocomplete(object):

    def __init__(self, document, document_view):
        self.document = document
        self.document_view = document_view
        self.main_window = ServiceLocator.get_main_window()
        self.font_manager = ServiceLocator.get_font_manager()
        self.font_manager.register_observer(self)

        self.view = view.DocumentAutocompleteView()
        self.mark_start = Gtk.TextMark.new('ac_session_start', True)
        self.mark_end = Gtk.TextMark.new('ac_session_end', False)
        self.matching_mark_start = Gtk.TextMark.new('ac_session_second_start', True)
        self.matching_mark_end = Gtk.TextMark.new('ac_session_second_end', False)

        self.provider = ServiceLocator.get_autocomplete_provider()

        self.blank_session = session_blank.SessionBlank(self, self.document)
        self.session = self.blank_session

        self.shortcuts_bar_height = 37
        self.cursor_offset = None

        char_width, line_height = self.font_manager.get_char_dimensions()
        self.view.scrolled_window.set_max_content_height(5 * line_height)
        self.view.scrolled_window.set_min_content_width(35 * char_width)

        self.focus_hide = False

        self.items = list()

        self.view.list.connect('row-activated', self.on_row_activated)
        self.view.list.connect('row-selected', self.on_row_selected)

        self.document.source_buffer.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'text_inserted':
            buffer, location_iter, text, text_length = parameter
            self.session.on_insert_text(buffer, location_iter, text, text_length)

        if change_code == 'text_deleted':
            buffer, start_iter, end_iter = parameter
            self.session.on_delete_range(buffer, start_iter, end_iter)

        if change_code == 'buffer_changed':
            self.update(True)

        if change_code in ['insert_mark_set', 'insert_mark_deleted']:
            self.update(False)

        if change_code == 'font_string_changed':
            char_width, line_height = self.font_manager.get_char_dimensions()
            self.view.scrolled_window.set_max_content_height(5 * line_height)
            self.view.scrolled_window.set_min_content_width(35 * char_width)

    def on_adjustment_value_changed(self, adjustment, user_data=None):
        self.update_visibility()
        return False

    def on_row_activated(self, box, row, user_data=None):
        self.document_view.source_view.grab_focus()
        self.submit()

    def on_row_selected(self, box, row, user_data=None):
        char_width, line_height = self.font_manager.get_char_dimensions()

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

    def on_focus_out(self, widget, event, user_data=None):
        self.focus_hide = True
        self.update_visibility()

    def on_focus_in(self, widget, event, user_data=None):
        self.focus_hide = False
        self.update_visibility()

    def on_keypress(self, event):
        ''' returns whether the keypress has been handled. '''

        return self.session.on_keypress(event)

    def submit(self):
        self.session.submit()

    def update(self, can_activate=False):
        if self.is_active():
            self.session.update(can_activate)
        if not self.is_active():
            line = self.document.get_line_at_cursor()
            offset = self.document.get_cursor_line_offset()
            line = line[:offset] + '%•%' + line[offset:]
            match = ServiceLocator.get_regex_object(r'.*\\(begin|end)\{((?:[^\{\[\(])*)%•%((?:[^\{\[\(])*)\}.*').match(line)
            if match:
                word_offset = self.document.get_cursor_offset() - len(match.group(2))
                word_len = len(match.group(2)) + len(match.group(3))
                self.start_session(session_begin_end.SessionBeginEnd(self, word_offset, word_len))
                self.session.update(can_activate)
                return
            current_word = self.document.get_latex_command_at_cursor()
            if can_activate:
                items = self.provider.get_items(current_word)
                if not items: return
                for item in items:
                    if item['command'] == current_word:
                        return
                self.start_session(session_default.SessionDefault(self, self.document))

    def update_visibility(self):
        if self.session.will_show and self.position_is_visible() and not self.focus_hide and len(self.items) > 0:
            self.view.show_all()
        else:
            self.view.hide()

    #@timer.timer
    def populate(self, offset):
        self.view.empty_list()
        for command in reversed(self.items):
            item = view.DocumentAutocompleteItem(command, offset)
            self.view.prepend(item)
        if len(self.items) > 0:
            self.view.select_first()

    def position_is_visible(self):
        line_height = self.font_manager.get_line_height()

        height = min(len(self.items), 5) * line_height + 20

        buffer = self.document.get_buffer()
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        iter_location = self.document_view.source_view.get_iter_location(insert_iter)
        start_iter = insert_iter.copy()
        start_iter.backward_chars(self.session.get_offset())
        start_iter_location = self.document_view.source_view.get_iter_location(start_iter)
        gutter = self.document_view.source_view.get_window(Gtk.TextWindowType.LEFT)
        if gutter != None:
            gutter_width = gutter.get_width()
        else:
            gutter_width = 0
        x_offset = - self.document_view.scrolled_window.get_hadjustment().get_value()
        y_offset = - self.document_view.scrolled_window.get_vadjustment().get_value()
        x_position = x_offset + start_iter_location.x - 2 + gutter_width
        y_position = y_offset + iter_location.y + line_height

        full_height = 5 * line_height + 20

        if y_position >= line_height - 1 and y_position <= self.document_view.scrolled_window.get_allocated_height() - full_height - line_height:
            self.view.set_margin_top(y_position + self.shortcuts_bar_height)
        else:
            self.view.set_margin_top(y_position + self.shortcuts_bar_height - height - line_height)

        char_width, line_height = self.font_manager.get_char_dimensions()
        width = 25 * char_width
        max_width = 35 * char_width
        while x_position <= self.main_window.preview_paned.get_allocated_width() - width - char_width:
            width += char_width
            if width == max_width:
                break
        if x_position >= 0 and x_position <= self.main_window.preview_paned.get_allocated_width() - width:
            self.view.set_margin_left(x_position)
        else:
            self.view.set_margin_left(self.main_window.preview_paned.get_allocated_width() - width)
        self.view.scrolled_window.set_min_content_width(width)

        show_x = False
        show_y = False

        if y_position >= line_height - 1 and y_position <= self.document_view.scrolled_window.get_allocated_height() - full_height - line_height:
            show_y = True
        elif y_position >= line_height - 1 and y_position <= self.document_view.scrolled_window.get_allocated_height():
            show_y = True
        else:
            show_y = False

        if x_position >= 0 and x_position <= self.main_window.preview_paned.get_allocated_width() - width:
            show_x = True
        elif x_position >= 0 and x_position <= self.main_window.preview_paned.get_allocated_width():
            show_x = True
        else:
            show_x = False
        return (show_x and show_y)

    def cursor_moved(self):
        cursor_offset = self.document.get_cursor_offset()
        if self.cursor_offset != cursor_offset:
            self.cursor_offset = cursor_offset
            return True
        return False

    def start_session(self, session):
        self.session = session
        self.session.update()

    def end_session(self):
        self.session = self.blank_session
        self.session.update()

    def is_active(self):
        return self.session.is_active()

    def is_visible(self):
        return self.session.will_show and self.position_is_visible() and not self.focus_hide


