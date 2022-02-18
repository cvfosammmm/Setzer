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

import setzer.document.document_structure.document_structure_viewgtk as document_structure_view
from setzer.helpers.observable import Observable


class DocumentStructure(Observable):

    def __init__(self, document):
        Observable.__init__(self)

        self.marks_start = dict()
        self.sections = dict()
        self.scroll_to = None

        self.levels = {'part': 0, 'chapter': 1, 'section': 2, 'subsection': 3, 'subsubsection': 4, 'paragraph': 5, 'subparagraph': 6}

        self.view = document_structure_view.DocumentStructureView()

        self.view.connect('row-activated', self.row_activated)
        self.view.connect('draw', self.draw)

        self.document = document
        self.document.content.connect('buffer_changed', self.on_buffer_changed)

    def on_buffer_changed(self, content, parameter):
        self.update_sections()

    def update_sections(self):
        self.sections = dict()
        last_line = -1

        for block in self.document.content.get_blocks():
            if block[1] != None and block[4] in self.levels and block[2] != last_line:
                self.sections[block[2]] = {'offset_start': block[0], 'starting_line': block[2], 'block': block}
                last_line = block[2]

        self.update_tree_store()

    def update_tree_store(self):
        offset = self.view.get_vadjustment().get_value()
        self.view.tree_store.clear()
        current_level = 0
        predecessor_iter = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None}
        for section in self.sections.values():
            section_type = section['block'][4]
            level = self.levels[section_type]
            tree_iter = self.view.tree_store.append(predecessor_iter[level], [section['starting_line'], section_type + '-symbolic', ' '.join(section['block'][5].splitlines())])
            for i in range(level + 1, 8):
                predecessor_iter[i] = tree_iter
        self.view.expand_all()
        self.scroll_to = offset

    def row_activated(self, tree_view, path, column):
        line_number = self.view.tree_store[path][0]
        self.document.content.place_cursor(line_number)
        self.document.content.scroll_cursor_onscreen()

    def draw(self, widget, cr):
        if self.scroll_to != None:
            self.view.get_vadjustment().set_value(self.scroll_to)
            self.scroll_to = None
        return False


