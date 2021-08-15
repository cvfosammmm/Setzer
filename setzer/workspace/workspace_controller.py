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
from setzer.dialogs.dialog_locator import DialogLocator

import time


class WorkspaceController(object):
    ''' Mediator between workspace and view. '''
    
    def __init__(self, workspace):

        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()

        self.main_window.headerbar.sidebar_toggle.connect('toggled', self.on_sidebar_toggle_toggled)
        self.main_window.headerbar.preview_toggle.connect('toggled', self.on_preview_toggle_toggled)
        self.main_window.headerbar.help_toggle.connect('toggled', self.on_help_toggle_toggled)

        # populate workspace
        self.workspace.populate_from_disk()
        open_documents = self.workspace.open_documents
        if len(open_documents) > 0:
            self.workspace.set_active_document(open_documents[-1])

    def on_sidebar_toggle_toggled(self, toggle_button, parameter=None):
        self.workspace.set_show_sidebar(toggle_button.get_active())

    def on_preview_toggle_toggled(self, toggle_button, parameter=None):
        show_preview = toggle_button.get_active()
        if show_preview:
            show_help = False
            self.main_window.headerbar.help_toggle.set_active(False)
        else:
            show_help = self.workspace.show_help
        self.workspace.set_show_preview_or_help(show_preview, show_help)

    def on_help_toggle_toggled(self, toggle_button, parameter=None):
        show_help = toggle_button.get_active()
        if show_help:
            show_preview = False
            self.main_window.headerbar.preview_toggle.set_active(False)
        else:
            show_preview = self.workspace.show_preview
        self.workspace.set_show_preview_or_help(show_preview, show_help)


