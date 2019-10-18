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

import model.model_document as model_document
import viewgtk.viewgtk as view
import controller.controller_document as documentcontroller
import controller.controller_sidebar as sidebarcontroller
import controller.controller_preview as previewcontroller
import controller.controller_document_wizard as document_wizard_controller
import backend.backend as backend
import helpers.helpers as helpers
import dialogs.open_document.open_document as open_document_dialog
import dialogs.save_document.save_document as save_document_dialog
import dialogs.document_wizard.document_wizard as document_wizard

import time


class WorkspaceController(object):
    ''' Mediator between workspace and view. '''
    
    def __init__(self, workspace, main_window, settings, main_controller):

        self.workspace = workspace
        self.main_window = main_window
        self.backend = backend.Backend()
        self.settings = settings
        self.main_controller = main_controller

        # init dialogs
        self.open_document_dialog = open_document_dialog.OpenDocumentDialog(self.main_window, self.workspace)
        self.save_document_dialog = save_document_dialog.SaveDocumentDialog(self.main_window, self.workspace)
        self.document_wizard_dialog = document_wizard.DocumentWizard(self.main_window, self.workspace, self.settings)

        self.document_controllers = dict()
        self.sidebar_controller = sidebarcontroller.SidebarController(self.main_window.sidebar, self, self.main_window)
        self.preview_controller = previewcontroller.PreviewController(self.main_window.preview, self, self.main_window)

        self.observe_workspace()
        self.observe_workspace_view()
        
        self.untitled_documents_no = 0

        self.show_document_name(None)
        self.main_window.headerbar.save_document_button.hide()
        self.main_window.headerbar.build_wrapper.hide()
        self.main_window.shortcuts_bar.sidebar_toggle.set_sensitive(False)
        self.main_window.headerbar.preview_toggle.set_sensitive(False)
        self.main_window.headerbar.preview_toggle.hide()
        
        self.main_window.shortcuts_bar.hide()
        self.main_window.sidebar.hide()
        self.main_window.preview.hide()
        
        self.save_as_action = Gio.SimpleAction.new('save-as', None)
        self.save_as_action.connect('activate', self.on_save_as_clicked)
        self.save_as_action.set_enabled(False)
        
        self.save_all_action = Gio.SimpleAction.new('save-all', None)
        self.save_all_action.connect('activate', self.on_save_all_clicked)
        self.save_all_action.set_enabled(False)
        
        self.find_action = Gio.SimpleAction.new('find', None)
        self.find_action.connect('activate', self.on_menu_find_clicked)
        self.find_action.set_enabled(False)
        
        self.find_next_action = Gio.SimpleAction.new('find-next', None)
        self.find_next_action.connect('activate', self.find_next)
        self.find_next_action.set_enabled(False)
        
        self.find_prev_action = Gio.SimpleAction.new('find-prev', None)
        self.find_prev_action.connect('activate', self.find_prev)
        self.find_prev_action.set_enabled(False)
        
        self.find_replace_action = Gio.SimpleAction.new('find-replace', None)
        self.find_replace_action.connect('activate', self.on_menu_find_replace_clicked)
        self.find_replace_action.set_enabled(False)
        
        self.close_all_action = Gio.SimpleAction.new('close-all-documents', None)
        self.close_all_action.connect('activate', self.on_close_all_clicked)
        self.close_all_action.set_enabled(False)
        
        self.close_document_action = Gio.SimpleAction.new('close-active-document', None)
        self.close_document_action.connect('activate', self.on_close_document_clicked)
        self.close_document_action.set_enabled(False)
        
        self.insert_before_after_action = Gio.SimpleAction.new('insert-before-after', GLib.VariantType('as'))
        self.insert_before_after_action.connect('activate', self.insert_before_after)
        self.insert_before_after_action.set_enabled(False)

        self.insert_symbol_action = Gio.SimpleAction.new('insert-symbol', GLib.VariantType('as'))
        self.insert_symbol_action.connect('activate', self.insert_symbol)
        self.insert_symbol_action.set_enabled(False)

        self.document_wizard_action = Gio.SimpleAction.new('show-document-wizard', None)
        self.document_wizard_action.connect('activate', self.start_wizard)
        self.document_wizard_action.set_enabled(False)

        # populate workspace
        self.workspace.populate_from_disk()
        open_documents = self.workspace.open_documents
        if len(open_documents) > 0:
            self.workspace.set_active_document(open_documents[-1])

    def observe_workspace(self):
        self.workspace.register_observer(self)
        
    def observe_workspace_view(self):
        self.observe_document_chooser()
        self.main_window.headerbar.new_document_button.connect('clicked', self.on_new_document_button_click)
        self.main_window.headerbar.open_docs_popover.document_list.connect('row-activated', self.on_doclist_row_activated)
        self.main_window.headerbar.open_docs_popover.connect('closed', self.on_doclist_row_popdown)
        self.main_window.headerbar.save_document_button.connect('clicked', self.on_save_button_click)
        self.main_window.shortcuts_bar.sidebar_toggle.connect('toggled', self.on_sidebar_toggle_toggled)
        self.main_window.headerbar.preview_toggle.connect('toggled', self.on_preview_toggle_toggled)

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
        
    def observe_doclist_item(self, item):
        item.document_close_button.connect('clicked', self.on_doclist_close_clicked, item.document)

    '''
    *** decorators
    '''
    
    def _assert_has_active_document(original_function):
        def new_function(self, *args, **kwargs):
            if self.workspace.get_active_document() != None:
                return original_function(self, *args, **kwargs)
        return new_function    

    '''
    *** notification handlers, get called by observed workspace
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_document':
            document = parameter
            document.set_use_dark_scheme(helpers.is_dark_mode(self.main_window))

            # init view
            document_view = view.DocumentView(document)
            doclist_item = self.main_window.headerbar.open_docs_popover.add_document(document)
            
            # add controller
            document_controller = documentcontroller.DocumentController(document, document_view, doclist_item, self.backend, self.settings, self.main_window, self.workspace, self.main_controller)
            self.document_controllers[document] = document_controller
            self.observe_doclist_item(doclist_item)

            # show
            self.main_window.notebook.append_page(document_view)
            
        if change_code == 'document_removed':
            document = parameter
            document_view = self.document_controllers[document].document_view
            notebook = self.main_window.notebook
            self.main_window.headerbar.open_docs_popover.remove_document(document)
            self.main_window.notebook.remove(document_view)
            del(self.document_controllers[document])
            if self.workspace.active_document == None:
                notebook.set_current_page(notebook.page_num(self.main_window.blank_slate))
                self.show_document_name(None)
                self.main_window.headerbar.save_document_button.hide()
                self.main_window.headerbar.build_wrapper.hide()
                self.main_window.headerbar.preview_toggle.hide()
                self.main_window.shortcuts_bar.sidebar_toggle.set_sensitive(False)
                self.main_window.headerbar.preview_toggle.set_sensitive(False)
                self.main_window.shortcuts_bar.hide()
                self.save_as_action.set_enabled(False)
                self.find_action.set_enabled(False)
                self.find_next_action.set_enabled(False)
                self.find_prev_action.set_enabled(False)
                self.find_replace_action.set_enabled(False)
                self.sidebar_controller.hide_sidebar(True, False)
                self.preview_controller.hide_preview(True, False)
                self.close_document_action.set_enabled(False)
                self.insert_before_after_action.set_enabled(False)
                self.insert_symbol_action.set_enabled(False)
                self.document_wizard_action.set_enabled(True)
                self.close_all_action.set_enabled(False)
            
        if change_code == 'new_active_document':
            document = parameter
            document_view = self.document_controllers[document].document_view
            notebook = self.main_window.notebook
            notebook.set_current_page(notebook.page_num(document_view))
            document_view.source_view.grab_focus()
            self.main_window.preview_paned_overlay.add_overlay(document_view.autocomplete)
            self.document_controllers[document].autocomplete_controller.update_autocomplete_position()

            self.show_document_name(document)
            self.main_window.headerbar.open_docs_popover.document_list.invalidate_sort()
            if document.get_modified():
                self.main_window.headerbar.save_document_button.set_sensitive(True)
            elif document.get_filename() == None:
                self.main_window.headerbar.save_document_button.set_sensitive(True)
            else:
                self.main_window.headerbar.save_document_button.set_sensitive(False)
            self.main_window.headerbar.save_document_button.show_all()
            self.main_window.headerbar.menu_button.show_all()
            self.on_sidebar_toggle_toggled(self.main_window.shortcuts_bar.sidebar_toggle)
            self.on_preview_toggle_toggled(self.main_window.headerbar.preview_toggle)

            self.set_build_button_state()
            self.main_window.shortcuts_bar.sidebar_toggle.set_sensitive(True)
            self.main_window.headerbar.preview_toggle.set_sensitive(True)
            self.main_window.headerbar.preview_toggle.show_all()
            self.main_window.shortcuts_bar.show_all()
            self.set_shortcuts_bar_bottom()
            
            self.save_as_action.set_enabled(True)
            self.find_action.set_enabled(True)
            self.find_next_action.set_enabled(True)
            self.find_prev_action.set_enabled(True)
            self.find_replace_action.set_enabled(True)
            self.close_document_action.set_enabled(True)
            self.close_all_action.set_enabled(True)
            self.insert_before_after_action.set_enabled(True)
            self.insert_symbol_action.set_enabled(True)
            self.document_wizard_action.set_enabled(True)
            
            self.preview_controller.set_active_document(document)
        
        if change_code == 'new_inactive_document':
            document = parameter
            document_view = self.document_controllers[document].document_view
            notebook = self.main_window.notebook
            self.main_window.preview_paned_overlay.remove(document_view.autocomplete)

        if change_code == 'update_recently_opened_documents':
            items = list()
            data = parameter.values()
            for item in sorted(data, key=lambda val: -val['date']):
                items.append(item['filename'].rsplit('/', 1)[::-1])
            self.main_window.headerbar.document_chooser.update_autosuggest(items)
            if len(data) > 0:
                self.main_window.headerbar.open_document_button.show_all()
                self.main_window.headerbar.open_document_blank_button.hide()
            else:
                self.main_window.headerbar.open_document_button.hide()
                self.main_window.headerbar.open_document_blank_button.show_all()
        
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

        if isinstance(document_candidate, model_document.Document):
            self.workspace.set_active_document(document_candidate)
        else:
            document = model_document.Document(self.workspace.pathname, with_buffer=True)
            document.set_filename(filename)
            document.populate_from_filename()
            self.workspace.add_document(document)
            self.workspace.set_active_document(document)

    def on_open_document_button_click(self, button_object=None):
        self.open_document_dialog.run()

    def on_new_document_button_click(self, button_object=None):
        document = model_document.Document(self.workspace.pathname, with_buffer=True)
        self.workspace.add_document(document)
        self.workspace.set_active_document(document)

    def on_doclist_close_clicked(self, button_object, document):
        if document.get_modified():
            documents = list()
            documents.append(document)
            self.workspace.set_active_document(document)
            save_changes_dialog = view.dialogs.CloseConfirmation(self.main_window, documents)
            response = save_changes_dialog.run()
            if response == Gtk.ResponseType.NO:
                self.workspace.remove_document(document)
            elif response == Gtk.ResponseType.YES:
                if document.get_filename() == None:
                    if self.save_document_dialog.run(document, '.tex'):
                        self.workspace.remove_document(document)
                else:
                    document.save_to_disk()
                    self.workspace.remove_document(document)
            save_changes_dialog.hide()
        else:
            self.workspace.remove_document(document)
        
    def on_doclist_row_activated(self, box, row, data=None):
        self.main_window.headerbar.open_docs_popover.popdown()
        self.workspace.set_active_document(row.document)

    def on_doclist_row_popdown(self, popover, data=None):
        self.main_window.headerbar.open_docs_popover.document_list.unselect_all()
        
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
        filename = document.get_filename()
        if filename != None:
            self.save_document_dialog.run(document, filename)
        else:
            self.save_document_dialog.run(document, '.tex')
        
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
                    self.save_document_dialog.run(document, '.tex')
                else:
                    document.save_to_disk()
            if return_to_active_document == True:
                self.workspace.set_active_document(document)

    @_assert_has_active_document
    def on_menu_find_clicked(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        view = self.document_controllers[active_document].document_view
        view.shortcuts_bar_bottom.button_find.set_active(True)
        GLib.idle_add(self.document_controllers[active_document].search_controller.search_entry_grab_focus, None)

    @_assert_has_active_document
    def find_next(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        controller = self.document_controllers[active_document]
        if controller.document_view.source_view.has_focus() or controller.document_view.search_bar.entry.has_focus() or controller.document_view.search_bar.replace_entry.has_focus():
            controller.document_view.search_bar.entry.emit('next-match')

    @_assert_has_active_document
    def find_prev(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        controller = self.document_controllers[active_document]
        if controller.document_view.source_view.has_focus() or controller.document_view.search_bar.entry.has_focus() or controller.document_view.search_bar.replace_entry.has_focus():
            controller.document_view.search_bar.entry.emit('previous-match')

    @_assert_has_active_document
    def on_menu_find_replace_clicked(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        self.document_controllers[active_document].document_view.shortcuts_bar_bottom.button_find_and_replace.set_active(True)
        GLib.idle_add(self.document_controllers[active_document].search_controller.search_entry_grab_focus, None)

    @_assert_has_active_document
    def on_close_all_clicked(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        documents = self.workspace.get_all_documents()
        unsaved_documents = self.workspace.get_unsaved_documents()
        if unsaved_documents != None: 
            save_changes_dialog = view.dialogs.CloseConfirmation(self.main_window, unsaved_documents)
            response = save_changes_dialog.run()
            if response == Gtk.ResponseType.NO:
                save_changes_dialog.hide()
                document = self.workspace.get_active_document()
                while document != None:
                    self.workspace.remove_document(document)
                    document = self.workspace.get_active_document()
            elif response == Gtk.ResponseType.YES:
                selected_documents = list()
                if len(unsaved_documents) == 1:
                    selected_documents.append(unsaved_documents[0])
                else:
                    for child in save_changes_dialog.chooser.get_children():
                        if child.get_child().get_active():
                            number = int(child.get_child().get_name()[29:])
                            selected_documents.append(unsaved_documents[number])
                for document in documents:
                    if document in selected_documents:
                        if document.get_filename() == None:
                            self.workspace.set_active_document(document)
                            if self.save_document_dialog.run(document, '.tex'):
                                self.workspace.remove_document(document)
                        else:
                            document.save_to_disk()
                            self.workspace.remove_document(document)
                    else:
                        self.workspace.remove_document(document)
                save_changes_dialog.hide()
            else:
                save_changes_dialog.hide()
        else:
            document = self.workspace.get_active_document()
            while document != None:
                self.workspace.remove_document(document)
                document = self.workspace.get_active_document()

    def activate_quotes_popover(self, action=None, parameter=None):
        self.main_window.shortcuts_bar.quotes_button.set_active(True)

    def on_close_document_clicked(self, action=None, parameter=None):
        document = self.workspace.get_active_document()
        self.on_doclist_close_clicked(None, document)
        
    def on_sidebar_toggle_toggled(self, toggle_button, parameter=None):
        if toggle_button.get_active() == True:
            self.sidebar_controller.show_sidebar(True, True)
        else:
            self.sidebar_controller.hide_sidebar(True, True)

    def on_preview_toggle_toggled(self, toggle_button, parameter=None):
        if toggle_button.get_active() == True:
            self.preview_controller.show_preview(True)
        else:
            self.preview_controller.hide_preview(True)

    '''
    *** actions
    '''
    
    @_assert_has_active_document
    def switch_to_earliest_open_document(self):
        self.workspace.set_active_document(self.workspace.get_earliest_active_document())
    
    def set_build_button_state(self):
        document = self.workspace.active_document
        state = document.get_state()
            
        document_view = self.document_controllers[self.workspace.active_document].document_view
        headerbar = self.main_window.headerbar
        prev_widget = headerbar.build_wrapper.get_center_widget()
        if prev_widget != None:
            headerbar.build_wrapper.remove(prev_widget)
        headerbar.build_wrapper.set_center_widget(document_view.build_widget)
        headerbar.build_wrapper.show()
        document_view.build_widget.show()
        if document_view.build_widget.has_result():
            document_view.build_widget.hide_timer(4000)

    def set_shortcuts_bar_bottom(self):
        document = self.workspace.active_document
            
        document_view = self.document_controllers[self.workspace.active_document].document_view
        shortcuts_bar = self.main_window.shortcuts_bar

        if shortcuts_bar.current_bottom != None:
            shortcuts_bar.remove(shortcuts_bar.current_bottom)
        shortcuts_bar.current_bottom = document_view.shortcuts_bar_bottom
        shortcuts_bar.pack_end(document_view.shortcuts_bar_bottom, False, False, 0)

    def show_document_name(self, document):
        headerbar = self.main_window.headerbar
        if document == None:
            headerbar.center_button.hide()
            headerbar.center_label_welcome.show_all()
        else:
            doclist_item = headerbar.open_docs_popover.document_list_items[document]
            
            if headerbar.name_binding != None: headerbar.name_binding.unbind()
            headerbar.document_name_label.set_text(doclist_item.label.get_text())
            headerbar.name_binding = doclist_item.label.bind_property('label', headerbar.document_name_label, 'label', 0)
            
            if headerbar.folder_binding != None: headerbar.folder_binding.unbind()
            headerbar.folder_binding = doclist_item.flabel.bind_property('label', headerbar.document_folder_label, 'label', 0, self.folder_transform_func)

            if headerbar.mod_binding != None: headerbar.mod_binding.unbind()
            headerbar.document_mod_label.set_text(doclist_item.mlabel.get_text())
            headerbar.mod_binding = doclist_item.mlabel.bind_property('label', headerbar.document_mod_label, 'label', 0, self.modified_transform_func)

            headerbar.center_label_welcome.hide()
            headerbar.center_button.show_all()

            self.folder_transform_func(headerbar.folder_binding, doclist_item.folder)
            self.modified_transform_func(headerbar.mod_binding, doclist_item.mlabel.get_text())
            
    def modified_transform_func(self, binding, from_value, to_value=None):
        headerbar = self.main_window.headerbar
        if from_value == 'False' and headerbar.document_folder_label.get_text() != '':
            headerbar.save_document_button.set_sensitive(False)
            self.save_all_action.set_enabled(False)
        else:
            headerbar.save_document_button.set_sensitive(True)
            self.save_all_action.set_enabled(True)

    def folder_transform_func(self, binding, from_value, to_value=None):
        headerbar = self.main_window.headerbar
        headerbar.document_folder_label.set_text(from_value)
        if from_value == '':
            headerbar.document_folder_label.hide()
        else:
            headerbar.document_folder_label.show_all()
    
    @_assert_has_active_document
    def insert_symbol(self, action, parameter):
        ''' insert text at the cursor. '''
        
        text = parameter[0]
        
        active_document = self.workspace.get_active_document()
        document_view = self.document_controllers[active_document].document_view
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
            document_view.source_view.scroll_to_mark(buff.get_insert(), 0, False, 0, 0)

            buff.end_user_action()

    @_assert_has_active_document
    def start_wizard(self, action, parameter=None):
        document = self.workspace.get_active_document()
        self.document_wizard_dialog.run(document)

    @_assert_has_active_document
    def insert_before_after(self, action, parameter):
        ''' wrap text around current selection. '''

        before = parameter[0]
        after = parameter[1]

        active_document = self.workspace.get_active_document()
        document_view = self.document_controllers[active_document].document_view
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
                document_view.source_view.scroll_to_mark(buff.get_insert(), 0, False, 0, 0)
            else:
                text = before + '•' + after
                buff.insert_at_cursor(text)
                cursor_pos = buff.get_iter_at_mark(buff.get_insert())
                cursor_pos.backward_chars(len(after))
                bound = cursor_pos.copy()
                bound.backward_chars(1)
                buff.select_range(bound, cursor_pos)
                document_view.source_view.scroll_to_mark(buff.get_insert(), 0, False, 0, 0)
            buff.end_user_action()


