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
from gi.repository import Gtk, Gdk

from setzer.popovers.context_menu.context_menu_viewgtk import ContextMenuView


class ContextMenu(object):

    def __init__(self, popover_manager, workspace):
        self.workspace = workspace
        self.popover_manager = popover_manager
        self.view = ContextMenuView(popover_manager)

        self.key_controller = Gtk.EventControllerKey()
        self.key_controller.connect('key-pressed', self.on_keypress)
        self.view.add_controller(self.key_controller)

        self.workspace.connect('new_active_document', self.on_new_active_document)

    def on_keypress(self, controller, keyval, keycode, state):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if keyval == Gdk.keyval_from_name('F12'):
            if state & modifiers == 0:
                self.popover_manager.popdown()
                return True

        return False

    def on_new_active_document(self, workspace=None, parameter=None):
        document = self.workspace.active_document
        self.view.comment_button.set_visible(document != None and document.is_latex_document())
        self.view.sync_button.set_visible(document != None and document.is_latex_document())
        self.view.latex_buttons_separator.set_visible(document != None and document.is_latex_document())


