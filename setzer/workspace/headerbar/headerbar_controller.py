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


class HeaderbarController(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view

        actions = self.model.workspace.actions
        self.view.button_latex.connect('clicked', self.on_new_document_button_click, actions.new_latex_document_action)
        self.view.button_bibtex.connect('clicked', self.on_new_document_button_click, actions.new_bibtex_document_action)

        self.view.button_restore_session.connect('clicked', self.model.on_restore_session_click, None)
        self.view.button_save_session.connect('clicked', self.on_hamburger_button_click, actions.save_session_action)

        self.view.button_save_as.connect('clicked', self.on_hamburger_button_click, actions.save_as_action)
        self.view.button_save_all.connect('clicked', self.on_hamburger_button_click, actions.save_all_action)
        self.view.button_about.connect('clicked', self.on_hamburger_button_click, actions.show_about_action)
        self.view.button_close_all.connect('clicked', self.on_hamburger_button_click, actions.close_all_action)
        self.view.button_close_active.connect('clicked', self.on_hamburger_button_click, actions.close_document_action)
        self.view.button_quit.connect('clicked', self.on_hamburger_button_click, actions.quit_action)

    def on_new_document_button_click(self, button, action):
        self.view.new_document_popover.popdown()
        action.activate()

    def on_hamburger_button_click(self, button, action):
        self.view.hamburger_popover.popdown()
        action.activate()


