#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2018 Robert Griesel
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
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib

import sys, time

from workspace.workspace import Workspace
import workspace.workspace_viewgtk as view
import helpers.helpers as helpers
from app.service_locator import ServiceLocator


class MainApplicationController(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        ''' Everything starts here. '''
        
        settings = ServiceLocator.get_settings()

        # setup dark mode
        dm_default = GLib.Variant.new_boolean(settings.get_value('preferences', 'prefer_dark_mode'))
        self.toggle_dark_mode_action = Gio.SimpleAction.new_stateful('toggle-dark-mode', None, dm_default)
        settings.gtksettings.get_default().set_property('gtk-application-prefer-dark-theme', dm_default)
        
        # init main window, model, dialogs
        self.main_window = view.MainWindow(self)
        self.main_window.add_action(self.toggle_dark_mode_action)
        self.toggle_dark_mode_action.connect('activate', self.toggle_dark_mode)
        ServiceLocator.init_main_window(self.main_window)
        self.workspace = Workspace()
        ServiceLocator.init_dialogs(self.main_window, self.workspace)

        # init view
        if settings.get_value('window_state', 'is_maximized'):
            self.main_window.maximize()
        else: 
            self.main_window.unmaximize()
        self.main_window.set_default_size(settings.get_value('window_state', 'width'), 
                                          settings.get_value('window_state', 'height'))
        self.main_window.current_width = settings.get_value('window_state', 'width')
        self.main_window.current_height = settings.get_value('window_state', 'height')
        self.fg_color = helpers.theme_color_to_rgba(self.main_window.get_style_context(), 'theme_fg_color')
        self.bg_color = helpers.theme_color_to_rgba(self.main_window.get_style_context(), 'theme_bg_color')
        self.style_context = self.main_window.get_style_context()
        self.first_window_state_event = True
        self.main_window.show_all()
        self.observe_main_window()

        # init controller
        self.workspace.init_workspace_controller()
        self.main_window.quit_action.connect('activate', self.on_quit_action)
        self.workspace.shortcuts.accel_group.connect(Gdk.keyval_from_name('q'), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.MASK, self.save_quit)

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def observe_main_window(self):
        self.main_window.connect('size-allocate', self.on_window_size_allocate)
        self.main_window.connect('notify::is-maximized', self.on_window_maximize_event)
        self.main_window.connect('delete-event', self.on_window_close)
        self.main_window.connect('draw', self.on_window_draw)
    
    def on_window_size_allocate(self, main_window, window_size):
        ''' signal handler, update window size variables '''

        if not main_window.ismaximized:
            main_window.current_width, main_window.current_height = main_window.get_size()

    def on_window_maximize_event(self, main_window, state_event):
        ''' signal handler, update window state variables '''

        main_window.ismaximized = main_window.is_maximized()
        return False
    
    def on_window_draw(self, main_window, context):
        ''' check for theme changes, update sidebar, textviews '''

        fg_color = helpers.theme_color_to_rgba(self.style_context, 'theme_fg_color')
        bg_color = helpers.theme_color_to_rgba(self.style_context, 'theme_bg_color')
        if self.fg_color.red != fg_color.red or self.bg_color.red != bg_color.red:
            self.fg_color = fg_color
            self.bg_color = bg_color
            
            try: documents = self.workspace.open_documents
            except AttributeError: pass
            else:
                is_dark_mode = helpers.is_dark_mode(main_window)
                for document in documents:
                    document.set_use_dark_scheme(is_dark_mode)
                
                parent_folder = 'dark' if is_dark_mode else 'light'
                for page_view in self.workspace.sidebar.page_views:
                    page_view.change_parent_folder(parent_folder)
        return False

    def save_window_state(self):
        ''' save window state variables '''

        settings = ServiceLocator.get_settings()
        main_window = self.main_window
        settings.set_value('window_state', 'width', main_window.current_width)
        settings.set_value('window_state', 'height', main_window.current_height)
        settings.set_value('window_state', 'is_maximized', main_window.ismaximized)
        settings.set_value('window_state', 'show_sidebar', self.workspace.show_sidebar)
        settings.set_value('window_state', 'sidebar_paned_position', self.workspace.sidebar_position)
        settings.set_value('window_state', 'show_preview', self.workspace.show_preview)
        settings.set_value('window_state', 'preview_paned_position', self.workspace.preview_position)
        settings.set_value('window_state', 'show_build_log', self.workspace.show_build_log)
        settings.set_value('window_state', 'build_log_paned_position', self.workspace.build_log_position)
        settings.pickle()

    def on_window_close(self, window=None, parameter=None):
        self.save_quit()
        return True

    def on_quit_action(self, action=None, parameter=None):
        self.save_quit()

    def save_quit(self, accel_group=None, window=None, key=None, mask=None):
        for document in self.workspace.open_documents: document.save_document_data()

        documents = self.workspace.get_unsaved_documents()
        active_document = self.workspace.get_active_document()

        if documents == None or active_document == None or ServiceLocator.get_dialog('close_confirmation').run(documents)['all_save_to_close']:
            self.save_window_state()
            self.workspace.save_to_disk()
            self.quit()

    def toggle_dark_mode(self, action, parameter=None):
        settings = ServiceLocator.get_settings()
        new_state = not action.get_state().get_boolean()
        action.set_state(GLib.Variant.new_boolean(new_state))
        settings.gtksettings.get_default().set_property('gtk-application-prefer-dark-theme', new_state)
        settings.set_value('preferences', 'prefer_dark_mode', new_state)
    

main_controller = MainApplicationController()
exit_status = main_controller.run(sys.argv)
sys.exit(exit_status)
