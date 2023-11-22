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
from setzer.app.font_manager import FontManager

import os.path


class WorkspacePresenter(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.settings = ServiceLocator.get_settings()

        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('new_inactive_document', self.on_new_inactive_document)
        self.workspace.connect('root_state_change', self.on_root_state_change)
        self.workspace.connect('set_show_symbols_or_document_structure', self.on_set_show_symbols_or_document_structure)
        self.workspace.connect('set_show_preview_or_help', self.on_set_show_preview_or_help)
        self.workspace.connect('show_build_log_state_change', self.on_show_build_log_state_change)
        self.settings.connect('settings_changed', self.on_settings_changed)

        self.main_window.mode_stack.set_visible_child_name('welcome_screen')
        self.update_font()
        self.update_colors()
        self.setup_paneds()

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter

        if item in ['font_string', 'use_system_font']:
            self.update_font()

        if item == 'color_scheme':
            self.update_colors()

    def on_new_document(self, workspace, document):
        self.main_window.document_stack.append_page(document.view)

    def on_document_removed(self, workspace, document):
        self.main_window.document_stack.remove_page(self.main_window.document_stack.page_num(document.view))

        if self.workspace.active_document == None:
            self.main_window.mode_stack.set_visible_child_name('welcome_screen')

    def on_new_active_document(self, workspace, document):
        self.main_window.mode_stack.set_visible_child_name('documents')
        self.main_window.document_stack.set_current_page(self.main_window.document_stack.page_num(document.view))
        self.focus_active_document()

        if document.is_latex_document():
            try: self.main_window.preview_paned_overlay.add_overlay(document.autocomplete.widget.view)
            except AttributeError: pass

        self.update_sidebar_visibility(False)
        self.update_build_log_visibility(False)
        self.update_preview_help_visibility(False)

    def on_root_state_change(self, workspace, state):
        self.update_build_log_visibility(False)
        self.update_preview_help_visibility(False)

    def on_new_inactive_document(self, workspace, document):
        if document.is_latex_document():
            try: self.main_window.preview_paned_overlay.remove_overlay(document.autocomplete.widget.view)
            except AttributeError: pass

    def on_set_show_symbols_or_document_structure(self, workspace):
        if self.workspace.show_symbols:
            self.main_window.sidebar.set_visible_child_name('symbols')
        elif self.workspace.show_document_structure:
            self.main_window.sidebar.set_visible_child_name('document_structure')
        self.focus_active_document()

        self.update_sidebar_visibility()

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
        self.update_preview_help_visibility()

    def on_show_build_log_state_change(self, workspace, show_build_log):
        self.update_build_log_visibility()

    def update_sidebar_visibility(self, animate=True):
        sidebar_visible_for_latex_docs = self.workspace.show_symbols or self.workspace.show_document_structure
        show_sidebar = self.workspace.get_active_latex_document() and sidebar_visible_for_latex_docs
        self.main_window.sidebar_paned.set_show_widget(show_sidebar)
        self.main_window.sidebar_paned.animate(animate)

    def update_build_log_visibility(self, animate=True):
        show_build_log = self.workspace.get_root_or_active_latex_document() and self.workspace.show_build_log
        self.main_window.build_log_paned.set_show_widget(show_build_log)
        self.main_window.build_log_paned.animate(animate)

    def update_preview_help_visibility(self, animate=True):
        preview_help_visible_for_latex_docs = self.workspace.show_preview or self.workspace.show_help
        show_preview_help = self.workspace.get_root_or_active_latex_document() and preview_help_visible_for_latex_docs
        self.main_window.preview_paned.set_show_widget(show_preview_help)
        self.main_window.preview_paned.animate(animate)

    def focus_active_document(self):
        active_document = self.workspace.get_active_document()
        if active_document != None:
            active_document.view.source_view.grab_focus()

    def update_font(self):
        if self.settings.get_value('preferences', 'use_system_font'):
            FontManager.font_string = FontManager.default_font_string
        else:
            FontManager.font_string = self.settings.get_value('preferences', 'font_string')
        FontManager.propagate_font_setting()

    def update_colors(self):
        name = self.settings.get_value('preferences', 'color_scheme')
        path = os.path.join(ServiceLocator.get_resources_path(), 'themes', name + '.css')
        self.main_window.css_provider_colors.load_from_path(path)
        try: self.workspace.help_panel.update_colors()
        except AttributeError: pass

    def setup_paneds(self):
        sidebar_visible_for_latex_docs = self.workspace.show_symbols or self.workspace.show_document_structure
        show_sidebar = self.workspace.get_active_latex_document() and sidebar_visible_for_latex_docs
        preview_help_visible_for_latex_docs = self.workspace.show_preview or self.workspace.show_help
        show_preview_help = self.workspace.get_root_or_active_latex_document() and preview_help_visible_for_latex_docs
        show_build_log = self.workspace.get_root_or_active_latex_document() and self.workspace.get_show_build_log()

        sidebar_position = self.workspace.settings.get_value('window_state', 'sidebar_paned_position')
        preview_position = self.workspace.settings.get_value('window_state', 'preview_paned_position')
        build_log_position = self.workspace.settings.get_value('window_state', 'build_log_paned_position')

        if sidebar_position in [None, -1]: self.main_window.sidebar_paned.set_start_on_first_show()
        if preview_position in [None, -1]: self.main_window.preview_paned.set_center_on_first_show()
        if build_log_position in [None, -1]: self.main_window.build_log_paned.set_end_on_first_show()

        if self.workspace.show_symbols: self.main_window.sidebar.set_visible_child_name('symbols')
        elif self.workspace.show_document_structure: self.main_window.sidebar.set_visible_child_name('document_structure')

        if self.workspace.show_preview: self.main_window.preview_help_stack.set_visible_child_name('preview')
        elif self.workspace.show_help: self.main_window.preview_help_stack.set_visible_child_name('help')

        self.main_window.sidebar_paned.first_set_show_widget(show_sidebar)
        self.main_window.preview_paned.first_set_show_widget(show_preview_help)
        self.main_window.build_log_paned.first_set_show_widget(show_build_log)

        self.main_window.sidebar_paned.set_target_position(sidebar_position)
        self.main_window.preview_paned.set_target_position(preview_position)
        self.main_window.build_log_paned.set_target_position(build_log_position)

        self.main_window.headerbar.symbols_toggle.set_active(self.workspace.show_symbols)
        self.main_window.headerbar.document_structure_toggle.set_active(self.workspace.show_document_structure)
        self.main_window.headerbar.preview_toggle.set_active(self.workspace.show_preview)
        self.main_window.headerbar.help_toggle.set_active(self.workspace.show_help)


