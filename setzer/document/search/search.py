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
from gi.repository import GLib
from gi.repository import Gtk

from setzer.dialogs.dialog_locator import DialogLocator


class Search(object):
    ''' Control find, find and replace. '''
    
    def __init__(self, document, document_view, search_bar):

        self.search_bar = search_bar
        self.search_bar_mode = 'search'

        self.document_view = document_view
        self.document = document

        self.observe_search_bar()
        self.observe_shortcuts_bar()
        self.search_bar.connect('size-allocate', self.on_search_bar_size_allocate)
        self.search_bar.match_counter.connect('size-allocate', self.on_match_counter_size_allocate)

    def observe_shortcuts_bar(self):
        self.document_view.shortcuts_bar_bottom.button_find.connect('toggled', self.on_find_button_clicked)
        self.document_view.shortcuts_bar_bottom.button_find_and_replace.connect('toggled', self.on_find_replace_button_clicked)

    def observe_search_bar(self):
        self.search_bar.entry.connect('search-changed', self.on_search_entry_changed)
        self.search_bar.entry.connect('stop-search', self.on_search_stop)
        self.search_bar.entry.connect('next-match', self.on_search_next_match)
        self.search_bar.entry.connect('previous-match', self.on_search_previous_match)
        self.search_bar.entry.connect('activate', self.on_search_entry_activate)
        self.search_bar.close_button.connect('clicked', self.on_search_close_button_click)
        self.search_bar.next_button.connect('clicked', self.on_search_next_button_click)
        self.search_bar.prev_button.connect('clicked', self.on_search_prev_button_click)
        self.search_bar.replace_button.connect('clicked', self.on_replace_button_click)
        self.search_bar.replace_all_button.connect('clicked', self.on_replace_all_button_click)
    
    '''
    *** signal handlers: search bar
    '''
    
    def on_search_close_button_click(self, button_object=None):
        self.on_search_stop()
    
    def on_search_next_button_click(self, button_object=None):
        self.on_search_next_match()
        
    def on_search_prev_button_click(self, button_object=None):
        self.on_search_previous_match()
        
    def on_replace_button_click(self, button_object=None):
        if self.document.get_buffer() != None:
            buffer = self.document.get_buffer()
            search_context = self.document.get_search_context()
            replacement = self.search_bar.replace_entry.get_text()
            
            bounds = buffer.get_selection_bounds()
            if len(bounds) == 2:
                search_context.replace(*bounds, replacement, -1)
                self.on_search_next_match()        

    def on_replace_all_button_click(self, button_object=None):
        if self.document.get_buffer() != None:
            search_context = self.document.get_search_context()
            original = self.search_bar.entry.get_text()
            replacement = self.search_bar.replace_entry.get_text()
            number_of_occurrences = search_context.get_occurrences_count()
            
            if number_of_occurrences > 0:
                dialog = DialogLocator.get_dialog('replace_confirmation')
                if dialog.run(original, replacement, number_of_occurrences):
                    search_context.replace_all(replacement, -1)

    def on_search_entry_activate(self, entry=None):
        self.on_search_next_match(entry, True)
        self.document_view.source_view.grab_focus()

    def on_search_next_match(self, entry=None, include_current_highlight=False):
        if self.document.get_buffer() != None:
            buffer = self.document.get_buffer()
            search_context = self.document.get_search_context()
            insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
            bound_iter = buffer.get_iter_at_mark(buffer.get_selection_bound())

            if include_current_highlight:
                if insert_iter.get_offset() < bound_iter.get_offset(): search_iter = insert_iter
                else: search_iter = bound_iter
                result = search_context.forward(search_iter)
            else:
                if insert_iter.get_offset() < bound_iter.get_offset(): search_iter = bound_iter
                else: search_iter = insert_iter
                result = search_context.forward(search_iter)

            if result[0] == True:
                buffer.select_range(result[2], result[1])
                self.document_view.source_view.scroll_to_iter(result[1], 0, False, 0, 0)
                self.set_match_counter(search_context.get_occurrence_position(result[1], result[2]), search_context.get_occurrences_count())
            else:
                search_iter = buffer.get_start_iter()
                result = search_context.forward(search_iter)

                if result[0] == True:
                    buffer.select_range(result[2], result[1])
                    self.document_view.source_view.scroll_to_iter(result[1], 0, False, 0, 0)
                    self.set_match_counter(search_context.get_occurrence_position(result[1], result[2]), search_context.get_occurrences_count())
    
    def on_search_previous_match(self, entry=None):
        if self.document.get_buffer() != None:
            buffer = self.document.get_buffer()
            search_context = self.document.get_search_context()
            insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
            bound_iter = buffer.get_iter_at_mark(buffer.get_selection_bound())
            
            if insert_iter.get_offset() > bound_iter.get_offset(): search_iter = bound_iter
            else: search_iter = insert_iter
            result = search_context.backward(search_iter)

            if result[0] == True:
                buffer.select_range(result[1], result[2])
                self.document_view.source_view.scroll_to_iter(result[2], 0, False, 0, 0)
                self.set_match_counter(search_context.get_occurrence_position(result[1], result[2]), search_context.get_occurrences_count())
            else:
                search_iter = buffer.get_end_iter()
                result = search_context.backward(search_iter)

                if result[0] == True:
                    buffer.select_range(result[1], result[2])
                    self.document_view.source_view.scroll_to_iter(result[2], 0, False, 0, 0)
                    self.set_match_counter(search_context.get_occurrence_position(result[1], result[2]), search_context.get_occurrences_count())
    
    def on_search_entry_changed(self, entry):
        if self.document.get_buffer() != None:
            search_context = self.document.get_search_context()
            search_view = self.document_view.search_bar
            self.document.set_search_text(entry.get_text())
            search_view.replace_entry.set_text(entry.get_text())
            
            # scan buffer, then highlight match
            if len(entry.get_text()) > 0:
                buffer = self.document.get_buffer()
                result = search_context.forward(buffer.get_start_iter())
                if result[0] == False:
                    self.set_match_counter(-1, -1)
                    search_view.entry.get_style_context().add_class('error')
                    search_view.entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, 'face-uncertain-symbolic')
                    search_view.replace_button.set_sensitive(False)
                    search_view.replace_all_button.set_sensitive(False)
                else:
                    search_view.entry.get_style_context().remove_class('error')
                    search_view.entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, search_view.icon_name)
                    while search_context.get_occurrences_count() == -1 and result[0] == True:
                        result = search_context.forward(result[2])
                    self.on_search_next_match(entry, include_current_highlight=True)
                    search_view.replace_button.set_sensitive(True)
                    search_view.replace_all_button.set_sensitive(True)
            else:
                self.set_match_counter(-1, -1)
                search_view.entry.get_style_context().remove_class('error')
                search_view.entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, search_view.icon_name)
                search_view.replace_button.set_sensitive(False)
                search_view.replace_all_button.set_sensitive(False)
    
    def on_search_stop(self, entry=None):
        self.document_view.shortcuts_bar_bottom.button_find_and_replace.set_active(False)
        self.document_view.shortcuts_bar_bottom.button_find.set_active(False)

    def on_find_button_clicked(self, button_object=None):
        if button_object.get_active() == True:
            self.document_view.shortcuts_bar_bottom.button_find_and_replace.set_active(False)
            self.show_search_bar()
            self.set_mode_search()
        elif self.document_view.shortcuts_bar_bottom.button_find_and_replace.get_active() == False:
            self.hide_search_bar()

    def on_find_replace_button_clicked(self, button_object=None):
        if button_object.get_active() == True:
            self.document_view.shortcuts_bar_bottom.button_find.set_active(False)
            self.show_search_bar()
            self.set_mode_replace()
        elif self.document_view.shortcuts_bar_bottom.button_find.get_active() == False:
            self.hide_search_bar()

    def on_search_bar_size_allocate(self, search_bar=None, allocation=None):
        allocated_width = self.search_bar.get_allocated_width()
        if allocated_width < 640:
            self.search_bar.entry.set_size_request(270, -1)
            self.search_bar.replace_entry.set_size_request(105, -1)
            if self.search_bar.replace_wrapper.get_parent() == self.search_bar.super_box: return
            self.search_bar.box.remove(self.search_bar.replace_wrapper)
            self.search_bar.super_box.pack_start(self.search_bar.replace_wrapper, False, False, 0)
            self.search_bar.arrow.set_margin_left(6)
            self.search_bar.replace_entry.set_margin_right(60)
            self.search_bar.replace_wrapper.set_margin_top(6)
        else:
            if self.search_bar_mode == 'replace':
                self.search_bar.entry.set_size_request(230, -1)
            else:
                self.search_bar.entry.set_size_request(270, -1)
            self.search_bar.replace_entry.set_size_request(105, -1)
            if self.search_bar.replace_wrapper.get_parent() == self.search_bar.box: return
            self.search_bar.super_box.remove(self.search_bar.replace_wrapper)
            self.search_bar.box.pack_start(self.search_bar.replace_wrapper, False, False, 0)
            self.search_bar.arrow.set_margin_left(0)
            self.search_bar.replace_entry.set_margin_right(0)
            self.search_bar.replace_wrapper.set_margin_top(0)
            self.document_view.queue_draw()
        
    '''
    *** actions: search bar
    '''
    
    def show_search_bar(self):
        search_bar = self.document_view.search_bar
        search_bar.set_reveal_child(True)
        self.on_search_bar_size_allocate()
        GLib.idle_add(self.search_entry_grab_focus, None)
        
    def hide_search_bar(self):
        self.on_search_next_match(None, True)
        self.document_view.source_view.grab_focus()
        search_bar = self.document_view.search_bar
        search_bar.set_reveal_child(False)
        search_bar.entry.set_text('')
        
    def search_entry_grab_focus(self, args=None):
        entry = self.document_view.search_bar.entry
        did_set_text = self.set_text_current_selection()
        entry.grab_focus_without_selecting()
        entry.set_position(entry.get_text_length())
        if not did_set_text:
            entry.select_region(0, entry.get_text_length())
            self.on_search_entry_changed(entry)

    def set_mode_search(self):
        self.search_bar_mode = 'search'
        self.search_bar.replace_wrapper.hide()
    
    def set_mode_replace(self):
        self.search_bar_mode = 'replace'
        self.search_bar.replace_wrapper.show_all()
        
    def set_text_current_selection(self):
        buff = self.document.get_buffer()
        if buff != None and buff.get_has_selection():
            bounds = buff.get_selection_bounds()
            if len(bounds) > 0:
                if bounds[1].get_offset() - bounds[0].get_offset() <= 100:
                    selection = buff.get_text(bounds[0], bounds[1], True)
                else:
                    end = bounds[0].copy()
                    end.forward_chars(100)
                    selection = buff.get_text(bounds[0], end, True)
                search_bar = self.document_view.search_bar
                search_bar.entry.set_text(selection)
                return True
        return False

    '''
    *** control match counter
    '''

    def set_match_counter(self, match_no=-1, total=-1):
        search_bar = self.document_view.search_bar
        search_bar.match_counter.set_margin_end(6 + 2*search_bar.next_button.get_allocated_width())
        if total == -1:
            search_bar.match_counter.set_text('')
        else:
            search_bar.match_counter.set_text(str(match_no) + ' of ' + str(total))
            
    def on_match_counter_size_allocate(self, widget=None, allocation=None):
        search_bar = self.document_view.search_bar
        allocated_width = search_bar.match_counter.get_allocated_width()
        if allocated_width < 5:
            number = str(6)
        else:
            number = str(12 + allocated_width)
        search_bar.entry_css_provider.load_from_data(('entry { padding-right: ' + number + 'px; }').encode('utf-8'))
        

