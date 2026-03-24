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
from setzer.keyboard_shortcuts.shortcut_controller import ShortcutController
from setzer.keyboard_shortcuts.keybind_parser import KeybindParser


class ShortcutControllerDocument(ShortcutController):

    def __init__(self):
        ShortcutController.__init__(self)

        self.main_window = ServiceLocator.get_main_window()
        self.workspace = ServiceLocator.get_workspace()
        self.actions = self.workspace.actions

        self.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)

        doc_keybinds = KeybindParser.get_category_keybinds('document')
        for action_name, shortcut_array in doc_keybinds.items():
            shortcut = KeybindParser.to_gtk(shortcut_array)
            # Handle alternative actions (like redo_alt)
            real_action_name = action_name.split('_alt')[0]
            if real_action_name in self.actions.actions:
                self.create_and_add_shortcut(shortcut, self.actions.actions[real_action_name].activate)
            elif hasattr(self, real_action_name):
                self.create_and_add_shortcut(shortcut, getattr(self, real_action_name))
