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
gi.require_version('GtkSource', '3.0')
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GtkSource

from workspace.build_log.build_log_viewgtk import *
from workspace.headerbar.headerbar_viewgtk import *
from workspace.shortcutsbar.shortcutsbar_viewgtk import *
from workspace.bibtex_shortcutsbar.bibtex_shortcutsbar_viewgtk import *
from workspace.preview.preview_viewgtk import *
from workspace.sidebar.sidebar_viewgtk import *
from app.service_locator import ServiceLocator

import os


class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(self, application=app)
        self.app = app
        self.set_size_request(-1, 550)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.dirname(__file__) + '/../resources/icons')
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.dirname(__file__) + '/../resources/symbols/light/arrows')
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.dirname(__file__) + '/../resources/symbols/light/greek_letters')
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.dirname(__file__) + '/../resources/symbols/light/misc_math')
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.dirname(__file__) + '/../resources/symbols/light/misc_text')
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.dirname(__file__) + '/../resources/symbols/light/operators')
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.dirname(__file__) + '/../resources/symbols/light/relations')
       
        # window state variables
        self.current_width = 0
        self.current_height = 0
        self.ismaximized = False

        # headerbar
        self.headerbar = HeaderBar()
        self.set_titlebar(self.headerbar)

        # notebook
        self.notebook_wrapper = Gtk.VBox()
        self.notebook = DocumentViewWrapper()
        self.shortcuts_bar = ShortcutsBar()
        self.notebook_wrapper.pack_start(self.shortcuts_bar, False, False, 0)
        self.notebook_wrapper.pack_start(self.notebook, True, True, 0)

        # bibtex notebook
        self.bibtex_notebook = Gtk.Notebook()
        self.bibtex_notebook.set_show_tabs(False)
        self.bibtex_notebook.set_show_border(False)
        self.bibtex_notebook.set_scrollable(True)
        self.bibtex_shortcuts_bar = BibTeXShortcutsBar()
        self.bibtex_notebook_wrapper = Gtk.VBox()
        self.bibtex_notebook_wrapper.pack_start(self.bibtex_shortcuts_bar, False, False, 0)
        self.bibtex_notebook_wrapper.pack_start(self.bibtex_notebook, True, True, 0)

        # build log
        self.build_log = BuildLogView()
        self.build_log_paned = Gtk.VPaned()
        self.build_log_paned.pack1(self.notebook_wrapper, True, False)
        self.build_log_paned.pack2(self.build_log, False, True)
        self.build_log_visible = None

        # preview
        self.preview = PreviewView()
        self.preview_visible = None
        
        # sidebar
        self.sidebar = Sidebar()
        self.sidebar_visible = None

        # paneds
        self.preview_paned_overlay = Gtk.Overlay()
        self.overlay_widget = None
        self.preview_paned = Gtk.HPaned()
        self.preview_paned.pack1(self.build_log_paned, True, False)
        self.preview_paned.pack2(self.preview, False, True)
        self.preview_paned_overlay.add(self.preview_paned)
        self.sidebar_paned = Gtk.HPaned()
        self.sidebar_paned.pack1(self.sidebar, False, True)
        self.sidebar_paned.pack2(self.preview_paned_overlay, True, False)
        self.sidebar_paned.get_style_context().add_class('sidebar_paned')
        
        # blank slate
        self.blank_slate = BlankSlate()

        # mode stack
        self.mode_stack = Gtk.Stack()
        self.mode_stack.add_named(self.blank_slate, 'blank_slate')
        self.mode_stack.add_named(self.sidebar_paned, 'latex_documents')
        self.mode_stack.add_named(self.bibtex_notebook_wrapper, 'bibtex_documents')
        self.add(self.mode_stack)

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_path(os.path.dirname(__file__) + '/../resources/style_gtk.css')
        self.style_context = Gtk.StyleContext()
        self.style_context.add_provider_for_screen(self.get_screen(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # actions
        self.new_latex_document_action = Gio.SimpleAction.new('new-latex-document', None)
        self.add_action(self.new_latex_document_action)

        self.new_bibtex_document_action = Gio.SimpleAction.new('new-bibtex-document', None)
        self.add_action(self.new_bibtex_document_action)

        self.save_as_action = Gio.SimpleAction.new('save-as', None)
        self.add_action(self.save_as_action)

        self.save_all_action = Gio.SimpleAction.new('save-all', None)
        self.add_action(self.save_all_action)

        self.find_action = Gio.SimpleAction.new('find', None)
        self.add_action(self.find_action)

        self.find_next_action = Gio.SimpleAction.new('find-next', None)
        self.add_action(self.find_next_action)

        self.find_prev_action = Gio.SimpleAction.new('find-prev', None)
        self.add_action(self.find_prev_action)

        self.find_replace_action = Gio.SimpleAction.new('find-replace', None)
        self.add_action(self.find_replace_action)

        self.close_all_action = Gio.SimpleAction.new('close-all-documents', None)
        self.add_action(self.close_all_action)

        self.close_document_action = Gio.SimpleAction.new('close-active-document', None)
        self.add_action(self.close_document_action)

        self.insert_before_after_action = Gio.SimpleAction.new('insert-before-after', GLib.VariantType('as'))
        self.add_action(self.insert_before_after_action)

        self.insert_symbol_action = Gio.SimpleAction.new('insert-symbol', GLib.VariantType('as'))
        self.add_action(self.insert_symbol_action)

        self.document_wizard_action = Gio.SimpleAction.new('show-document-wizard', None)
        self.add_action(self.document_wizard_action)

        self.include_bibtex_file_action = Gio.SimpleAction.new('include-bibtex-file', None)
        self.add_action(self.include_bibtex_file_action)

        self.shortcuts_window_action = Gio.SimpleAction.new('show-shortcuts-window', None)
        self.add_action(self.shortcuts_window_action)

        self.show_preferences_action = Gio.SimpleAction.new('show-preferences-dialog', None)
        self.add_action(self.show_preferences_action)

        self.show_about_action = Gio.SimpleAction.new('show-about-dialog', None)
        self.add_action(self.show_about_action)

        self.quit_action = Gio.SimpleAction.new('quit', None)
        self.add_action(self.quit_action)

        self.close_build_log_action = Gio.SimpleAction.new('close-build-log', None)
        self.add_action(self.close_build_log_action)


class DocumentViewWrapper(Gtk.Notebook):

    def __init__(self):
        Gtk.Notebook.__init__(self)

        self.set_show_tabs(False)
        self.set_show_border(False)
        self.set_scrollable(True)

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 440, 440


class BlankSlate(Gtk.HBox):

    def __init__(self):
        Gtk.HBox.__init__(self)
        
        self.pack_start(Gtk.Label("No open documents"), True, True, 0)
        

