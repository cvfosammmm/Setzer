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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib, Pango

from setzer.app.service_locator import ServiceLocator


class DocumentAutocompleteView(Gtk.Box):

    def __init__(self, model):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('autocomplete')

        self.main_window = ServiceLocator.get_main_window()
        self.model = model
        self.content = self.model.document.content

        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.START)

        self.shortcutsbar_height = 37
        self.x_position, self.y_position = (None, None)

        self.list = Gtk.ListBox()
        self.list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list.set_can_focus(False)
        self.items = list()
        self.selected_index = 0

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.add(self.list)

        self.infobox = Gtk.Label('')
        self.infobox.set_xalign(0)
        self.infobox.set_ellipsize(Pango.EllipsizeMode.END)
        self.infobox.set_max_width_chars(30)
        self.infobox.get_style_context().add_class('infobox')

        self.pack_start(self.scrolled_window, True, True, 0)
        self.pack_start(self.infobox, False, False, 0)
        self.list.show_all()
        self.infobox.show_all()

        self.font_manager = ServiceLocator.get_font_manager()
        self.font_manager.connect('font_string_changed', self.on_font_string_changed)

        self.focus_hide = False

        self.line_height, self.char_width, self.full_height = (None, None, None)
        self.update_sizes()

        self.model.document_view.scrolled_window.get_vadjustment().connect('value-changed', self.on_adjustment_value_changed)
        self.model.document_view.scrolled_window.get_hadjustment().connect('value-changed', self.on_adjustment_value_changed)
        self.model.document_view.source_view.connect('focus-out-event', self.on_focus_out)
        self.model.document_view.source_view.connect('focus-in-event', self.on_focus_in)
        self.list.connect('row-selected', self.on_row_selected)

    def on_adjustment_value_changed(self, adjustment, user_data=None):
        self.update_position()
        self.update_visibility()
        self.update_margins()
        return False

    def on_focus_out(self, widget, event, user_data=None):
        self.focus_hide = True
        self.update_position()
        self.update_visibility()
        self.update_margins()

    def on_focus_in(self, widget, event, user_data=None):
        self.focus_hide = False
        self.update_position()
        self.update_visibility()
        self.update_margins()

    def on_row_selected(self, box, row, user_data=None):
        if row != None:
            command = row.get_child().command
            scroll_min = row.get_index() * self.line_height
            scroll_max = scroll_min - 4 * self.line_height
            current_offset = self.scrolled_window.get_vadjustment().get_value()
            if scroll_min < current_offset:
                self.scrolled_window.get_vadjustment().set_value(scroll_min)
            elif scroll_max > current_offset:
                self.scrolled_window.get_vadjustment().set_value(scroll_max)
            self.infobox.set_text(command['description'])

    def on_font_string_changed(self, font_manager):
        self.update_sizes()

    def empty_list(self):
        self.items = list()
        self.list.foreach(self.list.remove)

    def prepend(self, item):
        self.items.insert(0, item)
        self.list.prepend(item)

    def select_next(self):
        if self.selected_index >= len(self.items) - 1:
            self.select_first()
        else:
            self.selected_index += 1
            row = self.list.get_row_at_index(self.selected_index)
            self.list.select_row(row)

    def select_previous(self):
        if self.selected_index == 0:
            self.select_last()
        else:
            self.selected_index -= 1
            row = self.list.get_row_at_index(self.selected_index)
            self.list.select_row(row)

    def select_first(self):
        row = self.list.get_row_at_index(0)
        self.list.select_row(row)
        self.selected_index = 0

    def select_last(self):
        row = self.list.get_row_at_index(len(self.items) - 1)
        self.list.select_row(row)
        self.selected_index = len(self.items) - 1

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE

    def update_position(self):
        start_iter = self.content.source_buffer.get_iter_at_mark(self.content.source_buffer.get_insert())
        start_iter.backward_chars(self.model.get_current_word_len())
        self.x_position, self.y_position = self.content.get_screen_offsets_by_iter(start_iter)

    def update_margins(self):
        vertical_cutoff = self.model.document_view.scrolled_window.get_allocated_height() - self.full_height - self.line_height
        horizontal_cutoff = self.main_window.preview_paned.get_allocated_width() - self.get_width()

        if self.y_position >= self.line_height - 1 and self.y_position <= vertical_cutoff:
            self.set_margin_top(self.y_position + self.shortcutsbar_height)
        else:
            self.set_margin_top(self.y_position + self.shortcutsbar_height - self.get_height() - self.line_height)

        if self.x_position >= 0 and self.x_position <= horizontal_cutoff:
            self.set_margin_left(self.x_position)
        else:
            self.set_margin_left(self.main_window.preview_paned.get_allocated_width() - self.get_width())
        self.scrolled_window.set_min_content_width(self.get_width())

    def update_sizes(self):
        self.char_width, self.line_height = self.font_manager.get_char_dimensions()
        self.full_height = 5 * self.line_height + 20
        self.scrolled_window.set_max_content_height(5 * self.line_height)
        self.scrolled_window.set_min_content_width(35 * self.char_width)

    def update_visibility(self):
        if self.model.is_visible():
            self.show_all()
        else:
            self.hide()

    def position_is_visible(self):
        return ((self.y_position >= self.line_height - 1) and
            (self.y_position <= self.model.document_view.scrolled_window.get_allocated_height()) and
            (self.x_position >= 0) and
            (self.x_position <= self.main_window.preview_paned.get_allocated_width()))

    def get_height(self):
        return min(len(self.model.items), 5) * self.line_height + 20

    def get_width(self):
        width = 25 * self.char_width
        max_width = 35 * self.char_width
        while self.x_position <= self.main_window.preview_paned.get_allocated_width() - width - self.char_width:
            width += self.char_width
            if width == max_width:
                break
        return width

class DocumentAutocompleteItem(Gtk.Box):

    def __init__(self, command, offset=0):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.HORIZONTAL)

        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.START)

        self.command = command
        if offset != 0:
            command_text = '<b>' + GLib.markup_escape_text(command['command'][:offset]) + '</b>'
            command_text += GLib.markup_escape_text(command['command'][offset:])
        else:
            command_text = GLib.markup_escape_text(command['command'])

        self.dotlabels = filter(None, command['dotlabels'].split('###'))
        for dotlabel in self.dotlabels:
            command_text = command_text.replace('•', '<span alpha="60%">' + GLib.markup_escape_text(dotlabel) + '</span>', 1)

        self.label = Gtk.Label()
        self.label.set_markup(command_text)
        self.label.get_style_context().add_class('monospace')
        self.pack_start(self.label, True, True, 0)
        self.show_all()

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE


