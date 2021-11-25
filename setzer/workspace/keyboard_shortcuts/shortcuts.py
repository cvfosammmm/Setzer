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

        self.accel_group.connect(Gdk.keyval_from_name('o'), c_mask | s_mask, flags, self.shortcut_doc_chooser)
        self.accel_group.connect(Gdk.keyval_from_name('t'), c_mask, flags, self.shortcut_show_open_docs)
        self.accel_group.connect(Gdk.keyval_from_name('F1'), 0, flags, self.shortcut_help)
        self.accel_group.connect(Gdk.keyval_from_name('F8'), 0, flags, self.shortcut_build_log)
        self.accel_group.connect(Gdk.keyval_from_name('F9'), 0, flags, self.shortcut_sidebar)
        self.accel_group.connect(Gdk.keyval_from_name('F10'), 0, flags, self.shortcut_preview)
        self.accel_group.connect(Gdk.keyval_from_name('t'), c_mask | s_mask, flags, self.shortcut_switch_document)
        self.accel_group.connect(Gdk.keyval_from_name('j'), c_mask | a_mask, flags, self.shortcut_forward_sync)
        self.main_window.app.set_accels_for_action('win.new-latex-document', ['<Control>n'])

        # zoom
        self.main_window.app.set_accels_for_action('win.zoom-in', ['<Control>plus'])
        self.main_window.app.set_accels_for_action('win.zoom-out', ['<Control>minus'])
        self.main_window.app.set_accels_for_action('win.reset-zoom', ['<Control>0'])

        # text search
        self.main_window.app.set_accels_for_action('win.find', ['<Control>f'])
        self.main_window.app.set_accels_for_action('win.find-next', ['<Control>g'])
        self.main_window.app.set_accels_for_action('win.find-prev', ['<Control><Shift>g'])
        self.main_window.app.set_accels_for_action('win.find-replace', ['<Control>h'])
        self.main_window.app.set_accels_for_action('win.open-document-dialog', ['<Control>o'])
        self.main_window.app.set_accels_for_action('win.save-and-build', ['F5'])
        self.main_window.app.set_accels_for_action('win.build', ['F6'])
        self.main_window.app.set_accels_for_action('win.show-shortcuts-window', ['<Control>question'])
        self.main_window.app.set_accels_for_action('win.save', ['<Control>s'])
        self.main_window.app.set_accels_for_action('win.save-as', ['<Control><Shift>s'])
        self.main_window.app.set_accels_for_action('win.close-active-document', ['<Control>w'])
        self.main_window.app.set_accels_for_action('win.spellchecking', ['F7'])
        self.main_window.app.set_accels_for_action('win.quit', ['<Control>q'])

        # document edit shortcuts
        self.accel_group.connect(Gdk.keyval_from_name('quotedbl'), c_mask, flags, self.shortcut_quotes)

    def set_document_type(self, document_type):
        if document_type == 'latex':
            self.set_accels_for_insert_before_after_action(['\\textbf{', '}'], ['<Control>b'])
            self.set_accels_for_insert_before_after_action(['\\textit{', '}'], ['<Control>i'])
            self.set_accels_for_insert_before_after_action(['\\underline{', '}'], ['<Control>u'])
            self.set_accels_for_insert_before_after_action(['\\emph{', '}'], ['<Control><Shift>e'])
            self.set_accels_for_insert_before_after_action(['\\texttt{', '}'], ['<Control>m'])
            self.set_accels_for_insert_before_after_action(['$ ', ' $'], ['<Control><Shift>m'])
            self.set_accels_for_insert_before_after_action(['\\[ ', ' \\]'], ['<Alt><Shift>m'])
            self.set_accels_for_insert_before_after_action(['\\begin{equation}\n\t', '\n\\end{equation}'], ['<Control><Shift>n'])
            self.set_accels_for_insert_before_after_action(['\\begin{•}\n\t', '\n\\end{•}'], ['<Control>e'])
            self.set_accels_for_insert_before_after_action(['_{', '}'], ['<Control><Shift>d'])
            self.set_accels_for_insert_before_after_action(['^{', '}'], ['<Control><Shift>u'])
            self.set_accels_for_insert_before_after_action(['\\sqrt{', '}'], ['<Control><Shift>q'])
            self.set_accels_for_insert_symbol_action(['\\frac{•}{•}'], ['<Alt><Shift>f'])
            self.set_accels_for_insert_symbol_action(['\\left •'], ['<Control><Shift>l'])
            self.set_accels_for_insert_symbol_action(['\\right •'], ['<Control><Shift>r'])
            self.set_accels_for_insert_symbol_action(['\\item •'], ['<Control><Shift>i'])
            self.set_accels_for_insert_symbol_action(['\\\\\n'], ['<Control>Return'])
            self.main_window.app.set_accels_for_action('win.comment-uncomment', ['<Control>K'])
        elif document_type == 'bibtex':
            self.set_accels_for_insert_before_after_action(['\\textbf{', '}'], [])
            self.set_accels_for_insert_before_after_action(['\\textit{', '}'], [])
            self.set_accels_for_insert_before_after_action(['\\underline{', '}'], [])
            self.set_accels_for_insert_before_after_action(['\\emph{', '}'], [])
            self.set_accels_for_insert_before_after_action(['\\texttt{', '}'], [])
            self.set_accels_for_insert_before_after_action(['$ ', ' $'], [])
            self.set_accels_for_insert_before_after_action(['\\[ ', ' \\]'], [])
            self.set_accels_for_insert_before_after_action(['\\begin{equation}\n\t', '\n\\end{equation}'], [])
            self.set_accels_for_insert_before_after_action(['_{', '}'], [])
            self.set_accels_for_insert_before_after_action(['^{', '}'], [])
            self.set_accels_for_insert_before_after_action(['\\sqrt{', '}'], [])
            self.set_accels_for_insert_symbol_action(['\\frac{•}{•}'], [])
            self.set_accels_for_insert_symbol_action(['\\left •'], [])
            self.set_accels_for_insert_symbol_action(['\\right •'], [])
            self.set_accels_for_insert_symbol_action(['\\item •'], [])
            self.set_accels_for_insert_symbol_action(['\\\\\n'], [])
            self.main_window.app.set_accels_for_action('win.comment-uncomment', [])
        else:
            self.set_accels_for_insert_before_after_action(['\\textbf{', '}'], [])
            self.set_accels_for_insert_before_after_action(['\\textit{', '}'], [])
            self.set_accels_for_insert_before_after_action(['\\underline{', '}'], [])
            self.set_accels_for_insert_before_after_action(['\\emph{', '}'], [])
            self.set_accels_for_insert_before_after_action(['\\texttt{', '}'], [])
            self.set_accels_for_insert_before_after_action(['$ ', ' $'], [])
            self.set_accels_for_insert_before_after_action(['\\[ ', ' \\]'], [])
            self.set_accels_for_insert_before_after_action(['\\begin{equation}\n\t', '\n\\end{equation}'], [])
            self.set_accels_for_insert_before_after_action(['_{', '}'], [])
            self.set_accels_for_insert_before_after_action(['^{', '}'], [])
            self.set_accels_for_insert_before_after_action(['\\sqrt{', '}'], [])
            self.set_accels_for_insert_symbol_action(['\\frac{•}{•}'], [])
            self.set_accels_for_insert_symbol_action(['\\left •'], [])
            self.set_accels_for_insert_symbol_action(['\\right •'], [])
            self.set_accels_for_insert_symbol_action(['\\item •'], [])
            self.set_accels_for_insert_symbol_action(['\\\\\n'], [])
            self.main_window.app.set_accels_for_action('win.comment-uncomment', [])

    def shortcut_doc_chooser(self, accel_group=None, window=None, key=None, mask=None):
        if self.main_window.headerbar.open_document_button.get_sensitive():
            self.main_window.headerbar.open_document_button.clicked()

    def shortcut_show_open_docs(self, accel_group=None, window=None, key=None, mask=None):
        if self.main_window.headerbar.center_widget.center_button.get_sensitive():
            self.main_window.headerbar.center_widget.center_button.clicked()

    def shortcut_sidebar(self, accel_group=None, window=None, key=None, mask=None):
        toggle = self.main_window.headerbar.sidebar_toggle
        if toggle.get_sensitive():
            toggle.clicked()
        return True

    def shortcut_build_log(self, accel_group=None, window=None, key=None, mask=None):
        show_build_log = not self.workspace.get_show_build_log()
        self.workspace.set_show_build_log(show_build_log)

    def shortcut_preview(self, accel_group=None, window=None, key=None, mask=None):
        toggle = self.main_window.headerbar.preview_toggle
        if toggle.get_sensitive():
            toggle.clicked()
        return True

    def shortcut_help(self, accel_group=None, window=None, key=None, mask=None):
        toggle = self.main_window.headerbar.help_toggle
        if toggle.get_sensitive():
            toggle.clicked()
        return True

    def shortcut_switch_document(self, accel_group=None, window=None, key=None, mask=None):
        self.workspace.switch_to_earliest_open_document()

    def shortcut_quotes(self, accel_group=None, window=None, key=None, mask=None):
        active_document = self.workspace.get_active_document()
        if active_document != None and active_document.is_latex_document():
            self.main_window.latex_shortcutsbar.quotes_button.set_active(True)

    def shortcut_forward_sync(self, accel_group=None, window=None, key=None, mask=None):
        self.workspace.forward_sync(self.workspace.active_document)


