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

from setzer.app.service_locator import ServiceLocator


class WorkspacePresenter(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()

        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)

        self.activate_welcome_screen_mode()

    def on_new_document(self, workspace, document):
        if document.is_latex_document():
            self.main_window.latex_notebook.append_page(document.view)
        elif document.is_bibtex_document():
            self.main_window.bibtex_notebook.append_page(document.view)
        else:
            self.main_window.others_notebook.append_page(document.view)

    def on_document_removed(self, workspace, document):
        if document.is_latex_document():
            self.main_window.latex_notebook.remove(document.view)
        elif document.is_bibtex_document():
            self.main_window.bibtex_notebook.remove(document.view)
        else:
            self.main_window.others_notebook.remove(document.view)

        if self.workspace.active_document == None:
            self.activate_welcome_screen_mode()

    def on_new_active_document(self, workspace, document):
        if document.is_latex_document():
            notebook = self.main_window.latex_notebook
            notebook.set_current_page(notebook.page_num(document.view))
            document.view.source_view.grab_focus()
            self.activate_latex_documents_mode()
        elif document.is_bibtex_document():
            notebook = self.main_window.bibtex_notebook
            notebook.set_current_page(notebook.page_num(document.view))
            document.view.source_view.grab_focus()
            self.activate_bibtex_documents_mode()
        else:
            notebook = self.main_window.others_notebook
            notebook.set_current_page(notebook.page_num(document.view))
            document.view.source_view.grab_focus()
            self.activate_other_documents_mode()

    def activate_welcome_screen_mode(self):
        self.main_window.mode_stack.set_visible_child_name('welcome_screen')

    def activate_latex_documents_mode(self):
        self.main_window.mode_stack.set_visible_child_name('latex_documents')

    def activate_bibtex_documents_mode(self):
        self.main_window.mode_stack.set_visible_child_name('bibtex_documents')

    def activate_other_documents_mode(self):
        self.main_window.mode_stack.set_visible_child_name('other_documents')

    def focus_active_document(self):
        active_document = self.workspace.get_active_document()
        if active_document != None:
            active_document.view.source_view.grab_focus()


