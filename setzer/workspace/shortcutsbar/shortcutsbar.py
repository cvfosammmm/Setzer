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
        self.latex_shortcutsbar = ServiceLocator.get_main_window().latex_shortcutsbar
        self.bibtex_shortcutsbar = ServiceLocator.get_main_window().bibtex_shortcutsbar
        self.others_shortcutsbar = ServiceLocator.get_main_window().others_shortcutsbar

        self.latex_shortcutsbar.button_build_log.set_active(self.workspace.get_show_build_log())
        self.latex_shortcutsbar.button_build_log.connect('clicked', self.on_build_log_button_clicked)
        self.latex_shortcutsbar.button_build_log.get_child().set_sensitive(False)
        self.latex_shortcutsbar.button_search.connect('clicked', self.on_find_button_clicked)
        self.latex_shortcutsbar.button_replace.connect('clicked', self.on_find_replace_button_clicked)

        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('show_build_log_state_change', self.update_buttons)

        self.document = self.workspace.active_document
        if self.document != None:
            self.document.connect('changed', self.on_document_changed)
            self.document.search.connect('mode_changed', self.update_buttons)
            self.latex_shortcutsbar.wizard_button_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
            self.update_wizard_button()

    def on_document_removed(self, workspace=None, parameter=None):
        if self.workspace.active_document == None:
            self.document.disconnect('changed', self.update_buttons)
            self.document.search.disconnect('mode_changed', self.update_buttons)
            self.document == None

        self.update_buttons()

    def on_new_active_document(self, workspace=None, parameter=None):
        if self.document != None:
            self.document.disconnect('changed', self.on_document_changed)
            self.document.search.disconnect('mode_changed', self.update_buttons)

        self.document = self.workspace.active_document
        if self.document != None:
            self.document.connect('changed', self.on_document_changed)
            self.document.search.connect('mode_changed', self.update_buttons)
            self.latex_shortcutsbar.wizard_button_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
            self.update_wizard_button()

        self.update_buttons()

    def on_document_changed(self, workspace=None, parameter=None):
        self.latex_shortcutsbar.wizard_button_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        self.update_wizard_button()

    def update_wizard_button(self):
        if self.document == None: return

        if self.document.is_latex_document():
            if self.document.source_buffer.get_char_count() > 0:
                self.latex_shortcutsbar.wizard_button_revealer.set_reveal_child(False)
            else:
                self.latex_shortcutsbar.wizard_button_revealer.set_reveal_child(True)

    def update_buttons(self, workspace=None, parameter=None):
        if self.document == None: return

        if self.document.is_latex_document():
            self.latex_shortcutsbar.button_more.set_popover(self.document.context_menu.popover_more)
            self.latex_shortcutsbar.button_search.set_active(self.document.search.search_bar_mode == 'search')
            self.latex_shortcutsbar.button_replace.set_active(self.document.search.search_bar_mode == 'replace')
        else:
            self.latex_shortcutsbar.button_more.set_popover(None)

        show_build_log = self.workspace.get_show_build_log()
        self.latex_shortcutsbar.button_build_log.set_active(show_build_log)

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


