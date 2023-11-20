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


class ShortcutControllerLaTeX(ShortcutController):

    def __init__(self):
        ShortcutController.__init__(self)

        self.main_window = ServiceLocator.get_main_window()
        self.workspace = ServiceLocator.get_workspace()
        self.actions = self.workspace.actions

        self.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)

        self.set_accels_for_insert_before_after_action(['\\textbf{', '}'], ['<Control>b'])
        self.set_accels_for_insert_before_after_action(['\\textit{', '}'], ['<Control>i'])
        self.set_accels_for_insert_before_after_action(['\\underline{', '}'], ['<Control>u'])
        self.set_accels_for_insert_before_after_action(['\\texttt{', '}'], ['<Control><Shift>t'])
        self.set_accels_for_insert_before_after_action(['\\emph{', '}'], ['<Control><Shift>e'])
        self.set_accels_for_insert_before_after_action(['$ ', ' $'], ['<Control>m'])
        self.set_accels_for_insert_before_after_action(['\\[ ', ' \\]'], ['<Control><Shift>m'])
        self.set_accels_for_insert_before_after_action(['\\begin{equation}\n\t', '\n\\end{equation}'], ['<Control><Shift>n'])
        self.set_accels_for_insert_before_after_action(['\\begin{•}\n\t', '\n\\end{•}'], ['<Control>e'])
        self.set_accels_for_insert_before_after_action(['_{', '}'], ['<Control><Shift>d'])
        self.set_accels_for_insert_before_after_action(['^{', '}'], ['<Control><Shift>u'])
        self.set_accels_for_insert_symbol_action(['\\frac{•}{•}'], ['<Alt><Shift>f'])
        self.set_accels_for_insert_symbol_action(['\\left •'], ['<Control><Shift>l'])
        self.set_accels_for_insert_symbol_action(['\\right •'], ['<Control><Shift>r'])
        self.set_accels_for_insert_symbol_action(['\\item •'], ['<Control><Shift>i'])
        self.set_accels_for_insert_symbol_action(['\\\\\n'], ['<Control>Return'])

        self.create_and_add_shortcut('<Control>k', self.actions.toggle_comment)
        self.create_and_add_shortcut('<Control>quotedbl', self.shortcut_quotes)

    def set_accels_for_insert_before_after_action(self, parameter, accels):
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', parameter)), accels)

    def set_accels_for_insert_symbol_action(self, parameter, accels):
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', parameter)), accels)

    def shortcut_quotes(self, accel_group=None, window=None, key=None, mask=None):
        PopoverManager.popup_at_button('quotes_menu')


