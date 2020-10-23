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
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib

import setzer.workspace.build_log.build_log_viewgtk as build_log_view
import setzer.workspace.headerbar.headerbar_viewgtk as headerbar_view
import setzer.workspace.shortcutsbar.shortcutsbar_viewgtk as shortcutsbar_view
import setzer.workspace.bibtex_shortcutsbar.bibtex_shortcutsbar_viewgtk as bibtex_shortcutsbar_view
import setzer.workspace.preview_panel.preview_panel_viewgtk as preview_panel_view
import setzer.workspace.help_panel.help_panel_viewgtk as help_panel_view
import setzer.workspace.sidebar.sidebar_viewgtk as sidebar_view
from setzer.app.service_locator import ServiceLocator

import os.path


class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(self, application=app)
        self.app = app
        self.set_size_request(-1, 550)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)

        # window state variables
        self.current_width = 0
        self.current_height = 0
        self.ismaximized = False

        # headerbar
        self.headerbar = headerbar_view.HeaderBar()
        self.set_titlebar(self.headerbar)

        # notebook
        self.notebook_wrapper = Gtk.VBox()
        self.notebook = DocumentViewWrapper()
        self.shortcuts_bar = shortcutsbar_view.ShortcutsBar()
        self.notebook_wrapper.pack_start(self.shortcuts_bar, False, False, 0)
        self.notebook_wrapper.pack_start(self.notebook, True, True, 0)

        # bibtex notebook
        self.bibtex_notebook = Gtk.Notebook()
        self.bibtex_notebook.set_show_tabs(False)
        self.bibtex_notebook.set_show_border(False)
        self.bibtex_notebook.set_scrollable(True)
        self.bibtex_shortcuts_bar = bibtex_shortcutsbar_view.BibTeXShortcutsBar()
        self.bibtex_notebook_wrapper = Gtk.VBox()
        self.bibtex_notebook_wrapper.pack_start(self.bibtex_shortcuts_bar, False, False, 0)
        self.bibtex_notebook_wrapper.pack_start(self.bibtex_notebook, True, True, 0)

        # build log
        self.build_log = build_log_view.BuildLogView()
        self.build_log_paned = Gtk.VPaned()
        self.build_log_paned.pack1(self.notebook_wrapper, True, False)
        self.build_log_paned.pack2(self.build_log, False, True)
        self.build_log_visible = None

        # preview
        self.preview_panel = preview_panel_view.PreviewPanelView()
        self.preview_visible = None

        # help
        self.help_panel = help_panel_view.HelpPanelView()
        self.help_visible = None

        # sidebar
        self.sidebar = sidebar_view.Sidebar()
        self.sidebar_visible = None

        # paneds
        self.preview_paned_overlay = Gtk.Overlay()
        self.overlay_widget = None
        self.preview_help_stack = Gtk.Stack()
        self.preview_help_stack.add_named(self.preview_panel, 'preview')
        self.preview_help_stack.add_named(self.help_panel, 'help')
        self.preview_paned = Gtk.HPaned()
        self.preview_paned.pack1(self.build_log_paned, True, False)
        self.preview_paned.pack2(self.preview_help_stack, False, True)
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
        resources_path = ServiceLocator.get_resources_path()
        self.css_provider.load_from_path(os.path.join(resources_path, 'style_gtk.css'))
        self.style_context = Gtk.StyleContext()
        self.style_context.add_provider_for_screen(self.get_screen(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.css_provider_font_size = Gtk.CssProvider()
        self.style_context.add_provider_for_screen(self.get_screen(), self.css_provider_font_size, Gtk.STYLE_PROVIDER_PRIORITY_USER)


class DocumentViewWrapper(Gtk.Notebook):

    def __init__(self):
        Gtk.Notebook.__init__(self)

        self.set_show_tabs(False)
        self.set_show_border(False)
        self.set_scrollable(True)

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 550, 550


class BlankSlate(Gtk.HBox):

    def __init__(self):
        Gtk.HBox.__init__(self)
        
        self.pack_start(Gtk.Label(_('No open documents')), True, True, 0)
        

