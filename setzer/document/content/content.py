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
gi.require_version('GtkSource', '5')
from gi.repository import Gdk
from gi.repository import GtkSource

from setzer.helpers.observable import Observable
from setzer.app.service_locator import ServiceLocator


class Content(Observable):

    def __init__(self, language, document):
        Observable.__init__(self)
        self.document = document
        self.settings = ServiceLocator.get_settings()

        self.source_buffer = GtkSource.Buffer()
        self.source_buffer.set_language(ServiceLocator.get_source_language(language))
        self.source_view = GtkSource.View.new_with_buffer(self.source_buffer)
        self.source_buffer.set_style_scheme(ServiceLocator.get_style_scheme())

        self.source_buffer.connect('modified-changed', self.on_modified_changed)

        self.scroll_to = None

    def on_modified_changed(self, buffer):
        self.add_change_code('modified_changed')

    def initially_set_text(self, text):
        self.source_buffer.begin_irreversible_action()
        self.source_buffer.set_text(text)
        self.source_buffer.end_irreversible_action()
        self.source_buffer.set_modified(False)

    def get_all_text(self):
        return self.source_buffer.get_text(self.source_buffer.get_start_iter(), self.source_buffer.get_end_iter(), True)

    def get_selected_text(self):
        bounds = self.source_buffer.get_selection_bounds()
        if len(bounds) == 2:
            return self.source_buffer.get_text(bounds[0], bounds[1], True)
        else:
            return None

    def place_cursor(self, line_number, offset=0):
        _, text_iter = self.source_buffer.get_iter_at_line_offset(line_number, offset)
        self.source_buffer.place_cursor(text_iter)

    def cut(self):
        self.copy()
        self.delete_selection()

    def copy(self):
        text = self.get_selected_text()
        if text != None:
            clipboard = self.source_view.get_clipboard(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(text, -1)

    def paste(self):
        self.source_view.emit('paste-clipboard')

    def delete_selection(self):
        self.source_buffer.delete_selection(True, True)

    def select_all(self, widget=None):
        self.source_buffer.select_range(self.source_buffer.get_start_iter(), self.source_buffer.get_end_iter())

    def get_modified(self):
        return self.source_buffer.get_modified()

    def set_modified(self, modified):
        self.source_buffer.set_modified(modified)
        self.add_change_code('modified_changed')

    def undo(self):
        self.source_buffer.undo()

    def redo(self):
        self.source_buffer.redo()

    def scroll_cursor_onscreen(self):
        text_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        iter_position = self.source_view.get_iter_location(text_iter).y
        end_yrange = self.source_view.get_line_yrange(self.source_buffer.get_end_iter())
        buffer_height = end_yrange.y + end_yrange.height
        font_manager = ServiceLocator.get_font_manager()
        line_height = font_manager.get_line_height()
        visible_lines = math.floor(self.source_view.get_visible_rect().height / line_height)
        window_offset = self.source_view.get_visible_rect().y
        window_height = self.source_view.get_visible_rect().height
        gap = min(math.floor(max((visible_lines - 2), 0) / 2), 5)
        if iter_position < window_offset + gap * line_height:
            self.scroll_view(max(iter_position - gap * line_height, 0))
            return
        gap = min(math.floor(max((visible_lines - 2), 0) / 2), 8)
        if iter_position > (window_offset + window_height - (gap + 1) * line_height):
            self.scroll_view(min(iter_position + gap * line_height - window_height, buffer_height))

    def scroll_view(self, position, duration=0.2):
        view = self.document.view.scrolled_window
        adjustment = view.get_vadjustment()
        self.scroll_to = {'position_start': adjustment.get_value(), 'position_end': position, 'time_start': time.time(), 'duration': duration}
        view.set_kinetic_scrolling(False)
        GObject.timeout_add(15, self.do_scroll)

    def do_scroll(self):
        view = self.document.view.scrolled_window
        if self.scroll_to != None:
            adjustment = view.get_vadjustment()
            time_elapsed = time.time() - self.scroll_to['time_start']
            if self.scroll_to['duration'] == 0:
                time_elapsed_percent = 1
            else:
                time_elapsed_percent = time_elapsed / self.scroll_to['duration']
            if time_elapsed_percent >= 1:
                adjustment.set_value(self.scroll_to['position_end'])
                self.scroll_to = None
                view.set_kinetic_scrolling(True)
                return False
            else:
                adjustment.set_value(self.scroll_to['position_start'] * (1 - self.ease(time_elapsed_percent)) + self.scroll_to['position_end'] * self.ease(time_elapsed_percent))
                return True
        return False

    def ease(self, time): return (time - 1)**3 + 1


