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
from gi.repository import GLib, Gio

from document.document import Document, LaTeXDocument, BibTeXDocument
import helpers.helpers as helpers
from app.service_locator import ServiceLocator


class WorkspacePresenter(object):
    ''' Mediator between workspace and view. '''
    
    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.workspace.register_observer(self)

        self.sidebars_initialized = False
        self.sidebar = self.main_window.sidebar
        self.sidebar_animating = False
        self.preview_animating = False
        self.build_log_animating = False
        self.activate_blank_slate_mode()

        def on_window_state(widget, event): self.on_realize()
        self.main_window.connect('draw', on_window_state)
        
    '''
    *** notification handlers, get called by observed workspace
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_document':
            document = parameter
            document.set_use_dark_scheme(helpers.is_dark_mode(self.main_window))

            if isinstance(document, LaTeXDocument):
                self.main_window.notebook.append_page(document.view)

            elif isinstance(document, BibTeXDocument):
                self.main_window.bibtex_notebook.append_page(document.view)

        if change_code == 'document_removed':
            document = parameter

            if isinstance(document, LaTeXDocument):
                self.main_window.notebook.remove(document.view)

            elif isinstance(document, BibTeXDocument):
                self.main_window.bibtex_notebook.remove(document.view)

            if self.workspace.active_document == None:
                self.activate_blank_slate_mode()

        if change_code == 'new_active_document':
            document = parameter

            if isinstance(document, LaTeXDocument):
                notebook = self.main_window.notebook
                notebook.set_current_page(notebook.page_num(document.view))
                document.view.source_view.grab_focus()
                self.main_window.preview_paned_overlay.add_overlay(document.autocomplete.view)
                document.autocomplete.update_autocomplete_position()

                self.update_latex_shortcuts_bar()
                self.set_preview_document()
                self.activate_latex_documents_mode()

            elif isinstance(document, BibTeXDocument):
                notebook = self.main_window.bibtex_notebook
                notebook.set_current_page(notebook.page_num(document.view))
                document.view.source_view.grab_focus()

                self.update_bibtex_shortcuts_bar()
                self.activate_bibtex_documents_mode()

        if change_code == 'new_inactive_document':
            document = parameter

            if isinstance(document, LaTeXDocument):
                self.main_window.preview_paned_overlay.remove(document.autocomplete.view)
                self.main_window.shortcuts_bar.top_icons.remove(document.view.wizard_button)

        if change_code == 'set_show_sidebar':
            self.animate_sidebar(parameter, True)

        if change_code == 'set_show_preview':
            self.animate_preview(parameter, True)

        if change_code == 'show_build_log_state_change':
            self.build_log_animate(parameter, True)

        if change_code == 'master_state_change':
            self.set_preview_document()

        if change_code == 'set_dark_mode':
            ServiceLocator.get_settings().gtksettings.get_default().set_property('gtk-application-prefer-dark-theme', parameter)

    def activate_blank_slate_mode(self):
        self.main_window.mode_stack.set_visible_child_name('blank_slate')
        self.main_window.save_all_action.set_enabled(False)
        self.main_window.shortcuts_bar.button_build_log.get_child().set_sensitive(False)
        self.set_document_actions_active(False)
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\textbf{', '}'])), [])
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\textit{', '}'])), [])

    def activate_latex_documents_mode(self):
        self.main_window.mode_stack.set_visible_child_name('latex_documents')
        self.main_window.shortcuts_bar.button_build_log.get_child().set_sensitive(True)
        self.set_document_actions_active(True)
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\textbf{', '}'])), ['<Control>b'])
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\textit{', '}'])), ['<Control>i'])

    def activate_bibtex_documents_mode(self):
        self.main_window.mode_stack.set_visible_child_name('bibtex_documents')
        self.main_window.shortcuts_bar.button_build_log.get_child().set_sensitive(False)
        self.set_document_actions_active(True)
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\textbf{', '}'])), [])
        self.main_window.app.set_accels_for_action(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\textit{', '}'])), [])

    def update_latex_shortcuts_bar(self):
        document = self.workspace.active_document
        shortcuts_bar = self.main_window.shortcuts_bar

        if shortcuts_bar.current_bottom != None:
            shortcuts_bar.remove(shortcuts_bar.current_bottom)
        shortcuts_bar.current_bottom = document.view.shortcuts_bar_bottom
        shortcuts_bar.pack_end(document.view.shortcuts_bar_bottom, False, False, 0)
        shortcuts_bar.top_icons.insert(document.view.wizard_button, 0)

    def update_bibtex_shortcuts_bar(self):
        document = self.workspace.active_document
        shortcuts_bar = self.main_window.bibtex_shortcuts_bar

        if shortcuts_bar.current_bottom != None:
            shortcuts_bar.remove(shortcuts_bar.current_bottom)
        shortcuts_bar.current_bottom = document.view.shortcuts_bar_bottom
        shortcuts_bar.pack_end(document.view.shortcuts_bar_bottom, False, False, 0)

    def set_preview_document(self):
        if self.workspace.get_active_document() != None:
            if self.workspace.master_document != None:
                self.workspace.preview.set_active_document(self.workspace.master_document)
            else:
                self.workspace.preview.set_active_document(self.workspace.active_document)

    def set_document_actions_active(self, value):
        self.main_window.save_as_action.set_enabled(value)
        self.main_window.find_action.set_enabled(value)
        self.main_window.find_next_action.set_enabled(value)
        self.main_window.find_prev_action.set_enabled(value)
        self.main_window.find_replace_action.set_enabled(value)
        self.main_window.close_document_action.set_enabled(value)
        self.main_window.close_all_action.set_enabled(value)
        self.main_window.insert_before_after_action.set_enabled(value)
        self.main_window.insert_symbol_action.set_enabled(value)
        self.main_window.document_wizard_action.set_enabled(value)

    def on_realize(self, view=None, cr=None, user_data=None):
        if self.sidebars_initialized == False:
            self.animate_sidebar(self.workspace.show_sidebar, False)
            self.animate_preview(self.workspace.show_preview, False)
            self.build_log_animate(self.workspace.get_show_build_log(), False)
            self.sidebars_initialized = True

    def animate_sidebar(self, show_sidebar=False, animate=False, set_toggle=True):
        def set_position_on_tick(paned, frame_clock_cb, user_data=None):
            show_sidebar, set_toggle = user_data
            now = frame_clock_cb.get_frame_time()
            if now < end_time and paned.get_position != end:
                t = self.ease((now - start_time) / (end_time - start_time))
                paned.set_position(int(start + t * (end - start)))
                return True
            else:
                paned.set_position(end)
                if not show_sidebar:
                    self.sidebar.hide()
                    self.main_window.sidebar_visible = False
                else:
                    self.main_window.sidebar_paned.child_set_property(self.sidebar, 'shrink', False)
                    self.main_window.sidebar_visible = True
                    self.workspace.set_sidebar_position(paned.get_position())
                if set_toggle: self.main_window.headerbar.sidebar_toggle.set_active(show_sidebar)
                self.sidebar_animating = False
                return False

        if self.main_window.sidebar_visible == show_sidebar: return
        if self.sidebar_animating: return

        frame_clock = self.main_window.sidebar_paned.get_frame_clock()
        duration = 200

        if show_sidebar:
            end = self.workspace.sidebar_position
            if end == -1:
                end = 216
        else:
            end = 0

        if frame_clock != None and animate:
            if self.main_window.sidebar_paned.get_position() != end:
                if show_sidebar:
                    self.sidebar.show_all()
                    start = 0
                else:
                    start = self.workspace.sidebar_position
                start_time = frame_clock.get_frame_time()
                end_time = start_time + 1000 * duration
                self.sidebar_animating = True
                self.main_window.sidebar_paned.add_tick_callback(set_position_on_tick, (show_sidebar, set_toggle))
                self.main_window.sidebar_paned.child_set_property(self.sidebar, 'shrink', True)
        else:
            if show_sidebar:
                self.main_window.sidebar_paned.child_set_property(self.sidebar, 'shrink', False)
                self.sidebar.show_all()
                self.main_window.sidebar_visible = True
            else:
                self.main_window.sidebar_paned.child_set_property(self.sidebar, 'shrink', True)
                self.main_window.sidebar.hide()
                self.main_window.sidebar_visible = False
            self.main_window.sidebar_paned.set_position(end)
            if set_toggle: self.main_window.headerbar.sidebar_toggle.set_active(show_sidebar)

    def animate_preview(self, show_preview=False, animate=False, set_toggle=True):
        def set_position_on_tick(paned, frame_clock_cb, user_data=None):
            show_preview, set_toggle = user_data
            now = frame_clock_cb.get_frame_time()
            if now < end_time and paned.get_position != end:
                t = self.ease((now - start_time) / (end_time - start_time))
                paned.set_position(int(start + t * (end - start)))
                return True
            else:
                paned.set_position(end)
                if not show_preview:
                    self.main_window.preview.hide()
                    self.main_window.preview_visible = False
                else:
                    self.main_window.preview_paned.child_set_property(self.main_window.preview, 'shrink', False)
                    self.main_window.preview_visible = True
                    self.workspace.set_preview_position(paned.get_position())
                if set_toggle: self.main_window.headerbar.preview_toggle.set_active(show_preview)
                self.preview_animating = False
                return False

        if self.preview_animating: return
        if self.main_window.preview_visible == show_preview: return

        frame_clock = self.main_window.preview_paned.get_frame_clock()
        duration = 200

        if show_preview:
            self.main_window.preview_paned.get_style_context().remove_class('hidden-separator')
            self.main_window.preview_paned.get_style_context().add_class('visible-separator')
            end = self.workspace.preview_position
            if end == -1:
                end = self.main_window.preview_paned.get_allocated_width() / 2
        else:
            self.main_window.preview_paned.get_style_context().add_class('hidden-separator')
            self.main_window.preview_paned.get_style_context().remove_class('visible-separator')
            end = self.main_window.preview_paned.get_allocated_width()

        if frame_clock != None and animate:
            if show_preview:
                start = self.main_window.preview_paned.get_allocated_width()
                self.main_window.preview.show_all()
            else:
                start = self.workspace.preview_position
            if start != end:
                start_time = frame_clock.get_frame_time()
                end_time = start_time + 1000 * duration
                self.preview_animating = True
                self.main_window.preview_paned.add_tick_callback(set_position_on_tick, (show_preview, set_toggle))
                self.main_window.preview_paned.child_set_property(self.main_window.preview, 'shrink', True)
        else:
            if show_preview:
                if self.workspace.show_sidebar == False and self.main_window.sidebar.get_allocated_width() > 1:
                    end -= self.main_window.sidebar.get_allocated_width()
                self.main_window.preview_paned.child_set_property(self.main_window.preview, 'shrink', False)
                self.main_window.preview_visible = True
            else:
                self.main_window.preview_paned.child_set_property(self.main_window.preview, 'shrink', True)
                self.main_window.preview_visible = False
                self.main_window.preview.hide()
            self.main_window.preview_paned.set_position(end)
            if set_toggle: self.main_window.headerbar.preview_toggle.set_active(show_preview)

    def build_log_animate(self, show_build_log=True, animate=False):
        def set_position_on_tick(paned, frame_clock_cb, user_data=None):
            def ease(time): return (time - 1)**3 + 1;

            show_build_log = user_data
            now = frame_clock_cb.get_frame_time()
            if now < end_time and paned.get_position != end:
                t = ease((now - start_time) / (end_time - start_time))
                paned.set_position(int(start + t * (end - start)))
                return True
            else:
                paned.set_position(end)
                if not show_build_log:
                    self.main_window.build_log.hide()
                    self.main_window.build_log_visible = False
                else:
                    paned.child_set_property(self.main_window.build_log, 'shrink', False)
                    self.main_window.build_log_visible = True
                    self.workspace.set_build_log_position(paned.get_position())
                self.main_window.shortcuts_bar.button_build_log.set_active(show_build_log)
                self.build_log_animating = False
                return False

        if self.build_log_animating: return
        if self.main_window.build_log_visible == show_build_log: return

        frame_clock = self.main_window.build_log_paned.get_frame_clock()
        duration = 200

        if show_build_log:
            self.main_window.build_log.show_all()
            start = self.main_window.build_log_paned.get_allocated_height()
            end = self.workspace.build_log_position
            if end == -1:
                end = self.main_window.build_log_paned.get_allocated_height() - 201
        else:
            start = self.main_window.build_log_paned.get_position()
            end = self.main_window.build_log_paned.get_allocated_height()
            self.main_window.build_log_paned.child_set_property(self.main_window.build_log, 'shrink', True)
        if frame_clock != None and animate:
            start_time = frame_clock.get_frame_time()
            end_time = start_time + 1000 * duration
            self.build_log_animating = True
            self.main_window.build_log_paned.add_tick_callback(set_position_on_tick, show_build_log)
        else:
            if show_build_log:
                self.main_window.build_log_paned.child_set_property(self.main_window.build_log, 'shrink', False)
                self.main_window.build_log_visible = True
                self.main_window.build_log_paned.set_position(end)
            else:
                self.main_window.build_log_paned.child_set_property(self.main_window.build_log, 'shrink', True)
                self.main_window.build_log_visible = False
                self.main_window.build_log.hide()
            self.main_window.shortcuts_bar.button_build_log.set_active(show_build_log)

    def ease(self, time):
        return (time - 1)**3 + 1;


