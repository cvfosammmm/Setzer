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
gi.require_version('Adw', '1')
from gi.repository import Adw, Gdk, Gtk

import setzer.workspace.build_log.build_log_viewgtk as build_log_view
import setzer.workspace.headerbar.headerbar_viewgtk as headerbar_view
import setzer.workspace.shortcutsbar.shortcutsbar_viewgtk as shortcutsbar_view
import setzer.workspace.preview_panel.preview_panel_viewgtk as preview_panel_view
import setzer.workspace.help_panel.help_panel_viewgtk as help_panel_view
import setzer.workspace.sidebar.sidebar_viewgtk as sidebar_view
import setzer.workspace.welcome_screen.welcome_screen_viewgtk as welcome_screen_view
import setzer.widgets.animated_paned.animated_paned as animated_paned
from setzer.app.service_locator import ServiceLocator

import os.path


class MainWindow(Adw.ApplicationWindow):

    def __init__(self, app):
        Adw.ApplicationWindow.__init__(self, application=app)

        self.app = app
        self.set_size_request(-1, 550)

        self.popoverlay = Gtk.Overlay()
        self.set_content(self.popoverlay)

    def create_widgets(self):
        self.shortcutsbar = shortcutsbar_view.Shortcutsbar()

        self.document_stack = Gtk.Notebook()
        self.document_stack.set_show_tabs(False)
        self.document_stack.set_show_border(False)
        self.document_stack.set_scrollable(True)
        self.document_stack.set_size_request(550, -1)
        self.document_stack.set_vexpand(True)

        self.document_stack_wrapper = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.document_stack_wrapper.append(self.shortcutsbar)
        self.document_stack_wrapper.append(self.document_stack)

        self.build_log = build_log_view.BuildLogView()
        self.build_log_paned = animated_paned.AnimatedVPaned(self.document_stack_wrapper, self.build_log, False)

        self.preview_panel = preview_panel_view.PreviewPanelView()

        self.help_panel = help_panel_view.HelpPanelView()

        self.sidebar = sidebar_view.Sidebar()

        self.preview_paned_overlay = Gtk.Overlay()
        self.preview_help_stack = Gtk.Stack()
        self.preview_help_stack.add_named(self.preview_panel, 'preview')
        self.preview_help_stack.add_named(self.help_panel, 'help')
        self.preview_paned = animated_paned.AnimatedHPaned(self.build_log_paned, self.preview_help_stack, False)
        self.preview_paned.set_wide_handle(True)
        self.preview_paned_overlay.set_child(self.preview_paned)

        self.sidebar_paned = animated_paned.AnimatedHPaned(self.sidebar, self.preview_paned_overlay, True)
        self.sidebar_paned.set_wide_handle(True)
        self.sidebar_paned.get_style_context().add_class('sidebar_paned')

        self.welcome_screen = welcome_screen_view.WelcomeScreenView()

        self.mode_stack = Gtk.Stack()
        self.mode_stack.add_named(self.welcome_screen, 'welcome_screen')
        self.mode_stack.add_named(self.sidebar_paned, 'documents')

        self.headerbar = headerbar_view.HeaderBar()
        self.headerbar.set_vexpand(False)
        self.headerbar.set_valign(Gtk.Align.START)

        self.main_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.main_box.append(self.headerbar)
        self.main_box.append(self.mode_stack)
        self.popoverlay.set_child(self.main_box)

        self.css_provider = Gtk.CssProvider()
        resources_path = ServiceLocator.get_resources_path()
        self.css_provider.load_from_path(os.path.join(resources_path, 'style_gtk.css'))
        Gtk.StyleContext.add_provider_for_display(self.get_display(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.css_provider_font_size = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(self.get_display(), self.css_provider_font_size, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.css_provider_colors = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(self.get_display(), self.css_provider_colors, Gtk.STYLE_PROVIDER_PRIORITY_USER)


