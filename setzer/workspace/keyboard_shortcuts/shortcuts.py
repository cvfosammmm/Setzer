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
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Gtk
from setzer.app.service_locator import ServiceLocator
from setzer.dialogs.dialog_locator import DialogLocator


class Shortcut(Gtk.Shortcut):

    def __init__(self, trigger_string, callback):
        Gtk.Shortcut.__init__(self)

        self.set_action(Gtk.CallbackAction.new(self.action, callback))
        self.set_trigger(Gtk.ShortcutTrigger.parse_string(trigger_string))

    def action(self, a, b, callback):
        callback()


class Shortcuts(object):

    def __init__(self, workspace):
        self.main_window = ServiceLocator.get_main_window()
        self.workspace = workspace

        self.shortcut_controller = Gtk.ShortcutController()
        self.shortcut_controller.set_scope(Gtk.ShortcutScope.GLOBAL)
        self.shortcut_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.main_window.add_controller(self.shortcut_controller)

        actions = self.workspace.actions
        self.shortcut_controller.add_shortcut(Shortcut('<Control>n', actions.new_latex_document_action.activate))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>o', actions.open_document_dialog_action.activate))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>s', actions.save_action.activate))
        self.shortcut_controller.add_shortcut(Shortcut('<Control><Shift>s', actions.save_as_action.activate))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>w', actions.close_document_action.activate))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>q', actions.quit_action.activate))
        self.shortcut_controller.add_shortcut(Shortcut('F10', self.shortcut_workspace_menu))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>t', self.shortcut_show_open_docs))
        self.shortcut_controller.add_shortcut(Shortcut('<Control><Shift>t', self.shortcut_switch_document))
        self.shortcut_controller.add_shortcut(Shortcut('<Control><Shift>o', self.shortcut_show_document_chooser))
        self.shortcut_controller.add_shortcut(Shortcut('F1', self.shortcut_help))
        self.shortcut_controller.add_shortcut(Shortcut('F5', actions.save_and_build_action.activate))
        self.shortcut_controller.add_shortcut(Shortcut('F6', actions.build_action.activate))
        self.shortcut_controller.add_shortcut(Shortcut('F8', self.shortcut_build_log))
        self.shortcut_controller.add_shortcut(Shortcut('F9', self.shortcut_preview))

    def shortcut_show_document_chooser(self):
        if self.main_window.headerbar.open_document_button.get_sensitive():
            self.main_window.headerbar.open_document_button.popup()

    def shortcut_show_open_docs(self):
        if self.main_window.headerbar.center_widget.center_button.get_sensitive():
            self.main_window.headerbar.center_widget.center_button.activate()

    def shortcut_workspace_menu(self):
        if self.main_window.headerbar.menu_button.get_sensitive():
            self.main_window.headerbar.menu_button.activate()

    def shortcut_switch_document(self):
        self.workspace.switch_to_earliest_open_document()

    def shortcut_build_log(self):
        show_build_log = not self.workspace.get_show_build_log()
        self.workspace.set_show_build_log(show_build_log)

    def shortcut_preview(self):
        toggle = self.main_window.headerbar.preview_toggle
        if toggle.get_sensitive():
            toggle.set_active(not toggle.get_active())
        return True

    def shortcut_help(self, accel_group=None, window=None, key=None, mask=None):
        toggle = self.main_window.headerbar.help_toggle
        if toggle.get_sensitive():
            toggle.set_active(not toggle.get_active())
        return True


