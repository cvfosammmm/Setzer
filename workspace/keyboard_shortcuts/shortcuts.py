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

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Gtk
from app.service_locator import ServiceLocator


class Shortcuts(object):
    ''' Handle Keyboard shortcuts. '''
    
    def __init__(self, workspace, workspace_controller):
        self.main_window = ServiceLocator.get_main_window()
        self.workspace = workspace
        self.workspace_controller = workspace_controller
        
        self.setup_shortcuts()

    def setup_shortcuts(self):
    
        self.accel_group = Gtk.AccelGroup()
        self.main_window.add_accel_group(self.accel_group)
        
        c_mask = Gdk.ModifierType.CONTROL_MASK
        s_mask = Gdk.ModifierType.SHIFT_MASK
        m_mask = Gdk.ModifierType.META_MASK
        flags = Gtk.AccelFlags.MASK
        
        self.accel_group.connect(Gdk.keyval_from_name('o'), c_mask, flags, self.shortcut_open)
        self.accel_group.connect(Gdk.keyval_from_name('o'), c_mask | s_mask, flags, self.shortcut_doc_chooser)
        self.accel_group.connect(Gdk.keyval_from_name('n'), c_mask, flags, self.shortcut_new)
        self.accel_group.connect(Gdk.keyval_from_name('t'), c_mask, flags, self.shortcut_show_open_docs)
        self.accel_group.connect(Gdk.keyval_from_name('F6'), 0, flags, self.shortcut_build)
        self.accel_group.connect(Gdk.keyval_from_name('F8'), 0, flags, self.shortcut_build_log)
        self.accel_group.connect(Gdk.keyval_from_name('F9'), 0, flags, self.shortcut_sidebar)
        self.accel_group.connect(Gdk.keyval_from_name('F10'), 0, flags, self.shortcut_preview)
        self.accel_group.connect(Gdk.keyval_from_name('s'), c_mask, flags, self.shortcut_save)
        self.accel_group.connect(Gdk.keyval_from_name('s'), c_mask | s_mask, flags, self.shortcut_save_as)
        self.accel_group.connect(Gdk.keyval_from_name('t'), c_mask | s_mask, flags, self.shortcut_switch_document)

        # text search
        self.main_window.app.set_accels_for_action('win.find', ['<Control>f'])
        self.main_window.app.set_accels_for_action('win.find-next', ['<Control>g'])
        self.main_window.app.set_accels_for_action('win.find-prev', ['<Control><Shift>g'])
        self.main_window.app.set_accels_for_action('win.find-replace', ['<Control>h'])

        # document edit shortcuts
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\textbf{', '}'])), ['<Control>b'])
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\textit{', '}'])), ['<Control>i'])
        self.accel_group.connect(Gdk.keyval_from_name('quotedbl'), c_mask, flags, self.shortcut_quotes)
        
    def shortcut_open(self, accel_group=None, window=None, key=None, mask=None):
        self.workspace_controller.on_open_document_button_click()

    def shortcut_doc_chooser(self, accel_group=None, window=None, key=None, mask=None):
        if self.main_window.headerbar.open_document_button.get_sensitive():
            self.main_window.headerbar.open_document_button.clicked()

    def shortcut_new(self, accel_group=None, window=None, key=None, mask=None):
        self.workspace_controller.on_new_document_button_click()

    def shortcut_show_open_docs(self, accel_group=None, window=None, key=None, mask=None):
        if self.main_window.headerbar.center_button.get_sensitive():
            self.main_window.headerbar.center_button.clicked()

    def shortcut_build(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.get_active_document() != None:
            if self.workspace.master_document != None:
                document = self.workspace.master_document
            else:
                document = self.workspace.active_document
            document.controller.build_document_request()
        return True

    def shortcut_sidebar(self, accel_group=None, window=None, key=None, mask=None):
        toggle = self.main_window.headerbar.sidebar_toggle.get_child()
        if toggle.get_sensitive():
            toggle.clicked()
        return True

    def shortcut_preview(self, accel_group=None, window=None, key=None, mask=None):
        toggle = self.main_window.headerbar.preview_toggle
        if toggle.get_sensitive():
            toggle.clicked()
        return True

    def shortcut_build_log(self, accel_group=None, window=None, key=None, mask=None):
        document = self.workspace.get_active_document()
        if document != False:
            document.set_show_build_log(not document.get_show_build_log())
        return True

    def shortcut_switch_document(self, accel_group=None, window=None, key=None, mask=None):
        self.workspace_controller.switch_to_earliest_open_document()

    def shortcut_save(self, accel_group=None, window=None, key=None, mask=None):
        self.main_window.headerbar.save_document_button.clicked()

    def shortcut_save_as(self, accel_group=None, window=None, key=None, mask=None):
        self.workspace_controller.save_as_action.activate()

    def shortcut_quotes(self, accel_group=None, window=None, key=None, mask=None):
        self.workspace_controller.activate_quotes_popover()


