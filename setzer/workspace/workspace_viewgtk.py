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

import os


class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, app, settings):
        Gtk.Window.__init__(self, application=app)
        self.app = app
        self.set_size_request(-1, 550)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        resources_path = ServiceLocator.get_resources_path()
        app_icons_path = ServiceLocator.get_app_icons_path()
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.join(resources_path, 'icons'))
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.join(resources_path, 'symbols', 'arrows'))
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.join(resources_path, 'symbols', 'greek_letters'))
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.join(resources_path, 'symbols', 'misc_math'))
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.join(resources_path, 'symbols', 'misc_text'))
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.join(resources_path, 'symbols', 'operators'))
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.join(resources_path, 'symbols', 'relations'))
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), app_icons_path)

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
        self.css_provider.load_from_path(os.path.join(resources_path, 'style_gtk.css'))
        self.style_context = Gtk.StyleContext()
        self.style_context.add_provider_for_screen(self.get_screen(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.css_provider_font_size = Gtk.CssProvider()
        self.style_context.add_provider_for_screen(self.get_screen(), self.css_provider_font_size, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # actions
        self.new_latex_document_action = Gio.SimpleAction.new('new-latex-document', None)
        self.add_action(self.new_latex_document_action)

        self.new_bibtex_document_action = Gio.SimpleAction.new('new-bibtex-document', None)
        self.add_action(self.new_bibtex_document_action)

        self.save_as_action = Gio.SimpleAction.new('save-as', None)
        self.add_action(self.save_as_action)

        self.save_all_action = Gio.SimpleAction.new('save-all', None)
        self.add_action(self.save_all_action)

        self.save_session_action = Gio.SimpleAction.new('save-session', None)
        self.add_action(self.save_session_action)

        self.restore_session_action = Gio.SimpleAction.new('restore-session', GLib.VariantType('as'))
        self.add_action(self.restore_session_action)

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

        self.insert_before_document_end_action = Gio.SimpleAction.new('insert-before-document-end', GLib.VariantType('as'))
        self.add_action(self.insert_before_document_end_action)

        self.document_wizard_action = Gio.SimpleAction.new('show-document-wizard', None)
        self.add_action(self.document_wizard_action)

        self.create_new_bibtex_entry_action = Gio.SimpleAction.new('create-new-bibtex-entry', None)
        self.add_action(self.create_new_bibtex_entry_action)

        self.show_previous_bibtex_entries_action = Gio.SimpleAction.new('show-previous-bibtex-entries', None)
        self.add_action(self.show_previous_bibtex_entries_action)

        self.search_online_for_bibtex_entries_action = Gio.SimpleAction.new('search-online-for-bibtex-entries', None)
        self.add_action(self.search_online_for_bibtex_entries_action)

        self.include_bibtex_file_action = Gio.SimpleAction.new('include-bibtex-file', None)
        self.add_action(self.include_bibtex_file_action)

        self.include_latex_file_action = Gio.SimpleAction.new('include-latex-file', None)
        self.add_action(self.include_latex_file_action)

        self.add_remove_packages_dialog_action = Gio.SimpleAction.new('add-remove-packages-dialog', None)
        self.add_action(self.add_remove_packages_dialog_action)

        self.add_packages_action = Gio.SimpleAction.new('add-packages', GLib.VariantType('as'))
        self.add_action(self.add_packages_action)

        self.comment_uncomment_action = Gio.SimpleAction.new('comment-uncomment', None)
        self.add_action(self.comment_uncomment_action)

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

        sc_default = GLib.Variant.new_boolean(settings.get_value('preferences', 'inline_spellchecking'))
        self.toggle_spellchecking_action = Gio.SimpleAction.new_stateful('toggle-spellchecking', None, sc_default)
        self.add_action(self.toggle_spellchecking_action)

        self.set_spellchecking_language_action = Gio.SimpleAction.new('set-spellchecking-language', None)
        self.add_action(self.set_spellchecking_language_action)

        self.spellchecking_action = Gio.SimpleAction.new('spellchecking', None)
        self.add_action(self.spellchecking_action)

        dm_default = GLib.Variant.new_boolean(settings.get_value('preferences', 'prefer_dark_mode'))
        self.toggle_dark_mode_action = Gio.SimpleAction.new_stateful('toggle-dark-mode', None, dm_default)
        self.add_action(self.toggle_dark_mode_action)
        settings.gtksettings.get_default().set_property('gtk-application-prefer-dark-theme', dm_default)

        ip_default = GLib.Variant.new_boolean(settings.get_value('preferences', 'invert_pdf'))
        self.toggle_invert_pdf_action = Gio.SimpleAction.new_stateful('toggle-invert-pdf', None, ip_default)
        self.add_action(self.toggle_invert_pdf_action)

        self.zoom_out_action = Gio.SimpleAction.new('zoom-out', None)
        self.add_action(self.zoom_out_action)

        self.zoom_in_action = Gio.SimpleAction.new('zoom-in', None)
        self.add_action(self.zoom_in_action)

        self.reset_zoom_action = Gio.SimpleAction.new('reset-zoom', None)
        self.add_action(self.reset_zoom_action)


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
        

