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
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib

from document.document import Document
import helpers.helpers as helpers
from app.service_locator import ServiceLocator

import time


class WorkspaceController(object):
    ''' Mediator between workspace and view. '''
    
    def __init__(self, workspace):

        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()

        self.observe_workspace_view()
        
        self.untitled_documents_no = 0

        self.p_allocation = 0
        self.pp_allocation = 0
        self.s_allocation = 0
        self.bl_allocation = 0

        self.main_window.save_as_action.connect('activate', self.on_save_as_clicked)
        self.main_window.save_all_action.connect('activate', self.on_save_all_clicked)
        self.main_window.find_action.connect('activate', self.on_menu_find_clicked)
        self.main_window.find_next_action.connect('activate', self.find_next)
        self.main_window.find_prev_action.connect('activate', self.find_prev)
        self.main_window.find_replace_action.connect('activate', self.on_menu_find_replace_clicked)
        self.main_window.close_all_action.connect('activate', self.on_close_all_clicked)
        self.main_window.close_document_action.connect('activate', self.on_close_document_clicked)
        self.main_window.insert_before_after_action.connect('activate', self.insert_before_after)
        self.main_window.insert_symbol_action.connect('activate', self.insert_symbol)
        self.main_window.document_wizard_action.connect('activate', self.start_wizard)
        self.main_window.shortcuts_window_action.connect('activate', self.show_shortcuts_window)
        self.main_window.show_preferences_action.connect('activate', self.show_preferences_dialog)
        self.main_window.show_about_action.connect('activate', self.show_about_dialog)
        self.main_window.close_build_log_action.connect('activate', self.close_build_log)

        # populate workspace
        self.workspace.populate_from_disk()
        open_documents = self.workspace.open_documents
        if len(open_documents) > 0:
            self.workspace.set_active_document(open_documents[-1])

    def observe_workspace_view(self):
        self.observe_document_chooser()
        self.main_window.headerbar.new_document_button.connect('clicked', self.on_new_document_button_click)
        self.main_window.headerbar.save_document_button.connect('clicked', self.on_save_button_click)
        self.main_window.headerbar.sidebar_toggle.connect('toggled', self.on_sidebar_toggle_toggled)
        self.main_window.headerbar.preview_toggle.connect('toggled', self.on_preview_toggle_toggled)
        self.main_window.sidebar.connect('size-allocate', self.on_sidebar_size_allocate)
        self.main_window.preview.connect('size-allocate', self.on_preview_size_allocate)
        self.main_window.preview_paned.connect('size-allocate', self.on_preview_paned_size_allocate)
        self.main_window.notebook_wrapper.connect('size-allocate', self.on_build_log_size_allocate)
        self.main_window.shortcuts_bar.button_build_log.connect('clicked', self.on_build_log_button_clicked)

    def observe_document_chooser(self):
        document_chooser = self.main_window.headerbar.document_chooser
        document_chooser.connect('closed', self.on_document_chooser_closed)
        search_buffer = document_chooser.search_entry.get_buffer()
        search_buffer.connect('inserted-text', self.on_document_chooser_search_changed)
        search_buffer.connect('deleted-text', self.on_document_chooser_search_changed)
        auto_suggest_box = document_chooser.auto_suggest_box
        auto_suggest_box.connect('row-activated', self.on_document_chooser_selection)
        document_chooser.other_documents_button.connect('clicked', self.on_open_document_button_click)
        self.main_window.headerbar.open_document_blank_button.connect('clicked', self.on_open_document_button_click)

    '''
    *** decorators
    '''
    
    def _assert_has_active_document(original_function):
        def new_function(self, *args, **kwargs):
            if self.workspace.get_active_document() != None:
                return original_function(self, *args, **kwargs)
        return new_function    

    ''' 
    *** signal handlers: headerbar
    '''
    
    def on_document_chooser_closed(self, document_chooser, data=None):
        document_chooser.search_entry.set_text('')
        document_chooser.auto_suggest_box.unselect_all()
        
    def on_document_chooser_search_changed(self, search_entry, position=None, chars1=None, chars2=None, user_data=None):
        self.main_window.headerbar.document_chooser.search_filter()
    
    def on_document_chooser_selection(self, box, row):
        self.main_window.headerbar.document_chooser.popdown()
        filename = row.folder + '/' + row.filename
        document_candidate = self.workspace.get_document_by_filename(filename)

        if isinstance(document_candidate, Document):
            self.workspace.set_active_document(document_candidate)
        else:
            document = Document(self.workspace, self.workspace.pathname, with_buffer=True)
            document.set_filename(filename)
            document.populate_from_filename()
            self.workspace.add_document(document)
            self.workspace.set_active_document(document)

    def on_open_document_button_click(self, button_object=None):
        filename = ServiceLocator.get_dialog('open_document').run()
        if filename != None:
            document_candidate = self.workspace.get_document_by_filename(filename)
            if document_candidate != None:
                self.workspace.set_active_document(document_candidate)
            else:
                document = Document(self.workspace, self.workspace.pathname, with_buffer=True)
                document.set_filename(filename)
                document.populate_from_filename()
                self.workspace.add_document(document)
                self.workspace.set_active_document(document)

    def on_new_document_button_click(self, button_object=None):
        document = Document(self.workspace, self.workspace.pathname, with_buffer=True)
        self.workspace.add_document(document)
        self.workspace.set_active_document(document)

    def on_doclist_close_clicked(self, button_object, document):
        if document.get_modified():
            dialog = ServiceLocator.get_dialog('close_confirmation')
            not_save_to_close = dialog.run([document])['not_save_to_close_documents']
            if document not in not_save_to_close:
                self.workspace.remove_document(document)
        else:
            self.workspace.remove_document(document)
        
    def on_build_log_button_clicked(self, toggle_button, parameter=None):
        self.workspace.set_show_build_log(toggle_button.get_active())

    @_assert_has_active_document
    def on_save_button_click(self, button_object=None):
        active_document = self.workspace.get_active_document()
        if active_document.filename == None:
            self.on_save_as_clicked()
        else:
            active_document.save_to_disk()
    
    '''
    *** workspace menu
    '''
    
    @_assert_has_active_document
    def on_save_as_clicked(self, action=None, parameter=None):
        document = self.workspace.get_active_document()
        filename = document.get_filename().rsplit('/', 1)[1]
        if filename != None:
            ServiceLocator.get_dialog('save_document').run(document, filename)
        else:
            ServiceLocator.get_dialog('save_document').run(document, '.tex')
        
    @_assert_has_active_document
    def on_save_all_clicked(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        return_to_active_document = False
        documents = self.workspace.get_unsaved_documents()
        if documents != None: 
            for document in documents:
                if document.get_filename() == None:
                    self.workspace.set_active_document(document)
                    return_to_active_document = True
                    ServiceLocator.get_dialog('save_document').run(document, '.tex')
                else:
                    document.save_to_disk()
            if return_to_active_document == True:
                self.workspace.set_active_document(document)

    @_assert_has_active_document
    def on_menu_find_clicked(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        active_document.view.shortcuts_bar_bottom.button_find.set_active(True)
        GLib.idle_add(active_document.search.search_entry_grab_focus, None)

    @_assert_has_active_document
    def find_next(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        if active_document.view.source_view.has_focus() or active_document.view.search_bar.entry.has_focus() or active_document.view.search_bar.replace_entry.has_focus():
            active_document.view.search_bar.entry.emit('next-match')

    @_assert_has_active_document
    def find_prev(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        if active_document.controller.document_view.source_view.has_focus() or active_document.controller.document_view.search_bar.entry.has_focus() or active_document.controller.document_view.search_bar.replace_entry.has_focus():
            active_document.controller.document_view.search_bar.entry.emit('previous-match')

    @_assert_has_active_document
    def on_menu_find_replace_clicked(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        active_document.view.shortcuts_bar_bottom.button_find_and_replace.set_active(True)
        GLib.idle_add(active_document.search.search_entry_grab_focus, None)

    @_assert_has_active_document
    def on_close_all_clicked(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        documents = self.workspace.get_all_documents()
        unsaved_documents = self.workspace.get_unsaved_documents()
        dialog = ServiceLocator.get_dialog('close_confirmation')
        not_save_to_close_documents = dialog.run(unsaved_documents)['not_save_to_close_documents']

        for document in documents:
            if document not in not_save_to_close_documents:
                self.workspace.remove_document(document)

    def activate_quotes_popover(self, action=None, parameter=None):
        self.main_window.shortcuts_bar.quotes_button.set_active(True)

    def on_close_document_clicked(self, action=None, parameter=None):
        document = self.workspace.get_active_document()
        self.on_doclist_close_clicked(None, document)
        
    def on_sidebar_toggle_toggled(self, toggle_button, parameter=None):
        self.workspace.set_show_sidebar(toggle_button.get_active(), True)

    def on_preview_toggle_toggled(self, toggle_button, parameter=None):
        self.workspace.set_show_preview(toggle_button.get_active(), True)

    def on_sidebar_size_allocate(self, sidebar, allocation):
        if not self.workspace.presenter.sidebars_initialized: return
        if allocation.width != self.s_allocation:
            self.s_allocation = allocation.width
            if self.workspace.show_sidebar and self.workspace.active_document != None:
                if not self.workspace.presenter.sidebar_animating:
                    self.workspace.set_sidebar_position(allocation.width)

    def on_preview_size_allocate(self, preview, allocation):
        if not self.workspace.presenter.sidebars_initialized: return
        if allocation.width != self.p_allocation:
            self.p_allocation = allocation.width
            if self.workspace.show_preview and self.workspace.active_document != None:
                if not self.workspace.presenter.preview_animating:
                    self.workspace.set_preview_position(self.main_window.preview_paned.get_position())

    def on_build_log_size_allocate(self, build_log, allocation):
        if not self.workspace.presenter.sidebars_initialized: return
        if allocation.height != self.bl_allocation:
            self.bl_allocation = allocation.height
            if self.workspace.show_build_log and self.workspace.active_document != None:
                if not self.workspace.presenter.build_log_animating:
                    self.workspace.set_build_log_position(self.main_window.build_log_paned.get_position())

    def on_preview_paned_size_allocate(self, preview, allocation):
        if not self.workspace.presenter.sidebars_initialized: return
        if allocation.width != self.pp_allocation:
            self.pp_allocation = allocation.width
            if self.workspace.show_preview and self.workspace.active_document != None:
                if not self.workspace.presenter.preview_animating:
                    self.workspace.set_preview_position(self.main_window.preview_paned.get_position())

    '''
    *** actions
    '''
    
    @_assert_has_active_document
    def switch_to_earliest_open_document(self):
        self.workspace.set_active_document(self.workspace.get_earliest_active_document())
    
    @_assert_has_active_document
    def insert_symbol(self, action, parameter):
        ''' insert text at the cursor. '''
        
        text = parameter[0]
        active_document = self.workspace.get_active_document()
        buff = active_document.get_buffer()

        if buff != False:
            buff.begin_user_action()

            dotindex = text.find('•')
            dotcount = text.count('•')
            if dotcount == 1:
                bounds = buff.get_selection_bounds()
                selection = buff.get_text(bounds[0], bounds[1], True)
                if len(selection) > 0:
                    text = text.replace('•', selection, 1)
                buff.delete_selection(False, False)
                buff.insert_at_cursor(text)
                start = buff.get_iter_at_mark(buff.get_insert())
                start.backward_chars(abs(dotindex + len(selection) - len(text)))
                buff.place_cursor(start)
            elif dotcount > 0:
                buff.delete_selection(False, False)
                buff.insert_at_cursor(text)
                start = buff.get_iter_at_mark(buff.get_insert())
                start.backward_chars(abs(dotindex - len(text)))
                end = start.copy()
                end.forward_char()
                buff.select_range(start, end)
            else:
                buff.delete_selection(False, False)
                buff.insert_at_cursor(text)
            active_document.view.source_view.scroll_to_mark(buff.get_insert(), 0, False, 0, 0)

            buff.end_user_action()

    @_assert_has_active_document
    def start_wizard(self, action, parameter=None):
        document = self.workspace.get_active_document()
        ServiceLocator.get_dialog('document_wizard').run(document)

    def show_shortcuts_window(self, action, parameter=''):
        ServiceLocator.get_dialog('keyboard_shortcuts').run()

    def show_preferences_dialog(self, action=None, parameter=''):
        ServiceLocator.get_dialog('preferences').run()

    def show_about_dialog(self, action, parameter=''):
        ServiceLocator.get_dialog('about').run()

    def close_build_log(self, action, parameter=''):
        self.workspace.set_show_build_log(False)
        
    @_assert_has_active_document
    def insert_before_after(self, action, parameter):
        ''' wrap text around current selection. '''

        before = parameter[0]
        after = parameter[1]

        active_document = self.workspace.get_active_document()
        buff = active_document.get_buffer()
        if buff != False:
            bounds = buff.get_selection_bounds()
            buff.begin_user_action()
            if len(bounds) > 1:
                text = before + buff.get_text(*bounds, 0) + after
                buff.delete_selection(False, False)
                buff.insert_at_cursor(text)
                cursor_pos = buff.get_iter_at_mark(buff.get_insert())
                cursor_pos.backward_chars(len(after))
                buff.place_cursor(cursor_pos)
                active_document.view.source_view.scroll_to_mark(buff.get_insert(), 0, False, 0, 0)
            else:
                text = before + '•' + after
                buff.insert_at_cursor(text)
                cursor_pos = buff.get_iter_at_mark(buff.get_insert())
                cursor_pos.backward_chars(len(after))
                bound = cursor_pos.copy()
                bound.backward_chars(1)
                buff.select_range(bound, cursor_pos)
                active_document.view.source_view.scroll_to_mark(buff.get_insert(), 0, False, 0, 0)
            buff.end_user_action()


