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
        return True


class Shortcuts(object):

    def __init__(self, workspace):
        self.main_window = ServiceLocator.get_main_window()
        self.workspace = workspace

        self.shortcut_controller = Gtk.ShortcutController()
        self.shortcut_controller.set_scope(Gtk.ShortcutScope.GLOBAL)
        self.shortcut_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.main_window.add_controller(self.shortcut_controller)

        actions = self.workspace.actions
        self.shortcut_controller.add_shortcut(Shortcut('<Control>n', actions.new_latex_document))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>o', actions.open_document_dialog))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>s', actions.save))
        self.shortcut_controller.add_shortcut(Shortcut('<Control><Shift>s', actions.save_as))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>w', actions.close_active_document))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>q', actions.actions['quit'].activate))
        self.shortcut_controller.add_shortcut(Shortcut('F10', self.shortcut_workspace_menu))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>question', actions.show_shortcuts_dialog))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>t', self.shortcut_show_open_docs))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>Page_Down', self.shortcut_switch_document))
        self.shortcut_controller.add_shortcut(Shortcut('<Control><Shift>o', self.shortcut_show_document_chooser))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>plus', actions.zoom_in))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>minus', actions.zoom_out))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>0', actions.reset_zoom))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>f', actions.start_search))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>h', actions.start_search_and_replace))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>g', actions.find_next))
        self.shortcut_controller.add_shortcut(Shortcut('<Control><Shift>g', actions.find_previous))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>x', actions.cut))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>c', actions.copy))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>v', actions.paste))
        self.shortcut_controller.add_shortcut(Shortcut('F1', self.shortcut_help))
        self.shortcut_controller.add_shortcut(Shortcut('F2', self.shortcut_document_structure_toggle))
        self.shortcut_controller.add_shortcut(Shortcut('F3', self.shortcut_symbols_toggle))
        self.shortcut_controller.add_shortcut(Shortcut('F5', actions.save_and_build))
        self.shortcut_controller.add_shortcut(Shortcut('F6', actions.build))
        self.shortcut_controller.add_shortcut(Shortcut('F8', self.shortcut_build_log))
        self.shortcut_controller.add_shortcut(Shortcut('F9', self.shortcut_preview))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>z', actions.undo))
        self.shortcut_controller.add_shortcut(Shortcut('<Control><Shift>z', actions.redo))
        self.shortcut_controller.add_shortcut(Shortcut('<Control>k', actions.toggle_comment))

    def set_document_type(self, document_type):
        if document_type == 'latex':
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
        else:
            self.set_accels_for_insert_before_after_action(['\\textbf{', '}'], [])
            self.set_accels_for_insert_before_after_action(['\\textit{', '}'], [])
            self.set_accels_for_insert_before_after_action(['\\underline{', '}'], [])
            self.set_accels_for_insert_before_after_action(['\\texttt{', '}'], [])
            self.set_accels_for_insert_before_after_action(['\\emph{', '}'], [])
            self.set_accels_for_insert_before_after_action(['$ ', ' $'], [])
            self.set_accels_for_insert_before_after_action(['\\[ ', ' \\]'], [])
            self.set_accels_for_insert_before_after_action(['\\begin{equation}\n\t', '\n\\end{equation}'], [])
            self.set_accels_for_insert_before_after_action(['_{', '}'], [])
            self.set_accels_for_insert_before_after_action(['^{', '}'], [])
            self.set_accels_for_insert_symbol_action(['\\frac{•}{•}'], [])
            self.set_accels_for_insert_symbol_action(['\\left •'], [])
            self.set_accels_for_insert_symbol_action(['\\right •'], [])
            self.set_accels_for_insert_symbol_action(['\\item •'], [])
            self.set_accels_for_insert_symbol_action(['\\\\\n'], [])

    def set_accels_for_insert_before_after_action(self, parameter, accels):
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', parameter)), accels)

    def set_accels_for_insert_symbol_action(self, parameter, accels):
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', parameter)), accels)

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

    def shortcut_document_structure_toggle(self, accel_group=None, window=None, key=None, mask=None):
        toggle = self.main_window.headerbar.document_structure_toggle
        if toggle.get_sensitive():
            toggle.set_active(not toggle.get_active())
        return True

    def shortcut_symbols_toggle(self, accel_group=None, window=None, key=None, mask=None):
        toggle = self.main_window.headerbar.symbols_toggle
        if toggle.get_sensitive():
            toggle.set_active(not toggle.get_active())
        return True


