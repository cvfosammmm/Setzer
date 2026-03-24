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
from gi.repository import Gtk, GLib, Gio

from setzer.app.service_locator import ServiceLocator
from setzer.keyboard_shortcuts.shortcut_controller import ShortcutController
from setzer.popovers.popover_manager import PopoverManager
from setzer.keyboard_shortcuts.keybind_parser import KeybindParser


class ShortcutControllerLaTeX(ShortcutController):

    def __init__(self):
        ShortcutController.__init__(self)

        self.main_window = ServiceLocator.get_main_window()
        self.workspace = ServiceLocator.get_workspace()
        self.actions = self.workspace.actions

        self.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)

        # Register before-after expansions
        before_after_keybinds = KeybindParser.get_category_keybinds('latex-before-after')
        for expansion, shortcut_array in before_after_keybinds.items():
            shortcut = KeybindParser.to_gtk(shortcut_array)
            # Replace escaped newlines and tabs
            expansion = expansion.replace('\\n', '\n').replace('\\t', '\t')
            # Split by @@ to get before and after parts
            parts = expansion.split('@@')
            if len(parts) == 2:
                self.set_accels_for_insert_before_after_action(parts, [shortcut])

        # Register symbol expansions
        symbol_keybinds = KeybindParser.get_category_keybinds('latex-symbol')
        for symbol, shortcut_array in symbol_keybinds.items():
            shortcut = KeybindParser.to_gtk(shortcut_array)
            # Replace escaped newlines and tabs
            symbol = symbol.replace('\\n', '\n').replace('\\t', '\t')
            self.set_accels_for_insert_symbol_action([symbol], [shortcut])

        # Register standard latex shortcuts
        latex_keybinds = KeybindParser.get_category_keybinds('latex')
        for action_name, shortcut_array in latex_keybinds.items():
            shortcut = KeybindParser.to_gtk(shortcut_array)
            if action_name in self.actions.actions:
                self.create_and_add_shortcut(shortcut, self.actions.actions[action_name].activate)
            elif hasattr(self, action_name):
                self.create_and_add_shortcut(shortcut, getattr(self, action_name))

    def set_accels_for_insert_before_after_action(self, parameter, accels):
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', parameter)), accels)

    def set_accels_for_insert_symbol_action(self, parameter, accels):
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', parameter)), accels)

    def shortcut_quotes(self, accel_group=None, window=None, key=None, mask=None):
        PopoverManager.popup_at_button('quotes_menu')
