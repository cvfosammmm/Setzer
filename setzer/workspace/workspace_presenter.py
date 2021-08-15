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
    ''' Mediator between workspace and view. '''

    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.workspace.register_observer(self)

        self.preview_animating = False
        self.build_log_animation_id = None
        self.activate_welcome_screen_mode()

        self.main_window.sidebar_paned.set_target_position(self.workspace.sidebar_position)
        self.main_window.preview_paned.set_target_position(self.workspace.preview_position)
        self.main_window.build_log_paned.set_target_position(self.workspace.build_log_position)

        def on_window_state(widget, event): self.on_realize()
        self.main_window.connect('draw', on_window_state)

    '''
    *** notification handlers, get called by observed workspace
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_document':
            document = parameter
            document.set_dark_mode(ServiceLocator.get_is_dark_mode())

            if document.is_latex_document():
                self.main_window.latex_notebook.append_page(document.view)
            elif document.is_bibtex_document():
                self.main_window.bibtex_notebook.append_page(document.view)
            else:
                self.main_window.others_notebook.append_page(document.view)

        if change_code == 'document_removed':
            document = parameter

            if document.is_latex_document():
                self.main_window.latex_notebook.remove(document.view)
            elif document.is_bibtex_document():
                self.main_window.bibtex_notebook.remove(document.view)
            else:
                self.main_window.others_notebook.remove(document.view)

            if self.workspace.active_document == None:
                self.activate_welcome_screen_mode()

        if change_code == 'new_active_document':
            document = parameter

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

        if change_code == 'new_inactive_document':
            document = parameter

            if document.is_latex_document():
                try:
                    self.main_window.preview_paned_overlay.remove(document.autocomplete.view)
                except AttributeError: pass

        if change_code == 'set_show_sidebar':
            self.main_window.sidebar_paned.animate(parameter, True)

        if change_code == 'set_show_preview_or_help':
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
            self.main_window.preview_paned.animate(self.workspace.show_preview or self.workspace.show_help, True)

        if change_code == 'show_build_log_state_change':
            self.main_window.build_log_paned.animate(self.workspace.show_build_log, True)

        if change_code == 'set_dark_mode':
            ServiceLocator.get_settings().gtksettings.get_default().set_property('gtk-application-prefer-dark-theme', parameter)

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

    def on_realize(self, view=None, cr=None, user_data=None):
        if self.main_window.sidebar_paned.is_initialized == False:
            self.main_window.sidebar_paned.animate(self.workspace.show_sidebar, False)
            self.main_window.headerbar.sidebar_toggle.set_active(self.main_window.sidebar_paned.is_visible)
            self.main_window.sidebar_paned.is_initialized = True

        if self.main_window.preview_paned.is_initialized == False:
            if self.workspace.show_preview:
                self.main_window.preview_help_stack.set_visible_child_name('preview')
            elif self.workspace.show_help:
                self.main_window.preview_help_stack.set_visible_child_name('help')

            if self.workspace.show_preview or self.workspace.show_help:
                if self.workspace.show_sidebar == False and self.main_window.sidebar.get_allocated_width() > 1:
                    self.main_window.preview_paned.set_target_position(self.main_window.preview_paned.target_position - self.main_window.sidebar.get_allocated_width() - 1)
                else:
                    self.main_window.preview_paned.set_target_position(self.main_window.preview_paned.target_position - self.main_window.sidebar.get_allocated_width() + 216)
            self.main_window.preview_paned.animate(self.workspace.show_preview or self.workspace.show_help, False)
            self.main_window.headerbar.preview_toggle.set_active(self.main_window.preview_paned.is_visible and self.workspace.show_preview)
            self.main_window.headerbar.help_toggle.set_active(self.main_window.preview_paned.is_visible and self.workspace.show_help)
            self.main_window.preview_paned.is_initialized = True

        if self.main_window.build_log_paned.is_initialized == False:
            self.main_window.build_log_paned.animate(self.workspace.get_show_build_log(), False)
            self.main_window.build_log_paned.is_initialized = True


