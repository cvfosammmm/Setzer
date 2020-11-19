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

        self.observe_workspace_view()
        
        self.untitled_documents_no = 0

        self.p_allocation = 0
        self.pp_allocation = 0
        self.s_allocation = 0
        self.bl_allocation = 0

        # populate workspace
        self.workspace.populate_from_disk()
        open_documents = self.workspace.open_documents
        if len(open_documents) > 0:
            self.workspace.set_active_document(open_documents[-1])

    def observe_workspace_view(self):
        self.main_window.headerbar.sidebar_toggle.connect('toggled', self.on_sidebar_toggle_toggled)
        self.main_window.headerbar.preview_toggle.connect('toggled', self.on_preview_toggle_toggled)
        self.main_window.headerbar.help_toggle.connect('toggled', self.on_help_toggle_toggled)
        self.main_window.sidebar.connect('size-allocate', self.on_sidebar_size_allocate)
        self.main_window.preview_help_stack.connect('size-allocate', self.on_preview_size_allocate)
        self.main_window.preview_paned.connect('size-allocate', self.on_preview_paned_size_allocate)
        self.main_window.latex_notebook_wrapper.connect('size-allocate', self.on_build_log_size_allocate)
        self.main_window.latex_shortcuts_bar.button_build_log.connect('clicked', self.on_build_log_button_clicked)

    def on_build_log_button_clicked(self, toggle_button, parameter=None):
        self.workspace.set_show_build_log(toggle_button.get_active())

    '''
    *** workspace menu
    '''

    def on_sidebar_toggle_toggled(self, toggle_button, parameter=None):
        self.workspace.set_show_sidebar(toggle_button.get_active())

    def on_preview_toggle_toggled(self, toggle_button, parameter=None):
        show_preview = toggle_button.get_active()
        if show_preview:
            show_help = False
        else:
            show_help = self.workspace.show_help
        self.workspace.set_show_preview_or_help(show_preview, show_help)

    def on_help_toggle_toggled(self, toggle_button, parameter=None):
        show_help = toggle_button.get_active()
        if show_help:
            show_preview = False
        else:
            show_preview = self.workspace.show_preview
        self.workspace.set_show_preview_or_help(show_preview, show_help)

    def on_sidebar_size_allocate(self, sidebar, allocation):
        if not self.workspace.presenter.sidebars_initialized: return
        if allocation.width != self.s_allocation:
            self.s_allocation = allocation.width
            if self.workspace.show_sidebar and self.workspace.active_document != None:
                if not self.workspace.presenter.sidebar_animating:
                    self.workspace.set_sidebar_position(allocation.width)

    def on_preview_size_allocate(self, preview, allocation):
        if not self.workspace.presenter.sidebars_initialized: return
        if allocation.width != self.p_allocation:
            self.p_allocation = allocation.width
            if (self.workspace.show_preview or self.workspace.show_help) and self.workspace.active_document != None:
                if not self.workspace.presenter.preview_animating:
                    self.workspace.set_preview_position(self.main_window.preview_paned.get_position())

    def on_build_log_size_allocate(self, build_log, allocation):
        if not self.workspace.presenter.sidebars_initialized: return
        if allocation.height != self.bl_allocation:
            self.bl_allocation = allocation.height
            if self.workspace.show_build_log and self.workspace.active_document != None:
                if not self.workspace.presenter.build_log_animating:
                    self.workspace.set_build_log_position(self.main_window.build_log_paned.get_position())

    def on_preview_paned_size_allocate(self, preview, allocation):
        if not self.workspace.presenter.sidebars_initialized: return
        if allocation.width != self.pp_allocation:
            self.pp_allocation = allocation.width
            if self.workspace.show_preview and self.workspace.active_document != None:
                if not self.workspace.presenter.preview_animating:
                    self.workspace.set_preview_position(self.main_window.preview_paned.get_position())


