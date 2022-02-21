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

import setzer.workspace.sidebar.document_structure_page.document_structure_page_viewgtk as document_structure_page_view
import setzer.helpers.path as path_helpers
from setzer.app.service_locator import ServiceLocator
from setzer.helpers.timer import timer


class DocumentStructurePage(object):

    def __init__(self, workspace):
        self.view = document_structure_page_view.DocumentStructurePageView()

        self.document = None
        self.integrated_includes = dict()

        self.workspace = workspace

        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('root_state_change', self.on_root_state_change)

        self.sections = dict()
        self.scroll_to = None

        self.levels = {'part': 0, 'chapter': 1, 'section': 2, 'subsection': 3, 'subsubsection': 4, 'paragraph': 5, 'subparagraph': 6, 'file': 7}

        self.view.tree_view.connect('row-activated', self.row_activated)
        self.view.tree_view.connect('draw', self.draw)

    def on_new_document(self, workspace, document):
        if document in self.integrated_includes:
            self.update_integrated_includes()
            self.update_sections()

    def on_document_removed(self, workspace, document):
        if document in self.integrated_includes:
            self.update_integrated_includes()
            self.update_sections()

    def on_new_active_document(self, workspace, document):
        self.set_document()

    def on_root_state_change(self, workspace, root_state):
        self.set_document()

    def on_buffer_changed(self, content, parameter):
        self.update_integrated_includes()
        self.update_sections()

    def on_is_root_changed(self, document, parameter):
        self.update_integrated_includes()
        self.update_sections()

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
                    file_block = [0, 0, 0, 0, 'file', includes[0]['filename'], includes[0]['filename']]
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
        self.update_tree_store()

    #@timer
    def update_tree_store(self):
        offset = self.view.tree_view.get_vadjustment().get_value()
        self.view.tree_store.clear()
        current_level = 0
        predecessor_iter = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None}
        for section in self.sections.values():
            section_type = section['block'][4]
            level = self.levels[section_type]
            tree_iter = self.view.tree_store.append(predecessor_iter[level], [section['filename'], section['starting_line'], section_type + '-symbolic', ' '.join(section['block'][5].splitlines())])
            for i in range(level + 1, 8):
                predecessor_iter[i] = tree_iter
        self.view.tree_view.expand_all()
        self.scroll_to = offset

    def draw(self, widget, cr):
        if self.scroll_to != None:
            self.view.tree_view.get_vadjustment().set_value(self.scroll_to)
            self.scroll_to = None
        return False

    def row_activated(self, tree_view, path, column):
        filename = self.view.tree_store[path][0]
        line_number = self.view.tree_store[path][1]
        document = self.workspace.open_document_by_filename(filename)
        document.content.place_cursor(line_number)
        document.content.scroll_cursor_onscreen()


