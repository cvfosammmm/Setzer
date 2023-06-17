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
from gi.repository import Gtk

import setzer.workspace.headerbar.headerbar_viewgtk as headerbar_view
import setzer.workspace.welcome_screen.welcome_screen_viewgtk as welcome_screen_view
import setzer.widgets.animated_paned.animated_paned as animated_paned
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

        # latex notebook
        self.latex_notebook = Gtk.Notebook()
        self.latex_notebook.set_show_tabs(False)
        self.latex_notebook.set_show_border(False)
        self.latex_notebook.set_scrollable(True)
        self.latex_notebook.set_size_request(550, -1)
        self.latex_notebook_wrapper = Gtk.VBox()
        self.latex_notebook_wrapper.pack_start(self.latex_notebook, True, True, 0)

        # bibtex notebook
        self.bibtex_notebook = Gtk.Notebook()
        self.bibtex_notebook.set_show_tabs(False)
        self.bibtex_notebook.set_show_border(False)
        self.bibtex_notebook.set_scrollable(True)
        self.bibtex_notebook.set_size_request(550, -1)
        self.bibtex_notebook_wrapper = Gtk.VBox()
        self.bibtex_notebook_wrapper.pack_start(self.bibtex_notebook, True, True, 0)

        # others notebook
        self.others_notebook = Gtk.Notebook()
        self.others_notebook.set_show_tabs(False)
        self.others_notebook.set_show_border(False)
        self.others_notebook.set_scrollable(True)
        self.others_notebook.set_size_request(550, -1)
        self.others_notebook_wrapper = Gtk.VBox()
        self.others_notebook_wrapper.pack_start(self.others_notebook, True, True, 0)

        # build log
        self.build_log = Gtk.Label('build log placeholder')
        self.build_log_paned = animated_paned.AnimatedVPaned(self.latex_notebook_wrapper, self.build_log, False)
        self.build_log_visible = None

        # preview
        self.preview_panel = Gtk.Label('preview placeholder')
        self.preview_visible = None

        # help
        self.help_panel = Gtk.Label('help panel placeholder')
        self.help_visible = None

        # paneds
        self.preview_paned_overlay = Gtk.Overlay()
        self.overlay_widget = None
        self.preview_help_stack = Gtk.Stack()
        self.preview_help_stack.add_named(self.preview_panel, 'preview')
        self.preview_help_stack.add_named(self.help_panel, 'help')
        self.preview_paned = animated_paned.AnimatedHPaned(self.build_log_paned, self.preview_help_stack, False)
        self.preview_paned_overlay.add(self.preview_paned)
        self.sidebar_paned = animated_paned.AnimatedHPaned(Gtk.Label('sidebar placeholder'), self.preview_paned_overlay, True)
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
        self.add(self.mode_stack)

        self.css_provider = Gtk.CssProvider()
        resources_path = ServiceLocator.get_resources_path()
        self.css_provider.load_from_path(os.path.join(resources_path, 'style_gtk.css'))
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.css_provider_font_size = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(), self.css_provider_font_size, Gtk.STYLE_PROVIDER_PRIORITY_USER)


