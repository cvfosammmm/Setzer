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


class ShortcutsBar(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()

        self.main_window.latex_shortcuts_bar.button_build_log.set_active(self.workspace.get_show_build_log())
        self.main_window.latex_shortcuts_bar.button_build_log.connect('clicked', self.on_build_log_button_clicked)
        self.main_window.latex_shortcuts_bar.button_build_log.get_child().set_sensitive(False)

        self.workspace.register_observer(self)

    '''
    *** notification handlers, get called by observed workspace
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'document_removed':
            if self.workspace.active_document == None:
                self.main_window.latex_shortcuts_bar.button_build_log.get_child().set_sensitive(False)

        if change_code == 'new_active_document':
            document = parameter

            if document.is_latex_document():
                self.update_latex_shortcuts_bar(self.main_window.latex_shortcuts_bar)
                self.main_window.latex_shortcuts_bar.top_icons.insert(document.view.wizard_button, 0)
                self.main_window.latex_shortcuts_bar.button_build_log.get_child().set_sensitive(True)
            elif document.is_bibtex_document():
                self.update_latex_shortcuts_bar(self.main_window.bibtex_shortcuts_bar)
                self.main_window.latex_shortcuts_bar.button_build_log.get_child().set_sensitive(False)
            else:
                self.update_latex_shortcuts_bar(self.main_window.others_shortcuts_bar)
                self.main_window.latex_shortcuts_bar.button_build_log.get_child().set_sensitive(False)

        if change_code == 'new_inactive_document':
            document = parameter

            if document.is_latex_document():
                self.main_window.latex_shortcuts_bar.top_icons.remove(document.view.wizard_button)

        if change_code == 'show_build_log_state_change':
            show_build_log = parameter
            self.main_window.latex_shortcuts_bar.button_build_log.set_active(show_build_log)

    def update_shortcuts_bar(self, shortcuts_bar):
        document = self.workspace.active_document

        if shortcuts_bar.current_bottom != None:
            shortcuts_bar.remove(shortcuts_bar.current_bottom)
        shortcuts_bar.current_bottom = document.view.shortcuts_bar_bottom
        shortcuts_bar.pack_end(document.view.shortcuts_bar_bottom, False, False, 0)

    def on_build_log_button_clicked(self, toggle_button, parameter=None):
        self.workspace.set_show_build_log(toggle_button.get_active())


