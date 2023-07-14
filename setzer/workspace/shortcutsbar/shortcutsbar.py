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


class Shortcutsbar(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.latex_shortcutsbar = ServiceLocator.get_main_window().latex_shortcutsbar
        self.bibtex_shortcutsbar = ServiceLocator.get_main_window().bibtex_shortcutsbar
        self.others_shortcutsbar = ServiceLocator.get_main_window().others_shortcutsbar

        self.latex_shortcutsbar.button_build_log.set_active(self.workspace.get_show_build_log())
        self.latex_shortcutsbar.button_build_log.connect('clicked', self.on_build_log_button_clicked)
        self.latex_shortcutsbar.button_build_log.get_child().set_sensitive(False)

        self.workspace.connect('document_removed', self.update_document)
        self.workspace.connect('new_active_document', self.update_document)
        self.workspace.connect('show_build_log_state_change', self.update_buttons)

        self.document = None
        self.update_document()

    def update_document(self, workspace=None, parameter=None):
        if self.document != None: self.document.disconnect('changed', self.update_buttons)
        self.document = self.workspace.active_document
        if self.document != None: self.document.connect('changed', self.update_buttons)

        self.update_buttons()

    def update_buttons(self, workspace=None, parameter=None):
        if self.document == None: return

        if self.document.is_latex_document():
            if self.document.source_buffer.get_char_count() > 0:
                self.latex_shortcutsbar.wizard_button_revealer.set_reveal_child(False)
            else:
                self.latex_shortcutsbar.wizard_button_revealer.set_reveal_child(True)
            self.latex_shortcutsbar.button_more.set_popover(self.document.context_menu.popover_more)
        else:
            self.latex_shortcutsbar.button_more.set_popover(None)

        show_build_log = self.workspace.get_show_build_log()
        self.latex_shortcutsbar.button_build_log.set_active(show_build_log)

    def on_build_log_button_clicked(self, toggle_button, parameter=None):
        self.workspace.set_show_build_log(toggle_button.get_active())


