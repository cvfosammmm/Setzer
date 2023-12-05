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
from gi.repository import Gtk, Gdk, Pango

import setzer.document.autocomplete.autocomplete_widget_viewgtk as autocomplete_view
from setzer.app.service_locator import ServiceLocator
from setzer.app.font_manager import FontManager


class AutocompleteWidget(object):

    def __init__(self, model):
        self.main_window = ServiceLocator.get_main_window()
        self.model = model
        self.document = self.model.document
        self.source_view = self.document.view.source_view
        self.source_buffer = self.model.document.source_buffer

        self.view = autocomplete_view.AutocompleteWidgetView(self)

        self.line_height = None
        self.height = None
        self.shortcutsbar_height = None
        self.x_position, self.y_position = (None, None)
        self.focus_hide = self.model.document.source_view.has_focus()

        self.focus_controller = Gtk.EventControllerFocus()
        self.focus_controller.connect('enter', self.on_focus_in)
        self.focus_controller.connect('leave', self.on_focus_out)
        self.model.document.source_view.add_controller(self.focus_controller)

        self.view.set_draw_func(self.view.draw)
        self.queue_draw()

    def on_focus_out(self, widget):
        self.focus_hide = True
        self.queue_draw()

    def on_focus_in(self, widget):
        self.focus_hide = False
        self.queue_draw()

    def queue_draw(self):
        self.update_size()
        self.update_position()
        self.update_margins()

        self.view.set_visible(self.model.is_active and self.position_is_visible() and not self.focus_hide)
        self.view.queue_draw()

    def update_size(self):
        self.line_height = FontManager.get_line_height(self.source_view)
        self.char_width = FontManager.get_char_width(self.source_view)
        self.shortcutsbar_height = self.main_window.shortcutsbar.get_allocated_height()

        if self.model.items != None:
            self.height = min(len(self.model.items), 5) * self.line_height
            self.width = (5 + min(max(self.get_max_chars(), 25), 45)) * self.char_width
            self.view.set_size_request(self.width, self.height)

    def get_max_chars(self):
        if len(self.model.items) > 0:
            return max([len(item['command']) + len(item['dotlabels']) - 4 * item['dotlabels'].count('###') for item in self.model.items])
        else:
            return 0

    def update_position(self):
        start_iter = self.source_buffer.get_iter_at_mark(self.source_buffer.get_insert())
        if self.model.current_word != None:
            start_iter.backward_chars(len(self.model.current_word))

        iter_location = self.source_view.get_iter_location(start_iter)
        x_offset = - self.document.view.scrolled_window.get_hadjustment().get_value()
        x_offset += self.document.view.margin.get_allocated_width()
        y_offset = - self.document.view.scrolled_window.get_vadjustment().get_value()
        self.x_position = x_offset + iter_location.x
        self.y_position = y_offset + iter_location.y + self.line_height

    def update_margins(self):
        vertical_cutoff = self.document.view.scrolled_window.get_allocated_height() - self.height - self.line_height
        horizontal_cutoff = self.main_window.preview_paned.get_allocated_width() - self.view.get_allocated_width()

        if self.y_position >= self.line_height and self.y_position <= vertical_cutoff:
            self.view.set_margin_top(self.y_position + self.shortcutsbar_height)
        else:
            self.view.set_margin_top(self.y_position + self.shortcutsbar_height - self.height - self.line_height)

        if self.x_position >= 0 and self.x_position <= horizontal_cutoff:
            self.view.set_margin_start(self.x_position)
        else:
            self.view.set_margin_start(self.main_window.preview_paned.get_allocated_width() - self.view.get_allocated_width())

    def position_is_visible(self):
        return ((self.y_position >= self.line_height) and
            (self.y_position <= self.document.view.scrolled_window.get_allocated_height()) and
            (self.x_position >= 0) and
            (self.x_position < self.main_window.preview_paned.get_allocated_width()))


