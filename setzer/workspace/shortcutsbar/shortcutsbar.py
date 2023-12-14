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
from gi.repository import Gtk

from setzer.app.service_locator import ServiceLocator


class Shortcutsbar(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.view = ServiceLocator.get_main_window().shortcutsbar

        self.view.button_build_log.set_active(self.workspace.get_show_build_log())
        self.view.button_build_log.connect('clicked', self.on_build_log_button_clicked)
        self.view.button_build_log.get_child().set_sensitive(False)

        self.view.button_search.connect('clicked', self.on_find_button_clicked)
        self.view.button_replace.connect('clicked', self.on_find_replace_button_clicked)

        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('show_build_log_state_change', self.update_buttons)
        self.workspace.connect('root_state_change', self.on_root_state_change)

        self.preview_paned = ServiceLocator.get_main_window().preview_paned
        self.width = 0
        self.preview_paned.connect('notify::position', self.on_paned_position_changed)

        self.document = self.workspace.active_document
        if self.document != None:
            self.document.connect('changed', self.on_document_changed)
            self.document.search.connect('mode_changed', self.update_buttons)
            self.update_wizard_button()

    def on_document_removed(self, workspace=None, parameter=None):
        if self.workspace.active_document == None:
            self.document.disconnect('changed', self.update_buttons)
            self.document.search.disconnect('mode_changed', self.update_buttons)
            self.document = None

        self.update_buttons()

    def on_new_active_document(self, workspace=None, parameter=None):
        if self.document != None:
            self.document.disconnect('changed', self.on_document_changed)
            self.document.search.disconnect('mode_changed', self.update_buttons)

        self.document = self.workspace.active_document
        if self.document != None:
            self.document.connect('changed', self.on_document_changed)
            self.document.search.connect('mode_changed', self.update_buttons)
            self.update_wizard_button()

        self.update_buttons()

    def on_root_state_change(self, workspace, state):
        self.update_buttons()

    def on_paned_position_changed(self, paned, position=None):
        self.width = paned.get_position()
        self.update_wizard_button(animate=False)

    def on_document_changed(self, workspace=None, parameter=None):
        self.update_wizard_button(animate=True)

    def update_wizard_button(self, animate=False):
        if self.document == None: return

        if self.document.is_latex_document():
            self.view.wizard_button.set_visible(True)

            is_visible = self.document.source_buffer.get_char_count() == 0 and self.width > 675
            if is_visible and animate == False:
                self.view.wizard_button_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
                self.view.wizard_button_revealer.set_reveal_child(True)
                self.view.wizard_button_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
                self.view.wizard_button_revealer.set_visible(True)
            elif is_visible:
                self.view.wizard_button_revealer.set_visible(True)
                self.view.wizard_button_revealer.set_reveal_child(True)
            elif animate == False:
                self.view.wizard_button_revealer.set_visible(False)
            else:
                self.view.wizard_button_revealer.set_reveal_child(False)
        else:
            self.view.wizard_button.set_visible(False)

    def update_buttons(self, workspace=None, parameter=None):
        if self.document == None: return

        self.view.button_search.set_active(self.document.search.search_bar_mode == 'search')
        self.view.button_replace.set_active(self.document.search.search_bar_mode == 'replace')

        is_latex = self.document.is_latex_document()
        self.view.beamer_button.set_visible(is_latex)
        self.view.bibliography_button.set_visible(is_latex)
        self.view.text_button.set_visible(is_latex)
        self.view.quotes_button.set_visible(is_latex)
        self.view.math_button.set_visible(is_latex)
        self.view.insert_object_button.set_visible(is_latex)
        self.view.italic_button.set_visible(is_latex)
        self.view.bold_button.set_visible(is_latex)
        self.view.document_button.set_visible(is_latex)

        root_or_active_latex = self.workspace.get_root_or_active_latex_document()
        self.view.button_build_log.set_active(self.workspace.get_show_build_log())
        self.view.button_build_log.set_sensitive(root_or_active_latex)
        self.view.button_build_log.set_visible(root_or_active_latex)

    def on_build_log_button_clicked(self, toggle_button, parameter=None):
        self.workspace.set_show_build_log(toggle_button.get_active())

    def on_find_button_clicked(self, button=None):
        if button.get_active():
            self.workspace.actions.start_search()
        else:
            self.workspace.actions.stop_search()

    def on_find_replace_button_clicked(self, button=None):
        if button.get_active():
            self.workspace.actions.start_search_and_replace()
        else:
            self.workspace.actions.stop_search()


