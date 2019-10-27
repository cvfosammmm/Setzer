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

from viewgtk.viewgtk_headerbar import *
from viewgtk.viewgtk_shortcutsbar import *
from viewgtk.viewgtk_document_search import *
from viewgtk.viewgtk_document_autocomplete import *
from viewgtk.viewgtk_sidebar import *
from viewgtk.viewgtk_preview import *

import os


class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(self, application=app)
        self.set_size_request(-1, 550)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.dirname(__file__) + '/../resources/icons')
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.dirname(__file__) + '/../resources/symbols/light/arrows')
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.dirname(__file__) + '/../resources/symbols/light/delimiters')
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
        self.notebook_wrapper = Gtk.HBox()
        self.notebook = DocumentViewWrapper()
        self.shortcuts_bar = ShortcutsBar()
        self.notebook_wrapper.pack_start(self.shortcuts_bar, False, False, 0)
        self.notebook_wrapper.pack_start(self.notebook, True, True, 0)

        # preview
        self.preview = PreviewView()
        self.preview_visible = False
        self.headerbar.preview_toggle.set_active(app.settings.get_value('window_state', 'show_preview'))
        
        # sidebar
        self.sidebar = Sidebar()
        self.sidebar_visible = False
        self.shortcuts_bar.sidebar_toggle.set_active(app.settings.get_value('window_state', 'show_sidebar'))

        # paneds
        self.preview_paned_overlay = Gtk.Overlay()
        self.overlay_widget = None
        self.preview_paned = Gtk.HPaned()
        self.preview_paned.pack1(self.notebook_wrapper, True, False)
        self.preview_paned.pack2(self.preview, False, True)
        self.preview_paned_overlay.add(self.preview_paned)
        self.sidebar_paned = Gtk.HPaned()
        self.sidebar_paned.pack1(self.sidebar, False, True)
        self.sidebar_paned.pack2(self.preview_paned_overlay, True, False)
        self.sidebar_paned.get_style_context().add_class('sidebar_paned')
        self.add(self.sidebar_paned)
        
        # blank slate
        self.blank_slate = BlankSlate()
        self.notebook.add(self.blank_slate)

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_path(os.path.dirname(__file__) + '/../resources/style_gtk.css')
        self.style_context = Gtk.StyleContext()
        self.style_context.add_provider_for_screen(self.get_screen(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)


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
        

