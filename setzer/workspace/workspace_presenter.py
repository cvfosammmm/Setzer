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

from setzer.app.service_locator import ServiceLocator


class WorkspacePresenter(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()

        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('new_inactive_document', self.on_new_inactive_document)
        self.workspace.connect('set_show_symbols_or_document_structure', self.on_set_show_symbols_or_document_structure)
        self.workspace.connect('set_show_preview_or_help', self.on_set_show_preview_or_help)
        self.workspace.connect('show_build_log_state_change', self.on_show_build_log_state_change)
        self.workspace.connect('set_dark_mode', self.on_set_dark_mode)

        self.activate_welcome_screen_mode()
        self.setup_paneds()

    def on_new_document(self, workspace, document):
        document.set_dark_mode(ServiceLocator.get_is_dark_mode())

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
            try:
                self.main_window.preview_paned_overlay.add_overlay(document.autocomplete.view)
                document.autocomplete.update()
            except AttributeError: pass

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

    def on_new_inactive_document(self, workspace, document):
        if document.is_latex_document():
            try:
                self.main_window.preview_paned_overlay.remove(document.autocomplete.view)
            except AttributeError: pass

    def on_set_show_symbols_or_document_structure(self, workspace):
        if self.workspace.show_symbols:
            self.main_window.sidebar.set_visible_child_name('symbols')
        elif self.workspace.show_document_structure:
            self.main_window.sidebar.set_visible_child_name('document_structure')
        self.focus_active_document()
        self.main_window.sidebar_paned.set_show_widget(self.workspace.show_symbols or self.workspace.show_document_structure)
        self.main_window.sidebar_paned.animate(True)

    def on_set_show_preview_or_help(self, workspace):
        if self.workspace.show_preview:
            self.main_window.preview_help_stack.set_visible_child_name('preview')
            self.focus_active_document()
        elif self.workspace.show_help:
            self.main_window.preview_help_stack.set_visible_child_name('help')
            if self.main_window.help_panel.stack.get_visible_child_name() == 'search':
                self.main_window.help_panel.search_entry.set_text('')
                self.main_window.help_panel.search_entry.grab_focus()
            else:
                self.focus_active_document()
        else:
            self.focus_active_document()
        self.main_window.preview_paned.set_show_widget(self.workspace.show_preview or self.workspace.show_help)
        self.main_window.preview_paned.animate(True)

    def on_show_build_log_state_change(self, workspace, show_build_log):
        self.main_window.build_log_paned.set_show_widget(self.workspace.show_build_log)
        self.main_window.build_log_paned.animate(True)

    def on_set_dark_mode(self, workspace, darkmode_enabled):
        settings = ServiceLocator.get_settings()
        settings.gtksettings.get_default().set_property('gtk-application-prefer-dark-theme', darkmode_enabled)

    def activate_welcome_screen_mode(self):
        self.workspace.welcome_screen.activate()
        self.main_window.mode_stack.set_visible_child_name('welcome_screen')

    def activate_latex_documents_mode(self):
        self.workspace.welcome_screen.deactivate()
        self.main_window.mode_stack.set_visible_child_name('latex_documents')

    def activate_bibtex_documents_mode(self):
        self.workspace.welcome_screen.deactivate()
        self.main_window.mode_stack.set_visible_child_name('bibtex_documents')

    def activate_other_documents_mode(self):
        self.workspace.welcome_screen.deactivate()
        self.main_window.mode_stack.set_visible_child_name('other_documents')

    def focus_active_document(self):
        active_document = self.workspace.get_active_document()
        if active_document != None:
            active_document.view.source_view.grab_focus()

    def setup_paneds(self):
        if self.workspace.show_document_structure:
            self.main_window.sidebar.set_visible_child_name('document_structure')
        elif self.workspace.show_symbols:
            self.main_window.sidebar.set_visible_child_name('symbols')

        if self.workspace.show_preview:
            self.main_window.preview_help_stack.set_visible_child_name('preview')
        elif self.workspace.show_help:
            self.main_window.preview_help_stack.set_visible_child_name('help')

        show_sidebar = (self.workspace.show_symbols or self.workspace.show_document_structure)
        self.main_window.sidebar_paned.set_show_widget(show_sidebar)
        self.main_window.preview_paned.set_show_widget(self.workspace.show_preview or self.workspace.show_help)
        self.main_window.build_log_paned.set_show_widget(self.workspace.get_show_build_log())

        preview_position = self.workspace.preview_position
        if self.workspace.show_preview or self.workspace.show_help:
            if show_sidebar == False:
                preview_position += - 253
            else:
                preview_position += self.workspace.sidebar_position - 252
        self.main_window.preview_paned.set_target_position(preview_position)
        self.main_window.sidebar_paned.set_target_position(self.workspace.sidebar_position)
        self.main_window.build_log_paned.set_target_position(self.workspace.build_log_position)

        self.main_window.headerbar.symbols_toggle.set_active(self.workspace.show_symbols)
        self.main_window.headerbar.document_structure_toggle.set_active(self.workspace.show_document_structure)
        self.main_window.headerbar.preview_toggle.set_active(self.workspace.show_preview)
        self.main_window.headerbar.help_toggle.set_active(self.workspace.show_help)


