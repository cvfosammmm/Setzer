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
from gi.repository import Gtk
from gi.repository import Gdk

import setzer.workspace.sidebar.document_structure_page.structure_widget as structure_widget
import setzer.workspace.sidebar.document_structure_page.labels_viewgtk as labels_section_view


class LabelsSection(structure_widget.StructureWidget):

    def __init__(self, data_provider, labels):
        structure_widget.StructureWidget.__init__(self, data_provider)

        self.headline_labels = labels
        self.view = labels_section_view.LabelsSectionView()
        self.init_view()

        self.labels = list()

    def on_button_press(self, drawing_area, event):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1 and event.state & modifiers == 0:
            item_num = max(0, min(int((event.y - 9) // self.view.line_height), len(self.labels) - 1))

            document = self.labels[item_num][2]
            line_number = document.content.get_line_number_at_offset(self.labels[item_num][1])
            self.data_provider.workspace.set_active_document(document)
            document.content.place_cursor(line_number)
            document.content.scroll_cursor_onscreen()
            self.data_provider.workspace.active_document.view.source_view.grab_focus()

    #@timer
    def update_items(self, *params):
        labels = list()
        for label in self.data_provider.document.get_labels_with_offset():
            document = self.data_provider.document
            label.append(document)
            labels.append(label)
        for document in self.data_provider.integrated_includes:
            for label in document.get_labels_with_offset():
                label.append(document)
                labels.append(label)
        labels.sort(key=lambda label: label[0].lower())
        self.labels = labels

        if len(labels) == 0:
            self.height = 0
            self.view.hide()
            self.headline_labels['inline'].hide()
            self.headline_labels['overlay'].hide()
        else:
            self.height = len(self.labels) * self.view.line_height + 33
            self.view.show()
            self.headline_labels['inline'].show()
            self.headline_labels['overlay'].show()
        self.view.set_size_request(-1, self.height)
        self.set_hover_item(None)
        self.view.queue_draw()

    def draw(self, drawing_area, ctx):
        if len(self.labels) == 0:
            return True

        first_line, last_line = self.get_first_line_last_line(ctx)
        self.drawing_setup(ctx)
        self.draw_background(ctx)

        for count, label in enumerate(self.labels):
            if count >= first_line and count <= last_line:
                self.draw_hover_background(ctx, count)
                self.draw_icon(ctx, 'tag-symbolic', 9, count)
                self.draw_text(ctx, 35, count, label[0])


