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
from gi.repository import GObject

import os.path
import time
from operator import itemgetter

import setzer.workspace.sidebar.document_structure_page.document_structure_page_viewgtk as document_structure_page_view
import setzer.workspace.sidebar.document_structure_page.document_structure_page_presenter as document_structure_page_presenter
import setzer.workspace.sidebar.document_structure_page.document_structure_page_controller as document_structure_page_controller
import setzer.helpers.path as path_helpers
from setzer.app.service_locator import ServiceLocator
from setzer.helpers.timer import timer


class DocumentStructurePage(object):

    def __init__(self, workspace):
        self.view = document_structure_page_view.DocumentStructurePageView()

        self.document = None
        self.nodes = list()
        self.nodes_in_line = list()
        self.structure_hover_item = None
        self.structure_view_height = 0

        self.includes = list()
        self.integrated_includes = dict()
        self.files_hover_item = None
        self.files_view_height = 0

        self.labels = list()
        self.labels_hover_item = None
        self.labels_view_height = 0

        self.workspace = workspace

        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('root_state_change', self.on_root_state_change)

        self.sections = dict()
        self.scroll_to = None

        self.levels = {'part': 0, 'chapter': 1, 'section': 2, 'subsection': 3, 'subsubsection': 4, 'paragraph': 5, 'subparagraph': 6, 'file': 7}

        self.presenter = document_structure_page_presenter.DocumentStructurePagePresenter(self, self.view)
        self.controller = document_structure_page_controller.DocumentStructurePageController(self, self.view)

    def on_new_document(self, workspace, document):
        if document in self.integrated_includes:
            self.update_integrated_includes()
            self.update_sections()
            self.update_labels()

    def on_document_removed(self, workspace, document):
        if document in self.integrated_includes:
            self.update_integrated_includes()
            self.update_sections()
            self.update_labels()

    def on_new_active_document(self, workspace, document):
        self.set_document()

    def on_root_state_change(self, workspace, root_state):
        self.set_document()

    def on_buffer_changed(self, content, parameter):
        self.update_integrated_includes()
        self.update_sections()
        self.update_labels()

    def on_is_root_changed(self, document, parameter):
        self.update_integrated_includes()
        self.update_sections()
        self.update_labels()

    def set_document(self):
        if self.workspace.get_active_document() == None:
            document = None
        else:
            if self.workspace.root_document != None:
                document = self.workspace.root_document
            elif self.workspace.active_document.is_latex_document():
                document = self.workspace.active_document
            else:
                document = None
        self.update_items(document)

    def update_items(self, document):
        if document != self.document:
            if self.document != None:
                self.document.content.disconnect('buffer_changed', self.on_buffer_changed)
                self.document.disconnect('is_root_changed', self.on_is_root_changed)
            self.document = document
            self.document.content.connect('buffer_changed', self.on_buffer_changed)
            self.document.connect('is_root_changed', self.on_is_root_changed)
            self.update_integrated_includes()
            self.update_sections()
            self.update_labels()

    def update_integrated_includes(self):
        integrated_includes = dict()
        if self.document.get_is_root():
            for filename, offset in self.document.content.get_included_latex_files():
                filename = path_helpers.get_abspath(filename, self.document.get_dirname())
                document = self.workspace.get_document_by_filename(filename)
                if document:
                    integrated_includes[document] = (document, offset)
                    document.content.connect('buffer_changed', self.on_buffer_changed)
        for document in self.integrated_includes:
            if document not in integrated_includes:
                document.content.disconnect('buffer_changed', self.on_buffer_changed)
        self.integrated_includes = integrated_includes
        self.update_files_view()

    def get_includes(self):
        includes = list()
        for filename, offset in self.document.content.get_included_latex_files():
            filename = path_helpers.get_abspath(filename, self.document.get_dirname())
            document = self.workspace.get_document_by_filename(filename)
            if document and document in self.integrated_includes:
                includes.append({'filename': filename, 'offset': offset, 'document': document})
            else:
                includes.append({'filename': filename, 'offset': offset, 'document': None})
        return includes

    #@timer
    def update_sections(self):
        sections = dict()

        includes = self.get_includes()
        blocks = list()
        for block in self.document.content.get_blocks():
            while len(includes) > 0 and includes[0]['offset'] < block[0]:
                if includes[0]['document'] != None:
                    for block_included in includes[0]['document'].content.get_blocks():
                        if len(block_included) < 7:
                            block_included.append(includes[0]['document'].get_filename())
                        blocks.append(block_included)
                else:
                    file_block = [0, 0, 0, 0, 'file', os.path.basename(includes[0]['filename']), includes[0]['filename']]
                    blocks.append(file_block)
                del(includes[0])
            if len(block) < 7:
                block.append(self.document.get_filename())
            blocks.append(block)

        while len(includes) > 0:
            if includes[0]['document'] != None:
                for block in includes[0]['document'].content.get_blocks():
                    if len(block) < 7:
                        block.append(includes[0]['document'].get_filename())
                    blocks.append(block)
            else:
                file_block = [0, 0, 0, 0, 'file', includes[0]['filename'], includes[0]['filename']]
                blocks.append(file_block)
            del(includes[0])

        last_line = -1
        for block in blocks:
            if block[1] != None and block[4] in self.levels and block[2] != last_line:
                sections[block[2]] = {'filename': block[6], 'offset_start': block[0], 'starting_line': block[2], 'block': block}
                last_line = block[2]

        self.sections = sections
        self.update_structure_view()

    #@timer
    def update_structure_view(self):
        current_level = 0
        height = 0
        nodes = list()
        predecessor = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None}
        for section in self.sections.values():
            section_type = section['block'][4]
            level = self.levels[section_type]
            node = {'item': [section['filename'], section['starting_line'], section_type + '-symbolic', ' '.join(section['block'][5].splitlines())], 'children': list()}
            if predecessor[level] == None:
                nodes.append(node)
            else:
                predecessor[level]['children'].append(node)
            for i in range(level + 1, 8):
                predecessor[i] = node
            height += self.view.line_height

        if height != 0:
            height += 33
        self.structure_view_height = height
        self.nodes = nodes
        self.view.content_structure.set_size_request(-1, self.structure_view_height)
        self.set_structure_hover_item(None)
        self.view.content_structure.queue_draw()

    def update_files_view(self):
        self.includes = self.get_includes()
        self.files_view_height = (len(self.includes) + 1) * self.view.line_height + 33
        self.view.content_files.set_size_request(-1, self.files_view_height)
        self.set_files_hover_item(None)
        self.view.content_files.queue_draw()

    #@timer
    def update_labels(self):
        labels = list()
        for label in self.document.content.get_labels_with_offset():
            filename = self.document.get_filename()
            label.append(filename)
            labels.append(label)
        for document in self.integrated_includes:
            for label in document.content.get_labels_with_offset():
                filename = document.get_filename()
                label.append(filename)
                labels.append(label)
        labels.sort(key=lambda label: label[0].lower())
        self.labels = labels

        if len(labels) == 0:
            self.labels_view_height = 0
        else:
            self.labels_view_height = len(self.labels) * self.view.line_height + 33
        self.view.content_labels.set_size_request(-1, self.labels_view_height)
        self.set_labels_hover_item(None)
        self.view.content_labels.queue_draw()

    def set_structure_hover_item(self, item_num): 
        if self.structure_hover_item != item_num:
            self.structure_hover_item = item_num
            self.view.content_structure.queue_draw()

    def set_files_hover_item(self, item_num): 
        if self.files_hover_item != item_num:
            self.files_hover_item = item_num
            self.view.content_files.queue_draw()

    def set_labels_hover_item(self, item_num): 
        if self.labels_hover_item != item_num:
            self.labels_hover_item = item_num
            self.view.content_labels.queue_draw()

    def scroll_view(self, position, duration=0.2):
        adjustment = self.view.scrolled_window.get_vadjustment()
        self.scroll_to = {'position_start': adjustment.get_value(), 'position_end': position, 'time_start': time.time(), 'duration': duration}
        self.view.scrolled_window.set_kinetic_scrolling(False)
        GObject.timeout_add(15, self.presenter.do_scroll)


