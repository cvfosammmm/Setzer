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
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import GtkSource

import viewgtk.viewgtk as view
import backend.backend as backend
import controller.controller_document_autocomplete as autocompletecontroller
import controller.controller_document_search as searchcontroller
import helpers.helpers as helpers

import time
import os.path
import shutil
import re


class DocumentController(object):
    ''' Mediator between workspace and view. '''
    
    def __init__(self, document, document_view, doclist_item, backend, settings, main_window, workspace):

        self.document = document
        self.document_view = document_view
        self.backend = backend
        self.settings = settings
        self.main_window = main_window
        self.workspace = workspace
        self.doclist_item = doclist_item
        self.modified_state = document.get_modified()
        self.build_button_state = ('idle', int(time.time()*1000))
        self.document_view.build_widget.build_button.show_all()
        self.document_view.build_widget.stop_button.hide()
        self.set_clean_button_state()

        self.autocomplete_controller = autocompletecontroller.DocumentAutocompleteController(self.document, self.document_view, self.main_window)
        self.search_controller = searchcontroller.DocumentSearchController(self.document, self.document_view, self.document_view.search_bar, self.main_window)
        
        self.observe_document()
        self.observe_document_view()
        self.observe_shortcuts_bar_bottom()
        self.observe_build_log()
        self.observe_settings()
        self.observe_backend()
        
        self.document_view.scrolled_window.get_vadjustment().connect('value-changed', self.on_adjustment_value_changed)
        self.document_view.scrolled_window.get_hadjustment().connect('value-changed', self.on_adjustment_value_changed)
        self.document_view.source_view.connect('key-press-event', self.on_keypress)
        
    def observe_document(self):
        self.document.register_observer(self)
        self.document.get_buffer().connect('modified-changed', self.on_modified_change)
        self.document.get_buffer().connect('changed', self.on_buffer_changed)
        self.document.get_buffer().connect('mark-set', self.on_mark_set)
        self.document.get_buffer().connect('mark-deleted', self.on_mark_deleted)
        
    def observe_document_view(self):
        self.document_view.build_widget.build_button.connect('clicked', self.on_build_button_click)
        self.document_view.build_widget.stop_button.connect('clicked', self.on_stop_build_button_click)
        self.document_view.build_widget.clean_button.connect('clicked', self.on_clean_button_click)
        self.document_view.source_view.connect('focus-out-event', self.on_focus_out)
        self.document_view.source_view.connect('focus-in-event', self.on_focus_in)

    def observe_shortcuts_bar_bottom(self):
        self.document_view.shortcuts_bar_bottom.button_build_log.connect('clicked', self.on_build_log_button_clicked)
        
    def observe_build_log(self):
        self.build_log_animating = False
        self.hide_build_log(False)
        self.document.set_show_build_log(False)
        self.document.build_log.register_observer(self)
        self.document_view.build_log_view.list.connect('row-activated', self.on_build_log_row_activated)
        self.document_view.build_log_view.close_button.connect('clicked', self.hide_build_log)
        self.document_view.build_log_view.connect('size-allocate', self.build_log_on_size_allocate)

    def observe_settings(self):
        self.settings.register_observer(self)
        
    def observe_backend(self):
        self.backend.register_observer(self)

    '''
    *** notification handlers, get called by observed document or the backend
    '''

    def change_notification(self, change_code, notifying_object, parameter):
    
        if change_code == 'filename_change':
            self.doclist_item.set_name(self.document.get_filename(), self.modified_state)

        if change_code == 'document_state_change' and parameter == 'ready_for_building':
            document = notifying_object
            insert = document.source_buffer.get_iter_at_mark(document.source_buffer.get_insert())
            synctex_arguments = dict()
            synctex_arguments['line'] = insert.get_line()
            synctex_arguments['line_offset'] = insert.get_line_offset()
            buffer = document.get_buffer()
            if buffer != None:
                query = backend.Query(buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True), self, synctex_arguments, self.settings.get_value('preferences', 'build_command'))
                self.backend.add_query(query)
                self.on_build_state_change()
            
        if change_code == 'document_state_change' and parameter == 'building_to_stop':
            document = notifying_object
            self.backend.stop_building_by_document(document)
        
        if change_code == 'building_started':
            query = parameter
            if self.document == query.get_document():
                self.document.change_state('building_in_progress')
                
        if change_code == 'reset_timer':
            document = parameter
            if self.document == document:
                self.document_view.build_widget.reset_timer()
                self.document_view.build_widget.label.set_text('0:00')

        if change_code == 'building_stopped':
            document = parameter
            if self.document == document:
                self.document.change_state('idle')
            self.on_build_state_change('')
            self.set_clean_button_state()

        if change_code == 'building_finished':
            result_blob = parameter
            if self == result_blob['document_controller']:
                try:
                    self.document.set_pdf(result_blob['pdf_filename'], result_blob['pdf_position'])
                except KeyError: pass

                build_log = self.document.build_log
                build_log.clear_items()
                try:
                    build_log_blob = result_blob['log_messages']
                except KeyError:
                    message = ''
                else:
                    for item in build_log_blob:
                        build_log.add_item(item[0].strip(), item[1].strip(), item[2].strip())
                    build_log.signal_finish_adding()
                    if build_log.has_items(self.settings.get_value('preferences', 'autoshow_build_log')):
                        self.show_build_log(True)
                    if build_log.has_items('errors'):
                        error_count = build_log.count_items('errors')
                        error_color = helpers.theme_color_to_css(self.document_view.get_style_context(), 'error_color')
                        message = '<span color="' + error_color + '">Failed</span> (' + str(error_count) + ' error' + ('s' if error_count > 1 else '') + ')!'
                    else:
                        message = 'Success!'
                    self.document_view.build_log_view.set_header_data(build_log.count_items('errors'), build_log.count_items('warnings') + build_log.count_items('badboxes'), True)
                            
                self.document.change_state('idle')
                self.on_build_state_change(message)
                self.set_clean_button_state()
        
        if change_code == 'show_build_log_state_change':
            show_build_log = parameter
            if show_build_log:
                self.show_build_log(True)
            else:
                self.hide_build_log(True)
            
        if change_code == 'pdf_update':
            pass
        
        if change_code == 'settings_changed':
            section, item, value = parameter
            if (section, item) == ('preferences', 'cleanup_build_files'):
                self.set_clean_button_state()

        if change_code == 'build_log_new_item':
            item = parameter
            symbols = {'Badbox': 'own-badbox-symbolic', 'Error': 'dialog-error-symbolic', 'Warning': 'dialog-warning-symbolic'}
            row = view.BuildLogRowView(symbols[item[0]], item[0], "Line " + str(item[1]), item[2])
            self.document_view.build_log_view.list.prepend(row)

        if change_code == 'build_log_finished_adding':
            self.document_view.build_log_view.list.show_all()
            for row in self.document_view.build_log_view.list:
                message_type = row.get_child().label_message_type.get_text()
                line_number = row.get_child().line_number

                if message_type != 'Error': return
                elif line_number >= 0:
                    row.activate()
                    return

        if change_code == 'build_log_cleared_items':
            for entry in self.document_view.build_log_view.list.get_children():
                self.document_view.build_log_view.list.remove(entry)

    '''
    *** signal handlers: changes in documents
    '''

    def on_adjustment_value_changed(self, adjustment, user_data=None):
        self.autocomplete_controller.update_autocomplete_position(False)
        return False

    def on_mark_set(self, buffer, insert, mark, user_data=None):
        self.autocomplete_controller.update_autocomplete_position(False)
    
    def on_buffer_changed(self, buffer, user_data=None):
        self.autocomplete_controller.update_autocomplete_position(True)
    
    def on_mark_deleted(self, buffer, mark, user_data=None):
        self.autocomplete_controller.update_autocomplete_position(False)
    
    def on_build_state_change(self, message=''):
        document = self.document
        state = document.get_state()
        selfstate = self.build_button_state
        build_widget = self.document_view.build_widget
        if state == 'idle' or state == '':
            build_button_state = ('idle', int(time.time()*1000))
        else:
            build_button_state = ('building', int(time.time()*1000))

        build_widget.build_timer.show_all()
        if selfstate[0] != build_button_state[0]:
            self.build_button_state = build_button_state
            if build_button_state[0] == 'idle':
                build_widget.build_button.set_sensitive(True)
                build_widget.build_button.show_all()
                build_widget.stop_button.hide()
                build_widget.stop_timer()
                build_widget.show_result(message)
                if build_widget.get_parent() != None:
                    build_widget.hide_timer(4000)
            else:
                build_widget.build_button.set_sensitive(False)
                build_widget.build_button.hide()
                build_widget.stop_button.show_all()
                build_widget.reset_timer()
                build_widget.show_timer()
                build_widget.start_timer()

    def on_modified_change(self, buff):
        if buff.get_modified() != self.modified_state:
            self.modified_state = buff.get_modified()
            self.doclist_item.set_name(self.document.get_filename(), self.modified_state)
            
    def on_build_button_click(self, button_object=None):
        self.build_document()

    def on_stop_build_button_click(self, button_object=None):
        document = self.document
        if document != None:
            if document.filename != None:
                self.stop_building_document()
    
    def on_clean_button_click(self, button_object=None):
        document = self.document
        if document != None:
            if document.filename != None:
                self.cleanup_build_files()
                self.set_clean_button_state()

    def on_build_log_row_activated(self, box, row, data=None):
        buff = self.document.get_buffer()
        if buff != None:
            line_number = int(row.get_child().line_number) - 1
            if line_number >= 0:
                buff.place_cursor(buff.get_iter_at_line(line_number))
            self.document_view.source_view.scroll_mark_onscreen(buff.get_insert())
            self.document_view.source_view.grab_focus()

    def on_keypress(self, widget, event, data=None):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.keyval == Gdk.keyval_from_name('Down'):
            if event.state & modifiers == 0:
                return self.autocomplete_controller.on_down_press()

        if event.keyval == Gdk.keyval_from_name('Up'):
            if event.state & modifiers == 0:
                return self.autocomplete_controller.on_up_press()

        if event.keyval == Gdk.keyval_from_name('Escape'):
            if event.state & modifiers == 0:
                return self.autocomplete_controller.on_escape_press()

        if event.keyval == Gdk.keyval_from_name('Return'):
            if event.state & modifiers == 0:
                return self.autocomplete_controller.on_return_press()

        if event.keyval == Gdk.keyval_from_name('Tab') or event.keyval == Gdk.keyval_from_name('ISO_Left_Tab'):
            if event.state & modifiers == 0:
                buffer = self.document.get_buffer()
                insert = buffer.get_iter_at_mark(buffer.get_insert())
                insert.forward_chars(1)
                limit_iter = insert.copy()
                limit_iter.forward_line()
                limit_iter.forward_line()
                limit_iter.backward_chars(1)
                result = insert.forward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.place_cursor(result[0])
                    buffer.select_range(result[0], result[1])
                    self.document_view.source_view.scroll_to_iter(result[1], 0, False, 0, 0)
                    return True
                
                insert.backward_chars(1)
                result = insert.forward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.select_range(result[0], result[1])
                    self.document_view.source_view.scroll_to_iter(result[1], 0, False, 0, 0)
                    return True
            elif event.state & modifiers == Gdk.ModifierType.SHIFT_MASK:
                buffer = self.document.get_buffer()
                insert = buffer.get_iter_at_mark(buffer.get_insert())
                limit_iter = insert.copy()
                limit_iter.backward_line()
                result = insert.backward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.select_range(result[0], result[1])
                    self.document_view.source_view.scroll_to_iter(result[0], 0, False, 0, 0)
                    return True

                insert.forward_chars(1)
                result = insert.backward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.select_range(result[0], result[1])
                    self.document_view.source_view.scroll_to_iter(result[0], 0, False, 0, 0)
                    return True
        return False

    def on_focus_out(self, widget, event, user_data=None):
        self.autocomplete_controller.focus_hide()

    def on_focus_in(self, widget, event, user_data=None):
        self.autocomplete_controller.focus_show()

    '''
    *** actions
    '''

    def on_build_log_button_clicked(self, toggle_button, parameter=None):
        self.document.set_show_build_log(toggle_button.get_active())

    def on_hide_build_log_clicked(self, button=None, user_data=None):
        self.hide_build_log(True)

    def hide_build_log(self, animate=False):
        if self.build_log_animating == False:
            self.build_log_animate(False, animate)
        
    def show_build_log(self, animate=False):
        if self.build_log_animating == False:
            self.build_log_animate(True, animate)
            self.document_view.shortcuts_bar_bottom.button_build_log.set_active(True)

    def build_log_animate(self, show_build_log=True, animate=False):
        def set_position_on_tick(paned, frame_clock_cb, user_data=None):
            show_build_log = user_data
            now = frame_clock_cb.get_frame_time()
            if now < end_time and paned.get_position != end:
                t = self.ease((now - start_time) / (end_time - start_time))
                paned.set_position(int(start + t * (end - start)))
                return True
            else:
                paned.set_position(end)
                if not show_build_log:
                    self.document_view.build_log_view.hide()
                else:
                    paned.child_set_property(self.document_view.build_log_view, 'shrink', False)
                self.document_view.shortcuts_bar_bottom.button_build_log.set_active(show_build_log)
                self.build_log_animating = False
                return False

        frame_clock = self.document_view.document_paned.get_frame_clock()
        duration = 200
        if show_build_log:
            self.document_view.build_log_view.show_all()
            start = self.document_view.get_allocated_height()
            end = self.document_view.get_allocated_height() - max(self.document_view.build_log_view.position, 200)
        else:
            start = self.document_view.document_paned.get_position()
            end = self.document_view.get_allocated_height()
            self.document_view.document_paned.child_set_property(self.document_view.build_log_view, 'shrink', True)
        if frame_clock != None and animate:
            start_time = frame_clock.get_frame_time()
            end_time = start_time + 1000 * duration
            self.build_log_animating = True
            self.document_view.document_paned.add_tick_callback(set_position_on_tick, show_build_log)
        else:
            self.document_view.document_paned.set_position(end)
            self.document_view.build_log_view.hide()
            self.document_view.shortcuts_bar_bottom.button_build_log.set_active(False)

    def ease(self, time):
        return (time - 1)**3 + 1;

    def build_log_on_size_allocate(self, view, allocation, user_data=None):
        if self.build_log_animating == False:
            self.document_view.build_log_view.position = allocation.height
    
    def build_document(self):
        document = self.document

        if document.filename == None:
            save_document_dialog = view.dialogs.BuildSaveDialog(self.main_window, document)
            response = save_document_dialog.run()
            if response == Gtk.ResponseType.YES:
                save_document_dialog.hide()
                dialog = view.dialogs.SaveDocument(self.main_window)
                dialog.set_current_name('.tex')
                response = dialog.run()
                if response == Gtk.ResponseType.OK:
                    filename = dialog.get_filename()
                    document.set_filename(filename)
                    document.save_to_disk()
                    self.workspace.update_recently_opened_document(filename)
                dialog.hide()
            else:
                save_document_dialog.hide()
                return False

        if document.filename != None:
            document.change_state('ready_for_building')

    def stop_building_document(self):
        self.document.change_state('building_to_stop')
        
    def cleanup_build_files(self):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' ,'.ilg', '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc']
        pathname = self.document.get_filename().rsplit('/', 1)
        for ending in file_endings:
            filename = pathname[0] + '/' + pathname[1].rsplit('.', 1)[0] + ending
            try: os.remove(filename)
            except FileNotFoundError: pass

    def set_clean_button_state(self):
        def get_clean_button_state(document):
            file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' ,'.ilg', '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc']
            if document != None:
                if document.filename != None:
                    pathname = document.get_filename().rsplit('/', 1)
                    for ending in file_endings:
                        filename = pathname[0] + '/' + pathname[1].rsplit('.', 1)[0] + ending
                        if os.path.exists(filename): return True
            return False

        if self.settings.get_value('preferences', 'cleanup_build_files') == True:
            self.document_view.build_widget.clean_button.hide()
        else:
            self.document_view.build_widget.clean_button.show_all()
            self.document_view.build_widget.clean_button.set_sensitive(get_clean_button_state(self.document))


