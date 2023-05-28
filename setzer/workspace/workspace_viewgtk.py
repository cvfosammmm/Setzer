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
gi.require_version('Handy', '1')
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Handy

import setzer.workspace.build_log.build_log_viewgtk as build_log_view
import setzer.workspace.headerbar.headerbar_viewgtk as headerbar_view
import setzer.workspace.shortcutsbar.latex_shortcutsbar.latex_shortcutsbar_viewgtk as latex_shortcutsbar_view
import setzer.workspace.shortcutsbar.bibtex_shortcutsbar.bibtex_shortcutsbar_viewgtk as bibtex_shortcutsbar_view
import setzer.workspace.shortcutsbar.others_shortcutsbar.others_shortcutsbar_viewgtk as others_shortcutsbar_view
import setzer.workspace.preview_panel.preview_panel_viewgtk as preview_panel_view
import setzer.workspace.help_panel.help_panel_viewgtk as help_panel_view
import setzer.workspace.sidebar.sidebar_viewgtk as sidebar_view
import setzer.workspace.welcome_screen.welcome_screen_viewgtk as welcome_screen_view
import setzer.widgets.animated_paned.animated_paned as animated_paned
from setzer.app.service_locator import ServiceLocator

import os.path


class MainWindow(Handy.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(self, application=app)
        self.app = app
        self.set_size_request(-1, 550)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.main_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)

        # window state variables
        self.current_width = 0
        self.current_height = 0
        self.ismaximized = False

        # headerbar
        self.headerbar = headerbar_view.HeaderBar()
        self.main_box.add(self.headerbar)

        # latex notebook
        self.latex_notebook = Gtk.Notebook()
        self.latex_notebook.set_show_tabs(False)
        self.latex_notebook.set_show_border(False)
        self.latex_notebook.set_scrollable(True)
        self.latex_notebook.set_size_request(550, -1)
        self.latex_shortcutsbar = latex_shortcutsbar_view.LaTeXShortcutsbar()
        self.latex_notebook_wrapper = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.latex_notebook_wrapper.pack_start(self.latex_shortcutsbar, False, False, 0)
        self.latex_notebook_wrapper.pack_start(self.latex_notebook, True, True, 0)

        # bibtex notebook
        self.bibtex_notebook = Gtk.Notebook()
        self.bibtex_notebook.set_show_tabs(False)
        self.bibtex_notebook.set_show_border(False)
        self.bibtex_notebook.set_scrollable(True)
        self.bibtex_notebook.set_size_request(550, -1)
        self.bibtex_shortcutsbar = bibtex_shortcutsbar_view.BibTeXShortcutsbar()
        self.bibtex_notebook_wrapper = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.bibtex_notebook_wrapper.pack_start(self.bibtex_shortcutsbar, False, False, 0)
        self.bibtex_notebook_wrapper.pack_start(self.bibtex_notebook, True, True, 0)

        # others notebook
        self.others_notebook = Gtk.Notebook()
        self.others_notebook.set_show_tabs(False)
        self.others_notebook.set_show_border(False)
        self.others_notebook.set_scrollable(True)
        self.others_notebook.set_size_request(550, -1)
        self.others_shortcutsbar = others_shortcutsbar_view.OthersShortcutsbar()
        self.others_notebook_wrapper = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.others_notebook_wrapper.pack_start(self.others_shortcutsbar, False, False, 0)
        self.others_notebook_wrapper.pack_start(self.others_notebook, True, True, 0)

        # build log
        self.build_log = build_log_view.BuildLogView()
        self.build_log_paned = animated_paned.AnimatedVPaned(self.latex_notebook_wrapper, self.build_log, False)
        self.build_log_visible = None

        # preview
        self.preview_panel = preview_panel_view.PreviewPanelView()
        self.preview_visible = None

        # help
        self.help_panel = help_panel_view.HelpPanelView()
        self.help_visible = None

        # sidebar
        self.sidebar = sidebar_view.Sidebar()

        # paneds
        self.preview_paned_overlay = Gtk.Overlay()
        self.overlay_widget = None
        self.preview_help_stack = Gtk.Stack()
        self.preview_help_stack.add_named(self.preview_panel, 'preview')
        self.preview_help_stack.add_named(self.help_panel, 'help')
        self.preview_paned = animated_paned.AnimatedHPaned(self.build_log_paned, self.preview_help_stack, False)
        self.preview_paned_overlay.add(self.preview_paned)
        self.sidebar_paned = animated_paned.AnimatedHPaned(self.sidebar, self.preview_paned_overlay, True)
        self.sidebar_paned.get_style_context().add_class('sidebar_paned')

        # welcome screen
        self.welcome_screen = welcome_screen_view.WelcomeScreenView()

        # mode stack
        self.mode_stack = Gtk.Stack()
        self.mode_stack.props.expand = True
        self.mode_stack.add_named(self.welcome_screen, 'welcome_screen')
        self.mode_stack.add_named(self.sidebar_paned, 'latex_documents')
        self.mode_stack.add_named(self.bibtex_notebook_wrapper, 'bibtex_documents')
        self.mode_stack.add_named(self.others_notebook_wrapper, 'other_documents')
        self.main_box.add(self.mode_stack)
        self.add(self.main_box)

        self.css_provider = Gtk.CssProvider()
        resources_path = ServiceLocator.get_resources_path()
        self.css_provider.load_from_path(os.path.join(resources_path, 'style_gtk.css'))
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.css_provider_font_size = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(), self.css_provider_font_size, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        Handy.init()

