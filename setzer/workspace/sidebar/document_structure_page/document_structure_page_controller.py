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


class DocumentStructurePageController(object):
    
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.scrolled_window.connect('enter-notify-event', self.on_enter)
        self.view.scrolled_window.connect('motion-notify-event', self.on_hover)
        self.view.scrolled_window.connect('leave-notify-event', self.on_leave)

        self.view.content_widgets['structure'].connect('button-press-event', self.on_button_press_structure)
        self.view.content_widgets['files'].connect('button-press-event', self.on_button_press_files)
        self.view.content_widgets['labels'].connect('button-press-event', self.on_button_press_labels)

        self.view.vbox.connect('size-allocate', self.on_scroll_or_resize)
        self.view.scrolled_window.get_vadjustment().connect('value-changed', self.on_scroll_or_resize)
        self.view.vbox.connect('realize', self.on_scroll_or_resize)

        self.view.next_button.connect('clicked', self.on_next_button_clicked)
        self.view.prev_button.connect('clicked', self.on_prev_button_clicked)

    def on_enter(self, widget, event):
        self.update_hover_state(event)

    def on_hover(self, widget, event):
        self.update_hover_state(event)

    def on_leave(self, widget, event):
        self.model.set_structure_hover_item(None)
        self.model.set_files_hover_item(None)
        self.model.set_labels_hover_item(None)

    def on_scroll_or_resize(self, *args):
        label_offsets = self.get_label_offsets()
        scrolling_offset = self.view.scrolled_window.get_vadjustment().get_value()

        self.view.prev_button.set_sensitive(scrolling_offset != 0)
        self.view.next_button.set_sensitive(scrolling_offset < label_offsets[-1] and scrolling_offset < self.view.content_vbox.get_allocated_height() - self.view.scrolled_window.get_allocated_height())

        self.update_labels()

    def update_labels(self):
        tabs_height = self.view.tabs_box.get_allocated_height()
        scrolling_offset = self.view.scrolled_window.get_vadjustment().get_value()

        self.view.tabs_box.get_style_context().remove_class('no-border')
        for label_name, label_offset in zip(self.view.labels, self.get_label_offsets()):
            margin_top = max(0, label_offset - int(scrolling_offset))
            self.view.labels[label_name]['overlay'].set_margin_top(margin_top)

            if margin_top > 0 and margin_top <= tabs_height:
                self.view.tabs_box.get_style_context().add_class('no-border')

    def update_hover_state(self, event):
        tabs_height = self.view.tabs_box.get_allocated_height()
        label_height = self.view.labels['labels']['inline'].get_allocated_height()
        structure_label_height = self.view.labels['structure']['inline'].get_allocated_height()
        structure_view_offset = self.model.files_view_height
        if self.model.structure_view_height:
            structure_view_offset += structure_label_height
        labels_view_offset = structure_view_offset + self.model.structure_view_height
        if self.model.labels_view_height:
            labels_view_offset += label_height

        scrolling_offset = self.view.scrolled_window.get_vadjustment().get_value()
        pointer_offset = scrolling_offset + event.y - 9
        offset = int((scrolling_offset + event.y - 9) // self.view.line_height)
        if pointer_offset >= 0 and pointer_offset <= self.model.files_view_height:
            offset = int(pointer_offset // self.view.line_height)
            self.model.set_structure_hover_item(None)
            self.model.set_files_hover_item(offset)
            self.model.set_labels_hover_item(None)
        elif pointer_offset >= structure_view_offset and pointer_offset <= structure_view_offset + self.model.structure_view_height:
            pointer_offset -= structure_view_offset
            offset = int(pointer_offset // self.view.line_height)
            self.model.set_structure_hover_item(offset)
            self.model.set_files_hover_item(None)
            self.model.set_labels_hover_item(None)
        elif pointer_offset >= labels_view_offset and pointer_offset <= labels_view_offset + self.model.labels_view_height:
            pointer_offset -= labels_view_offset
            offset = int(pointer_offset // self.view.line_height)
            self.model.set_structure_hover_item(None)
            self.model.set_files_hover_item(None)
            self.model.set_labels_hover_item(offset)
        else:
            self.model.set_structure_hover_item(None)
            self.model.set_files_hover_item(None)
            self.model.set_labels_hover_item(None)

    def on_button_press_structure(self, drawing_area, event):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1 and event.state & modifiers == 0:
            item_num = max(0, min(int((event.y - 9) // self.view.line_height), len(self.model.nodes_in_line) - 1))
            item = self.model.nodes_in_line[item_num]['item']

            filename = item[0]
            line_number = item[1]
            document = self.model.workspace.open_document_by_filename(filename)
            document.content.place_cursor(line_number)
            document.content.scroll_cursor_onscreen()
            self.model.workspace.active_document.view.source_view.grab_focus()

    def on_button_press_files(self, drawing_area, event):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1 and event.state & modifiers == 0:
            item_num = max(0, min(int((event.y - 9) // self.view.line_height), len(self.model.includes)))

            if item_num == 0:
                filename = self.model.document.get_filename()
            else:
                filename = self.model.includes[item_num - 1]['filename']
            document = self.model.workspace.open_document_by_filename(filename)
            document.content.scroll_cursor_onscreen()
            self.model.workspace.active_document.view.source_view.grab_focus()

    def on_button_press_labels(self, drawing_area, event):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1 and event.state & modifiers == 0:
            item_num = max(0, min(int((event.y - 9) // self.view.line_height), len(self.model.labels) - 1))

            filename = self.model.labels[item_num][2]
            document = self.model.workspace.open_document_by_filename(filename)
            line_number = document.content.get_line_number_at_offset(self.model.labels[item_num][1])
            document.content.place_cursor(line_number)
            document.content.scroll_cursor_onscreen()
            self.model.workspace.active_document.view.source_view.grab_focus()

    def on_next_button_clicked(self, button):
        scrolling_offset = self.view.scrolled_window.get_vadjustment().get_value()

        for label_offset in self.get_label_offsets():
            if scrolling_offset < label_offset:
                self.model.scroll_view(label_offset)
                break

    def on_prev_button_clicked(self, button):
        scrolling_offset = self.view.scrolled_window.get_vadjustment().get_value()

        for label_offset in reversed([0] + self.get_label_offsets()):
            if scrolling_offset > label_offset:
                self.model.scroll_view(label_offset)
                break

    def get_label_offsets(self):
        offsets = list()
        offset = self.view.tabs_box.get_allocated_height()
        labels = [label['inline'] for label in self.view.labels.values()]
        for child in self.view.content_vbox.get_children():
            if child in labels:
                offsets.append(offset)
            if child.is_visible():
                offset += child.get_allocated_height()
        return offsets


