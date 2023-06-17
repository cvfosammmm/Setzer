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
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Gtk
from setzer.app.service_locator import ServiceLocator
from setzer.dialogs.dialog_locator import DialogLocator


class Shortcuts(object):
    ''' Handle Keyboard shortcuts. '''
    
    def __init__(self, workspace):
        self.main_window = ServiceLocator.get_main_window()
        self.workspace = workspace
        
        self.setup_shortcuts()

    def set_accels_for_insert_before_after_action(self, parameter, accels):
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', parameter)), accels)

    def set_accels_for_insert_symbol_action(self, parameter, accels):
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', parameter)), accels)

    def setup_shortcuts(self):
        self.accel_group = Gtk.AccelGroup()
        self.main_window.add_accel_group(self.accel_group)

        c_mask = Gdk.ModifierType.CONTROL_MASK
        s_mask = Gdk.ModifierType.SHIFT_MASK
        a_mask = Gdk.ModifierType.MOD1_MASK
        m_mask = Gdk.ModifierType.META_MASK
        all_mask = Gdk.ModifierType.MODIFIER_MASK
        flags = Gtk.AccelFlags.MASK

        self.accel_group.connect(Gdk.keyval_from_name('t'), c_mask, flags, self.shortcut_show_open_docs)
        self.accel_group.connect(Gdk.keyval_from_name('F10'), 0, flags, self.shortcut_workspace_menu)
        self.accel_group.connect(Gdk.keyval_from_name('t'), c_mask | s_mask, flags, self.shortcut_switch_document)
        self.main_window.app.set_accels_for_action('win.new-latex-document', ['<Control>n'])

        # text search
        self.main_window.app.set_accels_for_action('win.open-document-dialog', ['<Control>o'])
        self.main_window.app.set_accels_for_action('win.save', ['<Control>s'])
        self.main_window.app.set_accels_for_action('win.save-as', ['<Control><Shift>s'])
        self.main_window.app.set_accels_for_action('win.close-active-document', ['<Control>w'])
        self.main_window.app.set_accels_for_action('win.quit', ['<Control>q'])

    def shortcut_show_open_docs(self, accel_group=None, window=None, key=None, mask=None):
        if self.main_window.headerbar.center_widget.center_button.get_sensitive():
            self.main_window.headerbar.center_widget.center_button.clicked()

    def shortcut_workspace_menu(self, accel_group=None, window=None, key=None, mask=None):
        if self.main_window.headerbar.menu_button.get_sensitive():
            self.main_window.headerbar.menu_button.clicked()

    def shortcut_switch_document(self, accel_group=None, window=None, key=None, mask=None):
        self.workspace.switch_to_earliest_open_document()


