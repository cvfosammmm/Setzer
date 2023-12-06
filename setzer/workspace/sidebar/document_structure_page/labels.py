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
from gi.repository import Gtk, Gdk

import setzer.workspace.sidebar.document_structure_page.labels_viewgtk as labels_section_view


class LabelsSection(object):

    def __init__(self, data_provider, labels):
        self.data_provider = data_provider
        self.data_provider.connect('data_updated', self.update_items)

        self.headline_labels = labels
        self.view = labels_section_view.LabelsSectionView(self)

        self.labels = list()

    def on_button_press(self, controller, n_press, x, y):
        if n_press == 1:
            item_num = max(0, min(int((y - 9) // self.view.line_height), len(self.labels) - 1))

            document = self.labels[item_num][2]
            line_number = document.source_buffer.get_iter_at_offset(self.labels[item_num][1]).get_line()
            self.data_provider.workspace.set_active_document(document)
            document.place_cursor(line_number)
            document.scroll_cursor_onscreen()
            self.data_provider.workspace.active_document.view.source_view.grab_focus()

    #@timer
    def update_items(self, *params):
        labels = list()
        for label in self.data_provider.document.parser.symbols['labels_with_offset']:
            document = self.data_provider.document
            label.append(document)
            labels.append(label)
        for document in self.data_provider.integrated_includes:
            for label in document.parser.symbols['labels_with_offset']:
                label.append(document)
                labels.append(label)
        labels.sort(key=lambda label: label[0].lower())
        self.labels = labels

        if len(labels) == 0:
            self.height = 0
        else:
            self.height = len(labels) * self.view.line_height + 33

        self.view.set_visible(len(labels) != 0)
        self.headline_labels['inline'].set_visible(len(labels) != 0)

        self.view.set_size_request(-1, self.height)
        self.view.set_hover_item(None)
        self.view.queue_draw()


