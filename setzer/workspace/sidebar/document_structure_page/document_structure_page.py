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


class DocumentStructurePage(object):

    def __init__(self, workspace):
        self.view = document_structure_page_view.DocumentStructurePageView()
        self.document = None
        self.workspace = workspace

        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('root_state_change', self.on_root_state_change)

    def on_new_active_document(self, workspace, document):
        self.set_document()

    def on_root_state_change(self, workspace, root_state):
        self.set_document()

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
            if self.document != None and self.document.document_structure.view in self.view.vbox.get_children():
                self.view.vbox.remove(self.document.document_structure.view)
            self.document = document
            self.view.vbox.pack_start(self.document.document_structure.view, True, True, 0)
            self.view.show_all()


