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
gi.require_version('GtkSource', '5')
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GtkSource

import setzer.document.search.search_viewgtk as search_view
from setzer.helpers.observable import Observable
from setzer.dialogs.dialog_locator import DialogLocator
from setzer.helpers.timer import timer


class Search(Observable):

    def __init__(self, document, document_view):
        Observable.__init__(self)

        self.view = search_view.SearchBar()
        self.search_bar_mode = None

        self.document_view = document_view
        self.document = document
        self.document_view.vbox.append(self.view)

        self.search_settings = GtkSource.SearchSettings()
        self.search_context = GtkSource.SearchContext.new(self.document.source_buffer, self.search_settings)
        self.search_context.set_highlight(True)

        self.view.entry.connect('changed', self.on_search_entry_changed)
        self.view.entry.connect('stop_search', self.on_search_stop)
        self.view.entry.connect('next_match', self.on_search_next_match)
        self.view.entry.connect('previous_match', self.on_search_previous_match)
        self.view.entry.connect('activate', self.on_search_entry_activate)
        self.view.close_button.connect('clicked', self.on_search_close_button_click)
        self.view.next_button.connect('clicked', self.on_search_next_button_click)
        self.view.prev_button.connect('clicked', self.on_search_prev_button_click)
        self.view.replace_button.connect('clicked', self.on_replace_button_click)
        self.view.replace_all_button.connect('clicked', self.on_replace_all_button_click)
        self.document.connect('cursor_position_changed', self.on_selection_might_have_changed)

    def on_selection_might_have_changed(self, document):
        self.update_replace_button()

    def on_search_close_button_click(self, button_object=None):
        self.on_search_stop()

    def on_search_next_button_click(self, button_object=None):
        self.on_search_next_match()
        
    def on_search_prev_button_click(self, button_object=None):
        self.on_search_previous_match()
        
    def on_replace_button_click(self, button_object=None):
        replacement = self.view.replace_entry.get_text()
        bounds = self.search_context.get_buffer().get_selection_bounds()
        if len(bounds) == 2:
            self.search_context.replace(*bounds, replacement, -1)
            self.on_search_next_match()

    def on_replace_all_button_click(self, button_object=None):
        original = self.view.entry.get_text()
        replacement = self.view.replace_entry.get_text()
        number_of_occurrences = self.search_context.get_occurrences_count()

        if number_of_occurrences > 0:
            dialog = DialogLocator.get_dialog('replace_confirmation')
            dialog.run(original, replacement, number_of_occurrences, self.search_context)

    def on_search_entry_activate(self, entry=None):
        self.on_search_next_match(entry, True)
        self.document_view.source_view.grab_focus()

    def on_search_next_match(self, entry=None, include_current_highlight=False):
        buffer = self.search_context.get_buffer()
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        bound_iter = buffer.get_iter_at_mark(buffer.get_selection_bound())

        if include_current_highlight:
            if insert_iter.get_offset() < bound_iter.get_offset(): search_iter = insert_iter
            else: search_iter = bound_iter
            result = self.search_context.forward(search_iter)
        else:
            if insert_iter.get_offset() < bound_iter.get_offset(): search_iter = bound_iter
            else: search_iter = insert_iter
            result = self.search_context.forward(search_iter)

        if result[0] == True:
            buffer.select_range(result[2], result[1])
            self.document.scroll_cursor_onscreen()
            self.set_match_counter(self.search_context.get_occurrence_position(result[1], result[2]), self.search_context.get_occurrences_count())
        else:
            search_iter = buffer.get_start_iter()
            result = self.search_context.forward(search_iter)

            if result[0] == True:
                buffer.select_range(result[2], result[1])
                self.document.scroll_cursor_onscreen()
                self.set_match_counter(self.search_context.get_occurrence_position(result[1], result[2]), self.search_context.get_occurrences_count())
    
    def on_search_previous_match(self, entry=None):
        buffer = self.search_context.get_buffer()
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        bound_iter = buffer.get_iter_at_mark(buffer.get_selection_bound())
        
        if insert_iter.get_offset() > bound_iter.get_offset(): search_iter = bound_iter
        else: search_iter = insert_iter
        result = self.search_context.backward(search_iter)

        if result[0] == True:
            buffer.select_range(result[1], result[2])
            self.document.scroll_cursor_onscreen()
            self.set_match_counter(self.search_context.get_occurrence_position(result[1], result[2]), self.search_context.get_occurrences_count())
        else:
            search_iter = buffer.get_end_iter()
            result = self.search_context.backward(search_iter)

            if result[0] == True:
                buffer.select_range(result[1], result[2])
                self.document.scroll_cursor_onscreen()
                self.set_match_counter(self.search_context.get_occurrence_position(result[1], result[2]), self.search_context.get_occurrences_count())

    def on_search_entry_changed(self, entry):
        search_view = self.view
        self.search_settings.set_search_text(entry.get_text())
        search_view.replace_entry.set_text(entry.get_text())

        # scan buffer, then highlight match
        if len(entry.get_text()) > 0:
            buffer = self.search_context.get_buffer()
            result = self.search_context.forward(buffer.get_start_iter())
            if result[0] == False:
                self.set_match_counter(-1, -1)
                search_view.entry.get_style_context().add_class('error')
                search_view.replace_all_button.set_sensitive(False)
            else:
                search_view.entry.get_style_context().remove_class('error')
                while self.search_context.get_occurrences_count() == -1 and result[0] == True:
                    result = self.search_context.forward(result[2])
                self.on_search_next_match(entry, include_current_highlight=True)
                search_view.replace_all_button.set_sensitive(True)
        else:
            self.set_match_counter(-1, -1)
            search_view.entry.get_style_context().remove_class('error')
            search_view.replace_all_button.set_sensitive(False)

    def update_replace_button(self):
        selected_text = self.document.get_selected_text()
        if selected_text != None and selected_text == self.view.entry.get_text():
            self.view.replace_button.set_sensitive(True)
        else:
            self.view.replace_button.set_sensitive(False)

    def on_search_stop(self, entry=None):
        self.hide_search_bar()

    '''
    *** actions: search bar
    '''

    def hide_search_bar(self):
        self.on_search_next_match(None, True)
        self.document_view.source_view.grab_focus()
        self.view.set_reveal_child(False)
        self.view.entry.set_text('')
        self.search_bar_mode = None
        self.add_change_code('mode_changed')

    def set_mode_search(self):
        self.view.set_reveal_child(True)
        GLib.idle_add(self.search_entry_grab_focus, None)
        self.search_bar_mode = 'search'
        self.view.entry.set_size_request(300, -1)
        self.view.match_counter.set_size_request(270, -1)
        self.view.replace_wrapper.set_visible(False)
        self.add_change_code('mode_changed')

    def set_mode_replace(self):
        self.view.set_reveal_child(True)
        GLib.idle_add(self.search_entry_grab_focus, None)
        self.search_bar_mode = 'replace'
        self.view.entry.set_size_request(230, -1)
        self.view.match_counter.set_size_request(200, -1)
        self.view.replace_wrapper.set_visible(True)
        self.add_change_code('mode_changed')

    def search_entry_grab_focus(self, args=None):
        entry = self.view.entry

        selection = self.document.get_selected_text()
        if selection != None:
            entry.set_text(selection)

        entry.grab_focus()
        entry.set_position(len(entry.get_text()))

        if selection == None:
            entry.select_region(0, len(entry.get_text()))
            self.on_search_entry_changed(entry)

    def set_match_counter(self, match_no=-1, total=-1):
        search_bar = self.view
        search_bar.match_counter.set_margin_end(6 + 2*search_bar.next_button.get_allocated_width())
        if total == -1:
            search_bar.match_counter.set_text('')
            search_bar.prev_button.set_sensitive(False)
            search_bar.next_button.set_sensitive(False)
        else:
            search_bar.match_counter.set_text(str(match_no) + ' of ' + str(total))
            search_bar.prev_button.set_sensitive(True)
            search_bar.next_button.set_sensitive(True)


